import requests
import pandas as pd
from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup
from requests.api import head
import smtplib


HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})


prod_tracker = pd.read_csv('products.csv', sep=";")
prod_tracker_URLS = prod_tracker.url

while(1):
    for x, url in enumerate(prod_tracker_URLS):
        page = requests.get(prod_tracker_URLS[x], headers=HEADERS)

        soup = BeautifulSoup(page.content, features="lxml")

        title = soup.find(id='productTitle').get_text().strip()

        # to prevent script from crashing when there isn't a price for the product
        try:
            price = float(soup.find(id='priceblock_ourprice').get_text().replace(
                '.', '').replace('€', '').replace(',', '.').strip())
        except:
            # this part gets the price in dollars from amazon.com store
            try:
                price = float(soup.find(id='priceblock_saleprice').get_text().replace(
                    '$', '').replace(',', '').strip())
            except:
                price = ''
        print(title + ": ")
        print(price)
        try:
            # This is where you can integrate an email alert!
            if price < prod_tracker.buy_below[x]:
                print('************************ ALERT! Buy the ' +
                      prod_tracker.code[x]+' ************************')

                credentials = pd.read_csv('credentials.csv', sep=";")
                username = credentials.email[0]
                password = credentials.password[0]
                reciver = credentials.reciver[0]
                server = smtplib.SMTP('smtp.gmail.com', 587)

                server.ehlo()
                server.starttls()
                server.login(username, password)

                msg = ('Subject: Price Alert\n\n\
Product price dropped: {}\nPrice: {}\n\nBuy now:\n {}\n\n'.format(title, price, prod_tracker.url[x]))

                # print(msg)
                server.sendmail(username,
                                reciver, msg)
                print('sent email.....')
            else:
                print("Non e' il momento")

        except:
            print("ERROR")
            # sometimes we don't get any price, so there will be an error in the if condition above
            pass

    sleep(18000)
