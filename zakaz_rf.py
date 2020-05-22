import json
import requests
import re
import sql_db as sql

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta, time
from multiprocessing import Queue


def get_scrap(url, params, region):
    result = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    html_page = requests.get(url, headers=headers, params=params)

    #print(html_page.url)
    #print(html_page.status_code)

    if html_page.status_code != 200:
        return -1

    soup = BeautifulSoup(html_page.content, 'html.parser')

    total_element = soup.find(
        "input", attrs={'id': 'TotalRowsView2D0D6A13720E853F9'})

    if total_element == None:
        return []

    total = total_element.get('value')  
    if total == "0":
        #print("По вашему запросу ничего не найдено.")
        return []

    #print("Find...")

    table_content = soup.find(attrs={'class': 'reporttable'})

    if table_content != None:
        table_elements = table_content.findAll('tr')
        
        if table_elements != None:
            # удаляем заголовок таблицы
            del table_elements[0]
            
            # перебераем строки таблицы
            for element in table_elements:                
                row = {}

                # идем по ячейкам строки
                tds = element.findAll('td')
                
                if tds == None:
                    continue
                
                i = 0
                row["place"] = region
                for td in tds:
                    
                    if i == 1:
                        row["number"] = td.text.strip()
                        
                        base_url = '{uri.scheme}://{uri.netloc}'.format(
                            uri=urlparse(url))
                        row["href"] = "{0}{1}".format(
                            base_url, td.a.get('href'))
                    
                    if i == 3:
                         row["type"] = td.text.strip()
                    
                    if i == 4:
                         row["name"] = td.text.strip()
                    
                    if i == 9:
                        row["start_date"] = td.text.strip()
                    
                    if i == 11:
                        row["end_date"] = td.text.split()[0].strip()

                    i = i + 1

                #print(row)
                result.append(row)            
    return result


def search(platform: [], words: []) -> []:
    url = platform["platform_url"]
    search_date_from = platform["last_update"]
    ticks = (datetime.strptime(platform["last_update"], "%d.%m.%Y") - datetime(1,1,1)).days * 24 * 60 * 60 * 1000 * 10000
    
    #637236288000000000
    #637134336000000000
    
    result_list = []

    regions = [
        {"name": "Алтайский край", "code": "22"},
        {"name": "Республика Алтай", "code": "04"},
        {"name": "Республика Тыва", "code": "17"},
        {"name": "Республика Хакасия", "code": "19"},
        {"name": "Иркутская область", "code": "38"},
        {"name": "Красноярский край", "code": "24"},
        {"name": "Кемеровская область", "code": "42"},
        {"name": "Новосибирская область", "code": "54"},
        {"name": "Омская область", "code": "55"},
        {"name": "Томская область", "code": "70"}
    ]

    
    
    for region in regions:
        #print(region)
        for word in words:
            #print(word["word"])            
            params = {
                "Filter": "1",
                "OrderName": word["word"],
                "RegionRF": region["code"],
                "ChangeDateTimeFrom": ticks,
                "ExpandFilter": "1"
            }
            result_list = result_list + get_scrap(url, params, region["name"])
            # print(len(result_list))

    if len(result_list) > 0:
        print(' '.join(["Запись в БД",platform['platform_name'],'...']))
        sql.create_row_object(platform, result_list)
    
    sql.update_platform_date(platform["id"])
    print(' '.join(["End",platform['platform_name'],'...']))
    return result_list
