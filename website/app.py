from flask import Flask, render_template, request, jsonify, redirect, abort
from model import DataModel
#from baskets import Baskets
import json
app = Flask(__name__)

data_model = DataModel()
#baskets = Baskets()

@app.route('/')
def index():
    print('in index')
    return render_template('starter_skin.html')


@app.route("/results")
def results():
    c1 = request.args.get('c1')
    c2 = request.args.get('c2')
    c3 = request.args.get('c3')
    budget = request.args.get('budget')
    concern_list = [c1,c2,c3]
    products = data_model.get_recommendations(budget, concern_list)
    results = {
        'c1':c1.title(),
        'c2':c2.title(),
        'c3':c3.title(),
        'budget':budget,
        'products':products
    }
    return render_template('results.html', results=results)


@app.route("/results2")
def results2():
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
