import sqlite3
from config import Config
def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    return conn
def init_db():
    conn =get_db()
    conn.cursor().execute('''CREATE TABLE IF NOT EXISTS results
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  score INTEGER NOT NULL, 
                  total INTEGER NOT NULL, 
                  percent INTEGER NOT NULL,
                  risk TEXT NOT NULL,
                  tier TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
if __name__ == "__main__":
    init_db()