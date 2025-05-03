import sqlite3

def init_db():
    conn = sqlite3.connect("notes.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_note_to_db(title, content):
    conn = sqlite3.connect("notes.db")
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()

def get_all_notes():
    conn = sqlite3.connect("notes.db")
    c = conn.cursor()
    c.execute("SELECT id, title FROM notes ORDER BY id DESC")
    notes = c.fetchall()
    conn.close()
    return notes

def get_note_by_id(note_id):
    conn = sqlite3.connect("notes.db")
    c = conn.cursor()
    c.execute("SELECT title, content FROM notes WHERE id=?", (note_id,))
    note = c.fetchone()
    conn.close()
    return note
