import pandas as pd
import numpy as np
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import string
#import json
#from scipy import spatial
#from collections import defaultdict

#df = pd.read_csv('moisturizer_reviews.csv')
#df = pd.read_csv('serum_reviews.csv')
#df_four_five = df.loc[df['rating'] > 4.0, ('asin','rating','reviewer_id','review')]
#asins = df_four_five.asin.unique()


stopwords_ = "%,amazon,skin,dry,product,products,every,sometimes,bought,cream,review,reviews,many,\
others,recommend,love,very,best,cant,with,after,compare,last,brickell,out,\
enough,long,skincare,skin-care,girlfriend,an,and,another,any,anyone,anymore,apply,applying,applied\
boyfriend,husband,wife,face,feel,feels,friend,friends,daily,week,weeks,month,months,look,looks,comment,comments,\
about,anything,after,a,am,ago,all,almost,along,already,also,always,are,as,at,be,because,been,being,big,\
bit,body,both,bottle,brand,brands,break,but,buy,buying,by,came,can,could,container,\
continue,couple,companies,comes,company,come,completely,daughter,decided,dear,did,didn',didn,do,does,doesn,doing,don,done,down,\
due,during,easily,easy,end,either,family,fan,far,fast,few,found,find,fine,finally,fact,\
else,ever,every,for,from,get,gets,getting,go,goes,going,gone,got,glad,give,gives,great,had,has,hair,have,having,he,help,helping,\
helps,helper,high,hopes,huge,her,hers,him,his,\
how,however,i,if,in,into,is,isn,it,its,jar,job,just,keep,keeps,know,lasts,last,leaves,leave,leaving,least,let,like,\
left,less,life,likely,may,made,makes,make,making,money,morning,much,me,might,most,must,my,neither,need,neutrogena,new,next,\
no,not,of,off,often,olay,on,once,order,ordered,ordering,only,or,other,over,our,own,problem,problems,purchase,purchased,\
rather,really,recieved,recieve,so,said,say,says,see,seeing,seen,seem,serum,she,should,since,small,soon,so,some,start,\
started,starting,than,thank,thanks,that,the,their,them,then,there,these,they,this,tis,to,too,top,try,truly,try,\
tried,twas,twice,two,type,under,until,up,us,used,uses,using,usually,use,ve,very,\
wants,was,way,we,were,wish,well,years,year,\
what,when,where,which,while,who,whom,why,will,with,would,yet,you,your]".split(',') + list(string.punctuation)

def get_product_df(product_type):
    df = pd.read_csv(product_type + '_reviews.csv')
    df_four_five = df.loc[df['rating'] > 4.0, ('asin','rating','reviewer_id','review')]
    asins = df_four_five.asin.unique()
    return(asins,df_four_five)


def join_reviews(review):
    return(' ' + review)

def create_corpus(asins,df_four_five):
    '''Get the reviews out of the dataframe and combine them per asin into new dataframe and
    grab the combined reviews into a corpus to be passed into Vectorizer'''
    df_reviews = pd.DataFrame(columns=['asin','reviews'])
    df_reviews.asin = asins
    df_reviews.set_index('asin',inplace=True)
    for asin in asins:
        each_review = df_four_five.loc[df_four_five['asin'] == asin, ('asin','review')]
        reviews = each_review.review
        start_review = ''
        for review in reviews:
            start_review += join_reviews(review)
        df_reviews.loc[asin,'reviews'] = start_review
        corpus = df_reviews.reviews
    return(corpus)

def run_nmf(X, asins,features,n_components=20):
    nmf = NMF(n_components)
    nmf.fit(X)
    W = nmf.transform(X)
    H = nmf.components_
    #make interpretable:
    W, H = (x for x in (W,H))
    W_df = pd.DataFrame(W,index=asins)
    H_df = pd.DataFrame(H,columns=features)
    return(W,H,W_df,H_df)

def run_model(product_type):
    asins, four_five_df = get_product_df(product_type)
    corpus = create_corpus(asins,four_five_df)
    X, features = tfidf_modeling(corpus)
    W, H, W_df, H_df = run_nmf(X, asins, features)
    return(W,H,W_df,H_df)


def tfidf_modeling(corpus,n_features=400):
    '''Takes the combined reviews and runs the tfidf vectorizer looking for latent features'''

    vec = TfidfVectorizer(stop_words=stopwords_,strip_accents=None,max_features=n_features)
    X = vec.fit_transform(corpus)
    X = X.toarray()
#    skin_type_vec = np.ones(len(vocabulary))
#    product_mean = find_product_mean(X,skin_type_vec)
    features = vec.get_feature_names()
    return(X, features)

def get_words(H,features,n):
    top_words_index = np.argsort(-H)[:,0:n]
    most_common_words_per_topic = np.array(features)[top_words_index]
    for i, items in enumerate(most_common_words_per_topic):
        print(i, items)
