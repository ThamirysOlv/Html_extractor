import urllib.request as ul
from bs4 import BeautifulSoup as bs
import re
import pymongo as pm

#f = open("/home/thamirys/Doutorado/Projects/Coding/Python/Html-extractor/htmltestsignal.txt", "w")
#f.write(pagesignal)
#f.close()

# criando db e collection
database = 'htmlextractor'
collection = 'pages'
def db_collection():
    connect = pm.MongoClient("mongodb://localhost:27017/")
    create_db = connect[database]
    create_collection = create_db[collection]
    return create_collection

# extraindo html da página
def extract_html(link):
    url = ul.Request("https://www.mql5.com" + link, headers={'User-Agent': 'Mozilla/5.0'})
    page = ul.urlopen(url).read().decode("utf-8")
    inspect_html = bs(page,"html.parser")
    return inspect_html

# inserindo html no mongodb
def insert_data_mongo(page_name, link):
    return db_collection().insert_one({
    "page_name": page_name, "html": extract_html(link)
    })
    
# extraindo link para página signals
def signals_link():
    for link in extract_html("").find(id="mainmenuItems").find_all(href=re.compile('signals')):
        signals_link = link['href']
    return signals_link

# extraindo link para página see all signals
def all_signals_link():
    link = signals_link()
    for link in extract_html(link).find_all("div", {"class": "signals-dashboard__see-all"}):
        all_signals_link = link.a['href']
    return all_signals_link
print(all_signals_link())

print(extract_html(all_signals_link()).find_all("div", {"class": "paginatorEx"}))