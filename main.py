import json
import multiprocessing as mp
import sql_db as sql

import gos_zak_scrap as gzs
import rzd_scrap as rzd
import rts_scrap as rts
import tek as tek
import zakaz_rf as zrf
import roseltorg as relt
import rostender as rten
import rad as rad

import selenium_sb_rf_scrap as sb



def main():
    platforms_list = json.loads(sql.get_search_platform())
    search_words_list = json.loads(sql.get_search_words())

    processes = []
    
    # List 
    selenium_processes = []

    # Count of processes to start
    count_of_selenium_processes = 2


    #result_list = []
    #queues = []

    # Selenium platforms       
    for platform in (platform for platform in platforms_list if platform["exclude_from_search"] == 0):
        if platform["platform_name"] == "Сбербанк" and platform["exclude_from_search"] == 0:
            try:
                print(len(search_words_list))
                for r in range(0, len(search_words_list), count_of_selenium_processes):
                    print(r)
                    # Делим на 4 процесса
                    sub_words_list = []
                    if len(search_words_list) - r > count_of_selenium_processes:
                        sub_words_list = search_words_list[r:r + count_of_selenium_processes]
                    else:
                        sub_words_list = search_words_list[r:r +
                                                           (len(search_words_list) - r)]

                    print(sub_words_list)

                    selenium_processes = []
                    for word in sub_words_list:
                        p = mp.Process(target=sb.search, args=(
                            platform, word), name=' '.join(['Process', word['word']]))
                        selenium_processes.append(p)
                        print('Start proccess: {}'.format(p.name))
                        p.start()
                    
                    if len(selenium_processes) > 0:
                        for p in selenium_processes:
                            p.join()
                            print('End proccess: {}'.format(p.name))
            except:
                print('Сбербанк Error!!!')        
              

    for platform in (platform for platform in platforms_list if platform["exclude_from_search"] == 0):
        if platform["platform_name"] == "Портал закупок":
            p = mp.Process(target=gzs.search, args=(platform, search_words_list), name=' '.join(
                ['Process', platform['platform_name']]))
            processes.append(p)
            print('Start proccess: {}'.format(p.name))
            p.start()           
        elif platform["platform_name"] == "РТС-тендер":
            p = mp.Process(target=rts.search, args=(platform, search_words_list), name=' '.join(
                ['Process', platform['platform_name']]))
            processes.append(p)
            print('Start proccess: {}'.format(p.name))
            p.start()
        elif platform["platform_name"] == "ТЭК":
            p = mp.Process(target=tek.search, args=(platform, search_words_list), name=' '.join(
                ['Process', platform['platform_name']]))
            processes.append(p)
            print('Start proccess: {}'.format(p.name))
            p.start()
        elif platform["platform_name"] == "Заказ РФ":
            p = mp.Process(target=zrf.search, args=(platform, search_words_list), name=' '.join(
                ['Process', platform['platform_name']]))
            processes.append(p)
            print('Start proccess: {}'.format(p.name))
            p.start()
        elif platform["platform_name"] == "РОСЭЛТОРГ":
            p = mp.Process(target=relt.search, args=(platform, search_words_list), name=' '.join(
                ['Process', platform['platform_name']]))
            processes.append(p)
            print('Start proccess: {}'.format(p.name))
            p.start()
        elif platform["platform_name"] == "РосТендер":
            p = mp.Process(target=rten.search, args=(platform, search_words_list), name=' '.join(
                ['Process', platform['platform_name']]))
            processes.append(p)
            print('Start proccess: {}'.format(p.name))
            p.start()
        elif platform["platform_name"] == "рад":
            p = mp.Process(target=rad.search, args=(platform, search_words_list), name=' '.join(
                ['Process', platform['platform_name']]))
            processes.append(p)
            print('Start proccess: {}'.format(p.name))
            p.start()
    

    if len(processes) > 0:
        print(len(processes))
        for p in processes:
            print(p.name)
            p.join()
            print('End proccess: {}'.format(p.name))


if __name__ == '__main__':
    mp.freeze_support()
    main()
