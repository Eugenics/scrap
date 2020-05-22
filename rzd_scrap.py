import json
import requests

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

    # print(html_page.url)
    # print(html_page.status_code)

    if html_page.status_code != 200:
        return {"status_code": html_page.status_code, "page_count": 0}

    soup = BeautifulSoup(html_page.content, 'html.parser')
    pages = soup.findAll('div', {'class': 'pageer col-md-18'})

    # print(pages)

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

    if html_page.status_code != 200:
        return -1

    soup = BeautifulSoup(html_page.content, 'html.parser')

    table_content = soup.find(attrs={'class': 'table j-datenow'})

    if table_content != None:
        tr_scope = table_content.find_all('tr')
        for tr in tr_scope:
            row = {}
            td_scope = tr.find_all('td')
            if len(td_scope) > 0:
                row["start_date"] = datetime.now(tz=timezone.utc).strftime("%d.%m.%Y")                
                if td_scope[0].string != None:
                    row["end_date"] = td_scope[0].string
                else:
                    row["end_date"] = datetime.now(tz=timezone.utc).strftime("%d.%m.%Y")
                row["number"] = td_scope[1].a.string
                row["type"] = td_scope[2].string
                row["name"] = td_scope[3].a.string
                row["place"] = td_scope[4].string
                base_url = '{uri.scheme}://{uri.netloc}'.format(
                    uri=urlparse(url))
                row["href"] = "{0}{1}".format(
                    base_url, td_scope[3].a.get('href'))

                result.append(row)
    return result


def search(platform: [], words: [], queue: Queue()) -> []:
    url = platform["platform_url"]
    search_date_from = platform["last_update"]

    result_list = []

    for word in words:
        params = {
            "cod": "",
            "deal_type": "",
            "CLIENT_ID": "",
            "OKPD2_label": "",
            "city_id": "",
            "OKATO_label": "",
            "name": word["word"],
            "DATE_START_from": "",
            "DATE_START_to": "",
            "PUBLISH_DATE_from": search_date_from,
            "PUBLISH_DATE_to": "",
            "date_from": "",
            "date_to": "",
            "TENDER_TYPE": "",
            "MSP_SUBJECT": "",
            "OKVED2_label": "",
            "search-expanded": "1",
            "action": "filtr",
            "STRUCTURE_ID": "4078",
            "pagesize4893_1465": "10000"
        }

        page_count = get_pages(url, params)

        # print(word["word"])
        # print(page_count)

        if page_count["status_code"] == 200 and page_count["page_count"] > 0:
            #print(word["word"])
            #print(page_count)

            for p in range(page_count["page_count"]):
                # print(p+1)
                params["pageNumber"] = str(p+1).strip()
                result_list = result_list + get_scrap(url, params)
                #print(result_list)

    
    queue.put(result_list)
    return result_list
