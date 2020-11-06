import requests
import json
import time
import threading
from bs4 import BeautifulSoup as Soup
from colorama import Fore, Back, Style 
from datetime import datetime
from itertools import cycle
prink_lock = threading.Lock()

def proxy_fix_func():
    proxy_list = [
        "23.234.142.22:60132:leaf:Vhh8tUxn",
        "23.234.142.220:56194:leaf:Vhh8tUxn",
        "23.234.142.221:55035:leaf:Vhh8tUxn",
        "23.234.142.222:55609:leaf:Vhh8tUxn",
        "23.234.142.223:56998:leaf:Vhh8tUxn",
        "23.234.142.224:62298:leaf:Vhh8tUxn",
        "23.234.142.225:60494:leaf:Vhh8tUxn",
        "23.234.142.226:55116:leaf:Vhh8tUxn",
        "23.234.142.227:57761:leaf:Vhh8tUxn"
        ]

    new_list = []
    for i in proxy_list:
        i = i.strip()
        if len(i.split(':')) == 4:
            proxy_temp = i.split(':')[0:2]
            password = i.split(':')[2:]
            password = ':'.join(password)
            proxy_temp = ':'.join(proxy_temp)
            new_proxy = '{}@{}'.format(password, proxy_temp)
            new_list.append(new_proxy)
        else:
            new_list.append(i)
    #print(new_list)
    return(new_list)

def add_coin(proxy, account_info, pid):
    not_loaded = True
    atc_link = 'https://catalog.usmint.gov/on/demandware.store/Sites-USM-Site/default/Cart-AddProduct?format=ajax'
    # atc_data = {
    #     'cartAction': 'add',
    #     'pid': '20CC',
    #     'cgid': 'silver-coins',
    #     'egc': 'null',
    #     'navid': '',
    #     'Quantity': '1'
    # }

    atc_data = {
        'cartAction': 'add',
        'pid': pid,
        'cgid': 'silver-dollars',
        'egc': 'null',
        'navid': '',
        'Quantity': '1'
    }

    account_link = 'https://catalog.usmint.gov/account-login'
    account_login_data = {
        'dwfrm_login_username': account_info[0],
        'dwfrm_login_password': account_info[1],
        'dwfrm_login_login': 'Login',
        'dwfrm_login_securekey': ''
    }

    #jayleen@ninosoles.com
    #Jayleen196800_

    #First you must login 
    session = requests.Session()
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
    while not_loaded:
        try:
            r = session.get(account_link, headers=headers, timeout=5)
            parsed_r = Soup(r.text, 'html.parser')
            temp_link = parsed_r.find('div',{'class':'loginForm contained-form'})
            account_login = temp_link.find('form',{'class':'clearfix'}).get('action')
            secure_key = temp_link.find('input',{'name':'dwfrm_login_securekey'}).get('value')
            account_login_data['dwfrm_login_securekey'] = secure_key
            if secure_key or account_login != None:
                with prink_lock:
                    print('{} : Found Secure Key {}'.format(threading.current_thread().name, secure_key))
                not_loaded = False
            else:
                with prink_lock:
                    print('{} : No Key found...'.format(threading.current_thread().name))
        except:
            with prink_lock:
                print('{} : Error Getting page...'.format(threading.current_thread().name))
            time.sleep(2)
            
    #You then fetch the unique login link, Also grabs secure key needed for login
    # temp_link = parsed_r.find('div',{'class':'loginForm contained-form'})
    # account_login = temp_link.find('form',{'class':'clearfix'}).get('action')
    # secure_key = temp_link.find('input',{'name':'dwfrm_login_securekey'}).get('value')
    # account_login_data['dwfrm_login_securekey'] = secure_key

    #Logs in
    not_logged_in = True
    while not_logged_in:
        try:
            with prink_lock:
                print('{} : Logging In with {}'.format(threading.current_thread().name, account_info[0]))
            r2 = session.post(account_login, data=account_login_data, headers=headers, timeout=10)
            if r2.status_code == 200 and r2.url == account_link:
                with prink_lock:
                    print('{} : Logged into {} account!'.format(threading.current_thread().name, account_info[0]))
                not_logged_in = False
            else:
                print('Error Logging in. Trying Again!')
                time.sleep(2)
        except:
            with prink_lock:
                print('{} : Error Logging in with {} ... Trying again'.format(threading.current_thread().name, account_info[0]))
                print('{} : Status Code {}'.format(threading.current_thread().name, r2.url))

    #Adds Item to Cart
    not_in_cart = True
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if current_time == '07:30:00' or current_time == '07:30:00':
            #print('{} : Time to add to cart'.format(threading.current_thread().name))
            print('\n')
            break
    start = time.time()
    while not_in_cart:
        with prink_lock:
            print('{} : Adding to Cart...'.format(threading.current_thread().name))
        while True:
            try:
                r3 = session.post(atc_link, data=atc_data, headers=headers, timeout=5)
                #print(r3.status_code)
            except:
                with prink_lock:
                    print('{} : Error adding to cart trying again...'.format(threading.current_thread().name))
                #time.sleep(2)
            try:
                if r3.status_code == 200:
                    cart_text = Soup(r3.text, 'html.parser')
                    price_text = cart_text.find('span',{'class':'mini-cart-total-label'}).text
                    title_text = cart_text.find('div',{'class':'mini-cart-name'}).text.strip()
                    with prink_lock:
                        print(Fore.GREEN + '{} : Account {} has added {} {} in {}'.format(threading.current_thread().name, account_info[0], title_text, price_text, time.time() - start))
                    not_in_cart = False
                    break
            except:      
                with prink_lock:
                    print('{} : Error adding to cart'.format(threading.current_thread().name))
    return

def main(pid):
    proxies = proxy_fix_func()
    proxy_pool = cycle(proxies)
    accounts = [['ninox1@ninosoles.com','Jayleen196800_'],['ninox2@ninosoles.com','Jayleen196800_'],['yunior.aguirre@yahoo.com', 'Jayleen196800_']]
    print('\n')

    for idx, val in enumerate(accounts):
        proxy = next(proxy_pool)
        t = threading.Thread(target=add_coin, args=[proxy, val, pid], name='Task {}'.format(idx))
        t.start()
    t.join()

#main()
