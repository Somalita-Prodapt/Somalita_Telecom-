from pathlib import Path
from itertools import combinations
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer, CountVectorizer
from sklearn.preprocessing import normalize
import joblib
import hashlib
import logging
from sklearn.metrics.pairwise import cosine_similarity
from .preprocessing import load_dataset, build_document, chunk_document
from src.utils.config import DATASET_PATH, SEMANTIC_WEIGHT, LEXICAL_WEIGHT, EMBEDDING_MODEL, USE_SENTENCE_TRANSFORMERS, VECTOR_DB_PATH, SEMANTIC_CANDIDATES, LEXICAL_CANDIDATES, STORAGE_PATH

logger = logging.getLogger("netops.retriever")


class HybridRetriever:
    """Hybrid keyword + semantic retrieval with robust metadata filtering."""

    FILTER_COLUMNS = {
        'state': 'State',
        'city': 'City',
        'season': 'Season',
        'weather': 'Weather',
    }

    def __init__(self):
        path = DATASET_PATH if DATASET_PATH.exists() else None
        self.df = load_dataset(path)
        # Build incident text vectorized across the full dataframe. Avoid row-by-row
        # Python iteration here because 100K rows would make startup unnecessarily slow.
        columns = [str(c) for c in self.df.columns]
        rows = self.df.fillna('').astype(str).itertuples(index=False, name=None)
        # Include column names so natural-language queries (e.g. 'latency', 'handover', 'alarm')
        # match the evidence fields instead of searching only unlabelled cell values.
        self.documents = [' | '.join(f'{col}: {value}' for col, value in zip(columns, row)) for row in rows]
        self.vectorizer = HashingVectorizer(
            ngram_range=(1, 2), n_features=2**17, alternate_sign=False,
            norm='l2', lowercase=True, stop_words='english'
        )
        self.semantic_vectorizer = HashingVectorizer(
            analyzer='word', ngram_range=(1, 3), n_features=2**16,
            alternate_sign=False, norm='l2', lowercase=True, stop_words='english'
        )
        # Persistent sparse-index cache keyed by dataset file metadata and row count.
        # It accelerates restarts without shipping generated cache files or altering source data.
        source_path = DATASET_PATH if DATASET_PATH.exists() else None
        source_sig = f"{source_path}:{source_path.stat().st_size}:{source_path.stat().st_mtime_ns}" if source_path else f"sample:{len(self.df)}"
        cache_key = hashlib.sha256((source_sig + f":{len(self.documents)}:hash-bm25-v2-labelled-docs").encode()).hexdigest()[:20]
        cache_dir = STORAGE_PATH / 'retrieval_cache'
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"indices_{cache_key}.joblib"
        cached = None
        if cache_file.exists():
            try:
                cached = joblib.load(cache_file)
                if cached.get('doc_count') != len(self.documents): cached = None
            except Exception:
                cached = None
        if cached:
            self.lexical_matrix = cached['lexical_matrix']
            self.semantic_matrix = cached['semantic_matrix']
            self.bm25_vectorizer = cached['bm25_vectorizer']
            self.bm25_matrix = cached['bm25_matrix']
            self.bm25_idf = cached['bm25_idf']
            self.doc_lengths = cached['doc_lengths']
            self.avg_doc_length = cached['avg_doc_length']
            logger.info('retrieval_index_cache=hit rows=%d', len(self.documents))
        else:
            self.lexical_matrix = self.vectorizer.transform(self.documents)
            self.semantic_matrix = self.semantic_vectorizer.transform(self.documents)
            self.bm25_vectorizer = CountVectorizer(lowercase=True, stop_words='english', max_features=150000, token_pattern=r"(?u)\b\w\w+\b", dtype=np.float32)
            self.bm25_matrix = self.bm25_vectorizer.fit_transform(self.documents).tocsr()
            dfreq = np.asarray((self.bm25_matrix > 0).sum(axis=0)).ravel()
            n_docs = max(1, self.bm25_matrix.shape[0])
            self.bm25_idf = np.log(1.0 + (n_docs - dfreq + 0.5) / (dfreq + 0.5)).astype(np.float32)
            self.doc_lengths = np.asarray(self.bm25_matrix.sum(axis=1)).ravel().astype(np.float32)
            self.avg_doc_length = float(self.doc_lengths.mean()) if len(self.doc_lengths) else 1.0
            try:
                joblib.dump({'doc_count':len(self.documents),'lexical_matrix':self.lexical_matrix,'semantic_matrix':self.semantic_matrix,
                    'bm25_vectorizer':self.bm25_vectorizer,'bm25_matrix':self.bm25_matrix,'bm25_idf':self.bm25_idf,
                    'doc_lengths':self.doc_lengths,'avg_doc_length':self.avg_doc_length}, cache_file, compress=1)
                logger.info('retrieval_index_cache=created rows=%d path=%s', len(self.documents), cache_file)
            except Exception as exc:
                logger.warning('retrieval_index_cache=write_failed error=%s', type(exc).__name__)
        self.embedder = None
        if USE_SENTENCE_TRANSFORMERS:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedder = SentenceTransformer(EMBEDDING_MODEL)
            except Exception:
                self.embedder = None
        self._chroma = None
        self._prepare_chroma()

    @staticmethod
    def _clean_filter(value):
        if value is None:
            return None
        value = str(value).strip()
        if not value or value.lower() in {'all', 'none', 'null'}:
            return None
        return value

    def _prepare_chroma(self):
        if not self.embedder:
            return
        # Do not synchronously encode/build a vector database for the 100K dataset.
        # Full-dataset TF-IDF semantic retrieval remains active; embeddings stay an
        # optional acceleration for smaller explicitly configured datasets.
        if len(self.documents) > 20000:
            return
        try:
            import chromadb
            VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))
            name = 'netops_incidents'
            collection = client.get_or_create_collection(name)
            if collection.count() != len(self.documents):
                try:
                    client.delete_collection(name)
                except Exception:
                    pass
                collection = client.create_collection(name)
                for start in range(0, len(self.documents), 500):
                    end = min(start + 500, len(self.documents))
                    ids = self.df.iloc[start:end].incident_id.tolist()
                    docs = self.documents[start:end]
                    metas = []
                    for _, r in self.df.iloc[start:end].iterrows():
                        metas.append({k: ('' if pd_isna(v) else str(v)) for k, v in r.to_dict().items()})
                    emb = self.embedder.encode(docs, normalize_embeddings=True, show_progress_bar=False).tolist()
                    collection.add(ids=ids, documents=docs, metadatas=metas, embeddings=emb)
            self._chroma = collection
        except Exception:
            self._chroma = None

    def network_condition(self, row):
        def num(col, default=0.0):
            try:
                return float(row.get(col, default))
            except (TypeError, ValueError):
                return default

        if num('Packet Loss Rate (%)') >= 5 or num('Latency (ms)') >= 80:
            return 'Degraded'
        if num('Throughput (Mbps)') < 500 or num('Cell Availability (%)') < 95:
            return 'At Risk'
        return 'Healthy'

    def _filter_mask(self, state=None, city=None, season=None, weather=None, network_condition=None):
        values = {
            'state': self._clean_filter(state),
            'city': self._clean_filter(city),
            'season': self._clean_filter(season),
            'weather': self._clean_filter(weather),
            'network_condition': self._clean_filter(network_condition),
        }
        mask = np.ones(len(self.df), dtype=bool)
        for key, col in self.FILTER_COLUMNS.items():
            val = values[key]
            if val is not None:
                # Strip whitespace and compare case-insensitively. This prevents harmless
                # CSV formatting differences from making a valid dropdown selection fail.
                series = self.df[col].fillna('').astype(str).str.strip().str.casefold()
                mask &= series.eq(val.casefold()).to_numpy()
        if values['network_condition'] is not None:
            cond = self.df.apply(self.network_condition, axis=1)
            mask &= cond.astype(str).str.strip().str.casefold().eq(values['network_condition'].casefold()).to_numpy()
        return mask

    def _filtered_indices(self, state=None, city=None, season=None, weather=None, network_condition=None):
        return np.where(self._filter_mask(state, city, season, weather, network_condition))[0]

    def filter_diagnostics(self, state=None, city=None, season=None, weather=None, network_condition=None):
        """Explain exactly how many rows remain after each selected filter."""
        selected = {
            'State': self._clean_filter(state),
            'City': self._clean_filter(city),
            'Season': self._clean_filter(season),
            'Weather': self._clean_filter(weather),
            'Network Condition': self._clean_filter(network_condition),
        }
        selected = {k: v for k, v in selected.items() if v is not None}
        counts = {}
        for label, value in selected.items():
            kwargs = {
                'state': state if label != 'State' else None,
                'city': city if label != 'City' else None,
                'season': season if label != 'Season' else None,
                'weather': weather if label != 'Weather' else None,
                'network_condition': network_condition if label != 'Network Condition' else None,
            }
            counts[label] = int(self._filter_mask(**kwargs).sum())

        exact = int(self._filter_mask(state, city, season, weather, network_condition).sum())
        return {
            'total_incidents': int(len(self.df)),
            'selected_filters': selected,
            'exact_match_count': exact,
            'single_filter_counts': counts,
        }

    def _semantic_candidates(self, query, allowed, n):
        if not self.embedder or self._chroma is None or len(allowed) == 0:
            return {}
        try:
            res = self._chroma.query(
                query_texts=None,
                query_embeddings=self.embedder.encode([query], normalize_embeddings=True).tolist(),
                n_results=min(max(n, 10), len(self.documents)),
                include=['distances', 'ids']
            )
            ids = res.get('ids', [[]])[0]
            distances = res.get('distances', [[]])[0]
            allowed_ids = set(self.df.iloc[allowed].incident_id)
            return {iid: max(0.0, 1.0 - float(d)) for iid, d in zip(ids, distances) if iid in allowed_ids}
        except Exception:
            return {}

    def _bm25_scores(self, query, indices):
        """Compute Okapi BM25 scores for the supplied document row indices."""
        if len(indices) == 0:
            return np.zeros(0, dtype=np.float32)
        q_counts = self.bm25_vectorizer.transform([query])
        terms = q_counts.indices
        if len(terms) == 0:
            return np.zeros(len(indices), dtype=np.float32)
        lengths = self.doc_lengths[indices]
        avg_len = max(self.avg_doc_length, 1.0)
        k1, b = 1.5, 0.75
        scores = np.zeros(len(indices), dtype=np.float32)
        matrix = self.bm25_matrix[indices]
        for term in terms:
            tf = matrix[:, int(term)].toarray().ravel().astype(np.float32)
            denom = tf + k1 * (1.0 - b + b * lengths / avg_len)
            scores += self.bm25_idf[int(term)] * (tf * (k1 + 1.0) / np.maximum(denom, 1e-9))
        # Bounded transform makes BM25 comparable with cosine similarities for blending.
        return scores / (scores + 8.0)

    def search(self, query, top_k=None, state=None, city=None, season=None, weather=None, network_condition=None, offset=0, page_size=500):
        """Rank every matching record, but materialize only one UI page.

        The full filtered dataset is scored; ``page_size`` only controls how many
        result objects are serialized for the caller. ``top_k`` remains supported
        for backwards compatibility with older evaluation/API clients.
        """
        idx = self._filtered_indices(state, city, season, weather, network_condition)
        if len(idx) == 0:
            return []

        qsem = self.semantic_vectorizer.transform([query])
        sem_all = cosine_similarity(qsem, self.semantic_matrix[idx]).ravel()
        qlex = self.vectorizer.transform([query])
        lex_all = cosine_similarity(qlex, self.lexical_matrix[idx]).ravel()
        bm25_all = self._bm25_scores(query, idx)
        combined_all = 0.45 * sem_all + 0.20 * lex_all + 0.35 * bm25_all
        order = np.argsort(-combined_all, kind='stable')

        total = len(order)
        if top_k is not None:
            order = order[:min(int(top_k), total)]
            total = len(order)

        start = max(0, int(offset))
        stop = min(start + max(1, int(page_size)), len(order))
        page_order = order[start:stop]

        out = []
        for p in page_order:
            i = int(idx[int(p)])
            row = self.df.iloc[i]
            out.append({
                'incident_id': row.incident_id,
                'score': round(float(combined_all[int(p)]), 6),
                'semantic_score': round(float(sem_all[int(p)]), 6),
                'lexical_score': round(float(lex_all[int(p)]), 6),
                'bm25_score': round(float(bm25_all[int(p)]), 6),
                'network_condition': self.network_condition(row),
                'metadata': row.to_dict(),
                'document': self.documents[i],
            })
        return out

    def search_export_dataframe(self, query, state=None, city=None, season=None, weather=None, network_condition=None):
        """Return every matching row with full-dataset hybrid scores for CSV export."""
        idx = self._filtered_indices(state, city, season, weather, network_condition)
        if len(idx) == 0:
            return self.df.iloc[0:0].copy()
        qsem=self.semantic_vectorizer.transform([query])
        qlex=self.vectorizer.transform([query])
        sem=cosine_similarity(qsem,self.semantic_matrix[idx]).ravel()
        lex=cosine_similarity(qlex,self.lexical_matrix[idx]).ravel()
        bm25=self._bm25_scores(query, idx)
        combined=0.45*sem + 0.20*lex + 0.35*bm25
        order=np.argsort(-combined,kind='stable')
        out=self.df.iloc[idx[order]].copy()
        out.insert(0,'hybrid_score',combined[order])
        out.insert(1,'semantic_score',sem[order])
        out.insert(2,'lexical_score',lex[order])
        out.insert(3,'bm25_score',bm25[order])
        return out

    def nearest_filter_matches(self, query, top_k=None, state=None, city=None, season=None, weather=None, network_condition=None):
        """Return transparent near-matches when an exact filter combination has no rows.

        The method relaxes the smallest possible number of selected filters. It never
        silently pretends a relaxed result is an exact match; the caller receives the
        relaxed filter names explicitly.
        """
        filters = [
            ('state', state), ('city', city), ('season', season),
            ('weather', weather), ('network_condition', network_condition)
        ]
        active = [name for name, value in filters if self._clean_filter(value) is not None]
        if not active:
            return [], []

        # Prefer the smallest relaxation. Among equally small relaxations, prefer the
        # one leaving the largest number of historical rows for useful evidence.
        best = None
        for drop_count in range(1, len(active) + 1):
            candidates = []
            for dropped in combinations(active, drop_count):
                args = {
                    'state': state, 'city': city, 'season': season,
                    'weather': weather, 'network_condition': network_condition
                }
                for key in dropped:
                    args[key] = None
                count = int(self._filter_mask(**args).sum())
                if count > 0:
                    candidates.append((count, dropped, args))
            if candidates:
                best = max(candidates, key=lambda x: x[0])
                break

        if not best:
            return [], active
        count, dropped, args = best
        results = self.search(query, top_k, **args)
        return results, list(dropped)


def pd_isna(v):
    try:
        import pandas as pd
        return bool(pd.isna(v))
    except Exception:
        return v is None
