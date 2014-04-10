'''
CREATE TABLE recipes (
    id serial primary key,
    url VARCHAR(300) NOT NULL,
    title VARCHAR(200) NOT NULL,
    contents text,
    hubby int,
    yummy int
);

'''

from bs4 import BeautifulSoup
import urllib
import psycopg2
import sys

# Connect to the database
try:
  conn = psycopg2.connect(dbname="pioneer", user='user', host='localhost', port=5432)
except:
  print "Could not connect to database: ", sys.exc_info()[1]
  sys.exit()

# Create a cursor for executing queries
cur = conn.cursor()


html = urllib.urlopen('http://thepioneerwoman.com/cooking/category/all-pw-recipes/?orderby=title&order=asc&posts_per_page=60000#archive-posts').read()
print "Loaded HTML"
soup = BeautifulSoup(html)

titles = soup.find("div", class_="entry").find_all("h1", class_="post-title")
print "Found all titles"

for title in titles:
  # each becomes a row with an autoincrementing primary key
  cur.execute("INSERT INTO recipes (url, title) VALUES (%(url)s, %(title)s)", {"url": title.a.get('href'), "title": title.a.get('title')})
  conn.commit()
  print "Finished one"

print "Done scrapping content"

cur.execute("SELECT id, url FROM recipes")
recipes = cur.fetchall()
for recipe in recipes:
  html = urllib.urlopen(recipe[1]).read()
  soup = BeautifulSoup(html)
  text = soup.findAll(text=True)
  all_text = ''.join(text)
  all_text = all_text.encode('utf-8')
  all_text = all_text.lower()
  all_text = all_text.replace('\n', '')
  all_text = all_text.replace('\t', '')
  all_text = all_text.replace('\r', '')
  cur.execute("UPDATE recipes SET contents = %(contents)s, yummy = %(yummy)s, hubby = %(hubby)s WHERE id = %(id)s", {"contents": all_text, "yummy": all_text.count('yummy'), "hubby": all_text.count('hubby'), "id": recipe[0]})
  conn.commit();
  print "Done with " + recipe[1]