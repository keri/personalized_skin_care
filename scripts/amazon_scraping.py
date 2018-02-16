from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
from selenium.common.exceptions import NoSuchElementException
chromedriver = "/Applications/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

driver = webdriver.Chrome(chromedriver)

#creating a shortcut for selecting css elements
select = driver.find_elements_by_css_selector
select_one = driver.find_element_by_css_selector

def search_products(product_type):
    driver.get('https://www.amazon.com/')
    # Waits 1 second for the page to load and then goes to the search box
    time.sleep(1);
    search_box = select_one('input#twotabsearchtextbox')
    search_box.click()
    query = 'face skin products ' + product_type
    search_box.send_keys(query)
    search_button = driver.find_element_by_css_selector('div.nav-search-submit input.nav-input')
    search_button.click()

def get_product_urls():
    '''returns all urls from one page'''
    url_list = []
    products = select('ul#s-results-list-atf li')
    for product in products:
        try:
            detail_link = product.find_element_by_css_selector('a.s-access-detail-page')
            url_list.append(detail_link.get_attribute('href'))
        except NoSuchElementException:
            continue
    return url_list

#click on next page
def next_page():
    next_page = select_one('div#bottomBar div#pagn a#pagnNextLink span.srSprite')
    next_page.click()
#    driver.get(url)


'''Got to each page and get product_information with the urls.'''

def get_ingredients_directions():
        ingredients_directions = select_one(('div#importantInformation div.bucket div.content'))
        #split the string based on double space. There are three strings, we want ingredient and direction
        ingredients_directions_string = ingredients_directions.text
        ingredients_directions_list = ingredients_directions_string.split('\n\n')
        return(ingredients_directions_list)

def parse_item(item):
    item_split = item.split('\n')
    key = item_split[0]
    try:
        description = item_split[1].split(':')
        if len(description) > 1:
            description = description[1]
    except IndexError:
        description = 'None'
    return(key,description)


def get_ingredient_directions_list(tag):
    html = select_one((tag))
    text = html.text
    #we are splitting on the new line.
    items = text.split('\n\n')
    return(items)

def get_product_details(lst):
    ASIN = ''
    ranking = ''
    n_reviews = ''
    for item in lst:
        item = item.text.split(':')
        if item[0] == 'ASIN':
            ASIN = item[1]
        elif item[0] == 'Amazon Best Sellers Rank':
            ranking = item[1]
        elif item[0] == 'Average Customer Review':
            n_reviews = item[1][2:-17]

    return(ASIN, ranking, n_reviews)

def get_review_url():
    link = select_one('a#acrCustomerReviewLink')
    return(link.get_attribute('href'))

def get_product_info(urls, product_type):

    #make a generic dictionary name for the specific product type
    product_info = {'review_number':'empty',
                    'ranking':'empty',}
    product_dict = {'ASIN':'', 'product_type':product_type, 'product_info': product_info,'review_url':''}

    for url in urls:
        driver.get(url)
        product_info['title'] = select_one('span#productTitle').text
        product_info['price'] = select_one('span#priceblock_ourprice').text
        url = get_review_url()
        product_dict['review_url'] = url

        try:
            ingredients_directions_list = get_ingredient_directions_list(('div#importantInformation div.content'))

            for item in ingredients_directions_list:
                key, value = parse_item(item)
                product_info[key] = value

        except NoSuchElementException:
            continue

        info_list = select('div#detail-bullets div.content li')
        ASIN, ranking, n_reviews = get_product_details(info_list)

        if ASIN:
            product_dict['ASIN'] = ASIN
            product_info['ranking'] = ranking
            product_info['review_number'] = n_reviews
            product_dict['product_info'] = product_info
        print(product_dict)

    return product_dict
