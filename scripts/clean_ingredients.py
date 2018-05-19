import pandas as pd
import numpy as np
import string
import nltk
from nltk.stem.porter import PorterStemmer
import re

stopwords_ = "&,1,2,3,4,5,6,7,8,9,%,a,and,acid,aqua,aqua/water,wat,agua,brands,water,about,acid,organic,oil,seed,derived,aqua,water,\
deionized,anything,after,a,in,under,medical,treatment,treatments,improve,improved,emulsify,emulsifying,emulsified,\
are,as,at,balance,balancine,balanced,be,because,been,but,by,can,could,dear,did,do,does,either,aging,best,water/eau,water/aqua/eau,\
wateraqua,easy,effect,effects,effected,frustrated,frustrate,hydrate,hydration,hydrating,antioxidant,anti-oxidant,antioxident\
else,enhances,enhance,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,irritate,irritating,irritates, wateragua,water/agua,water/aqua,\
how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,ourselves,comes,'water/agua','water/agua',many,\
me,might,minimizes,minimize,most,must,my,neither,no,not,of,off,often,on,only,or,other,over,our,above,see,ingredient,ingredients,image,\
box,please,see,'cruelty','free',above,none.nan,protective,protects,protect,protecting,enhancing,enhanced,enhancer,\
own,purified,percentage,percent,contains,quality,rather,so,said,say,says,she,should,since,skin,type,particular,skin-type,'water/aqua',\
so,some,specific,specifically,specifics,than,that,the,their,anti,aging,aging,made,product,products,starch,protects,protect,\
protection,vitamin,vitamine,provitamin,pro-vitamin,pro-vitamine,provitamine,lipid,lipids,sunscreen,suncreens,sun screen,\
them,then,there,these,they,this,tis,to,too,try,tried,twas,us,used,use,very,wants,was,we,were,texture,texturizer,base,\
texturizing,cream,creams,balance,balancing,serum,serums,balanced,natural,ingredients,ingredient,powder,soluble,complex,\
complexes,micro,micro-organisms,microorganism,organism,organisms,bioactive,bio,active,plant,plants,origin,origins,pure,\
routine,skin,\
what,when,where,which,while,who,whom,why,will,with,would,yet,you,your,(,),*,;,:,{,},[,],.,' '".split(',') + list(string.punctuation)

#
# def lower(string):
#     return(str(string).lower())

patterns = [('palmitic','hexadecanoic'),('hexadecanoic','hexadecanoic'),('cetylstearyl','cetearylalcohol'),
            ('retinyl',''),('retinol',''),(' ferment',''),(' honey',''),('methylsulfynolmethane','msm'),
            ('palmit','c-ester'),('ascorbic','vitamin-c'),('ascorbyl','c-ester'),('stearate',''),(' juice',''),
            ('benzoic','salicylic'),('ondascora','c-ester'),('methicon','dimethicone'),('isopropyl ',''),
            ('avobenzone','avobenzone'),('quicifal','c-ester'),('sodium ',''),(' acid',''),(' algae',''),
            ('salicylic','salicylic'),('helichrysum','helichrysum'),('stearic ','stearic'),('octadecanoic','stearic'),
            ('glycyrrhiza','licorice'),('cymbopogon','lemongrass'),('euphrasia','eyebright'),('disodium ',''),
            ('acylglycerol','glycaride'),('glycer','glycerin'),('octanediol','caprylyl'),('propylene','propylene'),
            ('dihydroxyoctane','caprylyl'),('caprylyl','caprylyl'),('octylene','caprylyl'),('aloe ',''),('rose ',''),
            ('cetyl','cetearylalcohol'),(' glucoside',''),('sodium ',''),('stearyl ',''),(' peptide',''),('flower ',''),
            (' oxide',''),('oxide ',''),('camellia sinensis','greentea'),('green tea','greentea'),(' oil',''),
            (' extract',''),('jojoba','jojoba'),('methosulfate','bms'),('btms','bms'),('ceramide','ceramide'),
            (' gluconate',''),(' alcohol',''),('persea grat','avocado'),('zimea','zimea'),('hyaluronic ',''),
            ('silsesquioxane','silsesquioxane'),('saccharide ',''),('tea',''),(' butter',''),(' esters',''),
            ('beeswax','beeswax'),('cocamidopropyl','cocamidopropyl'),('rosaeodora','rosewood'),('sclarea','sage'),
            ('cedrus','cedar'),('cananga','conanga'),('ylang ylang','conanga'),('jasmin','jasmin'),(' collagen',''),
            ('acryloyldimethyltaurate','acryloyldimethyl'),('acryloyldimethyl','acryloyldimethyl'),(' juice',''),
            ('iodopropynyl','iodopropynyl'),('copper ',''),('vitamin a','a'),('saccharomyces','yeast'),(' wood',''),
            ('polycottonseedate','polycottonseedate'),('sucrose','sucrose'),('saccharose','sucrose'),('saccharum','sucrose'),
            ('santalum','sandalwood'),('tocopherol','e'),('citrus sinensis','sweetorange'),('vitamin c','c'),('dmdm','dmdm'),
            ('vitamin b','b'),('vitamin d','d'),('vitamin e','e'),('acrylate','acrylate'),('akrylate','acrylate'),
            ('lysolecithin','lpc'),('lysophosphatidylcholine','lpc'),('hydrolysed lecithin','lpc'),('modified lecithin','lpc'),
            (' polyphenols',''),(' glutamate',''),(' silicate',''),(' flower',''),(' root',''),(' leaf','')]

