import sqlite3

db_location = 'content.db'
conn = sqlite3.connect(db_location)
cur = conn.cursor()

# ------------------------------------------------------
# load seed urls
seed_urls_file = 'seed_urls.txt'

with open(seed_urls_file, 'r') as f:
     for url in f:         
         cur.execute("""INSERT OR IGNORE INTO crawled_urls (url_link) VALUES (?)""", (url.rstrip(),))

conn.commit()

print("Seed URLs inserted successfully!")