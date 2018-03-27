from flask import Flask, render_template, request, jsonify, redirect, abort, url_for
from werkzeug import secure_filename
from model import DataModel
#from baskets import Baskets
import json
import os

UPLOAD_FOLDER = 'data/'
ALLOWED_EXTENSIONS = set(['txt','pdf', 'png', 'jpg', 'jpeg', 'gif','docx','doc'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

data_model = DataModel()
#baskets = Baskets()
def allowed_file(filename):
    print('filename = ',filename)
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    print('in index')
    return render_template('start.html')


@app.route("/results")
def results2():
    concerns = []
    concern_list = ['dry','oily','combination','skintone','eyes','antiaging','psoriasis','lightening','sunscreen',
                'night','pores','sensitive']
    for concern in concern_list:
        if request.args.get(concern):
            concerns.append(concern)
 #   concerns = list(filter((lambda x: request.args.get(x)), concern_list))
    print(concerns)
    budget = request.args.get('budget')
    products = data_model.get_recommendations(budget, concerns)
    results = {
        'concerns':concerns,
        'budget':budget,
        'products':products
    }
    return render_template('results.html', results=results)


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print('file = ',filename)
            print('saved in ',app.config['UPLOAD_FOLDER'])
            return render_template('starter_skin.html')
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>
        '''



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
    app.run(host='0.0.0.0', threaded=True)
