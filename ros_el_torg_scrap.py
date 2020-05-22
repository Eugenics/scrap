import json
import requests
import re

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta


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


def get_scrap(url):
    result = []

    #print(url)
    #print(params)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    html_page = requests.get(url, headers=headers)

    print(html_page.url)
    print(html_page.status_code)
    print(html_page.text)

    if html_page.status_code != 200:
        return -1
    else:
        return result


"""
    soup = BeautifulSoup(html_page.content, 'html.parser')

    cards = soup.find_all(attrs={'class': 'purchase-card'})

    # print(cards)

    if cards != None:
        for card in cards:
            # print(card)
            row = {}
            row["number"] = card.find(attrs={'class': 'number'}).string
            row["type"] = card.find(attrs={'class': 'tag__link'}).string
            name_lines = card.find(attrs={'class': 'spoiler'}).a.text.splitlines()
            if len(name_lines) > 2:
                row["name"] = name_lines[2]
            elif len(name_lines) > 1:
                row["name"] = name_lines[1]
            else:
                row["name"] = ""
                        
            base_url = '{uri.scheme}://{uri.netloc}'.format(
                uri=urlparse(url))
            row["href"] = "{0}".format(card.find(
                attrs={'class': 'spoiler'}).a.get('href'))

            main_props = card.find_all(attrs={'class': 'prop'})
            
            if len(main_props) > 0:
                #print(main_props[4])

                if main_props[2].find(attrs={'class':'value'}).string != None:
                    row["place"] = main_props[2].find(
                        attrs={'class': 'value'}).string.replace("\r\n",'').strip()
                
                if main_props[4].find(attrs={'class':'value'}).text != None:
                    value_string = main_props[4].find(attrs={'class': 'value'}).text.splitlines()
                    start_date = value_string[1].split()
                    
                    if get_month(start_date) != None:
                        row["start_date"] = start_date[0] + "." + get_month(start_date) + "." + start_date[2].replace(',','')                        
                    else:
                        row["start_date"] = datetime.now(tz=timezone.utc).strftime("%d.%m.%Y")
                
                if main_props[5].find(attrs={'class':'value'}).text != None:
                    value_string = main_props[5].find(attrs={'class': 'value'}).text.splitlines()
                    end_date = value_string[1].split()
                    
                    if get_month(end_date) != None:
                        row["end_date"] = end_date[0] + "." + get_month(end_date) + "." + end_date[2].replace(',','')                        
                    else:
                        row["end_date"] = datetime.now(tz=timezone.utc).strftime("%d.%m.%Y")
            result.append(row)

            #print(row)
"""
# return result


def search(platform, words):
    url = platform["platform_url"]

    tommorrow = datetime.strptime(platform["last_update"], "%d.%m.%Y").replace(
        tzinfo=timezone.utc) + timedelta(days=1)
    search_date_from = tommorrow.strftime("%d.%m.%Y")

    result_list = []

    for word in words:
        params = [
            ("query_field", "радио"),
            ("status[]", "0"),
            ("status[]", "1"),
            ("region[]", "04"),
            ("region[]", "17"),
            ("region[]", "19"),
            ("region[]", "22"),
            ("region[]", "24"),
            ("region[]", "38"),
            ("region[]", "42"),
            ("region[]", "54"),
            ("region[]", "55"),
            ("region[]", "70"),
            ("currency", "all"),
            ("start_date_published", search_date_from),
            ("form_id", "searchp_form"),
            ("page", "")
        ]

        #get_scrap(url, params)

        get_scrap("https://www.roseltorg.ru/procedures/search?query_field=%D1%80%D0%B0%D0%B4%D0%B8%D0%BE&customer=&status%5B%5D=0&status%5B%5D=1&address=&start_price=&end_price=&currency=all&start_date_published=&end_date_published=&guarantee_start_price=&guarantee_end_price=&start_date_requests=&end_date_requests=&form_id=searchp_form&page=&from=35&_=1586878454413")

        # "https://www.roseltorg.ru/procedures/search?query_field=%D1%80%D0%B0%D0%B4%D0%B8%D0%BE&status%5B%5D=1&region%5B%5D=70&form_id=searchp_form&page=&from=0&query_field=%D1%80%D0%B0%D0%B4%D0%B8%D0%BE&customer=&status%5B%5D=0&status%5B%5D=1&region%5B%5D=70&currency=all&start_date_published=01.01.20&form_id=searchp_form&page=&query_field=%D1%80%D0%B0%D0%B4%D0%B8%D0%BE&customer=&status%5B%5D=0&status%5B%5D=1&address=&start_price=&end_price=&currency=all&start_date_published=&end_date_published=&guarantee_start_price=&guarantee_end_price=&start_date_requests=&end_date_requests=&form_id=searchp_form&page="

        # result_list = result_list + \
        #    get_scrap(url, params)

    # print(result_list)

    return result_list


def get_month(date_list):
    if len(date_list[1]) > 0:
        if date_list[1] == 'января':
            return '01'
        elif date_list[1] == 'февраля':
            return '02'
        elif date_list[1] == 'марта':
            return '03'
        elif date_list[1] == 'апреля':
            return '04'
        elif date_list[1] == 'мая':
            return '05'
        elif date_list[1] == 'июня':
            return '06'
        elif date_list[1] == 'июля':
            return '07'
        elif date_list[1] == 'августа':
            return '08'
        elif date_list[1] == 'сентября':
            return '09'
        elif date_list[1] == 'октября':
            return '10'
        elif date_list[1] == 'ноября':
            return '11'
        elif date_list[1] == 'декабря':
            return '12'
    return None


def build_params_string(params):
    params_string = ""
    cnt = 0
    for param in params:
        print(param)
        if cnt == 0:
            params_string = params_string + param
        else:
            params_string = params_string + "&" + param
        cnt = cnt + 1

    return params_string
