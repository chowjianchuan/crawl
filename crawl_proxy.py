# -*- coding: UTF-8 -*-
import requests
import time
from lxml import etree
from threading import Thread
import pymysql
import random
import datetime
'''
从 西刺、快代理 获取免费代理并测试。可用存入数据库
'''


USER_AGENT = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
]


def random_user_agent():
    '''
    :return: User-agent
    '''
    User_Agent = random.choice(USER_AGENT)
    return User_Agent


def crawl_kuaidaili(page_num, proxy_list):
    '''
    crawl https://www.kuaidaili.com website date
    :param page_num: url page num
    :param proxy_list: save proxy
    :return: None
    '''
    url = 'https://www.kuaidaili.com/free/inha/' + page_num
    html = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    html = etree.HTML(html.text)
    ip = html.xpath('//*[@id="list"]/table/tbody/tr/td[1]')
    port = html.xpath('//*[@id="list"]/table/tbody/tr/td[2]')
    agreement = html.xpath('//*[@id="list"]/table/tbody/tr/td[4]')
    for num in range(len(ip)):
        if agreement[num].text == 'HTTP':
            item = 'http://' + ip[num].text + ':' + str(port[num].text) + 'A'
            proxy_list.append(item)
        if agreement[num].text == 'HTTPS':
            item = 'https://' + ip[num].text + ':' + str(port[num].text) + 'S'
            proxy_list.append(item)
    time.sleep(TIME_SLEEP)
    return None


def crawl_xicidaili(page_num, proxy_list):
    '''
    crawl https://www.xicidaili.com/ website date
    :param page_num: url page num
    :param proxy_list: save proxy
    :return: None
    '''
    url = 'https://www.xicidaili.com/nn/' + page_num
    html = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    html = etree.HTML(html.text)
    ip = html.xpath('//*[@id="ip_list"]//tr/td[2]')
    port = html.xpath('//*[@id="ip_list"]//tr/td[3]')
    agreement = html.xpath('//*[@id="ip_list"]//tr/td[6]')
    for num in range(len(ip)):
        if agreement[num].text == 'HTTP':
            item = 'http://' + ip[num].text + ':' + str(port[num].text) + 'A'
            proxy_list.append(item)
        if agreement[num].text == 'HTTPS':
            item = 'https://' + ip[num].text + ':' + str(port[num].text) + 'S'
            proxy_list.append(item)
    time.sleep(TIME_SLEEP)
    return proxy_list


def test_proxy(proxy, scucess_list, test_proxt):
    proxies = {'http': proxy[:-1]}
    try:
        html = requests.get(test_proxt, headers=HEADERS, timeout=TIMEOUT, proxies=proxies)
        if html.status_code == 200:
            if proxy[-1] == 'A':
                item = {'proxy': proxy[:-1], 'agreement': 'http'}
            if proxy[-1] == 'S':
                item = {'proxy': proxy[:-1], 'agreement': 'https'}
            scucess_list.append(item)
            return None
    except Exception:
        return None


def to_mysql(item):
    times = datetime.datetime.now().strftime('%b-%d-%Y %H:%M')
    data = dict(item)
    data['time'] = times
    keys = ','.join(data.keys())
    values = ','.join(['%s'] * len(data))
    database = pymysql.connect(host=HOST, user='root', password='chuan', port=3306, database='crawl_py')
    cursor = database.cursor()
    sql = 'INSERT INTO {TableName}({keys})VALUES({values})'.format(TableName='proxy', keys=keys, values=values)
    try:
        cursor.execute(sql, tuple(data.values()))
        database.commit()
    except Exception as e:
        database.rollback()
        print('Insert Erro', e)
    cursor.close()
    database.close()


if __name__ == '__main__':
    HOST = '120.78.204.15'
    TEST_URL = 'https://www.baidu.com/'  #
    TIMEOUT = 1
    HEADERS = {"User-agent": random_user_agent()}
    TIME_SLEEP = 1  # 网页抓取间隔时间
    MAX_PAGE = 6
    TEST_PROXY = []  # save test proxy
    SCUCESS_LIST = []  # save scucess proxy


    #  重置数据库
    database = pymysql.connect(host=HOST, user='root', password='chuan', port=3306, database='crawl_py')
    cursor = database.cursor()
    sql = "TRUNCATE table proxy"
    cursor.execute(sql)
    cursor.close()
    database.close()
    
    #  抓取主程序
    for page in range(1, MAX_PAGE):
        page = str(page)
        proxy_kuai = Thread(target=crawl_kuaidaili, args=(page, TEST_PROXY))
        proxy_xici = Thread(target=crawl_xicidaili, args=(page, TEST_PROXY))
        proxy_kuai.start()
        proxy_xici.start()
        proxy_xici.join()
        proxy_kuai.join()
    set_list = list(set(TEST_PROXY))
    while set_list:
        try:
            pro1 = set_list.pop()
            pro2 = set_list.pop()
            test_kuai = Thread(target=test_proxy, args=(pro1, SCUCESS_LIST, TEST_URL))
            test_xici = Thread(target=test_proxy, args=(pro2, SCUCESS_LIST, TEST_URL))
            test_kuai.start()
            test_xici.start()
            test_kuai.join()
            test_xici.join()
        except Exception:
            pass
    print(len(TEST_PROXY))  # 代理列表
    print(len(SCUCESS_LIST))  # 测试成功代理列表
    for item in SCUCESS_LIST:
        to_mysql(item)
    print('Crawl proxy Scucessfull')

