import sqlite3

con = sqlite3.connect('movie_database.db')
with con:
    con.execute("""CREATE TABLE favorites_movie (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        movie_id INTEGER,
        FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE
    )""")
    con.commit()