def replace_ingredient(ingredient):
    for pattern in patterns:
        if pattern[0] in ingredient:
            '''concatenating two words if pattern is a prefix or suffix'''
            if pattern[1] == '':
                if len(ingredient.split()) < 3: #checking if ingredient has more than 2 words
                    ingredient = ''.join(ingredient.split()) #joins the 2 words
                else:
                    before, keyword, after = ingredient.partition(pattern[0]) 
                    if keyword[-1] == ' ':
                        ingredient = ''.join([keyword.strip(),(after.split()[0]).strip()]) #if keyword is prefix 
                    elif len(before.split()) > 1:
                        ingredient = ''.join([(before.split()[-1]).strip(),keyword.strip()]) #if keyword is a suffix
                    else:
                        ingredient = ''.join([before.strip(),keyword.strip()]) #keyword suffix and only 1 word before it
            else:
                ingredient = pattern[1]
            return(ingredient)
    ingredient = ingredient.split()
    ingredient = [word.strip() for word in ingredient if word not in stopwords_]
    ingredient = ''.join(ingredient)
    if ingredient != '' and ingredient != None:
        return(ingredient)



def cleaned_listed_ingredients(ingredients):
    stemmer_porter = PorterStemmer()

    ingredients = ingredients.lower()
    ingredients = stemmer_porter.stem(ingredients)
    ingredients = ingredients.replace('%','')
    ingredients = ingredients.replace('"','')
    ingredients = ingredients.replace('(','')
    ingredients = ingredients.replace(')','')
    ingredients = ingredients.replace('*','')
    ingredients = ingredients.replace(';','')
    ingredients = ingredients.replace('.','')
    ingredients = ingredients.replace('{','')
    ingredients = ingredients.replace('}','')
    ingredients = ingredients.replace('/',' ')
    ingredients = ingredients.replace("'",'')
    ingredients = ingredients.replace("+",'')
    ingredients = ingredients.replace("&",'')
    ingredients = ingredients.replace("1",'')
    ingredients = ingredients.replace("0",'')
    ingredients = ingredients.replace("2",'')
    ingredients = ingredients.replace("3",'')
    ingredients = ingredients.replace("4",'')
    ingredients = ingredients.replace("5",'')
    ingredients = ingredients.replace("6",'')
    ingredients = ingredients.replace("7",'')
    ingredients = ingredients.replace("8",'')
    ingredients = ingredients.replace("9",'')
    ingredients = ingredients.replace("-",'')
    ingredients = ingredients.replace("!",'')
    ingredients = ingredients.replace("organic",'')

    ingredients = ingredients.split(',')

    filtered_ingredients = list(map(lambda x: replace_ingredient(x), ingredients))
    filtered_ingredients = set(filtered_ingredients)
    return(filtered_ingredients)
    
