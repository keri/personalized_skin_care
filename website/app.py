from flask import Flask, render_template, request, session, make_response
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
    session['product_categories'] = []
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
        return render_template('spa_results.html', basket=session['basket'],product_categories=session['categories'])


@app.route("/results", methods=['GET','POST'])
def results2():

    #This will be triggered if they clicked 'get personalized recommendations on home page'
    if request.method == 'POST':
        concerns = request.form.getlist('concern')
        if concerns == []:
            # concerns = ['antiaging','skintone','sensitive']
            return render_template('questionnaire.html',message='Tell us a little about yourself so we make the best recommondations for you')

        else:
            products_own = request.form.getlist('products_own')
            session['concerns'] = concerns
            # session['products_own'] = products_own
            products = data_model.get_recommendations(session['concerns'])
            basket.new_basket(concerns,products)
            day_routine = request.form.get('day-routine')
            night_routine = request.form.get('night-routine')
            age = request.form.get('age')
            skintone = request.form.get('ethnicity-img')
            gender = request.form.get('gender')
            session['all_products'] = products
            session['basket'] = basket.get_basket()
            session['product_categories'] = basket.get_products_in_each_category()
            session['instructions'] = data_model.instruction_dictionary
            session['scripts'] = data_model.script_dictionary
            print(session['categories'])
            print(session['profile'])

            #This will happen if they clicked on 'build a personal profile' on the home page and were prompted to fill out questionnaire before uploading images of themselves
            if session['profile'] == 'True':
                #if they didn't fill out any concerns on the questionnaire. The system needs that to attach labels to images so they will be asked to do that again on the questionnaire page.
                if session['concerns'] == []:
                    return render_template('questionnaire.html', message='Tell us a little more about yourself')
                else:
                    #this will go through the uploader route after images are loaded
                    return render_template('upload_images.html')

            
            else:
                return render_template('spa_results.html', basket=session['basket'],
                                product_categories=session['categories'],scripts=session['scripts'])

    elif session['concerns'] != []:
        concerns = session['concerns']
        return render_template('create_basket.html',product_dictionary=session['product_categories'],
                            categories_show=session['categories'],concerns=session['concerns'],basket=session['basket'],
                            scripts=session['scripts'])
    else:
        return render_template('questionnaire.html',message='Tell us a little about yourself so we make the best recommondations for you')



@app.route('/product_categories', methods=["GET","POST"])
def individual_categories():
    category = request.form.get('category')

    if category == 'product':
        return render_template('product_instructions.html',categories=session['categories'],instructions=session['instructions'])

    else:
        return render_template('products_page.html',products=session['product_categories'][category],concerns=session['concerns'])

@app.route('/product_instructions', methods=["GET","POST"])
def get_instructions():
    instruction_categories = ['cleanser','serum','moisturizer']
    return render_template('product_instructions.html',categories=instruction_categories,instructions=session['instructions'])

@app.route("/custom_basket", methods=["GET","POST"])
def custom_basket():
    basket.empty_basket(session['concerns'])
    session['basket'] = basket.get_basket()
    session['scripts'] = data_model.script_dictionary

    return render_template('create_basket.html',product_dictionary=session['product_categories'],
                            categories_show=session['categories'],concerns=session['concerns'],basket=session['basket'],
                            scripts=session['scripts'])

@app.route("/add_product",methods=["GET","POST"])
def add_to_basket():
    product = ast.literal_eval(request.form.get("product"))
    basket.add_product(product, session['concerns'], session['basket'])
    session['basket'] = basket.get_basket()

    return render_template('update_basket.html',basket=session['basket'],product_dictionary=session['product_categories'],
                            concerns=session['concerns'], categories_show=session['categories'],scripts=session['scripts'])

@app.route("/delete_product",methods=["GET","POST"])
def delete_from_basket():
    product = ast.literal_eval(request.form.get("product"))
    basket.delete_product(product, session['concerns'], session['basket'])
    session['basket'] = basket.get_basket()
    session['concerns'] = basket.concerns

    return render_template('update_basket.html',basket=session['basket'],product_dictionary=session['product_categories'],
                            concerns=session['concerns'], categories_show=session['categories'],scripts=session['scripts'])

@app.route("/replace_product",methods=["GET","POST"])
def replace_product_in_basket():
    product = ast.literal_eval(request.form.get("product"))
    basket.delete_product(product, session['concerns'], session['basket'])
    session['basket'] = basket.get_basket()
    category = product['category']

    return render_template('products_page.html',products=session['product_categories'][category],concerns=session['concerns'])

@app.route("/subscribe", methods=['GET'])
def subscribe_get():
    return render_template('subscribe.html')

@app.route("/subscribe", methods=['POST'])
def subscribe_post():
    email = request.form.get('email')
    print('email is: ',email)
    return redirect('/')

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

    return redirect('/')


if __name__ == '__main__':

#    app.debug = True
    app.run(host='0.0.0.0', threaded=True)
