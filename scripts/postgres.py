import psycopg2
import os
password = os.environ['DB_PASS']
user = os.environ['DB_USER_NAME']

class PostGres():

    def __init__(self,product_type):

        self.conn = psycopg2.connect(dbname='skinproducts', host='skinproducts.cgz2ffd3hzsl.us-west-2.rds.amazonaws.com',
        password=password,user=user)
#        self.conn = psycopg2.connect(dbname='postgres', host='localhost')
        self.cur = self.conn.cursor()
        self.conn.autocommit = True
        self.product_type = product_type
#        self.cur.close() # This is optional
#        self.conn.close()

#     def setup_db(self):
#         self.cur.execute('DROP DATABASE IF EXISTS skinproducts;')
#         self.cur.execute('CREATE DATABASE skinproducts;')
#         self.conn = psycopg2.connect(dbname='skinproducts', host='localhost')
#         self.cur = self.conn.cursor()
#         self.conn.autocommit = True
# #        self.cur.close() # This is optional
# #        self.conn.close()
# #        self.cur.execute('DROP DATABASE IF EXISTS skinproducts;')
# #        self.cur.execute('CREATE DATABASE skinproducts;')
#
#         query = '''
#                 CREATE TABLE reviews (
#                 ASIN varchar(15) ,
#                 stars integer,
#                 reviews varchar(10000),
#                 producttype varchar(20),
#                 PRIMARY KEY (ASIN)
#
#                 );
#                 '''
#         self.cur.execute(query)
#
#
#         query = '''
#                 CREATE TABLE productInfo (
#                     ASIN varchar(15),
#                     producttype varchar(20),
#                     url varchar(1000),
#                     reviewurl varchar(1000),
#                     price FLOAT,
#                     ranking varchar(10000),
#                     numberreviews integer,
#                     ingredients varchar(10000),
#                     directions varchar(10000),
#                     indications varchar(10000),
#                     title varchar(1000),
#                     PRIMARY KEY (ASIN, producttype)
#
#                 );
#                 '''
#
#         self.cur.execute(query)
#         self.close_cursor()

    def create_table(self, query):
        self.conn = psycopg2.connect(dbname='skinproducts', host='localhost')
        self.cur = self.conn.cursor()
        self.conn.autocommit = True
        try:
            self.cur.execute(query)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        if self.conn is not None:
            self.close_cursor()

    def insert_product(self,row):
        self.conn = psycopg2.connect(dbname='skinproducts', host='localhost')
        self.cur = self.conn.cursor()
        self.conn.autocommit = True

        query = '''
                INSERT INTO productInfo(ASIN,producttype,url,reviewurl,price,ranking,
                                        numberreviews, ingredients, indications, title)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

        try:
            self.cur.execute(query,row)
            # commit the changes to the database
            self.conn.commit()
            # close communication with the database
            #cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        if self.conn is not None:
            self.close_cursor()

    def modify_table(self,query):
            self.conn = psycopg2.connect(dbname='skinproducts', host='localhost')
            self.cur = self.conn.cursor()
            self.conn.autocommit = True

            try:
                self.cur.execute(query)
                # commit the changes to the database
                self.conn.commit()
                # close communication with the database
                #cur.close()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            if self.conn is not None:
                self.close_cursor()

    def insert_review(self,row):
        self.conn = psycopg2.connect(dbname='skinproducts', host='localhost')
        self.cur = self.conn.cursor()
        self.conn.autocommit = True
        #[ASIN, rater_id, rating, title, rater, review_date, review_text]
        query = '''
                INSERT INTO cleanser(ASIN, rater_id, rating, title, rater, review_date, review_text)
                VALUES(%s, %s, %s, %s, %s, %s, %s)
                '''
        try:
            self.cur.execute(query, row)
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        if self.conn is not None:
            self.close_cursor()


    def get_product_rows(self,query,args):
        self.conn = psycopg2.connect(dbname='skinproducts', host='localhost')
        self.cur = self.conn.cursor()
        self.conn.autocommit = True
        try:
            self.cur.execute(query,args)
            results = self.cur.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        if self.conn is not None:
            self.close_cursor()
        return(results)

    def close_cursor(self):
        self.conn.close()
        self.cur.close()
