import pandas as pd
import numpy as np
import string
import nltk
from nltk.stem.porter import PorterStemmer
import re

stopwords_ = "%,a,and,acid,aqua,aqua/water,brands,water,about,acid,jojoba,organic,oil,seed,derived,aqua,water,deionized,anything,after,\
are,as,at,balance,balancine,balanced,be,because,been,but,by,can,could,dear,did,do,does,either,aging,best,water/eau,water/aqua/eau,\
wateraqua,easy,effect,effects,effected,frustrated,frustrate,hydrate,hydration,hydrating,\
else,enhances,enhance,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,irritate,irritating,irritates, wateragua,water/agua,water/aqua,\
how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,ourselves,comes,'water/agua','water/agua',many,\
me,might,minimizes,minimize,most,must,my,neither,no,not,of,off,often,on,only,or,other,over,our,above,see,ingredient,ingredients,image,\
box,please,see,'cruelty','free',above,none.nan,protective,protects,protect,protecting,\
own,purified,percentage,percent,contains,quality,rather,so,said,say,says,she,should,since,skin,type,particular,skin-type,'water/aqua',\
so,some,specific,specifically,specifics,than,that,the,their,anti,aging,aging,made,product,products,\
them,then,there,these,they,this,tis,to,too,try,tried,twas,us,used,use,very,wants,was,we,were,\
what,when,where,which,while,who,whom,why,will,with,would,yet,you,your,(,),*,;,:,{,},[,],.,' ',".split(',') + list(string.punctuation)

#
# def lower(string):
#     return(str(string).lower())

def cleaned_listed_ingredients(ingredients):
    stemmer_porter = PorterStemmer()

    ingredients = ingredients.lower()
    stemmer_porter.stem(ingredients)
    ingredients = ingredients.replace('%','')
    ingredients = ingredients.replace('"','')
    ingredients = ingredients.replace('(','')
    ingredients = ingredients.replace(')','')
    ingredients = ingredients.replace('*','')
    ingredients = ingredients.replace(';','')
    ingredients = ingredients.replace('.','')
    ingredients = ingredients.replace('{','')
    ingredients = ingredients.replace(',','')
    ingredients = ingredients.replace('}','')
    ingredients = ingredients.replace('-acid','')
    ingredients = ingredients.replace('/',' ')
    ingredients = ingredients.replace("'",'')
    ingredients = ingredients.replace('zemea®','zemea')
    ingredients = ingredients.replace('glycerin', 'glycer')
    ingredients = ingredients.replace('glyceryl', 'glycer')
    ingredients = ingredients.replace('glycerine', 'glycer')
    ingredients = ingredients.replace('glycerol', 'glycer')
    ingredients = ingredients.replace('acylglycerols', 'glycerides')
    ingredients = ingredients.replace('persea', 'avocado')
    ingredients = ingredients.replace('gratissima', 'avocado')
    ingredients = ingredients.replace('euphrasia officinalis', 'eyebright')
    ingredients = ingredients.replace('helichrysum gymnocephalum ', 'helichrysum')
    ingredients = ingredients.replace('glycyrrhiza glabra', 'licorice')
    ingredients = ingredients.replace('cymbopogon schoenanthus', 'lemongrass')
    #capturing all variation of vitamin c palmitate
    pattern = 
    for i, item in enumerate(ingredients):
    if re.search(pattern, item):
        ingredients[i] = "vitamin-c-palmitate"
 
    ingredients = ingredients.replace(re.compile(r'*ascorbate*'), 'vitamin-c-palmitate')
    ingredients = ingredients.replace('palmitate'), 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ondascora', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('quicifal', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ascorbyl palmitic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('l-ascorbyl palmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('palmitoyl l ascorbic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('palmitoyl l-ascorbic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6-monopalmitoyl-l-ascorbate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6 monopalmitoyl l-ascorbate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6-monopalmitoyl l-ascorbate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('1-ascorbyl palmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('1 ascorbyl palmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('1 ascorbyl-palmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6-O-palmitoylascorbic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6 O palmitoylascorbic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ascorbic acid palmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ascorbic-acid-palmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6-hexadecanoyl-l-ascorbic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6 hexadecanoyl l-ascorbic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6-hexadecanoyl l-ascorbic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6 hexadecanoyl l ascorbic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6 hexadecanoyl', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('l ascorbic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('l-ascorbyl monopalmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('l ascorbyl monopalmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('monopalmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6-monopalmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ester with ascorbic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ascorbylpalmitic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ascorbylpalmitic', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('palmitoylascorbic', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('nsc 402451', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('4-dihydroxy-5-oxo-2', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('5-dihydrofuran-2-yl-2-hydroxyethyl', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('4-dihydroxy-5-oxo-2', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('Asc6Plm', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6-O-palmitoyl ascorbate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('asc-6-O-palmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6 palmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6-palmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('6-hexadecanoate, L-', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ccris 3930', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('hsdb 418', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ester', '')
    ingredients = ingredients.replace('c22h38O7', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ascorbylpalmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ascorbyl palmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ascorbyl 6-palmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ascorbyl-6-palmitate', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ncgc00161605-01', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ascorbic acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('ascorbic-acid', 'vitamin-c-palmitate')
    ingredients = ingredients.replace('hexadecanoic', 'vitamin-c-palmitate')
    



    ingredients = set(ingredients.split(' '))

    cleaned_ingredients = [word for word in ingredients if word not in stopwords_]
    print(cleaned_ingredients)
    return(cleaned_ingredients)

