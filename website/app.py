from flask import Flask, render_template, request, jsonify, redirect, abort, url_for, flash, session, make_response
from werkzeug import secure_filename
from model import DataModel
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
#baskets = Baskets()
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def insert_row_csv(converted_list):
    training_path = ('/Users/keri/git/galvanize/capstone/psc/website/data/training/images_for_training.csv')
    '''updates the csv with new images'''
    with open(training_path,"a", newline='') as f: 
            cw=csv.writer(f, delimiter=",", lineterminator="\r\n") 
            cw.writerows(converted_list)

def update_csv(concern_list):
    '''image was saved from start.html into the data/folder. Put an exention on the filename
    for each concern so the model can see what images are attached to which concern.'''
    converted_files = []
    path = '/Users/keri/git/galvanize/capstone/psc/website/data/images'
    files = listdir(path)
    for file in files:
        upload_images_to_s3(file, path)

        for concern in concern_list:
            converted_files.append((file, concern))
        os.remove('/Users/keri/git/galvanize/capstone/psc/website/data/images/'+file)
    insert_row_csv(converted_files)

def upload_images_to_s3(filename, path):
    path_file = path+'/'+filename
    k = Key(bucket)
    k.key = 'test/'+filename
    k.set_contents_from_filename(path_file)

def create_baskets(products, concerns):
    '''creating a basket of products in which product totals for each concern is greater than .9'''
    moisturizers = [result for result in products if result['category'] == 'moisturizer']
    print('moisturizers = ',moisturizers)
    serums = [result for result in products if result['category'] == 'serum']
    cleansers = [result for result in products if result['category'] == 'cleanser']

    combinations =  list(itertools.product(moisturizers, serums, cleansers))
    basket_dictionary = {}

    '''scales to any number of concerns the user chooses. Adds up total for each concern for each basket
        and appends to final list that comtains each basket as an element'''
    combo_idx = 0
    basket_count = 0

    for combination in combinations:
        basket_price = (combination[0]['price'] + combination[1]['price'] + 
                        combination[2]['price'])
        basket_concerns={}
        for concern in concerns:
            concern_total = (combination[0][concern] + combination[1][concern] + 
                            combination[2][concern])
            basket_concerns[concern] = concern_total
        if all(i >= .9 for i in basket_concerns.values()):
            temp_basket = {}
            temp_basket['products'] = combinations[combo_idx]
            temp_basket['basket_concerns'] = basket_concerns
            temp_basket['price'] = round(basket_price,2)
            basket_dictionary[basket_count] = temp_basket
            basket_count += 1
        elif all(i >= .5 for i in basket_concerns.values()):
            temp_basket = {}
            temp_basket['products'] = combinations[combo_idx]
            temp_basket['basket_concerns'] = basket_concerns
            temp_basket['price'] = round(basket_price,2)
            basket_dictionary[basket_count] = temp_basket
            basket_count += 1
        combo_idx += 1
    return(basket_dictionary, moisturizers, serums, cleansers)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/uploader', methods = ['GET','POST'])
def upload_file():
    if request.method == 'POST':
        for f in request.files:
            file = request.files[f]
            filename = secure_filename(file.filename)
            print('filename')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('questionnaire.html')

@app.route('/questions', methods=['GET','POST'])
def inputquestions():
    day_routine = request.form.getlist('day-routine')
    night_routine = request.form.getlist('night-routine')
    age = request.form.get('age')
    skintone = request.form.get('ethnicity-img')
    return (render_template('areas_of_concern.html'))

@app.route("/results", methods=['GET','POST'])
def results2():
    concerns = request.form.getlist('concern')
    update_csv(concerns)

    budget = request.form.get('budget')
    products = data_model.get_recommendations(budget, concerns)
    baskets, moisturizers, serums, cleansers = create_baskets(products, concerns)

    results = {
        'concerns':concerns,
        'budget':budget,
        'products':products
    }

    return render_template('spa_results.html', results=results, baskets=baskets, 
                            moisturizers=moisturizers,serums=serums,cleansers=cleansers)

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

# @app.route("/new_basket", methods=["POST"])
# def new_basket():
#     new_baskets = request.form.get('baskets')
#     return render_template('spa_results.html', baskets=ast.literal_eval(new_baskets))

@app.route("/subscribe", methods=['GET'])
def subscribe_get():
    return render_template('subscribe.html')

@app.route("/subscribe", methods=['POST'])
def subscribe_post():
    email = request.form.get('email')
    print(email)
    return redirect('/')

@app.route("/upload_images", methods=["GET","POST"])
def upload():
    return render_template('upload_images.html')

@app.route("/questionnaire",methods=["POST"])
def questionnaire():
    return render_template('questionnaire.html')

@app.route("/contact",methods=["GET"])
def contact_get():
    return render_template('contact.html')



if __name__ == '__main__':

#    app.debug = True
    app.run(host='0.0.0.0', threaded=True)

