from flask import Flask, render_template, request, jsonify, redirect, abort
from model import DataModel
import json
app = Flask(__name__)

data_model = DataModel()

@app.route('/')
def index():
    print('in index')
    return render_template('starter_skin.html')


@app.route("/results")
def results():
    print('in results')
    c1 = request.args.get('c1')
    c2 = request.args.get('c2')
    c3 = request.args.get('c3')
    budget = request.args.get('budget')
    concern_list = [c1,c2,c3]
    print('before get_recommendations')
    products = data_model.get_recommendations(budget, concern_list)
    print('after_recommendations')
    results = {
        'c1':c1.title(),
        'c2':c2.title(),
        'c3':c3.title(),
        'budget':budget,
        'products':products
    }
    print('before render')
    return render_template('results.html', results=results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)