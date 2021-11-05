import urllib.request as ul
from bs4 import BeautifulSoup as bs
import re
import pymongo as pm

class Page:
    def __init__(self, database = 'htmlextractor', collection = 'pages'):
        # criando db e collection
        self.database = database
        self.collection = collection

    def db_collection(self):
        connect = pm.MongoClient("mongodb://localhost:27017/")
        create_db = connect[self.database]
        create_collection = create_db[self.collection]
        return create_collection

    # extraindo html da página
    def extract_html(self, link):
        url = ul.Request("https://www.mql5.com" + link, headers={'User-Agent': 'Mozilla/5.0'})
        page = ul.urlopen(url).read().decode('utf-8')
        inspect_html = bs(page,"html.parser")
        return inspect_html

    # inserindo html no mongodb
    def insert_data_mongo(self, page_name, link):
        self.db_collection().insert_one({
        "page_name": page_name, "page_link": "https://www.mql5.com" + link, "html": str(self.extract_html(link))
        })
        
    # extraindo link para página signals
    def signals_link(self):
        for link in self.extract_html("").find(id="mainmenuItems").find_all(href=re.compile('signals')):
            signals_link = link['href']
        return signals_link

    # extraindo link para página see all signals
    def all_signals_link(self):
        link = self.signals_link()
        for link in self.extract_html(link).find_all("div", {"class": "signals-dashboard__see-all"}):
            all_signals = link.a['href']
        return all_signals

    # obtendo a última página disponível
    def get_last_page(self):
        extracted = self.extract_html(self.all_signals_link()).find_all("div", {"class": "paginatorEx"})
        for link in extracted:
            link_last = link.find_all('a')[-1].get('href')
            return link_last

    # como o html não possui uma lista com todas as páginas, mas apenas algumas
    # (page1, page2, ...., page30), não posso encontrar a última página
    # usando for ... len(...).

    # obtendo número da última página disponível
    def last_page_number(self):
        pattern = re.compile('page[0-9]{1,3}')
        result = pattern.findall(self.get_last_page())
        pattern2=re.compile('[0-9]{1,3}')
        return int(pattern2.findall(result[0])[0])
    #    ## Selecionando elemento 0 da lista retorna uma string.
    #print(last_page_number())

    def extract_all_pages(self):
        pages = []
        for i in range(1,self.last_page_number()+1):
            pages.append(self.all_signals_link().replace("/page1", "") + '/page' + str(i))
        return pages

    def add_data_mongo(self):
        for i in self.extract_all_pages():
            pattern = re.compile('page[0-9]{1,3}')
            page_name = pattern.findall(i)
            self.insert_data_mongo(str(page_name), i)


if __name__ == '__main__':
    page = Page()

    print(page.extract_all_pages())
    #page.add_data_mongo()