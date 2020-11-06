import requests
import random
import time
import threading
import discord_webhook
from itertools import cycle
from discord_webhook import DiscordWebhook, DiscordEmbed
from Coin_atc import main
from bs4 import BeautifulSoup as Soup
from colorama import Fore, Back, Style 
thread_lock = threading.Lock()

def proxy_fix_func():
    text = open('Proxies.txt' , 'r')
    proxy_list = text.readlines()
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
    return(new_list)

def monitor(link, proxy_list, pid):
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
    in_stock = False
    stock_status = None
    while True:
        proxy = random.choice(proxy_list)
        try:
            #print('Making request with Local Host')
            r = requests.get(link, headers=headers)
            if r.status_code == 200:
                parsed_r = Soup(r.text, 'html.parser')
                stock_status = parsed_r.find('img',{'id':'out-of-stock-image'}).get('src')
        except:
            with thread_lock:
                print(Fore.RED + 'Error Conncecting with Local Host... Trying Proxy')
        try:
            with thread_lock:
                print(Fore.YELLOW + 'Making request with {}'.format(proxy))
            r = requests.get(link, headers=headers, proxies={'https': 'http://'+proxy})
            if r.status_code == 200:
                parsed_r = Soup(r.text, 'html.parser')
                stock_status = parsed_r.find('img',{'id':'out-of-stock-image'}).get('src')
        except:
                print(Fore.RED + 'Error loading page... Might be proxy issue {}'.format(proxy))
        
        
        if stock_status == None and in_stock == False:
            with thread_lock:
                print(Fore.GREEN + 'In Stock!')
            if send_webhook(link, pid):
                with thread_lock:
                    print(Fore.YELLOW + 'Sent Webhook!')
            in_stock = True
        elif stock_status == None and in_stock == True:
            time.sleep(2)
            continue
        else:
            with thread_lock:
                print(Fore.YELLOW + 'Not in Stock')
            in_stock = False
            time.sleep(2)

def send_webhook(link, pid):
    token = 'https://discordapp.com/api/webhooks/774243792814604319/MPdtEck-zZadg5THtcdlJ0LOsklg02Znbnetpk1eGvHTltpD5ALMuIDSbnkI2ksmz-6h'
    #token = 'https://discordapp.com/api/webhooks/646904632601477140/LMd_Asxb1nUz46h-ukeMEloNgZE9PO4ShgNtm-mBHwPBKYjcjgkbGu5iZtVX2kxzlDwf'
    try:
        webhook = DiscordWebhook(url= token)
        embed = DiscordEmbed(title = 'Coin Restock!',color = 242424)
        embed.set_author(name='Lucky Cops Monitor')
        embed.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Seal_of_the_United_States_Mint.svg/1200px-Seal_of_the_United_States_Mint.svg.png')
        embed.set_footer(text = 'Bolt Cook Group')
        embed.set_timestamp()
        embed.add_embed_field(name = 'Link', value = link)
        embed.add_embed_field(name= 'ATC Link', value = 'https://catalog.usmint.gov/on/demandware.store/Sites-USM-Site/default/Cart-MiniAddProduct?pid={}&Quantity=1'.format(pid))
        webhook.add_embed(embed)
        webhook.execute()
        return True
    except:
        print('Error')
        return False

proxy_list = proxy_fix_func()
links = ['https://catalog.usmint.gov/end-of-world-war-ii-75th-anniversary-american-eagle-silver-proof-coin-20XF.html?cgid=silver-dollars', 'https://catalog.usmint.gov/end-of-world-war-ii-75th-anniversary-american-eagle-gold-proof-coin-20XE.html?cgid=gold-coins']
while True:
    for idx, val in enumerate(links):
        pid = val.split('https://catalog.usmint.gov/')[-1].split('.html')[0].split('-')[-1]
        t = threading.Thread(target=monitor, args=[val, proxy_list, pid], name='Task {}'.format(idx))
        t.start()
    t.join()
