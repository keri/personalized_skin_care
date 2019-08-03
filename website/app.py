from flask import Flask, render_template, request, session, make_response, url_for, redirect
from werkzeug import secure_filename
from model import DataModel
from basket import Basket
from os import listdir
import csv
import pdb
import hashlib
import random
import ast
import json
import os
from flask_session import Session
import boto3
from botocore.exceptions import NoCredentialsError

Bucketname = 'skin-care-app'
UPLOAD_FOLDER = 'data/training/images/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = b'\x96\x08\xac\xc2\x1b\xe7\xb6\x84u\xbaC\xcd'
data_model = DataModel()
basket = Basket()
Session(app)

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                      aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    local_file = UPLOAD_FOLDER + local_file
    s3_file = 'test/' + s3_file
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


#uploaded = upload_to_aws('local_file', 'bucket_name', 's3_file_name')

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
    path = UPLOAD_FOLDER
    files = listdir(path)
    for file in files:
        # upload_images_to_s3(file)
        if file[0] != '.':
            upload_to_aws(file,Bucketname,file)
            for concern in concern_list:
                converted_files.append((file, concern))
            os.remove('data/training/images/'+file)
    insert_row_csv(converted_files)

@app.route('/', methods=["GET","POST"])
def index():
    session['categories'] = ['cleanser','moisturizer','serum']

    session['concerns'] = []
    session['products_own'] = []
    session['all_products'] = []
    session['basket'] = []
    session['product_categories'] = [] #these are the categories in the basket so app knows what to show customer
    session['instructions'] = []
    session['scripts'] = []
    session['profile'] = ''
    return render_template('home.html')

@app.route('/faq')
def about():
    return render_template('faq.html')

@app.route('/uploader', methods=['POST'])
def upload_file():
    '''request.files returns an immutable dictionary with {label name, <FileStorage: 'filename'}'''
    for f in request.files:
        print('f in request.files ',f)
        print('all files = ',request.files)
        if request.files[f]:
            file = request.files[f]
            print('file into the if statement ', file)
            random_string = "%0.12d" % random.randint(0,999999999999)
            extension = file.filename.split('.')[-1]
            filename = (f + random_string + '.' + extension)
            #filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    if session['concerns'] == []:
        return render_template('questionnaire.html', message='Tell us a little more about yourself')
    else:
        update_csv(session['concerns'])
        return render_template('spa_results.html', basket=session['basket'], AWSAccessKeyId=os.environ['AWS_ASSOCIATES_ACCESS_KEY'],
                                product_categories=session['categories'],scripts=session['scripts'],prompt='Experts recommend adding additional serums to your routine to fully address all areas of concern')

