import psycopg2
import os
password = os.environ['DB_PASS']
user = os.environ['DB_USER_NAME']
host = os.environ['DB_HOST']
name = os.environ['DB_NAME']
port = 5432

class PostGres():

    def __init__(self):

        self.conn = psycopg2.connect(dbname=name, host=host, password=password,user=user)
        self.cur = self.conn.cursor()
        self.conn.autocommit = True

    def run_query(self, query):
        self.conn = psycopg2.connect(dbname=name, host=host, password=password,user=user)
        self.cur = self.conn.cursor()
        self.conn.autocommit = True
        try:
            self.cur.execute(query)
            results = self.cur.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        if self.conn is not None:
            self.close_cursor()
        return(results)

    def close_cursor(self):
        self.conn.close()
        self.cur.close()
