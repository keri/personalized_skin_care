from flask import Flask, render_template, request, jsonify, redirect, abort, url_for, flash, session, make_response
from werkzeug import secure_filename
from model import DataModel
from basket import Basket
from os import listdir
import csv
import pdb
import hashlib
import boto
import boto.s3.connection
from boto.s3.key import Key
import itertools
import random
import ast
import json
import os

Bucketname = 'skin-care-app'
conn = boto.s3.connect_to_region('us-west-2',
       aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
       aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
       is_secure=True,
       calling_format = boto.s3.connection.OrdinaryCallingFormat(),
       )
bucket = conn.get_bucket(Bucketname)


UPLOAD_FOLDER = 'data/images'
ALLOWED_EXTENSIONS = set(['txt','pdf', 'png', 'jpg', 'jpeg', 'gif','docx','doc'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"

data_model = DataModel()
basket = Basket()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def insert_row_csv(converted_list):
    training_path = ('data/training/images_for_training.csv')
    '''updates the csv with new images'''
    with open(training_path,"a", newline='') as f:
            cw=csv.writer(f, delimiter=",", lineterminator="\r\n")
            cw.writerows(converted_list)

def update_csv(concern_list):
    '''image was saved from start.html into the data/folder. Put an exention on the filename
    for each concern so the model can see what images are attached to which concern.'''
    converted_files = []
    path = 'data/images/'
    if path != None:
        files = listdir(path)
        for file in files:
            upload_images_to_s3(file, path)

            for concern in concern_list:
                converted_files.append((file, concern))
            os.remove('data/images/'+file)
        insert_row_csv(converted_files)

def upload_images_to_s3(filename, path):
    path_file = path+filename
    k = Key(bucket)
    k.key = 'test/'+filename
    k.set_contents_from_filename(path_file)

def get_basket_price(basket):
    return(round((basket[0]['price'] + basket[1]['price'] + basket[2]['price']),2))

def get_basket_concerns(basket, concerns):
    basket_concerns = {}
    for concern in concerns:
        concern_total = (basket[0][concern] + basket[1][concern] +
                        basket[2][concern])
        basket_concerns[concern] = concern_total
    return(basket_concerns)


def create_baskets(products, concerns):
    '''creating a basket of products in which product totals for each concern is greater than .9'''
    moisturizers = [result for result in products if result['category'] == 'moisturizer']
    serums = [result for result in products if result['category'] == 'serum']
    cleansers = [result for result in products if result['category'] == 'cleanser']

    baskets =  list(itertools.product(moisturizers, serums, cleansers))
    basket_dictionary = {}

    '''scales to any number of concerns the user chooses. Adds up total for each concern for each basket
        and appends to final list that comtains each basket as an element'''
    combo_idx = 0
    basket_count = 0

    for combination in baskets:
        basket_price = get_basket_price(combination)
        basket_concerns = get_basket_concerns(combination, concerns)

        if all(i >= .9 for i in basket_concerns.values()):
            temp_basket = {}
            temp_basket['products'] = baskets[combo_idx]
            temp_basket['basket_concerns'] = basket_concerns
            temp_basket['price'] = round(basket_price,2)
            basket_dictionary[basket_count] = temp_basket
            basket_count += 1
        elif all(i >= .7 for i in basket_concerns.values()):
            temp_basket = {}
            temp_basket['products'] = baskets[combo_idx]
            temp_basket['basket_concerns'] = basket_concerns
            temp_basket['price'] = round(basket_price,2)
            basket_dictionary[basket_count] = temp_basket
            basket_count += 1
        elif any(i >= .9 for i in basket_concerns.values()):
            temp_basket = {}
            temp_basket['products'] = baskets[combo_idx]
            temp_basket['basket_concerns'] = basket_concerns
            temp_basket['price'] = round(basket_price,2)
            basket_dictionary[basket_count] = temp_basket
            basket_count += 1
        elif any(i >= .7 for i in basket_concerns.values()):
            temp_basket = {}
            temp_basket['products'] = baskets[combo_idx]
            temp_basket['basket_concerns'] = basket_concerns
            temp_basket['price'] = round(basket_price,2)
            basket_dictionary[basket_count] = temp_basket
            basket_count += 1
        else:
            temp_basket = {}
            temp_basket['products'] = baskets[combo_idx]
            temp_basket['basket_concerns'] = basket_concerns
            temp_basket['price'] = round(basket_price,2)
            basket_dictionary[basket_count] = temp_basket
            basket_count += 1
        combo_idx += 1
    return(basket_dictionary, moisturizers, serums, cleansers)


def replace_product(basket, product_list, category, concerns):
    new_basket = {}
    products = basket['products']

    for product in products:
        if product['category'] == category:
            lbasket = list(products)
            product_idx = lbasket.index(product)
            lbasket.remove(product)
            new_product = random.choice(product_list)
            lbasket.insert( product_idx, new_product)
            new_basket['price'] = get_basket_price(lbasket)
            new_basket['basket_concerns'] = get_basket_concerns(lbasket, concerns)
            new_basket['products'] = tuple(lbasket)

            return(new_basket)


@app.route('/')
def index():
    return render_template('questionnaire_temp.html')

@app.route('/faq')
def about():
    return render_template('faq.html')

@app.route('/uploader', methods=['POST'])
def upload_file():
    '''request.files returns an immutable dictionary with {label name, <FileStorage: 'filename'}'''
    for f in request.files:
        if request.files[f]:
            file = request.files[f]
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('questionnaire.html')

@app.route('/questions', methods=['GET','POST'])
def inputquestions():
    day_routine = request.form.get('day-routine')
    night_routine = request.form.get('night-routine')
    age = request.form.get('age')
    skintone = request.form.get('ethnicity-img')
    gender = request.form.get('gender')
    print('day routine = ',day_routine)
    print('age = ',age)
    print('skine tone = ',skintone)
    print('gender = ',gender)
    return (render_template('areas_of_concern.html'))

@app.route("/results", methods=['GET','POST'])
def results2():
    concerns = request.form.getlist('concern')
    update_csv(concerns)

    budget = request.form.get('budget')
    products = data_model.get_recommendations(budget, concerns)
    baskets, moisturizers, serums, cleansers = create_baskets(products, concerns)
    basket = baskets.popitem()[1]

    results = {
        'concerns':concerns,
        'budget':budget,
        'products':products
    }

    return render_template('spa_results.html', results=results, baskets=baskets,
                            moisturizers=moisturizers,serums=serums,cleansers=cleansers,
                            basket=basket)

@app.route("/temp_results", methods=['GET','POST'])
def temp_results():
    concerns = request.form.getlist('concern')
    update_csv(concerns)
    if concerns == []:
        concerns = ['antiaging','skintone','pores','sensitive']
    budget = request.form.get('budget')
    products = data_model.get_recommendations(budget, concerns)
    baskets, moisturizers, serums, cleansers = create_baskets(products, concerns)
    basket = baskets.popitem()[1]

    results = {
        'concerns':concerns,
        'budget':budget,
        'products':products
    }

    day_routine = request.form.get('day-routine')
    night_routine = request.form.get('night-routine')
    age = request.form.get('age')
    skintone = request.form.get('ethnicity-img')
    gender = request.form.get('gender')

    return render_template('spa_results.html', results=results, baskets=baskets, 
                            moisturizers=moisturizers,serums=serums,cleansers=cleansers,
                            basket=basket)


@app.route("/moisturizers", methods=['POST'])
def moisturizer_results():
    moisturizers = request.form.get('moisturizers')
    concerns = request.form.get('concerns')
    return render_template('moisturizers.html', moisturizers=ast.literal_eval(moisturizers),
                            concerns=ast.literal_eval(concerns))

@app.route("/serums", methods=["POST"])
def serum_results():
    serums = request.form.get('serums')
    concerns = request.form.get('concerns')
    return render_template('serums.html', serums=ast.literal_eval(serums),
                            concerns=ast.literal_eval(concerns))

@app.route("/cleansers", methods=["POST"])
def cleanser_results():
    cleansers = request.form.get('cleansers')
    concerns = request.form.get('concerns')
    return render_template('cleansers.html', cleansers=ast.literal_eval(cleansers),
                            concerns=ast.literal_eval(concerns))

@app.route("/custom_basket", methods=["POST"])
def custom_basket():
    moisturizers = ast.literal_eval(request.form.get('moisturizers'))
    serums = ast.literal_eval(request.form.get('serums'))
    cleansers = ast.literal_eval(request.form.get('cleansers'))
    concerns = ast.literal_eval(request.form.get('concerns'))
    basket.new_basket()
    basket.create_basket(concerns)

    return render_template('custom_basket.html',moisturizers=moisturizers,serums=serums,
                            cleansers=cleansers,concerns=concerns)

@app.route("/add_product",methods=["POST"])
def add_to_basket():
    moisturizers = ast.literal_eval(request.form.get('moisturizers'))
    serums = ast.literal_eval(request.form.get('serums'))
    cleansers = ast.literal_eval(request.form.get('cleansers'))
    concerns = ast.literal_eval(request.form.get('concerns'))
    product = ast.literal_eval(request.form.get("product"))
    basket.add_product(product)
    current_basket = basket.get_basket()

    return render_template('/update_basket.html',basket=current_basket,serums=serums,moisturizers=moisturizers,
                            cleansers=cleansers,concerns=concerns)

@app.route("/delete_product",methods=["POST"])
def delete_from_basket():
    moisturizers = ast.literal_eval(request.form.get('moisturizers'))
    serums = ast.literal_eval(request.form.get('serums'))
    cleansers = ast.literal_eval(request.form.get('cleansers'))
    concerns = ast.literal_eval(request.form.get('concerns'))
    product = ast.literal_eval(request.form.get("product"))
    basket.delete_product(product)
    current_basket = basket.get_basket()

    return render_template('/update_basket.html',basket=current_basket,serums=serums,moisturizers=moisturizers,
                            cleansers=cleansers,concerns=concerns)

@app.route("/subscribe", methods=['GET'])
def subscribe_get():
    return render_template('subscribe.html')

@app.route("/subscribe", methods=['POST'])
def subscribe_post():
    email = request.form.get('email')
    return redirect('/')

@app.route("/upload_images", methods=["GET","POST"])
def upload():
    return render_template('upload_images.html')

@app.route("/questionnaire",methods=["GET"])
def questionnaire():
    return render_template('questionnaire.html')

@app.route("/areas_of_concern",methods=["GET"])
def input_concerns():
    return render_template('areas_of_concern.html')

@app.route("/contact",methods=["GET"])
def contact_get():
    return render_template('contact.html')


@app.route("/contact",methods=["POST"])
def contact_post():
    email = request.form.get('email')
    name = request.form.get('name')
    message = request.form.get('message')
    print('email = ',email)
    print('name = ',name)
    print('message = ',message)

    return redirect('/')


@app.route("/new_product",methods=["POST"])
def replace_product_in_basket():
    product_list = []
    basket = ast.literal_eval(request.form.get('basket'))
    moisturizers = ast.literal_eval(request.form.get('moisturizers'))
    serums = ast.literal_eval(request.form.get('serums'))
    cleansers = ast.literal_eval(request.form.get('cleansers'))
    baskets = ast.literal_eval(request.form.get('baskets'))
    results = ast.literal_eval(request.form.get('results'))
    concerns = ast.literal_eval(request.form.get('concerns'))
    category = request.form.get('category')
    if category == 'moisturizer':
        product_list = moisturizers
    elif category == 'cleanser':
        product_list = cleansers
    else:
        product_list = serums

    new_basket = replace_product(basket, product_list, category, concerns)

    return render_template('spa_results.html', results=results, baskets=baskets,
                            moisturizers=moisturizers,serums=serums,cleansers=cleansers,
                            basket=new_basket)



if __name__ == '__main__':

#    app.debug = True
    app.run(host='0.0.0.0', threaded=True)
