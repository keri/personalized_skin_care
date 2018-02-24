import pandas as pd
import numpy as np
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import string
import pickle
import psycopg2
import os

password = os.environ['DB_PASS']
user = os.environ['DB_USER_NAME']
host = os.environ['DB_HOST']
name = os.environ['DB_NAME']


stopwords_ = "%,amazon,skin,dry,product,products,every,sometimes,bought,cream,review,reviews,many,\
others,recommend,love,very,best,cant,with,after,compare,last,brickell,out,\
enough,long,skincare,skin-care,girlfriend,an,and,another,any,anyone,anymore,apply,applying,applied\
boyfriend,husband,wife,face,feel,feels,first,friend,friends,daily,week,weeks,month,months,look,looks,comment,comments,\
about,anything,after,a,am,ago,all,almost,along,already,also,always,are,as,at,be,because,been,being,big,\
bit,body,both,bottle,brand,brands,break,but,buy,buying,by,came,can,cleansing,cleanser,clean,cleaned,cleanse,cloth,could,container,\
continue,couple,companies,comes,company,come,completely,daughter,decided,dear,did,didn',didn,do,does,doesn,doing,don,done,down,\
due,during,easily,easy,end,either,family,fan,far,fast,few,foam,foaming,found,find,fine,finally,fact,free,\
else,ever,every,for,from,get,gets,getting,go,goes,going,gone,good,got,glad,give,gives,great,had,has,hair,have,having,he,help,helping,\
helps,helper,high,hopes,huge,her,hers,him,his,\
how,however,i,if,in,into,is,isn,it,its,jar,job,just,keep,keeps,know,lasts,last,lathers,lather,leaves,leave,leaving,least,let,like,\
left,less,life,likely,mascara,may,made,makes,make,makeup,making,money,morning,much,me,might,most,must,my,neither,need,neutrogena,new,next,\
no,not,nice,of,off,often,olay,on,once,order,ordered,ordering,only,or,other,over,our,own,problem,problems,purchase,purchased,\
rather,really,recieved,recieve,remove,remover,so,said,say,says,see,seeing,seen,seem,serum,she,should,since,small,soon,so,some,start,\
started,starting,than,thank,thanks,that,the,their,them,then,there,these,they,this,tis,to,too,top,try,truly,try,\
tried,twas,twice,two,type,under,until,up,us,used,uses,using,usually,use,ve,very,water, warm,\
wants,was,way,we,were,wipe,wipes,wish,well,years,year,\
what,when,where,which,while,who,whom,why,will,with,would,yet,you,your]".split(',') + list(string.punctuation)

def get_product_df(product_type):
    df = pd.read_csv(product_type + '_reviews.csv')
    df_four_five = df.loc[df['rating'] > 4.0, ('asin','rating','reviewer_id','review')]
    asins = df_four_five.asin.unique()
    return(asins,df_four_five)

def get_new_products(product_type):
    conn = psycopg2.connect(dbname=name, host=host,
                                    password=password,user=user)


    query = f'''SELECT p.asin, m.review_text, m.rating
                FROM products as p
                LEFT JOIN {product_type} as m ON p.asin=m.asin 
                WHERE p.producttype='cleanser' AND m.rating>=4;'''

    # SELECT review_text, asin
    #         FROM {product_type}
    #         WHERE rating >= 4 AND created_at >=;'''


#;
    df = pd.read_sql_query(query,conn)
    return(df)


def create_corpus(df):
    '''Get the reviews out of the dataframe and combine them per asin into new dataframe and
    grab the combined reviews into a corpus to be passed into Vectorizer'''
    asins = df['asin'].unique()
    df_reviews = pd.DataFrame({'asin':asins,'review_text':''})
    df_reviews.set_index('asin',inplace=True)
    for asin in asins:
        temp = df[df['asin']==asin]
        combined_review = temp.review_text.str.cat(sep=' ')
        df_reviews.loc[asin,'review_text'] = combined_review
        corpus = df_reviews['review_text']
    return(corpus)

def fit_nmf(X, n_components=20):
    nmf = NMF(n_components)
    nmf.fit(X)
    return(nmf)

def transform_nmf(X,nmf):
    W = nmf.transform(X)
    H = nmf.components_
    return(W,H)

def make_dataframe(matrix1, matrix2, asins,features):
    W, H = (x for x in (matrix1,matrix2))
    return( pd.DataFrame(W,index=asins), pd.DataFrame(H,columns=features) )


def train_model(product_type):
    asins, four_five_df = get_product_df(product_type)
    corpus = create_corpus(four_five_df)
    vec = tfidf_fit(corpus)
    nmf = fit_nmf(X, asins, features)
    return(vec,nmf)

def transform_new_products(vec,nmf,product_type):
    columns = ['scent','dry', 'oily', 'combination', 'antiaging',
                'psoriasis', 'lightening', 'sensitive', 'pores',
                'eyes', 'skintone','night',
                'sunscreen']
    #get new product reviews from database
    df = get_new_products(product_type)
    asins = df['asin'].unique()
    corpus = create_corpus(df)
    X,features = tfidf_transform(vec,corpus)
    W, H = transform_nmf(X,nmf)
    aoc_matrix = pd.read_csv('data/aoc_'+product_type+'.csv')
    aoc_matrix.drop(columns=('Unnamed: 0'),inplace=True)
    print(aoc_matrix.shape)
    aoc_matrix = aoc_matrix.values
    product_matrix = np.dot(W,aoc_matrix)
    print(product_matrix.shape)
    product_matrix_df = pd.DataFrame(product_matrix,columns=columns, index=asins)
    W_df, H_df = make_dataframe(W,H,asins,features)
    return(W,H,W_df,H_df,product_matrix_df)

def tfidf_fit(corpus,n_features=400):
    '''Takes the combined reviews and runs the tfidf vectorizer looking for latent features'''
    vec = TfidfVectorizer(stop_words=stopwords_,strip_accents=None,max_features=n_features)
    vec.fit(corpus)
    return(vec)

def save_model(model,filename):
    with open(filename,'wb') as f:
        pickle.dump(model, f)

def load_model(filename):
    with open(filename, 'rb') as f:
        return(pickle.load(f))

def tfidf_transform(vec,corpus):
    X = vec.transform(corpus)
    X = X.toarray()
    features = vec.get_feature_names()
    return(X, features)

def get_words(H,features,n):
    top_words_index = np.argsort(-H)[:,0:n]
    most_common_words_per_topic = np.array(features)[top_words_index]
    for i, items in enumerate(most_common_words_per_topic):
        print(i, items)
