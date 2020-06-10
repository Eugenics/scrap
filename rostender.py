import time
import os
import requests
import requests.exceptions as r_exc
from bs4 import BeautifulSoup
from urllib.parse import urlparse

import sql_db as sql


def get_pages(url):
    page_count = 0

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    try:
        html_page = requests.get(url, headers=headers)
        # print(html_page.url)
        # print(html_page.status_code)

        if html_page.status_code != 200:
            return {"status_code": html_page.status_code, "page_count": 0}

        soup = BeautifulSoup(html_page.content, 'html.parser')
        search_items = soup.find('div', {'class': 'b-paging'})

        if search_items != None:
            pages = search_items.text.splitlines()[1].split()[2].split('[')[0]
            #print(pages)
            if len(pages) > 0:
                page_count = int(pages)
                return {"status_code": html_page.status_code, "page_count": page_count}

        return {"status_code": html_page.status_code, "page_count": 0}
    except r_exc as exc:
        print(exc.HTTPError)
        return {"status_code": "404", "page_count": 0}


def get_scrap(url, search_date_from):
    result = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    html_page = requests.Response()

    try:
        html_page = requests.get(url, headers=headers)
    except r_exc as exc:
        print(exc.HTTPError)
        return -1

    if html_page.status_code != 200:
        return -1

    soup = BeautifulSoup(html_page.content, 'html.parser')

    search_items = soup.findAll('div', {'class': 'tender-row'})

    if search_items != None:
        if len(search_items) > 0:
            index = 0
            for item in search_items:
                if index == 0:
                    index = index + 1
                    continue
                
                index = index + 1      
                row = {}
                
                dates = item.findAll(attrs={'class','tender-date-info'})
                row["start_date"] = dates[0].text.splitlines()[1].strip()
                row["end_date"] = dates[2].text.split()[2]
                
                if item.find(attrs={'class','col-lg-6'}) != None:
                    number_text = item.find(attrs={'class','col-lg-6'}).text.split()
                    row["number"] = number_text[2].strip()
                    row["type"] = number_text[0].strip()
                else:
                    row["number"] = ''
                    row["type"] = ''

                if item.find(attrs={'class', 'description'}) != None:
                    base_url = '{uri.scheme}://{uri.netloc}'.format(
                        uri=urlparse(url))
                    _href = item.find(
                        attrs={'class', 'description'}).a.get('href')
                    if _href != None:
                        row["href"] = "{0}{1}".format(base_url, _href)                    
                    row["name"] = item.find(attrs={'class', 'description'}).text.splitlines()[2].strip()
                else:
                    row["href"] = ''
                    row["name"] = ''

                if item.find(attrs={'class', 'region-links-in-cabinet'}) != None:
                    region_text = item.find(
                        attrs={'class', 'region-links-in-cabinet'}).text.splitlines()                    
                    row["place"] = region_text[3].strip()
                else:
                    row["place"] = ''

                print(row)
                
                result.append(row)
    return result


def search(platform: [], words: []) -> []:
    """
    Returns: List of search result strings

    Parameters:
        platform([]): Platform for search,
        word({}): Search word
    """
    url = ""
    base_url = platform["platform_url"]
    search_date_from = platform["last_update"]

    result = []

    for word in words:
        print(word["word"])
        print('Seaching page count...')
        search_pages_result = []

        search_sub_url = 'pgsearch=1&extsearch=2&geo5=on&geo11=on&geo25=on&geo40=on&geo44=on&geo172597=on&geo55=on&geo56=on&geo70=on&geo21=on&geo23=on&kwd=' + \
            word['word'] + '&from=' + search_date_from+'&to=&pfrom=&pto='
        url = '?'.join([base_url, search_sub_url])

        search_pages_result = get_pages(url)
        if search_pages_result['page_count'] == 0:
            continue

        print(word)
        print(':'.join(['Find pages', str(search_pages_result['page_count'])]))

        for page in range(search_pages_result['page_count']):
            print('Seaching results on page:' + str(page + 1))
            search_sub_url = 'pgsearch=' + str(page + 1) +'&extsearch=2&geo5=on&geo11=on&geo25=on&geo40=on&geo44=on&geo172597=on&geo55=on&geo56=on&geo70=on&geo21=on&geo23=on&kwd=' + \
                word['word'] + '&from=' + search_date_from + '&to=&pfrom=&pto='
            url = '?'.join([base_url, search_sub_url])
            result = result + get_scrap(url, platform["last_update"])

    # Insert into db
    if len(result) > 0:
        print(''.join(["Запись в БД", platform["platform_name"], '...']))
        sql.create_row_object(platform, result)

    sql.update_platform_date(platform["id"])

    print(len(result))
    #print(result)

    return result
