import pandas as pd
import numpy as np
import psycopg2
import os
import random

password = os.environ['DB_PASS']
user = os.environ['DB_USER_NAME']
host = os.environ['DB_HOST']
name = os.environ['DB_NAME']
port = 5432


class DataModel(object):
    def __init__(self):
        self.conn = psycopg2.connect(dbname=name, host=host,
                                    password=password,user=user)
        self.categories = ['moisturizer','serum','cleanser']


    def get_query(self,category):
        ''''gets information from get_recommendations and makes a query for products 
        and all concerns'''
        table = category+'_rec'
        query = f'''
                SELECT m.*, p.price, p.title, p.imageurl, p.numberreviews
                FROM {table} as m
                LEFT JOIN products as p ON m.asin=p.asin;
                '''
        return(query)

    def run_query(self,query):
        try:
            df_results = pd.read_sql_query(query,self.conn)
            return(df_results)
        
        except psycopg2.Error as e:
            products = {'product1' : e.pgerror, 'product2' : ' ', 'product3' : ' '}

    def get_recommendations(self,budget,concern_list):
        '''central function that culls products and populates the page with 
        3 products for each concern equaling 18 products in total.'''
        self.product_list = []
        self.concerns = concern_list
        self.budget = float(budget)
        query = ''
        for category in self.categories:
            #gets each product category from list, runs a query for recommendations in 
            #each category
            self.category = category
            query = self.get_query(category)
            df = self.run_query(query)
            df = self.clean_df(df)
            df['category'] = category
            product_df = self.get_products(df)
            #generalize the concerns to produce a list to be passed back to the app.py
            # for i in range(len(self.concerns)): 
            #     product_df.rename(columns = {'p_unweighted_'+self.concerns[i] : 'concern'+str(i+1)}, inplace=True)
            for concern in self.concerns: 
                product_df.rename(columns = {'p_unweighted_'+concern : concern}, inplace=True)
            
            self.product_list.extend(product_df.to_dict(orient='records'))

        return(self.product_list)



    def create_weighted_concern(self, df, concern):
        df['weighted_'+ concern]  = (df['review_ratio'] * df[concern])

    def clean_df(self,df):
        '''columns are ints or floats, except asin and imageurl which are strings'''
        #Normalize the score by the number of reviews recieved, with 100 reviews == 1
        mask = df.numberreviews >= 100
        column_name = 'numberreviews'
        df.loc[mask, column_name] = 100
        df['review_ratio'] = df.numberreviews / 100
        df['new_budget'] = self.budget - df['price']
        #normalizes the concerns to the number of reviews the product recieved.
        for concern in self.concerns:
            self.create_weighted_concern(df, concern)
        #creating total for each product that will then be used to calculate proportion of total for each concern
        df['weighted_total'] = 0
        df['unweighted_total'] = 0
        for concern in self.concerns:
            df['weighted_total'] += df['weighted_'+concern]
            df['unweighted_total'] += df[concern]
        for concern in self.concerns:
            df['p_'+concern] = df['weighted_'+ concern] / df['weighted_total']
            df['p_unweighted_'+concern] = df[concern] / df['unweighted_total']
        df.fillna(0,inplace=True)
        return(df)

    def get_random_index_low_review(self,df,concern):
        mask = (df['weighted_total'] < .2) & (df['unweighted_total'] > .4) & (df[concern] > .1) & (df['price'] <= self.budget)
        idx_list = list(df.loc[mask].index)
        if len(idx_list) == 0:
            mask = (df['weighted_total'] < .2) & (df['unweighted_total'] > .2) & (df['price'] <= self.budget)
            idx_list = list(df.loc[mask].index)
        if len(idx_list) <= 1:
            mask = df['price'] <= self.budget
            idx_list = list(df.loc[mask].index)
        idx = random.choice(idx_list)
        return([idx])
        
    def get_random_index_high_review(self,df,concern):
        mask = (df['weighted_total'] > .4) & (df[concern] > .1) & (df['price'] <= self.budget)
        idx_list = list(df.loc[mask].index)
        if len(idx_list) < 2:
            mask = (df['weighted_total'] > .2) & (df['price'] <= self.budget)
            idx_list = list(df.loc[mask].index)
        if len(idx_list) <= 1:
            mask = df['price'] <= self.budget
            idx_list = list(df.loc[mask].index)
        idx1 = random.choice(idx_list)
        idx_list.remove(idx1)
        idx2 = random.choice(idx_list)
        return([idx1,idx2])

    def get_products(self,df):
        '''Get three products for each area of concern. Concerns = list
           Return a dataframe with all products and proportion product addresses each concern'''

        products = pd.DataFrame(columns=df.columns)

        for concern in self.concerns:
            product_idx_list = []
            product_idx_list.extend(self.get_random_index_high_review(df,concern))
            product_idx_list.extend(self.get_random_index_low_review(df,concern))
            temp = df.loc[product_idx_list]
            df.drop(product_idx_list,inplace=True)
            products = pd.concat([products,temp],axis=0)


        columns = ['title','price','asin','imageurl','category']
        df2 = products.filter(regex='p_unweighted')
        df3 = products.filter(columns)
        recommendations = pd.concat([df2,df3],axis=1)
        return(recommendations)

