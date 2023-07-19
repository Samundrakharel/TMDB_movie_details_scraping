import sqlite3


def create_table_movies():
    con = sqlite3.connect("tmdb.db")
    cur = con.cursor()
    create_table_sql ="""
        CREATE TABLE IF NOT EXISTS movies(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_name TEXT ,
            user_score TEXT,
            rating TEXT,
            mpaa TEXT,
            overview TEXT,
            genres TEXT,
            tagline TEXT,
            review_1 TEXT,
            review_2 TEXT,
            review_3 TEXT,
            review_4 TEXT,
            review_5 TEXT,
            status  TEXT
        )
    """
    try:
        cur.execute(create_table_sql)
        con.commit()
        print("Table created successfully")
    except sqlite3.Error as e:
        print("An error occurred:", e)
    finally:
        con.close()

def main():

    create_table_movies()


if __name__ == "__main__":
    main()