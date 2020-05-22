import json
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse


def sbrf_page_parse(url):
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    #main_content = soup.find(attr={'content': 'node:datarow'})
    #table_content = main_content.findAll('tbody')

    print(page.text)

    #for body in table_content:
    #    print('body')

    #scrap_data = {}

    #for tr in table_content:
    #    tds = tr.findAll('td')

        # <div content="leaf:PurchaseTypeName" class="es-el-type-name">Открытый конкурс в электронной форме</div>
    #    purchTypeName = tds[0].find('div',{'content':'leaf:PurchaseTypeName'})
    #    scrap_data['name'] = purchTypeName
        

    return None


#print("https://www.sberbank-ast.ru/purchaseList.aspx")

sbrf_page_parse("https://www.sberbank-ast.ru/SearchQuery.aspx?name=Main")
