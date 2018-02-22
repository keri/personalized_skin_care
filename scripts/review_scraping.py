from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, WebDriverException, StaleElementReferenceException
from collections import defaultdict
from bs4 import BeautifulSoup
import pandas as pd
#import json

import psycopg2

password = os.environ['DB_PASS']
user = os.environ['DB_USER_NAME']
host = os.environ['DB_HOST']
name = os.environ['DB_NAME']
port = 5432

class ReviewScraper:
    '''scrapes product reviews and puts into a database, ASIN, review url,
       review text, and star rating.'''

    def __init__(self, driver, product_type='moisturizer', con=''):
        self.conn = psycopg2.connect(dbname='skinproducts', host='skinproducts.cgz2ffd3hzsl.us-west-2.rds.amazonaws.com',
                                    password=password,user=user)
        self.con = con
        self.cur = self.conn.cursor()
        self.driver = driver
        self.select = self.driver.find_elements_by_css_selector
        self.select_one = self.driver.find_element_by_css_selector
        self.product_type = product_type


    def parse_review(self,review, ASIN):
        soup = BeautifulSoup(review, 'html.parser')
        rating = int(soup.select_one('i.review-rating span.a-icon-alt').text.split()[0][0])
        title = soup.select_one('a.review-title').text
        review_text = soup.select_one('span.review-text').text
        rater_find = soup.select_one('a.author')
        if rater_find:
            rater = rater_find.text
            rater_url = rater_find.attrs['href']

        else:
            rater = soup.select_one('span.a-profile-name').text
            rater_url = soup.select_one('a.a-profile').attrs['href']
        start = rater_url.find('account.')+8
        end = rater_url.find('/ref')
        rater_id = rater_url[start:end]
        review_date = soup.select_one('span.review-date')
        review_date = review_date.text[3:]
#        row = [ASIN, rater_id, rating, title, rater, review_date, review_text]
        df = pd.DataFrame({'asin':ASIN, 'rater_id':rater_id,'rating':rating,'title':title,
                            'rater':rater,'review_date':review_date,'review_text':review_text},index=['asin'])


        try:
            df.to_sql(name=self.product_type, if_exists='append', con=self.con,index=False)
#                    self.cur.execute(query)
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
             print(error)

    def see_all_reviews(self):
        allreviews_link = self.select_one('a#dp-summary-see-all-reviews')
        allreviews_link.click()
        time.sleep(3)


    def get_all_reviews(self, ASIN, url):
        '''start here and run through all urls in a list outside of class'''
        self.driver.get(url)
        time.sleep(1)
        self.see_all_reviews() #go to page with all of the reviews
        self.get_reviews(ASIN) #get the reviews on that page
        page = 1
        while page < 34 and self.goto_next_page():
            self.get_reviews(ASIN)
            page += 1


    def get_reviews(self, ASIN):
        reviews = self.driver.find_elements_by_css_selector('div.reviews-content div.review')
        time.sleep(1)
        for review in reviews:
            review = review.get_attribute('innerHTML')
            self.parse_review(review, ASIN) #enters the review into a database

            # with open(self.product_type + '.reviews.json', 'a') as f:
                # json.dump(json_dic, f)
                # f.write('\n')


    def goto_next_page(self):
        try:
            next_page_btn = self.driver.find_element_by_css_selector('li.a-last')
            if 'a-disabled' in next_page_btn.get_attribute('class'):
                return(False)
            if not next_page_btn:
                next_page_btn = self.driver.find_element_by_css_selector('li.a-last')
            else:
                next_page_btn.click()
                time.sleep(3)
                return(True)
        except NoSuchElementException:
            return(False)

