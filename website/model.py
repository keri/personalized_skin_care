import pandas as pd
import numpy as np
import psycopg2
import os
#from queries import PostGres

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

    # def find_product(self):
    #     '''Write some logic to determine what product should be used based on the budget they have left
    #     and what products they have in their basket'''
    #     if len(self.basket) == 0:
    #         self.product = 'moisturizer'
    #     if 'moisturizer' in self.basket:
    #         self.product = 'serum'
    #     elif 'serum' in self.basket:
    #         self.product = 'cleanser'
    #     else:
    #         self.product = 'end'

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
#        count = 1
        for product in self.products:
            self.product = product
#            query = self.query(concern1,concern2,concern3,budget)
            query = self.query()
            self.run_query(query)
#            temp_budget = self.cleaned_df['new_budget']
#            product_count = 1
#            while self.cleaned_df['new_budget'].max() > 0 and self.product != 'end':

            for concern in concern_list:
                product_df = self.get_products(concern)
                product_df.rename(columns = {'p_'+self.concern1 : 'concern1',
                                             'p_'+self.concern2 : 'concern2',
                                             'p_'+self.concern3 : 'concern3'}, inplace=True)


                self.product_list.extend(product_df.to_dict(orient='records'))
#                 for idx in product_df.index:
#                     count = int(count)
#                     count += 1
#                     count = str(count)
# #                    idx_list = product_df.index
#                     self.product_dictionary['product'+ count] =  product_df.loc[int(idx)].to_dict()
        print(self.product_list)
        return(self.product_list)

    def get_product_list_(self):
        return(self.product_list)
                    # self.baskets['product'+str(count+1)] =  product_df.loc[1]}
                    # self.baskets['basket'+str(count+2)] =  product_df.loc[2]}
#                    count += 3
#            product_count += 1
            # self.product = self.find_product()
            # budget = self.cleaned_df['new_budget'].max()
            # query = self.query(concern1,concern2,concern3,budget)
            # temp = self.cleaned_df['new_budget']
            # self.cleaned_df = self.clean_df(df_results,concern1,concern2,concern3,budget)
            # self.cleaned_df['new_budget'] = temp

#             self.product = self.find_product()
#                 self.basket = self.find_top_products(combined_df)
#
#             return(self.basket, combined_df)
# #            cur.rollback()

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
#        df['review_ratio'] = df['weighted_reviews'] / 350
        df['weighted_'+ self.concern1]  = df['review_ratio'] * df[self.concern1]
        df['weighted_' + self.concern2] = df['review_ratio'] * df[self.concern2]
        df['weighted_'+ self.concern3] = df['review_ratio'] * df[self.concern3]
        df['total'] = (df['weighted_'+ self.concern1] + df['weighted_'+ self.concern2] + df['weighted_'+ self.concern3])
        df['p_'+self.concern1] = df['weighted_'+ self.concern1] / (df.total+.000001)
        df['p_'+self.concern2] = df['weighted_'+ self.concern2] / (df.total+.000001)
        df['p_'+self.concern3] = df['weighted_'+ self.concern3] / (df.total+.000001)
        df = df.round(2)
        return(df)

    def get_products(self, concern):
        self.cleaned_df.sort_values(by=[concern],ascending=False,inplace=True)
        three_products_for_concern = self.cleaned_df.head(3)
        three_products_for_concern_idx = three_products_for_concern.index
        self.cleaned_df = self.cleaned_df.drop(three_products_for_concern_idx, axis=0)
        # mask = self.cleaned_df.price <= self.cleaned_df.new_budget
        # column_name = 'new_budget'
        # self.cleaned_df.loc[mask, column_name] = self.cleaned_df.new_budget - self.cleaned_df.price
        three_products_for_concern = three_products_for_concern.filter(
                                    ['asin','price','title','p_'+self.concern1,'p_'+self.concern2,
                                    'p_'+self.concern3,'new_budget','imageurl'],axis=1)
        return(three_products_for_concern)


#     def find_top_products(self,combined_df):
#         '''get box of several boxes of products. Include logic that
#         takes budget and percent of aoc covered for each product'''
# #        moisturizer =
#
#         self.basket['product1'] = 'moisturizerA'
#         self.basket['product2'] = 'serumB'
#         self.basket['product3'] = 'cleanserC'
#         self.basket['price'] = 23.00
#         return(self.basket)
