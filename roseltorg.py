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
        search_items = soup.findAll('div', {'class': 'search-results__item'})

        if search_items != None:
            if len(search_items) > 0:
                page_count = 1
                return {"status_code": html_page.status_code, "page_count": page_count}

        return {"status_code": html_page.status_code, "page_count": 0}
    except r_exc as exc:
        print(exc.HTTPError)
        return {"status_code": "404", "page_count": 0}


def get_scrap(url,search_date_from):
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

    search_items = soup.findAll('div', {'class': 'search-results__item'})

    if search_items != None:
        if len(search_items) > 0:
            for item in search_items:
                item_text = []
                item_text = item.text.splitlines()

                # print(item_text)

                row = {}
                row["start_date"] = search_date_from
                if len(item.find(attrs={'class', 'search-results__time'}).text.split()) > 0:
                    date_value = item.find(
                        attrs={'class', 'search-results__time'}).text.split()[0].split('.')
                    # print(date_value)
                    row["end_date"] = '.'.join(
                        [date_value[0], date_value[1], '20' + date_value[2]])
                else:
                    row["end_date"] = ""
                row["number"] = item_text[5].strip()
                row["type"] = item_text[20].strip()
                row["name"] = item_text[12].strip()
                base_url = '{uri.scheme}://{uri.netloc}'.format(
                    uri=urlparse(url))
                _href = item.find(
                    attrs={'class', 'search-results__lot'}).a.get('href')
                if _href != None:
                    row["href"] = "{0}{1}".format(base_url, _href)
                else:
                    row["href"] = ""

                if item.find(attrs={'class', 'search-results__region'}) != None:
                    region_text = item.find(
                        attrs={'class', 'search-results__region'}).text
                    # print(region_text)
                    row["place"] = region_text.split('.')[1].strip()
                else:
                    row["place"] = ""

                # print(row)
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
    date_value = platform["last_update"].split('.')
    search_date_from = '.'.join(
        [date_value[0], date_value[1], date_value[2][2:]])

    result = []

    for word in words:
        print(word["word"])
        print('Seaching page count...')
        page_from = 0
        search_pages = 1
        search_pages_result = []

        while search_pages > 0:
            search_sub_url = 'query_field=' + \
                word['word'] + '&customer=&status[]=0&status[]=1&status[]=2&status[]=3&status[]=4&region[]=04&region[]=17&region[]=19&region[]=22&region[]=24&region[]=38&region[]=42&region[]=54&region[]=55&region[]=70&currency=all&start_date_published=' + \
                search_date_from + \
                '&form_id=searchp_form&page=&from=' + str(page_from)
            url = '?'.join([base_url, search_sub_url])

            search_pages_result = get_pages(url)
            if search_pages_result['page_count'] == 1:
                page_from = page_from + 11
            else:
                search_pages = 0

        # print(word)
        #print(':'.join(['Find pages', str(page_from / 11)]))
        print('Page from:' + str(page_from))
        if page_from > 0:
            page_range = int((page_from / 11))
            print('Page range:' + str(page_range))

            for page in range(page_range):
                print('Seaching results on page:' + str(page))
                search_sub_url = 'query_field=' + \
                    word['word']+'&customer=&status[]=0&status[]=1&status[]=2&status[]=3&status[]=4&region[]=04&region[]=17&region[]=19&region[]=22&region[]=24&region[]=38&region[]=42&region[]=54&region[]=55&region[]=70&currency=all&start_date_published=' + \
                    search_date_from + \
                    '&form_id=searchp_form&page=&from=' + str(page * 11)
                url = '?'.join([base_url, search_sub_url])
                result = result + get_scrap(url, platform["last_update"])

    # Insert into db
    #if len(result) > 0:
    #    print(''.join(["Запись в БД", platform["platform_name"], '...']))
    #    sql.create_row_object(platform, result)

    #sql.update_platform_date(platform["id"])

    print(len(result))
    print(result)

    return result
