# create database
import sqlite3

db_location = 'content.db'
conn = sqlite3.connect(db_location)
cur = conn.cursor()

sql = """
CREATE TABLE `crawled_urls` (
	`url_id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`url_link`	TEXT UNIQUE,
	`url_content`	TEXT DEFAULT NULL,
	`is_scraped`	TEXT DEFAULT 0
);
"""
        
cur.execute(sql)
conn.commit()

print("DB created successfully.")