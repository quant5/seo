# -*- coding: utf-8 -*-

'''
this script compares SEO effectiveness of two companies by performing a 
specified series of Google searches for terms relevant to these companies, 
and recording how soon each company's search result shows up.
'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import random
import csv
import companies, user_agents, proxies
from socket import error as socket_error


BUSINESSES = companies.BUSINESSES

def get_new_proxy():

    rand_proxy = random.choice(proxies.PROXIES.keys())
    proxy = {
        "http": "{}:{}".format(rand_proxy,
                               proxies.PROXIES[rand_proxy])
    }
    return proxy

def get_random_user_agent():

    USER_AGENTS = user_agents.USER_AGENTS
    user_agent = random.choice(USER_AGENTS).format(random.randint(500,500)/100.0, \
        random.randint(0,100000)/100.0, random.randint(0,10000000)/100.0)
    return user_agent

def open_chrome():

    chrome_options = webdriver.ChromeOptions()
    proxy = get_new_proxy()
    user_agent = get_random_user_agent()
    chrome_options.add_argument('--proxy-server='.format(proxy))
    chrome_options.add_argument('--user-agent={}'.format(user_agent))

    chrome = webdriver.Chrome(chrome_options=chrome_options)
    chrome.set_page_load_timeout(30)
    chrome.set_window_size(250, 250)

    return chrome

def search_with_selenium(chrome, search_term, coupon=False):

    # if proxy / user-agent is declined, return 0 and try a different one
    try:
        chrome.get('https://www.google.com')
    except socket_error:
        return 0,0
    search_cookie = chrome.get_cookie('PREF')
    # add cookies to return 100 results per search
    search_cookie['value'] = search_cookie['value'].replace('FF=0','FF=0:LD=en:NR=100')
    search_cookie['value'] = search_cookie['value'].replace('S=','SG=2:S=')
    print search_cookie['value']
    chrome.add_cookie({'name': 'PREF', 'value': search_cookie['value'], 'path':'/', 'domain':'.google.com'})
    searchbar = chrome.find_element_by_name('q')

    if coupon:
        search_term += " coupon"
    # put the search term in google and hit return
    try:
        searchbar.send_keys(search_term)
    except UnicodeDecodeError: # in case some of the businesses have odd characters
        searchbar.send_keys(''.join([i if ord(i) < 128 else ' ' for i in search_term]))
    searchbar.send_keys(Keys.RETURN)
    print "searching: {}".format(search_term)
    sleep(random.random() + 1)
    results = chrome.find_elements_by_xpath('//h3[@class="r"]/a')
    if not results:
        print "this user agent was blocked - switching user agent"
        chrome.close()
        chrome.quit()
        return 0,0

    links = []
    for result in results:
        result_url = result.get_attribute('href').replace('google.com/url','')
        links.append(result_url)
        print result_url
    print "{} results found".format(len(results))
    chrome.close()
    chrome.quit()
    return filter_search_results(links,"groupon.com"),filter_search_results(links,"yelp.com")

def filter_search_results(links,site_string):

    rank = 0
    for link in links:
        if "google." in link:
            continue
        if site_string in link:
            if rank < 100:
                return rank + 1
            else:
                return "NA"
        rank += 1
    return "NA"

def main():

    # change path if desired. Change 'w' to 'a' if don't want to overwrite
    csv_open = open('results.csv', 'w') 
    csv_writer = csv.writer(csv_open)

    for i,biz in enumerate(BUSINESSES):
        if i > 0:
            print "Switching IP"

        print "Searching {} of {}".format(i+1,len(BUSINESSES))

        groupon_rank, groupon_rank_2 = 0, 0
        while groupon_rank == 0 or groupon_rank_2 == 0:
            chrome = open_chrome()
            if groupon_rank == 0:
                groupon_rank, yelp_rank = search_with_selenium(chrome,biz,coupon=False)
            if groupon_rank_2 == 0:
                groupon_rank_2, yelp_rank_2 = search_with_selenium(chrome,biz,coupon=True)
            sleep(random.random() + 1)

        csv_writer.writerow([biz, groupon_rank, yelp_rank, biz+" Coupon", groupon_rank_2,  yelp_rank_2])
        csv_open.flush()            

    chrome.quit()
    csv_open.close()


if __name__ == '__main__':
    main()
