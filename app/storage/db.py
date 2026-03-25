"""SQLite 状态库：记录已抓取文章，实现去重"""
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime


def get_connection(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str):
    conn = get_connection(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT    NOT NULL,
            publish_date TEXT,
            source_url   TEXT,
            content_hash TEXT    NOT NULL UNIQUE,
            status       TEXT    NOT NULL DEFAULT 'saved',
            saved_path   TEXT,
            created_at   TEXT    NOT NULL,
            updated_at   TEXT    NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS run_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at     TEXT NOT NULL,
            status     TEXT NOT NULL,
            message    TEXT,
            article_id INTEGER REFERENCES articles(id)
        )
    """)
    conn.commit()
    conn.close()


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def is_duplicate(db_path: str, content_hash: str) -> bool:
    conn = get_connection(db_path)
    row = conn.execute(
        "SELECT id FROM articles WHERE content_hash = ?", (content_hash,)
    ).fetchone()
    conn.close()
    return row is not None


def save_article(db_path: str, title: str, publish_date: str,
                 source_url: str, content_hash: str, saved_path: str) -> int:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    cur = conn.execute(
        """INSERT INTO articles
           (title, publish_date, source_url, content_hash, status, saved_path, created_at, updated_at)
           VALUES (?, ?, ?, ?, 'saved', ?, ?, ?)""",
        (title, publish_date, source_url, content_hash, saved_path, now, now),
    )
    article_id = cur.lastrowid
    conn.commit()
    conn.close()
    return article_id


def log_run(db_path: str, status: str, message: str, article_id: int = None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO run_logs (run_at, status, message, article_id) VALUES (?, ?, ?, ?)",
        (now, status, message, article_id),
    )
    conn.commit()
    conn.close()
