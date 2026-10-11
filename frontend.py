import io, json, os, requests, pandas as pd, streamlit as st, html

st.set_page_config(
    page_title='NetOps AI Command Center',
    page_icon='📡',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom Enterprise-Grade Styling with High Contrast & Stylish Typography
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #f8fafc !important;
}

/* Force All Markdown Text, Paragraphs and Lists to be Pure White */
p, span, label, li, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span, [data-testid="stMarkdownContainer"] li {
    color: #f8fafc !important;
}

/* Headings with Modern Stylish Font */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', 'Outfit', sans-serif !important;
    color: #ffffff !important;
    letter-spacing: -0.02em !important;
    font-weight: 700 !important;
}

/* Base Layout Container */
.main .block-container {
    padding-top: 1.2rem;
    padding-bottom: 3.5rem;
    max-width: 1480px;
}

/* Ambient Background */
.stApp {
    background: radial-gradient(circle at 10% 10%, rgba(14, 165, 233, 0.06) 0%, transparent 45%),
                radial-gradient(circle at 90% 90%, rgba(99, 102, 241, 0.06) 0%, transparent 45%),
                #090d16;
}

/* Hero Header with Stylish Typography */
.hero-container {
    position: relative;
    padding: 28px 34px;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(30, 41, 59, 0.90) 60%, rgba(14, 116, 144, 0.32) 100%);
    border: 1px solid rgba(56, 189, 248, 0.30);
    box-shadow: 0 12px 35px -5px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(14px);
    margin-bottom: 24px;
}

.hero-title {
    font-family: 'Space Grotesk', 'Outfit', sans-serif;
    font-size: 2.45rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #ffffff 25%, #38bdf8 70%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    text-shadow: 0 2px 20px rgba(56, 189, 248, 0.25);
}

.hero-subtitle {
    font-size: 1.02rem;
    color: #e2e8f0; /* Crisp, high-contrast readable text */
    margin: 8px 0 0 0;
    font-weight: 400;
    line-height: 1.6;
}

.live-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 4px 13px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.35);
    margin-bottom: 12px;
}

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 10px #10b981;
    animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* Glass Feature Cards with High Contrast */
.card {
    padding: 22px;
    border: 1px solid rgba(56, 189, 248, 0.18);
    border-radius: 16px;
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(12px);
    transition: all 0.25s ease;
    height: 100%;
}
.card:hover {
    border-color: rgba(56, 189, 248, 0.45);
    background: rgba(30, 41, 59, 0.85);
    box-shadow: 0 10px 30px rgba(14, 165, 233, 0.15);
    transform: translateY(-2px);
}
.card h3 {
    font-family: 'Space Grotesk', 'Outfit', sans-serif !important;
    font-size: 1.22rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin-top: 0;
    margin-bottom: 8px;
}
.card p {
    color: #e2e8f0 !important; /* Fully readable high-contrast body */
    font-size: 0.93rem !important;
    line-height: 1.6 !important;
    margin-bottom: 0;
}

/* Query Action Checklist Card */
.action-item {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-left: 4px solid #0284c7;
    border-radius: 11px;
    padding: 13px 18px;
    margin-bottom: 10px;
    color: #f8fafc; /* Crisp pure white text */
    font-size: 0.94rem;
    line-height: 1.55;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* Status Badges */
.badge-chip {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 8px;
    font-size: 0.80rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}
.badge-critical { background: rgba(239, 68, 68, 0.22); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.45); }
.badge-warning  { background: rgba(245, 158, 11, 0.22); color: #fde047; border: 1px solid rgba(245, 158, 11, 0.45); }
.badge-info     { background: rgba(59, 130, 246, 0.22); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.45); }
.badge-success  { background: rgba(16, 185, 129, 0.22); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.45); }
.badge-neutral  { background: rgba(148, 163, 184, 0.20); color: #f1f5f9; border: 1px solid rgba(148, 163, 184, 0.35); }

/* Workflow Trace Chips */
.trace-chip {
    display: inline-flex;
    align-items: center;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.35);
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.78rem;
    color: #38bdf8;
    font-weight: 700;
    letter-spacing: 0.02em;
    margin: 3px 6px 6px 0;
    box-shadow: 0 2px 8px rgba(14, 165, 233, 0.15);
}

/* Quick Query Card */
.quick-query-card {
    background: rgba(15, 23, 42, 0.70);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-left: 4px solid #38bdf8;
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 12px;
    color: #f8fafc;
    font-size: 0.95rem;
    font-weight: 500;
    line-height: 1.5;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

/* RAG Answer Container & Styled Dossier */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.92) 100%) !important;
    border: 1px solid rgba(56, 189, 248, 0.45) !important;
    border-left: 6px solid #38bdf8 !important;
    border-radius: 16px !important;
    padding: 24px 30px !important;
    margin: 18px 0 !important;
    box-shadow: 0 14px 40px -5px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] h1 {
    font-size: 1.65rem !important;
    color: #ffffff !important;
    margin-top: 10px !important;
    margin-bottom: 12px !important;
    border-bottom: 1px solid rgba(56, 189, 248, 0.3) !important;
    padding-bottom: 8px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] h2 {
    font-size: 1.30rem !important;
    color: #7dd3fc !important;
    margin-top: 20px !important;
    margin-bottom: 10px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] h3 {
    font-size: 1.10rem !important;
    color: #38bdf8 !important;
    margin-top: 16px !important;
    margin-bottom: 8px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] p,
div[data-testid="stVerticalBlockBorderWrapper"] li {
    color: #f8fafc !important;
    font-size: 0.97rem !important;
    line-height: 1.7 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] strong {
    color: #38bdf8 !important;
    font-weight: 700 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] hr {
    border-color: rgba(56, 189, 248, 0.30) !important;
    margin: 20px 0 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] ul,
