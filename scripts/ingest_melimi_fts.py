from app.melimi.fts import ensure_index

if __name__ == "__main__":
    ensure_index()
    print("Melimi SQLite FTS5 subject index updated.")
