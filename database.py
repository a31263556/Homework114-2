#負責建立 SQLite DB、插入資料、查詢資料
import sqlite3
from typing import List, Dict


DB_NAME = "books.db"


# 建立資料表 llm_books（若不存在）
def init_db() -> None:
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS llm_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                author TEXT,
                price INTEGER,
                link TEXT
            )
            """
        )
        conn.commit()


def insert_books(books: List[Dict]) -> int:
    if not books:
        return 0

    inserted = 0
    with sqlite3.connect(DB_NAME) as conn:
        for b in books:
            try:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO llm_books(title, author, price, link)
                    VALUES (?, ?, ?, ?)
                    """,
                    (b["title"], b["author"], b["price"], b["link"])
                )
                inserted += conn.total_changes  # 變化數
            except Exception:
                continue
        conn.commit()
    return inserted


def search_by_title(keyword: str) -> List[tuple]:
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute(
            """
            SELECT title, author, price, link
            FROM llm_books
            WHERE title LIKE ?
            """,
            (f"%{keyword}%",)
        )
        return cur.fetchall()


def search_by_author(keyword: str) -> List[tuple]:
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute(
            """
            SELECT title, author, price, link
            FROM llm_books
            WHERE author LIKE ?
            """,
            (f"%{keyword}%",)
        )
        return cur.fetchall()
