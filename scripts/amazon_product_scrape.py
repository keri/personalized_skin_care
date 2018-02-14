from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
#from postgres import PostGres
import pandas as pd
import numpy as np
import psycopg2
#from queries import PostGres

password = os.environ['DB_PASS']
user = os.environ['DB_USER_NAME']
host = os.environ['DB_HOST']
name = os.environ['DB_NAME']
port = 5432

class AmazonScraper():
    '''scrapes product info and puts into a dictionary for url, ASIN, description,
        ingredients, price, title, number of reviews, ranking, review url.
        external methods:
        get_product_urls: returns url_list
        next_page : no return
        get_product_info : returns dictionary'''

    def __init__(self, driver,product_type='moisturizer',con='',page=1):
        self.conn = psycopg2.connect(dbname='skinproducts', host='skinproducts.cgz2ffd3hzsl.us-west-2.rds.amazonaws.com',
                                    password=password,user=user)
        self.con = con
        self.cur = self.conn.cursor()
        self.page = page
        self.driver = driver
        self.select = self.driver.find_elements_by_css_selector
        self.select_one = self.driver.find_element_by_css_selector
        self.product_type = product_type
        self.search_products_()
        self.page_urls = self.collecting_page_urls(page)
        self.iterate_product_pages()

    def image_url(self):
        image_id = self.select_one('#imgTagWrapperId img')
        url = image_id.get_attribute('src')
        return(url)


    def search_products_(self):

 #       self.driver.get('https://www.amazon.com/')
        if self.product_type == 'serum':
            self.driver.get('https://www.amazon.com/s/ref=sr_pg_3?rh=n%3A3760911%2Cn%3A11060451%2Ck%3Askin+products+face+serum&page='+str(self.page)
                        +'&keywords=skin+products+face+serum&ie=UTF8&qid=1518549923')#        Waits 1 second for the page to load and then goes to the search box
            self.page += 1
        elif self.product_type == 'cleanser':
            self.driver.get('https://www.amazon.com/s/ref=sr_pg_3?rh=n%3A3760911%2Cn%3A11060451%2Ck%3Askin+products+face+cleanser&page='+str(self.page)
                        +'&keywords=skin+products+face+cleanser&ie=UTF8&qid=1518553730')
            self.page += 1
        # time.sleep(1);
        # search_box = self.select_one('input#twotabsearchtextbox')
        # search_box.click()
        # query = 'face skin products ' + self.product_type
        # search_box.send_keys(query)
        # search_button = self.driver.find_element_by_css_selector('div.nav-search-submit input.nav-input')
        # search_button.click()

    def collecting_page_urls(self,page):