@app.route("/results/<toResults>", methods=['GET','POST'])
# @app.route("/results", methods=['GET','POST'])
def results(toResults):

    if toResults == 'finishedquestionnaire':
        concerns = request.form.getlist('concern')
        if concerns == []:
            return render_template('questionnaire.html',message='Tell us a little about yourself so we make the best recommendations for you')

        else:
            products_own = request.form.getlist('products_own')
            session['concerns'] = concerns
            # session['products_own'] = products_own
            products = data_model.get_recommendations(session['concerns']) #list of product dictionaries: [{concern1:, concern2:, etc, asin:, category:, title: imageurl:, price:, confidence:}]
            basket.new_basket(concerns,products)
            day_routine = request.form.get('day-routine')
            night_routine = request.form.get('night-routine')
            age = request.form.get('age')
            skintone = request.form.get('ethnicity-img')
            gender = request.form.get('gender')
       #     session['all_products'] = products
            session['basket'] = basket.get_basket()
            session['all_products'] = basket.get_products_in_each_category() #[category: product_dict_list_in_category[{}]]
            session['instructions'] = data_model.instruction_dictionary
            session['scripts'] = data_model.script_dictionary
            session['no_show'] = ['cleanser','moisturizer','serum'] #this tracks the categories of products the customer said they don't want. This will be from custom basket or a future option included on questionnaire
            session['prompt'] = 'Experts recommend adding additional serums to your routine to fully address all areas of concern'
            for category in session['categories']: 
                if category not in session['no_show']:
                    session['product_categories'].append(category) #this will create a list with only categories they want to see and passed into spa_results template
            print(session['categories'])
            print(session['profile'])

            #Clicked on 'build a personal profile' on the home page and were prompted to fill out questionnaire before uploading images of themselves
            if session['profile'] == 'True':
                #if they didn't fill out any concerns on the questionnaire. The system needs that to attach labels to images so they will be asked to do that again on the questionnaire page.
                if session['concerns'] == []:
                    return render_template('questionnaire.html', message='Tell us a little more about yourself')
                else:
                    #this will go through the uploader route after images are loaded
                    return render_template('upload_images.html')

            
            else:
                return render_template('spa_results.html', basket=session['basket'], AWSAccessKeyId=os.environ['AWS_ASSOCIATES_ACCESS_KEY'],
                                product_categories=session['categories'],scripts=session['scripts'], prompt=session['prompt'])

    elif toResults == 'redirect': #This will happen from Recommended Products choice on nav bar
        return render_template('spa_results.html', basket=session['basket'], AWSAccessKeyId=os.environ['AWS_ASSOCIATES_ACCESS_KEY'],
                        product_categories=session['categories'],scripts=session['scripts'], prompt=session['prompt'])

    elif toResults == 'start':
        return render_template

    else:
        return render_template('questionnaire.html',message='Tell us a little about yourself so we make the best recommendations for you')



@app.route('/all_products', methods=["GET","POST"])
def individual_categories():
    category = request.form.get('category')

    if category == 'product': #Possible category option in skinlytics spa_results for instructions
        return render_template('product_instructions.html',categories=session['categories'],instructions=session['instructions'])

    elif category == None: #This happens when All Products clicked in the nav bar
        if session['all_products'] == []: #This happens before they have filled out the questionnaire
            return render_template('questionnaire.html',message='Narrow the product choices by telling us a bit about yourself')
        else:
            return render_template('update_basket.html',basket=session['basket'],products=session['all_products'], AWSAccessKeyId=os.environ['AWS_ASSOCIATES_ACCESS_KEY'],
                            concerns=session['concerns'], categories_show=session['categories'],scripts=session['scripts'])

    else: #When a category box is clicked from spa_results.html
        return render_template('products_page.html',products=session['all_products'][category],concerns=session['concerns'],scripts=session['scripts'])


@app.route('/product_instructions', methods=["GET","POST"])
def get_instructions():
    instruction_categories = ['cleanser','serum','moisturizer']
    return render_template('product_instructions.html',categories=instruction_categories,instructions=session['instructions'])

@app.route("/custom_basket", methods=["GET","POST"])
def custom_basket():
    basket.empty_basket(session['concerns'])
  #  session['product_categories'] = []
    session['basket'] = basket.get_basket()
    session['no_show'] = []
    print(session['basket'])
    session['scripts'] = data_model.script_dictionary
    return render_template('create_basket.html',products=session['all_products'],
                            categories_show=['cleanser'],concerns=session['concerns'], basket=session['basket'],
                            scripts=session['scripts'])

@app.route("/add_product/<path>",methods=["GET","POST"])
def add_to_basket(path):

    if path == 'pass': #'Look at Products in Other Categories' button was clicked on a page
        category = request.form.get('category')
        session['no_show'].append(category)

    elif path == 'add': #'Add product' was clicked. Creating a basket, or adding to existing basket. Tracks what categories have been shown and won't repeat. They have a chance to look at more categories when reached the spa_results page.
        product = ast.literal_eval(request.form.get("product"))
        basket.add_product(product, session['concerns'], session['basket'])
        category = product['category']
        session['no_show'].append(product['category']) #This tracks the current basket and shows product for categories they don't have.