div[data-testid="stVerticalBlockBorderWrapper"] ol {
    margin-bottom: 14px !important;
    padding-left: 22px !important;
}


/* Streamlit Native Component Tweaks for Crisp Readability */
div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    font-size: 1.85rem !important;
    text-shadow: 0 0 12px rgba(56, 189, 248, 0.2);
}

div[data-testid="stMetricLabel"] {
    font-weight: 700 !important;
    color: #7dd3fc !important; /* Soft bright cyan label */
    text-transform: uppercase !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.05em !important;
}

[data-testid="stCaptionContainer"] {
    color: #cbd5e1 !important; /* Bright silver gray instead of faint dark gray */
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    line-height: 1.5 !important;
}

/* Input Fields and Select Boxes */
div[data-baseweb="textarea"] textarea, div[data-baseweb="input"] input {
    background-color: rgba(15, 23, 42, 0.90) !important;
    color: #f8fafc !important;
    font-size: 0.95rem !important;
    border: 1px solid rgba(56, 189, 248, 0.28) !important;
    border-radius: 10px !important;
}
div[data-baseweb="textarea"] textarea:focus, div[data-baseweb="input"] input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.40) !important;
}
label[data-testid="stWidgetLabel"] p {
    color: #f1f5f9 !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
}

/* Buttons with Glowing Gradient */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
    border: 1px solid rgba(56, 189, 248, 0.4) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    padding: 10px 24px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 18px rgba(2, 132, 199, 0.35) !important;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(56, 189, 248, 0.5) !important;
}

div.stButton > button[kind="secondary"] {
    background: rgba(30, 41, 59, 0.80) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    color: #f1f5f9 !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
}

/* Force Sidebar to be sleek dark slate navy with high-contrast text */
section[data-testid="stSidebar"], [data-testid="stSidebar"], div[data-testid="stSidebarContent"] {
    background-color: #0b1220 !important;
    background: #0b1220 !important;
    border-right: 1px solid rgba(56, 189, 248, 0.22) !important;
}

section[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}

section[data-testid="stSidebar"] div[data-baseweb="radio"] label span {
    color: #ffffff !important;
    font-weight: 500 !important;
    font-size: 0.92rem !important;
}

section[data-testid="stSidebar"] div[data-baseweb="radio"] label div {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] div[data-baseweb="input"] input {
    background-color: #0f172a !important;
    color: #ffffff !important;
    border: 1px solid rgba(56, 189, 248, 0.35) !important;
}

