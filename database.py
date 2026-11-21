import sqlite3
from datetime import datetime, timezone
from scheduler import create_new_card, process_review

DB_NAME = "manki.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(""" 
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL, 
                translation TEXT NOT NULL,
                due_date TEXT NOT NULL,
                fsrs_data TEXT NOT NULL
            )
        """)

def add_word(word: str, translation: str):
    card_info = create_new_card()
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO cards (word, translation, due_date, fsrs_data) VALUES (?, ?, ?, ?)",
            (word.strip(), translation.strip(), card_info["due_date"], card_info["fsrs_data"])
        )


def get_due_cards() -> list[dict]:
    now_str = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM cards WHERE due_date <= ? ORDER BY due_date ASC",
            (now_str,)
        )
        return [dict(row) for row in cursor.fetchall()]

def review_word(card_id: int, rating_number: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT fsrs_data FROM cards WHERE id = ?", (card_id,))
        row = cursor.fetchone()
        if not row:
            return

        updated = process_review(row[0], rating_number)
        conn.execute(
            "UPDATE cards SET due_date = ?, fsrs_data = ? WHERE id = ?",
            (updated["due_date"], updated["fsrs_data"], card_id)
        )

if __name__ == "__main__":
    init_db()
    add_word("ubiquitous", "вездесущий")
    due = get_due_cards()
    print(f"Карточек на сегодня: {len(due)}")

    if due:
        first_card = due[0]
        print("Повторяем слово:", first_card["word"], "_", first_card["translation"])
        review_word(first_card["id"], 3)
        print(f"Осталось на сегодня после повторения: {len(get_due_cards())}")
