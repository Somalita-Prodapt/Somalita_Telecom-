import sqlite3
from pathlib import Path
from src.utils.config import STORAGE_PATH

class FeedbackService:
    def __init__(self, path=None):
        self.path = Path(path) if path else STORAGE_PATH/'feedback.db'
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as c:
            c.execute('CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY AUTOINCREMENT, query TEXT, incident_id TEXT, rating INTEGER, comment TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')

    def add(self,q,i,r,cmt):
        with sqlite3.connect(self.path) as c:
            c.execute('INSERT INTO feedback(query,incident_id,rating,comment) VALUES(?,?,?,?)',(q,i,r,cmt))
        return {'status':'recorded'}

    def summary(self):
        with sqlite3.connect(self.path) as c:
            row=c.execute('SELECT COUNT(*), COALESCE(AVG(rating),0) FROM feedback').fetchone()
        return {'count':row[0],'average_rating':round(row[1],2)}

    def recent(self, limit=50):
        with sqlite3.connect(self.path) as c:
            rows=c.execute('SELECT id,query,incident_id,rating,comment,created_at FROM feedback ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
        return [{'id':r[0],'query':r[1],'incident_id':r[2],'rating':r[3],'comment':r[4],'created_at':r[5]} for r in rows]