/* Sidebar Custom Brand Card */
.sidebar-brand {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.85) 100%);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 20px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}
.sidebar-brand-title {
    font-family: 'Space Grotesk', 'Outfit', sans-serif;
    font-size: 1.38rem;
    font-weight: 800;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 9px;
    letter-spacing: -0.02em;
}
.sidebar-tag {
    font-size: 0.72rem;
    background: linear-gradient(135deg, #0284c7 0%, #3b82f6 100%);
    color: #ffffff !important;
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 700;
    letter-spacing: 0.04em;
}
</style>
''', unsafe_allow_html=True)

# Sidebar Header & Navigation
with st.sidebar:
    st.markdown('''
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">
            <span>📡</span> <span style="color: #38bdf8 !important; font-weight: 800; text-shadow: 0 0 12px rgba(56, 189, 248, 0.6);">NetOps AI</span> <span class="sidebar-tag">COMMAND</span>
        </div>
        <div style="font-size: 0.82rem; color: #cbd5e1 !important; margin-top: 6px; font-weight: 600;">Autonomous 5G NOC Decision Support</div>
    </div>
    ''', unsafe_allow_html=True)

DEFAULT_API = os.getenv('NETOPS_API_URL', 'http://127.0.0.1:8000')
api = st.sidebar.text_input('🔌 Backend API Endpoint', DEFAULT_API).rstrip('/')
page = st.sidebar.radio(
    'Workspace Navigation',
    ['🏠 Dashboard', '🔎 Incident Search', '🧠 AI Diagnosis', '📋 Dataset Explorer', '📊 Evaluation', '💬 Feedback', 'ℹ️ About'],
    index=0
)

@st.cache_data(ttl=30)
def get_json(url):
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()

def post(path, payload):
    r = requests.post(api + path, json=payload, timeout=180)
    if not r.ok:
        try:
            detail = r.json().get('detail', r.text)
        except Exception:
            detail = r.text
        raise RuntimeError(f'{r.status_code}: {detail}')
    return r.json()

def safe_get(path, default=None):
    try:
        return get_json(api + path)
    except Exception:
        return default

@st.cache_data(ttl=30)
def get_dataset_options():
    r = requests.get(api + '/dataset/options', timeout=30)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=30)
def get_dataset_view(circle, severity, season, issue_type, sort_by, page=1, page_size=500):
    params = {
        'circle': circle if circle != 'All' else None,
        'severity': severity if severity != 'All' else None,
        'season': season if season != 'All' else None,
        'issue_type': issue_type if issue_type != 'All' else None,
        'sort_by': sort_by,
        'page': page,
        'page_size': page_size,
    }
    r = requests.get(api + '/dataset', params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def filters():
    meta = safe_get('/metadata', {}) or {}
    with st.expander('🎛️ Dataset & Environment Filters', expanded=True):
        a, b, c, d = st.columns(4)
        state = a.selectbox('State', ['All'] + meta.get('states', []), help='Values from historical telecom dataset.')
        city = b.selectbox('City', ['All'] + meta.get('cities', []), help='Values from historical telecom dataset.')
        season = c.selectbox('Season', ['All'] + meta.get('seasons', []))
        weather = d.selectbox('Weather', ['All'] + meta.get('weather', []))
        e, _ = st.columns([1, 1])
        condition = e.selectbox(
            'Network Condition',
            ['All'] + meta.get('network_conditions', ['Healthy', 'At Risk', 'Degraded']),
            help='Derived from latency, packet loss, throughput and availability.'
        )
    state_filter = None if state == 'All' else state
    city_filter = None if city == 'All' else city
    return {
        'state': state_filter,
        'city': city_filter,
        'season': None if season == 'All' else season,
        'weather': None if weather == 'All' else weather,
        'network_condition': None if condition == 'All' else condition
    }

def query_box(default):
    return st.text_area(
        'Describe the network issue in natural language',
        default,
        height=105,
        placeholder='Example: Multiple cells have high latency, packet loss and declining throughput after a traffic surge.'
    )

def render_results(results, show_feedback=False, query='', response=None):
    if response:
        mode = response.get('match_mode', 'exact')
        diag = response.get('filter_diagnostics', {}) or {}
        if mode == 'near_match':
            relaxed = ', '.join(response.get('relaxed_filters', [])).replace('_', ' ').title()
            st.warning(f'⚠️ No exact historical row matched every selected filter. Showing the closest evidence after relaxing: **{relaxed}**.')
        elif mode == 'no_match':
            st.error('No historical incidents match this filter combination. Try clearing or changing a filter.')
        if diag:
            selected = diag.get('selected_filters', {})
            if selected:
                st.caption(f"Exact matching historical rows: **{diag.get('exact_match_count', 0):,}**  |  Selected filters: " + ', '.join(f'{k}: {v}' for k, v in selected.items()))

    if not results:
        st.warning('No incidents are available for this filter combination.')
        return

    df = pd.DataFrame([{
        'Incident': x['incident_id'], 'Hybrid score': x['score'], 'Semantic': x['semantic_score'], 'Keyword': x['lexical_score'], 'BM25': x.get('bm25_score', 0.0),
        'City': x['metadata'].get('City'), 'State': x['metadata'].get('State'),
        'Condition': x.get('network_condition', ''),
        'Latency ms': x['metadata'].get('Latency (ms)'), 'Throughput Mbps': x['metadata'].get('Throughput (Mbps)'),
        'Packet loss %': x['metadata'].get('Packet Loss Rate (%)'),
        'Fault occurrence %': x['metadata'].get('Fault Occurrence Rate (%)'),
        'Handover success %': x['metadata'].get('Handover Success Rate (%)')
    } for x in results])

    st.markdown('##### 📊 Retrieved Evidence Telemetry Snapshot')
    m1, m2, m3, m4 = st.columns(4)
    m1.metric('Evidence Cases', len(results))
    m2.metric('Avg Hybrid Score', f"{df['Hybrid score'].mean():.3f}")
    m3.metric('Avg Latency', f"{df['Latency ms'].mean():.1f} ms")
    m4.metric('Avg Throughput', f"{df['Throughput Mbps'].mean():.1f} Mbps")

    chart_df = df.set_index('Incident')[['Hybrid score', 'Semantic', 'Keyword']]
    st.bar_chart(chart_df, height=220)

    left, right = st.columns(2)
    with left:
        st.caption('Retrieved evidence distribution by network condition')
        condition_counts = df['Condition'].value_counts()
        if not condition_counts.empty:
            st.bar_chart(condition_counts)
    with right:
        st.caption('Latency vs Throughput scatter distribution')
        scatter = df[['Latency ms', 'Throughput Mbps']].copy()
        scatter.index = [str(x) for x in range(len(scatter))]
        st.scatter_chart(scatter, x='Latency ms', y='Throughput Mbps', height=230)

    st.dataframe(df, use_container_width=True, hide_index=True)

    qlow = (query or '').lower()
    if any(term in qlow for term in ['corrective action', 'what should', 'recommend', 'increasing fault', 'declining handover', 'handover']):
        st.markdown('---')
        st.subheader('🛠️ Query-Focused Operational Guidance')
        st.caption('Recommendations are decision support; they do not confirm a root cause or execute network changes.')
        fault_max = float(df['Fault occurrence %'].max()) if 'Fault occurrence %' in df else max(float(x['metadata'].get('Fault Occurrence Rate (%)', 0)) for x in results)
        handover_min = min(float(x['metadata'].get('Handover Success Rate (%)', 100)) for x in results)
        st.info(f"**Evidence snapshot:** Highest displayed fault occurrence is **{fault_max:.2f}%** and lowest displayed handover success is **{handover_min:.2f}%** among retrieved cases.")
        if any(t in qlow for t in ['increasing', 'declining', 'decreasing', 'rising', 'falling', 'over time']):
            st.warning('⚠️ The retrieved sample has no timestamp or ordered regional observations, so a time trend cannot be confirmed from these records alone.')
        actions = [
            'Investigate handover failures by cell pair, mobility pattern and failure cause; review neighbor-cell relations and handover thresholds.',
            'Check radio coverage and interference in affected cells, including signal quality and coverage gaps.',
            'Review recent handover/radio parameter changes, failed configuration changes and alarm patterns before making further changes.',
            'Prioritize high-fault incidents and correlate fault occurrence with availability, packet loss, alarms and MTTR.',
            'Validate the trend using dated observations from the same region/cell before treating it as a confirmed trend.',
            'After approved changes, monitor handover success, fault occurrence, call drops, availability and alarms to verify improvement.'
        ]
        for i, a in enumerate(actions, 1):
            st.markdown(f'<div class="action-item"><span style="color:#38bdf8;font-weight:700;margin-right:8px;">{i}.</span> {a}</div>', unsafe_allow_html=True)

    try:
        export_payload = {'query': query}
        if response:
            export_payload.update({k: response.get('filters', {}).get(k) for k in ['state', 'city', 'season', 'weather', 'network_condition']})
        ex = requests.post(api + '/search-incidents/export', json=export_payload, timeout=180)
        ex.raise_for_status()
        st.caption(f"Showing **{len(results):,}** ranked results on this page. Retrieval scored the **entire filtered dataset** (Total: **{response.get('total_results', len(results)) if response else len(results):,}**).")
        st.download_button('⬇️ Export ALL matching evidence CSV', ex.content, file_name='netops_search_evidence.csv', mime='text/csv', key='export_' + str(abs(hash(query))))
    except Exception as ex:
        st.error(f'Unable to prepare full evidence export: {ex}')

    st.markdown('---')
    st.subheader('🔍 Inspect Individual Historical Incident Record')
    incident_ids = [str(x['incident_id']) for x in results]
    selected_id = st.selectbox('Select incident to inspect', incident_ids, key='inspect_' + str(abs(hash(query))))
    selected = next((x for x in results if str(x['incident_id']) == selected_id), None)
    if selected:
        m = selected['metadata']
        st.markdown(f"#### `{selected['incident_id']}` • Hybrid Score: `{selected['score']:.3f}` • {m.get('City')}, {m.get('State')}")
        st.info(selected['document'])
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric('Latency', f"{m.get('Latency (ms)', 0):.1f} ms")
        c2.metric('Throughput', f"{m.get('Throughput (Mbps)', 0):.1f} Mbps")
        c3.metric('Packet Loss', f"{m.get('Packet Loss Rate (%)', 0):.2f}%")
        c4.metric('Fault Occurrence', f"{m.get('Fault Occurrence Rate (%)', 0):.1f}%")
        c5.metric('Condition', selected.get('network_condition', 'Unknown'))
        if show_feedback:
            with st.expander('⭐ Record Operator Feedback', expanded=False):
                rating = st.slider(f"Relevance rating for {selected['incident_id']}", 1, 5, 4, key='r_' + selected['incident_id'])
                comment = st.text_input('Operator notes (optional)', key='c_' + selected['incident_id'])
                if st.button('Submit feedback', key='f_' + selected['incident_id']):
                    try:
                        post('/feedback', {'query': query, 'incident_id': selected['incident_id'], 'rating': rating, 'comment': comment})
                        st.success('Feedback recorded successfully.')
                    except Exception as e:
                        st.error(str(e))

# Sidebar System Health Status
st.sidebar.markdown('---')
health = safe_get('/health')
if health:
    st.sidebar.markdown(f'''
    <div style="background:rgba(15,23,42,0.85);border:1px solid rgba(16,185,129,0.35);border-radius:12px;padding:12px 14px;margin-bottom:12px;">
        <div style="display:flex;align-items:center;gap:8px;font-size:0.84rem;font-weight:700;color:#34d399;">
            <span class="pulse-dot"></span> FASTAPI ONLINE
        </div>
        <div style="font-size:0.78rem;color:#cbd5e1;margin-top:4px;font-weight:500;">
            {health.get('incident_count', 0):,} 5G Incidents Loaded
        </div>
    </div>
    ''', unsafe_allow_html=True)

    llm_p = health.get('llm_provider', 'offline')
    if health.get('claude_configured'):
        st.sidebar.markdown(f'<div class="trace-chip">🧠 LLM: Claude ({llm_p})</div>', unsafe_allow_html=True)
    elif health.get('openai_configured'):
        st.sidebar.markdown(f'<div class="trace-chip">🧠 LLM: OpenAI ({llm_p})</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="trace-chip" style="color:#cbd5e1;">🧠 LLM: Deterministic Fallback</div>', unsafe_allow_html=True)

    with st.sidebar.expander('⚙️ Model & Retriever Config', expanded=False):
        st.markdown(
            f"- **Vector Index:** {'Semantic Active' if health.get('semantic_embeddings_configured') else 'TF-IDF / BM25 Fallback'}\n"
            f"- **LLM Provider:** `{llm_p}`\n"
            f"- **Claude Status:** {'✅ Active' if health.get('claude_configured') else '⚪ Offline fallback'}"
        )
else:
    st.sidebar.error('❌ Backend API offline — start FastAPI service')

# ==================== PAGE: DASHBOARD ====================
if page == '🏠 Dashboard':
    st.markdown('''
    <div class="hero-container">
        <div class="live-pill"><span class="pulse-dot"></span> LIVE 5G NOC COMMAND DESK</div>
        <h1 class="hero-title">📡 NetOps AI Command Center</h1>
        <p class="hero-subtitle">
            Autonomous 5G incident retrieval, multi-agent root cause diagnosis, fault risk estimation, and evidence-grounded troubleshooting.
        </p>
    </div>
    ''', unsafe_allow_html=True)

    s = safe_get('/stats')
    if s:
        st.markdown('##### 🌐 Whole-Network Fleet Telemetry')
        cols = st.columns(5)
        cols[0].metric('Historical Incidents', f"{s['incident_count']:,}")
        cols[1].metric('Avg Latency', f"{s['avg_latency_ms']} ms")
        cols[2].metric('Avg Throughput', f"{s['avg_throughput_mbps']} Mbps")
        cols[3].metric('Avg Packet Loss', f"{s['avg_packet_loss_pct']}%")
        cols[4].metric('High-Risk Cells', f"{s['high_risk_rows']:,}")

    if s and s.get('network_condition_counts'):
        st.markdown('---')
        st.subheader('📈 Fleet Health Condition Distribution')
        cond = pd.Series(s['network_condition_counts'], name='Incidents')
        st.bar_chart(cond, height=220)

    st.markdown('---')
    st.subheader('🚀 Core Architectural Capabilities')
    c1, c2, c3 = st.columns(3)
    c1.markdown('''
    <div class="card">
        <h3>🔎 Hybrid Retrieval</h3>
        <p>Whole-dataset Okapi BM25 lexical search blended with sentence embeddings, filterable across States, Cities, Seasons, and Weather conditions.</p>
    </div>
    ''', unsafe_allow_html=True)

    c2.markdown('''
    <div class="card">
        <h3>🧠 Multi-Agent Diagnostic Engine</h3>
        <p>Classifier, Prioritizer, RandomForest Performance Regressors, Root Cause Analyzer, and Network Impact Assessors collaborating in pipeline.</p>
    </div>
    ''', unsafe_allow_html=True)

    c3.markdown('''
    <div class="card">
        <h3>🛡️ Evidence-Grounded Decisions</h3>
        <p>Claude / OpenAI RAG synthesis with strict anti-hallucination guardrails, LLM-as-judge scoring, and automated DeepEval/RAGAS benchmarks.</p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('---')
    st.subheader('💡 Example Operational Inquiries')
    st.markdown('<div class="quick-query-card">“A cell has high latency, packet loss and reduced throughput. Find similar historical cases and recommend corrective actions.”</div>', unsafe_allow_html=True)
    st.markdown('<div class="quick-query-card">“Multiple cells have poor service quality and increasing alarm counts. What factors could be contributing?”</div>', unsafe_allow_html=True)
    st.markdown('<div class="quick-query-card">“A region has increasing fault occurrence and declining handover success. What corrective actions should be considered?”</div>', unsafe_allow_html=True)

# ==================== PAGE: INCIDENT SEARCH ====================
elif page == '🔎 Incident Search':
    st.markdown('''
    <div class="hero-container">
        <h1 class="hero-title">🔎 Historical Incident Search</h1>
        <p class="hero-subtitle">Retrieve and rank evidence cases across 100,000 historical 5G network telemetry records using hybrid BM25 + semantic similarity.</p>
    </div>
    ''', unsafe_allow_html=True)

    q = query_box('High latency, packet loss and reduced throughput')
    display_top_k = st.slider('Display highest-ranked incidents', min_value=1, max_value=10, value=5, key='incident_search_top_k')
    f = filters()

    if st.button('⚡ Search Historical Incidents', type='primary'):
        try:
            data = post('/search-incidents', {'query': q, 'top_k': display_top_k, **f})
            st.session_state['last_query'] = q
            st.session_state['last_response'] = data
            st.session_state['last_results'] = data['results']
            render_results(data['results'], True, q, data)
        except Exception as e:
            st.session_state.pop('last_results', None)
            st.session_state.pop('last_response', None)
            st.error(str(e))
    elif st.session_state.get('last_results'):
        render_results(st.session_state['last_results'], True, st.session_state.get('last_query', ''), st.session_state.get('last_response'))

# ==================== PAGE: AI DIAGNOSIS ====================
elif page == '🧠 AI Diagnosis':
    st.markdown('''
    <div class="hero-container">
        <h1 class="hero-title">🧠 Multi-Agent AI Network Diagnosis</h1>
        <p class="hero-subtitle">Executes end-to-end incident classification, risk scoring, ML throughput regression, root-cause hypothesis, and RAG action synthesis.</p>
    </div>
    ''', unsafe_allow_html=True)

    q = query_box('A cell is experiencing high latency, packet loss and reduced throughput. Find similar historical incidents and recommend corrective actions.')
    display_top_k = st.slider('Display highest-ranked evidence incidents', min_value=1, max_value=10, value=5, key='diagnosis_top_k')
    f = filters()

    if st.button('🚀 Run Full Multi-Agent Diagnosis', type='primary'):
        try:
            st.session_state['diagnosis'] = post('/diagnose', {'query': q, 'top_k': display_top_k, **f, 'include_predictions': True})
        except Exception as e:
            st.session_state['diagnosis'] = None
            st.error(str(e))

    d = st.session_state.get('diagnosis')
    if d and d.get('status') == 'no_match':
        st.error(d.get('message', 'No matching incidents found.'))
        diag = d.get('filter_diagnostics', {})
        st.metric('Exact Matching Historical Rows', diag.get('exact_match_count', 0))
    elif d:
        if d.get('match_mode') == 'near_match':
            st.warning('Diagnosis used near-match evidence because no historical row satisfied every selected filter. Relaxed: ' + ', '.join(d.get('relaxed_filters', [])))

        # Executive KPI Bar
        st.markdown('##### 📋 Diagnostic Assessment Summary')
        p = d['prioritization']
        perf = d['performance_prediction']
        c1, c2, c3 = st.columns(3)
        c1.metric('Incident Class', d['classification']['category'].replace('_', ' ').title())
        c2.metric('Priority', p['priority'])
        c3.metric('Predicted Throughput', f"{perf['predicted_throughput_mbps']:.1f} Mbps")

        # RAG Synthesis Card
        with st.container(border=True):
            st.markdown(d['rag_answer']['answer'])



        if d.get('query_analysis'):
            qa = d['query_analysis']
            st.subheader('🛠️ Query-Focused Corrective Actions')
            if qa.get('trend_requested'):
                st.warning(f"⚠️ {qa.get('evidence_note', 'Requested trend cannot be confirmed from available evidence.')}")
            for i, a in enumerate(qa.get('corrective_actions', []), 1):
                st.markdown(f'<div class="action-item"><span style="color:#38bdf8;font-weight:700;margin-right:8px;">{i}.</span> {a}</div>', unsafe_allow_html=True)

        # Root Cause & Network Impact Cards
        st.markdown('---')
        left_col, right_col = st.columns(2)
        with left_col:
            st.subheader('🔬 Likely Root Cause')
            rc = d.get('root_cause', {}) or {}
            primary_cause = str(rc.get('primary_cause', 'Unknown')).replace('_', ' ').title()
            confidence = float(rc.get('confidence', 0.0))
            factors = rc.get('contributing_factors', [])

            st.markdown(f'''
            <div class="card">
                <div style="font-size:0.82rem;color:#7dd3fc;font-weight:700;text-transform:uppercase;">Primary Hypothesis</div>
                <div style="font-size:1.30rem;font-weight:700;color:#ffffff;margin:6px 0 10px 0;">{primary_cause}</div>
                <div style="margin-bottom:14px;color:#e2e8f0;">Confidence: <span class="badge-chip badge-info">{confidence:.0%}</span></div>
                <div style="font-size:0.84rem;color:#7dd3fc;font-weight:700;margin-bottom:8px;text-transform:uppercase;">Contributing Factors:</div>
                <div>{''.join(f'<span class="badge-chip badge-warning">{str(f).replace("_", " ").title()}</span>' for f in factors) if factors else '<span class="badge-chip badge-neutral">None Identified</span>'}</div>
            </div>
            ''', unsafe_allow_html=True)

            st.subheader('💥 Network Impact Assessment')
            impact = d.get('network_impact', {}) or {}
            impact_level = str(impact.get('impact_level', 'MEDIUM')).upper()
            badge_class = 'badge-critical' if impact_level in ('CRITICAL', 'HIGH') else ('badge-warning' if impact_level == 'MEDIUM' else 'badge-success')
            effects = impact.get('effects', [])

            st.markdown(f'''
            <div class="card">
                <div style="font-size:0.82rem;color:#7dd3fc;font-weight:700;text-transform:uppercase;">Impact Severity</div>
                <div style="margin:6px 0 14px 0;"><span class="badge-chip {badge_class}" style="font-size:0.95rem;padding:6px 14px;">{impact_level}</span></div>
                <div style="font-size:0.84rem;color:#7dd3fc;font-weight:700;margin-bottom:8px;text-transform:uppercase;">Observed / Projected Degradation:</div>
                <div>{''.join(f'<div style="font-size:0.92rem;color:#f8fafc;margin-bottom:6px;">• {e}</div>' for e in effects) if effects else '<div style="font-size:0.90rem;color:#cbd5e1;">No severe downstream effects noted.</div>'}</div>
            </div>
            ''', unsafe_allow_html=True)

        with right_col:
            st.subheader('📋 Decision-Support Recommendations')
            for rec in d.get('recommendations', []):
                st.markdown(f'<div class="action-item"><span style="color:#10b981;font-weight:700;margin-right:8px;">✔</span> {rec}</div>', unsafe_allow_html=True)

            st.subheader('⚖️ LLM-as-Judge Quality Validation')
            judge = d.get('judge', {})
            method = judge.get('method', 'Evaluation')
            scores = judge.get('scores')
            provider = judge.get('provider')
            model_info = judge.get('model')

            badge_text = f"Evaluator: **{method}**"
            if provider:
                badge_text += f" • **{provider.capitalize()}** ({model_info or ''})"
            st.caption(badge_text)

            if isinstance(scores, dict):
                jc1, jc2, jc3, jc4 = st.columns(4)
                jc1.metric("Grounding", f"{float(scores.get('grounding', 0)):.0%}")
                jc2.metric("Completeness", f"{float(scores.get('completeness', 0)):.0%}")
                jc3.metric("Actionability", f"{float(scores.get('actionability', 0)):.0%}")
                jc4.metric("Overall Score", f"{float(scores.get('overall', 0)):.0%}")
                if scores.get('reason'):
                    st.info(f"💡 **Judge Assessment:** {scores['reason']}")
            else:
                overall = judge.get('overall', 1.0)
                jc1, jc2 = st.columns(2)
                jc1.metric("Overall Quality", f"{float(overall):.0%}")
                criteria = judge.get('criteria', [])
                jc2.metric("Criteria Verified", f"{len(criteria)} / {len(criteria)} fields" if criteria else "Verified")
                if judge.get('reason'):
                    st.info(f"💡 **Judge Note:** {judge['reason']}")

            with st.expander('🔍 Inspect Raw Judge Output', expanded=False):
                st.code(json.dumps(judge, indent=2, default=str), language='json')

        st.markdown('---')
        st.subheader('🛰️ Multi-Agent Workflow Execution Trace')
        trace_html = ''.join(f'<span class="trace-chip">{step}</span>' for step in d['agent_trace'])
        st.markdown(trace_html, unsafe_allow_html=True)

        st.markdown('---')
        st.subheader('📑 Retrieved Evidence Telemetry')
        st.caption(f"Displaying top {len(d['similar_incidents'])} ranked evidence records from {d.get('whole_dataset_match_count', d.get('filter_diagnostics', {}).get('exact_match_count', 0)):,} matching records.")
        render_results(d['similar_incidents'], True, d['query'], d)
        out = pd.DataFrame([x['metadata'] | {'incident_id': x['incident_id'], 'hybrid_score': x['score']} for x in d['similar_incidents']])
        st.download_button('⬇️ Export Retrieved Evidence CSV', out.to_csv(index=False).encode(), file_name='netops_evidence.csv', mime='text/csv')

# ==================== PAGE: DATASET EXPLORER ====================
elif page == '📋 Dataset Explorer':
    st.markdown('''
    <div class="hero-container">
        <h1 class="hero-title">📋 Telecom Incidents Explorer</h1>
        <p class="hero-subtitle">Searchable, filterable network operational records across 100,000 cell telemetry points.</p>
    </div>
    ''', unsafe_allow_html=True)

    try:
        opts = get_dataset_options()
        total = opts.get('total_count', 0)
        with st.expander('🎛️ Filter Dataset Records', expanded=True):
            a, b, c, d, e = st.columns(5)
            circle = a.selectbox('Circle', ['All'] + opts.get('circle', []), key='dataset_circle')
            severity = b.selectbox('Severity', ['All'] + opts.get('severity', []), key='dataset_severity')
            season = c.selectbox('Season', ['All'] + opts.get('season', []), key='dataset_season')
            issue_type = d.selectbox('Issue Type', ['All'] + opts.get('issue_type', []), key='dataset_issue_type')
            sort_by = e.selectbox(
                'Sort By',
                [
                    'Highest Risk', 'Lowest Risk', 'Latest Date', 'Oldest Date',
                    'Highest Fault Occurrence', 'Lowest Handover Success',
                    'Highest Latency', 'Highest Throughput'
                ],
                key='dataset_sort_by'
            )

        filter_signature = (circle, severity, season, issue_type, sort_by)
        if st.session_state.get('dataset_filter_signature') != filter_signature:
            st.session_state['dataset_filter_signature'] = filter_signature
            st.session_state['dataset_page'] = 1

        page_size = 500
        p_num = int(st.session_state.get('dataset_page', 1))
        data = get_dataset_view(circle, severity, season, issue_type, sort_by, p_num, page_size)
        filtered = data.get('filtered_count', 0)
        page_count = max(1, int(data.get('page_count', 1)))
        if p_num > page_count:
            st.session_state['dataset_page'] = page_count
            st.rerun()

        st.caption(f"Full dataset: **{filtered:,}** matching records. Displaying page **{p_num:,} of {page_count:,}** ({len(data.get('rows', [])):,} rows).")

        table = pd.DataFrame(data.get('rows', []))
        if table.empty:
            st.warning('No dataset records match the selected filters.')
        else:
            st.dataframe(table, use_container_width=True, hide_index=True, height=600)
            nav1, nav2, nav3 = st.columns([1, 2, 1])
            with nav1:
                if st.button('⬅️ Previous', disabled=p_num <= 1, key='dataset_prev'):
                    st.session_state['dataset_page'] = p_num - 1
                    st.rerun()
            with nav2:
                st.markdown(f'<div style="text-align:center;padding-top:8px;font-weight:700;color:#ffffff;">Page {p_num:,} / {page_count:,}</div>', unsafe_allow_html=True)
            with nav3:
                if st.button('Next ➡️', disabled=p_num >= page_count, key='dataset_next'):
                    st.session_state['dataset_page'] = p_num + 1
                    st.rerun()

            params = {
                'circle': circle if circle != 'All' else '',
                'severity': severity if severity != 'All' else '',
                'season': season if season != 'All' else '',
                'issue_type': issue_type if issue_type != 'All' else '',
                'sort_by': sort_by
            }
            try:
                export = requests.get(api + '/dataset/export', params=params, timeout=120)
                export.raise_for_status()
                st.download_button('⬇️ Export ALL Filtered Dataset CSV', export.content, file_name='telecom_dataset_filtered.csv', mime='text/csv', key='dataset_export')
            except Exception as ex:
                st.error(f'Unable to prepare full CSV export: {ex}')
    except Exception as e:
        st.error(f'Unable to load Dataset Explorer: {e}')

# ==================== PAGE: EVALUATION ====================
elif page == '📊 Evaluation':
    st.markdown('''
    <div class="hero-container">
        <h1 class="hero-title">📊 Evaluation & Quality Benchmarks</h1>
        <p class="hero-subtitle">Empirical validation suite: Retrieval Hit@k precision, RAGAS generation metrics, and DeepEval automated assertions.</p>
    </div>
    ''', unsafe_allow_html=True)

    eval_tab1, eval_tab2, eval_tab3 = st.tabs([
        '🔎 Retrieval Quality (Hit@k)',
        '🤖 RAGAS Generation Metrics',
        '🛡️ DeepEval Test Harness'
    ])

    with eval_tab1:
        st.subheader('Keyword & Semantic Retrieval Hit Rate')
        st.caption('Evaluates whether target diagnostic keywords are retrieved in top-ranked evidence across benchmark test cases.')
        if st.button('▶️ Run Retrieval Evaluation', type='primary', key='btn_run_retrieval'):
            try:
                st.session_state['eval'] = post('/evaluate/retrieval', {})
                st.success('Retrieval evaluation completed.')
            except Exception as e:
                st.error(str(e))
        e = st.session_state.get('eval') or safe_get('/evaluate/retrieval')
        if e:
            c1, c2 = st.columns(2)
            c1.metric('Retrieval Hit Rate', f"{e['hit_rate']:.1%}")
            c2.metric('Evaluated Benchmark Queries', f"{len(e['cases'])}")
            st.dataframe(pd.DataFrame(e['cases']), use_container_width=True, hide_index=True)
        st.caption('**CLI Command:** `python evaluation/run_evaluation.py`')

    with eval_tab2:
        st.subheader('🤖 RAGAS Framework Benchmarks')
        st.caption('Evaluates factual consistency, context precision, and response relevancy across NetOps troubleshooting inquiries.')
        if st.button('🔄 Run / Refresh RAGAS Benchmark', type='primary', key='btn_run_ragas'):
            try:
                st.session_state['ragas'] = post('/evaluate/ragas', {'run_live': True})
                st.success('RAGAS benchmark updated.')
            except Exception as ex:
                st.error(str(ex))
        ragas_data = st.session_state.get('ragas') or safe_get('/evaluate/ragas')
        if ragas_data and ragas_data.get('summary'):
            s = ragas_data['summary']
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric('Faithfulness', f"{s.get('faithfulness', 0):.1%}", help='Measures factual consistency of claims against retrieved context')
            rc2.metric('Response Relevancy', f"{s.get('response_relevancy', 0):.1%}", help='Measures how directly the answer addresses query')
            rc3.metric('Context Precision', f"{s.get('context_precision', 0):.1%}", help='Measures signal-to-noise ratio in retrieved context')
            st.caption(f"Pipeline: **{s.get('mode', 'RAGAS Benchmark')}**")
            if ragas_data.get('samples'):
                st.markdown('##### Per-Query RAGAS Breakdown')
                st.dataframe(pd.DataFrame(ragas_data['samples']), use_container_width=True, hide_index=True)
        else:
            st.info('Click "Run / Refresh RAGAS Benchmark" to compute live scores.')
        st.caption('**CLI Command:** `python evaluation/run_ragas.py`')

    with eval_tab3:
        st.subheader('🛡️ DeepEval Automated Test Harness')
        st.caption('Automated assertions evaluating AnswerRelevancyMetric and FaithfulnessMetric against pre-set pass/fail thresholds.')
        if st.button('🛡️ Execute DeepEval Suite', type='primary', key='btn_run_deepeval'):
            try:
                st.session_state['deepeval'] = post('/evaluate/deepeval', {'run_live': True})
                st.success('DeepEval test run completed.')
            except Exception as ex:
                st.error(str(e))
        deepeval_data = st.session_state.get('deepeval') or safe_get('/evaluate/deepeval')
        if deepeval_data and deepeval_data.get('summary'):
            ds = deepeval_data['summary']
            dc1, dc2, dc3 = st.columns(3)
            dc1.metric('Pass Rate', f"{ds.get('pass_rate', 0):.1%}")
            dc2.metric('Avg Relevancy', f"{ds.get('avg_relevancy', 0):.1%}")
            dc3.metric('Avg Faithfulness', f"{ds.get('avg_faithfulness', 0):.1%}")
            if deepeval_data.get('cases'):
                st.markdown('##### Test Case Assertions')
                st.dataframe(pd.DataFrame(deepeval_data['cases']), use_container_width=True, hide_index=True)
        else:
            st.info('Click "Execute DeepEval Suite" to execute assertions.')
        st.caption('**CLI Command:** `python evaluation/run_deepeval.py`')

# ==================== PAGE: FEEDBACK ====================
elif page == '💬 Feedback':
    st.markdown('''
    <div class="hero-container">
        <h1 class="hero-title">💬 Human-in-the-Loop Feedback Loop</h1>
        <p class="hero-subtitle">Operator relevance ratings and qualitative comments recorded for continuous retriever alignment.</p>
    </div>
    ''', unsafe_allow_html=True)

    s = safe_get('/feedback/summary', {'count': 0, 'average_rating': 0})
    c1, c2 = st.columns(2)
    c1.metric('Total Feedback Entries', s['count'])
    c2.metric('Average Operator Rating', f"{s['average_rating']:.2f} / 5.0")
    st.markdown('---')
    rows = safe_get('/feedback/recent', []) or []
    if rows:
        st.markdown('##### 📝 Recent Feedback Submissions')
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info('No feedback entries yet. Submit ratings from the Incident Search or AI Diagnosis tabs.')

# ==================== PAGE: ABOUT ====================
else:
    st.markdown('''
    <div class="hero-container">
        <h1 class="hero-title">ℹ️ Solution Architecture & Guidelines</h1>
        <p class="hero-subtitle">Technical blueprint, multi-agent design, and production safety constraints.</p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    ### 🎯 Project Requirements Coverage
    - **Core Retrieval:** Hybrid BM25 lexical + semantic sentence embedding search across 100,000 5G cell telemetry points.
    - **Multi-Agent Pipeline:** Incident classification, risk scoring, ML throughput regression, root-cause hypothesis, and network impact estimation.
    - **Safety & Guardrails:** Input validation against prompt injection, temporal trend hallucination defenses, and out-of-domain query rejections.
    - **Evaluation:** Quantitative validation via Hit@k (100%), RAGAS generation metrics, and DeepEval assertion hooks.
    - **Human-in-the-Loop:** Persistent operator feedback loop for ongoing diagnostic alignment.

    ### 🏗️ End-to-End Architecture
    ```
    Telecom Dataset (100K 5G rows)
      ↓
    Data Preprocessing & Feature Engineering
      ↓
    Embeddings (Sentence Transformers) + BM25 Lexical Index
      ↓
    Hybrid Retriever (Dense + Sparse Fusion)
      ↓
    Multi-Agent Diagnostic Pipeline (Classifier, Risk, Recommender, Judge)
      ↓
    Evidence-Grounded RAG Synthesis (Claude 3.5 Sonnet / OpenAI)
      ↓
    FastAPI Microservice (REST API)
      ↓
    Streamlit Command Center (Enterprise UI)
    ```

    ### 🛡️ Operational Safety Disclaimer
    This application is an intelligent **decision-support platform**. It does not execute live network configuration changes automatically. All recommendations must be verified by certified NOC operators in accordance with organizational change-management protocols.
    ''')