#        session['product_categories'].append(category)

    elif path == 'replace': #when replace product is clicked. Don't track the 'no_show' session variable as they are just replacing, not adding to.
        product = ast.literal_eval(request.form.get("product"))
        basket.delete_product(product, session['concerns'], session['basket'])
        category = product['category']
        session['basket'] = basket.get_basket()
        return render_template('update_basket.html',basket=session['basket'],products=session['all_products'], AWSAccessKeyId=os.environ['AWS_ASSOCIATES_ACCESS_KEY'],
                                concerns=session['concerns'], categories_show=[category],scripts=session['scripts'])

    elif path == 'delete': #deleting the product doesn't update the session[no_show] variable
        product = ast.literal_eval(request.form.get("product"))
        basket.delete_product(product, session['concerns'], session['basket'])
        session['basket'] = basket.get_basket()
        return render_template('spa_results.html', basket=session['basket'], AWSAccessKeyId=os.environ['AWS_ASSOCIATES_ACCESS_KEY'],
                                    product_categories=session['categories'], scripts=session['scripts'], prompt=session['prompt'])


    session['basket'] = basket.get_basket() #getting the basket for add and pass paths
   
    if len(session['no_show']) >= 3:
            return render_template('spa_results.html', basket=session['basket'], AWSAccessKeyId=os.environ['AWS_ASSOCIATES_ACCESS_KEY'],
                                    product_categories=session['categories'],scripts=session['scripts'], prompt=session['prompt'])

    elif 'serum' not in session['no_show']:
            return render_template('update_basket.html',basket=session['basket'],products=session['all_products'], AWSAccessKeyId=os.environ['AWS_ASSOCIATES_ACCESS_KEY'],
                                concerns=session['concerns'], categories_show=['serum'],scripts=session['scripts'])
    
    elif 'moisturizer' not in session['no_show']:
             return render_template('update_basket.html',basket=session['basket'],products=session['all_products'], AWSAccessKeyId=os.environ['AWS_ASSOCIATES_ACCESS_KEY'],
                                concerns=session['concerns'], categories_show=['moisturizer'],scripts=session['scripts'])
    else:
        return render_template('spa_results.html', basket=session['basket'], AWSAccessKeyId=os.environ['AWS_ASSOCIATES_ACCESS_KEY'],
                        product_categories=session['categories'],scripts=session['scripts'],prompt=session['prompt'])


@app.route("/subscribe", methods=['GET'])
def subscribe_get():
    return render_template('subscribe.html')

@app.route("/subscribe", methods=['POST'])
def subscribe_post():
    email = request.form.get('email')
    print('email is: ',email)
    if session['concerns'] != []:
        session['basket'] = basket.get_basket()
        return render_template('spa_results.html', basket=session['basket'], AWSAccessKeyId=os.environ['AWS_ASSOCIATES_ACCESS_KEY'],
                        product_categories=session['categories'],scripts=session['scripts'],prompt=session['prompt'])

    else:
        return redirect('/questionnaire')

@app.route("/upload_images", methods=["GET","POST"])
def upload():
    session['profile'] = 'True'
    if session['concerns'] == []:
            # concerns = ['antiaging','skintone','sensitive']
        return render_template('questionnaire.html',message='Start by telling us a little about yourself')

    else:
        return render_template('upload_images.html')

@app.route("/questionnaire",methods=["GET","POST"])
def questionnaire():
    return render_template('questionnaire.html')


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
    if session['concerns'] != []:
        session['basket'] = basket.get_basket()
        return render_template('spa_results.html', basket=session['basket'], AWSAccessKeyId=os.environ['AWS_ASSOCIATES_ACCESS_KEY'],
                        product_categories=session['categories'],scripts=session['scripts'],prompt=session['prompt'])

    else:
        return redirect('/questionnaire')


if __name__ == '__main__':

#    app.debug = True
    app.run(host='0.0.0.0', threaded=True)
