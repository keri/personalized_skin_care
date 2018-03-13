import pandas as pd 
import numpy as np 
from model import DataModel
import json


data_model = DataModel()

class Baskets(object):
	'''creates baskets of products from list of concerns and budget from app.py'''
    def __init__(self, budget, concerns):
    	self.products = data_model.get_recommendations(budget, concerns)
    	self.budget = budget
    	self.baskets = []

    def create_category_df(self, catgory):
    	'''splits the dictinary from the model into three dataframes for each category
    	   to build combinations of baskets from'''
    	pass

    def create_product_combination(self):
    	'''creates a list of indices for all product combinations 
    	   that stay within budget'''
    	pass


    def make_basket(self):
    	'''creates baskets, calculates the total value basket addresses all concerns as well as 
    	   providing info from each product to be displayed on page'''
    	for category in ['moisturizer','serum','cleanser']:	
    		self.category+'df' = self.create_category_df(category)
    	combinations = self.create_product_combinations()
    	for combo in combinations:

    	pass

    def update_price(self):
    	pass

    def calculate_basket(self):
    	pass

    def calculate_basket_ratio(self):
    	pass

    def get_baskets(self):
    	pass
