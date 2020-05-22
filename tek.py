import json
import requests
import re
import sql_db as sql

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, timezone
from multiprocessing import Queue


def get_pages(url, params):
    page_count = 0

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    html_page = requests.get(url, headers=headers, params=params)

    print(html_page.url)
    print(html_page.status_code)

    if html_page.status_code != 200:
        return {"status_code": html_page.status_code, "page_count": 0}

    soup = BeautifulSoup(html_page.content, 'html.parser')
    pages = soup.find(attrs={'class': 'pagination__pages'})

    # print(soup.prettify())

    if soup.find_all(attrs={'class', "table j-datenow"}) != None:
        if pages != None:
            if len(pages) > 0:
                page_count = len(pages)
            else:
                page_count = 1
        else:
            page_count = 1

    return {"status_code": html_page.status_code, "page_count": page_count}


def get_scrap(url, params):
    result = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    html_page = requests.get(url, headers=headers, params=params)

    # print(html_page.url)
    # print(html_page.status_code)

    if html_page.status_code != 200:
        return -1

    soup = BeautifulSoup(html_page.content, 'html.parser')

    lines = soup.text.splitlines()
    for line in lines:
        if line == "По вашему запросу ничего не найдено.":
            #print("По вашему запросу ничего не найдено.")
            return []

    #print("Find...")

    table_content = soup.findAll(
        attrs={'class': 'section-procurement__item-information'})

    if table_content != None:
        for element in table_content:
            row = {}
            number = element.find(
                attrs={'class': 'section-procurement__item-numbers'}).span.text.splitlines()
            row["number"] = number[2].replace("\t\t\t", "").strip()

            element_type = element.find(attrs={'class':'section-procurement__item-request-price'})
            if element_type != None:
                row["type"] = element_type.text.strip()
            else:
                row["type"] = ""
            
            dateItem = element.find(
                attrs={'class': 'section-procurement__item-date'})
            if dateItem != None:
                dateToItems = dateItem.find_all(
                    attrs={'class': 'section-procurement__item-dateTo'})

                for dateItem in dateToItems:
                    # Статус
                    #if re.search(r'Статус', dateItem.text) != None:
                    #    typeItem = dateItem.text.splitlines()
                    #    if len(typeItem) > 2:
                    #        row["type"] = ""
                    #        #row["type"] = typeItem[2].strip().replace(
                    #        #    "\t", ":").split(':')[0].strip()
                    #    else:
                    #        row["type"] = ""

                    # Дата начала подачи заявок
                    if re.search(r'Дата публикации', dateItem.text) != None:
                        start_date = dateItem.text.splitlines()
                        row["start_date"] = start_date[2].replace(
                            "\t", "").strip().split()[0]

                    # Дата окончания подачи заявок
                    if re.search(r'Дата окончания приема заявок', dateItem.text) != None:
                        end_date = dateToItems[1].text.splitlines()
                        row["end_date"] = end_date[2].replace(
                            "\t", "").strip().split()[0]
                        #print(row["end_date"])

            row["name"] = element.find(
                attrs={'class': 'section-procurement__item-title'}).text
            row["place"] = params["region"]
            base_url = '{uri.scheme}://{uri.netloc}'.format(
                uri=urlparse(url))
            row["href"] = "{0}{1}".format(
                base_url, element.find(attrs={'class': 'section-procurement__item-title'}).get('href'))

            #print(row)
            result.append(row)
    return result


def search(platform: [], words: []) -> []:
    url = platform["platform_url"]
    search_date_from = platform["last_update"]

    result_list = []

    regions = [
        "Алтайский край",
        "Республика Алтай",
        "Республика Тыва",
        "Республика Хакасия",
        "Иркутская область",
        "Красноярский край",
        "Кемеровская область",
        "Новосибирская область",
        "Омская область",
        "Томская область"
    ]

    for region in regions:
        #print(region)
        for word in words:
            #print(word["word"])
            # print(region)
            params = {
                "q": word["word"],
                "dpfrom": search_date_from,
                "region": region,
                "limit": "500"
            }
            result_list = result_list + get_scrap(url, params)
            # print(len(result_list))

    if len(result_list) > 0:
        print(' '.join(["Запись в БД",platform['platform_name'],'...']))
        sql.create_row_object(platform, result_list)
    
    sql.update_platform_date(platform["id"])
    print(' '.join(["End",platform['platform_name'],'...']))
    return result_list
