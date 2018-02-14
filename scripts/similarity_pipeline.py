import pandas as pd
import numpy as np
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
import string
import json
from scipy import spatial
from collections import defaultdict

with open('pos_dictionary.json') as f:
    pos_dictionary = json.load(f)
with open('neg_dictionary.json') as f:
    neg_dictionary = json.load(f)

stopwords_ = "%,about,anything,after,skin,product,products,every,sometimes,bought,cream,review,reviews,many,\
others,recommend,about,a,love,very,best,cant,with,after,compare,last,enough,long,skincare,skin-care,girlfriend,\
boyfriend,husband,wife,friend,friends,daily,week,weeks,month,months,look,looks,comment,comments,\
are,as,at,be,because,been,but,by,can,could,dear,did,do,does,either,\
else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,\
how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,\
me,might,most,must,my,neither,no,not,of,off,often,on,only,or,other,over,our,\
own,rather,so,said,say,says,she,should,since,so,some,than,that,the,their,\
them,then,there,these,they,this,tis,to,too,try,tried,twas,us,used,use,very,wants,was,we,were,\
what,when,where,which,while,who,whom,why,will,with,would,yet,you,your]".split(',') + list(string.punctuation)

def create_review_dataframe(reviews_df):
    '''create an empty dataframe to be populated with the cosine similarities of each
    product with the various skin concerns.'''
    every_asin = reviews_df.asin.unique()
    columns = list(pos_dictionary.keys())
    columns.append('product')
    df_ratings = pd.DataFrame(columns=columns)
    df_ratings['product'] = every_asin
    df_ratings.set_index('product',inplace=True)
    return(df_ratings, every_asin)


def model_products(reviews_df):
    #iterating over each asin and modeling with each skin concern
    df_pos_features = defaultdict(list)
    df_neg_features = defaultdict(list)
    df_ratings, every_asin = create_review_dataframe(reviews_df)
    for asin in every_asin:
        df = reviews_df.loc[reviews_df['asin'] == asin, ('asin','review')]
        reviews = df.review
        for k,v in pos_dictionary.items():
            skin_type = k
            vocabulary_pos = v
            vocabulary_neg = neg_dictionary[k]
            asin_skin_type_pos_mean, pos_features = skin_type_modeling(vocabulary_pos,reviews)
            asin_skin_type_neg_mean, neg_features = skin_type_modeling(vocabulary_neg,reviews)
            final_mean = (asin_skin_type_pos_mean - asin_skin_type_neg_mean)
            df_ratings.loc[asin, skin_type] = final_mean
            for feature in pos_features:
                df_pos_features[asin].append(feature)
            for feature in neg_features:
                df_neg_features[asin].append(feature)
        return(df_neg_features, df_pos_feature)

def skin_type_modeling(vocabulary,reviews):
    '''Takes the skin type dictionary and runs the tfidf vectorizer with each vocabulary combined for every combination
    users can put into the system'''
    #get the dictionary vocabulary:
    vec = TfidfVectorizer(stop_words=stopwords_,vocabulary=vocabulary,strip_accents=None)
    X = vec.fit_transform(reviews)
    X = X.toarray()
    skin_type_vec = np.ones(len(vocabulary))
    product_mean = find_product_mean(X,skin_type_vec)
    terms = vec.get_feature_names()
    print('terms are : ',terms)
    feature_list = []
    for row in X:
        row = np.array(row)
        terms = np.array(terms)
        feature_list.append(terms[row>0])
        print('feature_list = ',feature_list)
    return(product_mean, feature_list)

def cosine_similarity(X,skin_type_vector):
    return(1 - spatial.distance.cosine(X, skin_type_vector))

def find_product_mean(X,skin_type_vec):
    similarity_list = []
    for row in X:
        if row.sum() > 0:
            similarity_list.append(cosine_similarity(row,skin_type_vec))
        else:
            similarity_list.append(0)
    similarity_array = np.array(similarity_list)
    similarity_array = similarity_array[similarity_array>0]
    if len(similarity_array) == 0:
        product_mean = 0
    else:
        product_mean = similarity_array.mean()

    return product_mean
