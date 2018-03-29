from flask import Flask, render_template, request, jsonify, redirect, abort, url_for, flash, session
from werkzeug import secure_filename
from model import DataModel
from os import listdir
import csv
import pdb

#from baskets import Baskets
import json
import os


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

def update_csv(image_list):
    training_path = ('/Users/keri/git/galvanize/capstone/psc/website/data/training/images_for_training.csv')
    '''updates the csv with new images'''
    with open(training_path,"a",newline='') as f:  
        cw = csv.writer(f)
        for row in image_list:
            cw.writerow([row])


def get_concerns():
    concerns = []
    concern_list = ['dry','oily','combination','skintone','eyes','antiaging','psoriasis','lightening','sunscreen',
                'night','pores','sensitive']
    for concern in concern_list:
        if request.args.get(concern):
            concerns.append(concern)
    return(concerns)

def upload_images(concern_list):
    '''image was saved from start.html into the data/folder. Put an exention on the filename
    for each concern so the model can see what images are attached to which concern.'''
    converted_files = []
    files = listdir('/Users/keri/git/galvanize/capstone/psc/website/data/images')
    for file in files:
        for concern in concern_list:
            converted_files.append(concern + '+' + file)
 #       os.remove('/Users/keri/git/galvanize/capstone/psc/website/data/images/'+file)
    update_csv(converted_files)


@app.route('/')
def index():
    return render_template('start.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():

    if request.method == 'POST':
        for f in request.files:
            file = request.files[f]
            filename = secure_filename(file.filename)
 #           pdb.set_trace()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('question_one.html')

@app.route('/questions', methods = ['GET','POST'])
def formtest():
    checks = request.form.getlist('questions')
    for check in checks:
        print('check = ', check)
# def upload_questions():
#     answers = request.form.getlist('questions')
#     print(answers)
    return render_template('starter_skin.html')


@app.route("/results")
def results2():
    concerns = get_concerns()
    upload_images(concerns)

 #   concerns = list(filter((lambda x: request.args.get(x)), concern_list))
    budget = request.args.get('budget')
    products = data_model.get_recommendations(budget, concerns)
    results = {
        'concerns':concerns,
        'budget':budget,
        'products':products
    }
    return render_template('results.html', results=results)








    #     # if user does not select file, browser also
    #     # submit a empty part without filename
    #     if file.filename == '':
    #         flash('No selected file')
    #         return redirect(request.url)
    #     if file and allowed_file(file1.filename):
    #         filename = secure_filename(file.filename)
    #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #         return render_template('starter_skin.html')
    #     return '''
    #     <!doctype html>
    #     <title>Upload new File</title>
    #     <h1>Upload new File</h1>
    #     <form method=post enctype=multipart/form-data>
    #       <p><input type=file name=file>
    #          <input type=submit value=Upload>
    #     </form>
    #     '''



@app.route("/results3")
def results3():
    concern_list = ['dry','oily','combination','skintone','eyes','antiaging','psoriasis','rosacea','sunscreen',
                'night','pores','sensitive']
    concerns = list(filter((lambda x: request.args.get(x)), concern_list))
    budget = request.args.get('budget')

    products = data_model.get_recommendations(budget, concerns)
    results = {
        'concerns':concerns,
        'budget':budget,
        'products':products
    }

    return render_template('results.html', results=results)




if __name__ == '__main__':

#    app.debug = True
    app.run(host='0.0.0.0', threaded=True)

