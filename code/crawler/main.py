import sqlite3
import urllib
import time
from bs4 import BeautifulSoup
from reppy.cache import RobotsCache
from reppy.robots import Robots

#################################################
default_crawl_delay = 5

# caching robots.txt files for fast access
robots_cache = RobotsCache(capacity=200)

# db commit rate
commit_rate = 1
current_r = 0

#################################################

db_location = 'content.db'
conn = sqlite3.connect(db_location)
cur = conn.cursor()

#################################################
#################################################
# populate url_frontier

url_frontier = set()

cur.execute("SELECT `url_link` FROM `crawled_urls` WHERE `is_scraped` = 0") 

for row in cur:
    url_frontier.add(row[0])

#################################################
#################################################
# fetch content of url

while len(url_frontier) != 0:
    # pop any random url
    url = url_frontier.pop()
    
    try:        
        print("\n---------------------------------------------------------")
        print("Crawling:", url)
        print("---------------------------------------------------------")


        # get crawl delay
        r = robots_cache.fetch(Robots.robots_url(url))[1]

        # check if its allowed to crawl that url? If not, then skip this url
        if not robots_cache.allowed(url, '*'):
            print("This URL is restricted to be crawled.")
            continue

        # insert this link to database
        cur.execute("INSERT OR IGNORE INTO crawled_urls (url_link) values(?)", (url,))

        # if its allowed to crawl, then get the crawling delay
        crawl_delay = r.agent("*").delay

        if crawl_delay is not None:
            time.sleep(crawl_delay)
        else:
            time.sleep(default_crawl_delay)
            
        #################################################
        #################################################
     
        # fetch html
    
        print("Fetching Document..") 
        
        fetched_doc = urllib.request.urlopen(url).read()
        cur.execute("""UPDATE `crawled_urls` SET url_content = ?, is_scraped = 1 
                    where url_link=?""", (fetched_doc, url))

        #################################################
        #################################################
        
        # parse content and get all absolute links
     
        print("Parsing Links from Document...")
        temp_frontier = set()
        soup = BeautifulSoup(fetched_doc, 'html.parser')
        
        for link in soup.findAll('a'):
            absolute_url = urllib.parse.urljoin(url, link.get('href'))

            # only get links
            temp_frontier.add(absolute_url)

        print("Total Links Parsed:", len(temp_frontier))

        #################################################
        #################################################

        # add only unique links to url_frontier
        print("Removing Duplicates...")

        duplicates = 0
        
        for link in temp_frontier:
            cur.execute("SELECT is_scraped FROM crawled_urls WHERE url_link = ?", (link,))
            data = cur.fetchone()
        
            if data is None and link not in url_frontier:
                    url_frontier.add(link)
            else:
                duplicates += 1

        print("Got", len(temp_frontier) - duplicates, "new links..")
        print("Duplicates removed: ", duplicates)

    except:
        pass

    current_r += 1

    if current_r == commit_rate:
        current_r = 0
        conn.commit()

print("Successfully Finished!")