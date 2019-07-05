from flask import Flask, render_template, request, session, make_response
from werkzeug import secure_filename
from model import DataModel
from basket import Basket
from os import listdir
import csv
import pdb
import hashlib
import boto
import random
import ast
import json
import os

Bucketname = 'skin-care-app'
# conn = boto.s3.connect_to_region('us-west-2',
#        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
#        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
#        is_secure=True,
#        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
#        )
# bucket = conn.get_bucket(Bucketname)

UPLOAD_FOLDER = 'data/training/images/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = b'\x96\x05\xac\xc2\x1b\xe7\xb6\x84u\xbaC\xcd'
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

def get_basket_price(basket):
    return(round((basket[0]['price'] + basket[1]['price'] + basket[2]['price']),2))


@app.route('/')
def index():
    return render_template('home2.html')

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
