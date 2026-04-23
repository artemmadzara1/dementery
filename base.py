import sqlite3
import os
from config import Config
def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    if os.path.exists(Config.DATABASE):
        os.remove(Config.DATABASE)
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE NOT NULL, 
                  password TEXT NOT NULL,
                  fio TEXT NOT NULL,
                  otchestvo TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  city TEXT NOT NULL,
                  consent INTEGER NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE results 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER NOT NULL,
                  score INTEGER NOT NULL, 
                  total INTEGER NOT NULL, 
                  percent INTEGER NOT NULL,
                  risk TEXT NOT NULL,
                  tier TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
if __name__ == '__main__':
    init_db()
