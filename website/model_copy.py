import pandas as pd
import numpy as np
import psycopg2
import os

password = os.environ['DB_PASS']
user = os.environ['DB_USER_NAME']
host = os.environ['DB_HOST']
name = os.environ['DB_NAME']
port = 5432


class DataModel(object):
    def __init__(self):
        self.conn = psycopg2.connect(dbname=name, host=host,
                                    password=password,user=user)
        self.product_list = []
        self.products = ['moisturizer','serum']

    def skin_concerns(self,concern_list):
        n = len(concern_list)
        if n > 0:
            concern1 = concern_list[0]
            n -= 1
        if n > 0:
            concern2 = concern_list[1]
            n -= 1
        if n > 0:
            concern3 = concern_list[2]
        return(concern1,concern2,concern3)

    def query(self):
        ''''gets information from get_recommendations and makes a query for products and concerns'''
        table = self.product+'_recommender'
        query = f'''
    SELECT
      DISTINCT({table}.asin)
    , productinfo.title
    , {table}.{self.concern1}
    , {table}.{self.concern2}
    , {table}.{self.concern3}
    , productinfo.price
    , productinfo.numberreviews
    , productinfo.imageurl
    FROM
      {table}
    , productinfo
    WHERE
      {table}.asin=productinfo.asin AND productinfo.price<={self.budget};
        '''
        return(query)

    def run_query(self,query):
        try:
            df_results = pd.read_sql_query(query,self.conn)
            self.cleaned_df = self.clean_df(df_results)
        except psycopg2.Error as e:
            self.products = {'product1' : e.pgerror, 'product2' : ' ', 'product3' : ' '}

    def get_recommendations(self,budget,concern_list):
        '''central function that creates basket of products and populates the page with 9  baskets,
        3 for each concern'''
        self.budget = float(budget)
        self.budget += self.budget*.1
        cur = self.conn.cursor()
        self.concern1,self.concern2,self.concern3 = self.skin_concerns(concern_list)
        for product in self.products:
            self.product = product
            query = self.query()
            self.run_query(query)

            for concern in [self.concern1,self.concern2,self.concern3]:
                product_df = self.get_products(concern)
                product_df.rename(columns = {'p_'+self.concern1 : 'concern1',
                                             'p_'+self.concern2 : 'concern2',
                                             'p_'+self.concern3 : 'concern3'}, inplace=True)


                self.product_list.extend(product_df.to_dict(orient='records'))

        return(self.product_list)

    def get_product_list_(self):
        return(self.product_list)


    def update_price(self):
        mask = self.cleaned_df.price <= self.cleaned_df.new_budget
        column_name = 'new_budget'
        self.cleaned_df.loc[mask, column_name] = self.cleaned_df.new_budget - self.cleaned_df.price


    def clean_df(self,df):
        mask = df.numberreviews >= 350
        column_name = 'numberreviews'
        df.loc[mask, column_name] = 350
        df['review_ratio'] = df.numberreviews / 350
        df['new_budget'] = self.budget - df['price']
        df[[self.concern1,self.concern2,self.concern3]] = df[[self.concern1,self.concern2,self.concern3]].apply(pd.to_numeric)
        #normalizes the concerns to the number of reviews the product recieved.
        df['weighted_'+ self.concern1]  = df['review_ratio'] * df[self.concern1]
        df['weighted_' + self.concern2] = df['review_ratio'] * df[self.concern2]
        df['weighted_'+ self.concern3] = df['review_ratio'] * df[self.concern3]
        df['total'] = (df['weighted_'+ self.concern1] + df['weighted_'+ self.concern2] + df['weighted_'+ self.concern3])
        df['p_'+self.concern1] = df['weighted_'+ self.concern1] / df.total
        df['p_'+self.concern2] = df['weighted_'+ self.concern2] / df.total
        df['p_'+self.concern3] = df['weighted_'+ self.concern3] / df.total
        #taking the unweighted totals as well to randomly include products with high scores but less reviews.
        df['low_reviews'] = 0
        mask = df['review_ratio'] < .06
        column_name = 'low_reviews'
        df.loc[mask, column_name] = 1
        df['unweighted_'+ self.concern1]  = df['low_reviews'] * df[self.concern1]
        df['unweighted_' + self.concern2] = df['low_reviews'] * df[self.concern2]
        df['unweighted_'+ self.concern3] = df['low_reviews'] * df[self.concern3]
        df['unweighted_total'] = (df['unweighted_'+ self.concern1] + df['unweighted_'+ self.concern2] + df['unweighted_'+ self.concern3])
        df['p_unweighted_'+self.concern1] = df['unweighted_'+ self.concern1] / df.unweighted_total
        df['p_unweighted_'+self.concern2] = df['unweighted_'+ self.concern2] / df.unweighted_total
        df['p_unweighted_'+self.concern3] = df['unweighted_'+ self.concern3] / df.unweighted_total
        df.fillna(0,inplace=True)
        return(df)

    def get_products(self, concern):
        #grab top two product with weighted review ratio
        temp = pd.DataFrame()
        for i in range(2):
            top_one = self.cleaned_df.sort_values(by=['weighted_'+concern],ascending=False)
            top_one = top_one.head(1)
            top_one_idx = top_one.index[0]
            if top_one.loc[top_one_idx,'p_'+concern] == 0:
                top_one_low_review = self.cleaned_df.sort_values(by=['unweighted_'+concern],ascending=False)
                top_one_low_review['p_' + concern] = top_one_low_review['p_unweighted_'+ concern]
                top_one = top_one_low_review
            top_one_idx = top_one.index
            self.cleaned_df = self.cleaned_df.drop(top_one_idx,axis=0)
            temp = pd.concat([top_one,temp])

        #grab top product with low reviews but high score for concern
        top_one_low_review = self.cleaned_df.sort_values(by=['unweighted_'+concern],ascending=False)
        top_one_low_review['p_' + concern] = top_one_low_review['p_unweighted_'+ concern]
        top_one_low_review_index = top_one_low_review.head(1).index
        self.cleaned_df = self.cleaned_df.drop(top_one_low_review_index,axis=0)
        three_products_for_concern = pd.concat([temp,top_one_low_review.head(1)])
        three_products_for_concern = three_products_for_concern.filter(
                                    ['asin','price','title','p_'+self.concern1,'p_'+self.concern2,
                                    'p_'+self.concern3,'new_budget','imageurl'],axis=1)
        return(three_products_for_concern)