#        self.driver.get('https://www.amazon.com/s/ref=sr_pg_3?rh=n%3A3760911%2Ck%3Aface+skin+products+moisturizer&page=3&keywords=face+skin+products+moisturizer&ie=UTF8&qid=1516071427')
        page_urls = []
        while self.page < (page + 20):
            self.page += 1
            url_list = self.get_product_urls_()
            page_urls.append(url_list)
            try:
                self.next_page()
            except ElementNotVisibleException:
                continue
        return page_urls

    def iterate_product_pages(self):
            for page in self.page_urls:
                self.get_product_info_(page)


    def page_urls(self):
        return(self.page_urls)

    def get_product_urls_(self):
        '''returns all urls from one page'''
        url_list = []
        products = self.select('ul#s-results-list-atf li')
        for product in products:
            try:
                detail_link = product.find_element_by_css_selector('a.s-access-detail-page')
                url_list.append(detail_link.get_attribute('href'))
            except NoSuchElementException:
                continue
        return url_list

    def next_page(self):
        next_page = self.select_one('div#bottomBar div#pagn a#pagnNextLink span.srSprite')
        if next_page:
            next_page.click()
        else:
            next_page = self.select_one('span.pagnNextArrow')
            if next_page:
                next_page.click()
            else:
                self.search_products_()

 #       time.sleep()


    def get_ingredients_directions_(self):
            ingredients_directions = self.select_one(('div#importantInformation div.bucket div.content'))
            #split the string based on double space. There are three strings, we want ingredient and direction
            ingredients_directions_string = ingredients_directions.text
            ingredients_directions_list = ingredients_directions_string.split('\n\n')
            return(ingredients_directions_list)

    def parse_item_(self, item):
        item_split = item.split('\n')
        key = item_split[0]
        try:
            description = item_split[1].split(':')
            if len(description) > 1:
                description = description[1]
        except IndexError:
            description = 'None'
        return(key,description)

    def get_ingredient_directions_list_(self, tag):
        html = self.select_one((tag))
        text = html.text
        #we are splitting on the new line.
        items = text.split('\n\n')
        return(items)

    def get_product_details_(self, info_list):
        ASIN = ''
        ranking = 'None'
        n_reviews = float(0.0)
        for item in info_list:
            item = item.text.split(':')
            if item[0] == 'ASIN':
                ASIN = item[1][1:]
            elif item[0] == 'Amazon Best Sellers Rank':
                ranking = item[1]
            elif item[0] == 'Average Customer Review':
                n_reviews = item[1][2:-17]
                n_reviews = n_reviews.replace(',','')
                n_reviews = n_reviews.replace(' ','')
                try:
                    n_reviews = int(n_reviews)
                except ValueError:
                    n_reviews = 0

        return(ASIN, ranking, n_reviews)

    def get_review_url_(self):
        try:
            link = self.select_one('a#acrCustomerReviewLink')
            review_link = link.get_attribute('href')
        except NoSuchElementException:
            review_link = 'None'
        return(review_link)

    def get_product_info_(self,page):
        '''Capturing:
                ASIN,product type, url, reviewurl, price,ranking,
                number of reviews, ingredients, directions, safety, title
          Inserting each row in to the database for every url.'''
        ingredients = 'None'
        directions = 'None'
        indications = 'None'

        for url in page:
            self.driver.get(url)
            try:
                title = self.select_one('span#productTitle').text
            except NoSuchElementException:
                title = 'None'
            try:
                price = (self.select_one('div#unifiedPrice_feature_div div#burjOneTimePrice div#snsPrice div.a-section span.a-size-large.a-color-price').text)
                price = float(price[1:])
            except ValueError:
                continue
            except NoSuchElementException:
                try:
                    price = (self.select_one('span#priceblock_ourprice').text)
                    price = float(price[1:])
                except ValueError:
                    continue
                except NoSuchElementException:
                    try:
                        price = (self.select_one('span#priceblock_dealprice').text)
                        price = float(price[1:])
                    except ValueError:
                        continue
                    except NoSuchElementException:
                        try:
                            price = (self.select_one('span#priceblock_saleprice').text)
                            price = float(price[1:])
                        except NoSuchElementException:
                                price = float(0)

            review_url = self.get_review_url_()

            try:
                ingredients_directions_list = self.get_ingredient_directions_list_(('div#importantInformation div.content'))

                for item in ingredients_directions_list:
                    key, value = self.parse_item_(item)
                    if key == 'Ingredients':
                        ingredients = value
                    elif key == 'Directions':
                        directions = value
                    elif key == 'Indications':
                        indications = value

            except NoSuchElementException:
                continue

            info_list = self.select('div#detail-bullets div.content li')
            ASIN, ranking, n_reviews = self.get_product_details_(info_list)
            image_url = self.image_url()

            df = pd.DataFrame({'asin':ASIN, 'producttype':self.product_type,'url':url,'reviewurl':review_url,
                                'price':price,'ranking':ranking,'numberreviews':n_reviews,'ingredients':ingredients,
                                'directions':directions,'indications':indications,'title':title,'imageurl':image_url},index=['asin'])

            if ASIN:
                # asin = ASIN
                # # row = [ASIN, self.product_type, url,review_url, price, ranking,
                # #         n_reviews, ingredients, indications, title,image_url]
                # query = '''
                # INSERT INTO productinfo(asin,producttype,url,reviewurl,price,ranking,
                #             numberreviews, ingredients, indications, title,imageurl)
                # VALUES(asin,producttype,url,reviewurl,price,ranking,
                #             numberreviews, ingredients, indications, title,imageurl)'''

#                df.to_sql(name='productinfo', if_exists='append', con=self.con,index=False)

                try:
                    df.to_sql(name='productinfo', if_exists='append', con=self.con,index=False)
#                    self.cur.execute(query)
                    self.conn.commit()
                except (Exception, psycopg2.DatabaseError) as error:
                     print(error)
