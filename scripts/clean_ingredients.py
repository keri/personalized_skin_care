import pandas as pd
import numpy as np
import string

stopwords_ = "%,and,aqua/water,about,acid,jojoba,organic,oil,seed,derived,aqua,water,deionized,anything,after,\
are,as,at,be,because,been,but,by,can,could,dear,did,do,does,either,aging,best,water/eau,water/aqua/eau,wateraqua,\
else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,wateragua,water/agua,water/aqua,\
how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,ourselves,comes,'water/agua','water/agua',\
me,might,most,must,my,neither,no,not,of,off,often,on,only,or,other,over,our,above,see,ingredient,ingredients,image,\
box,please,see,'cruelty','free',above,none.nan\
own,purified,percentage,percent,contains,quality,rather,so,said,say,says,she,should,since,'wateraqua',\
so,some,than,that,the,their,anti,aging,aging,made,product,products,\
them,then,there,these,they,this,tis,to,too,try,tried,twas,us,used,use,very,wants,was,we,were,\
what,when,where,which,while,who,whom,why,will,with,would,yet,you,your]".split(',') + list(string.punctuation)

#
# def lower(string):
#     return(str(string).lower())

def cleaned_listed_ingredients(ingredients):
    listed_ingredients = []
#    for ingredient in ingredients:
    listed_ingredients.append(set(clean_ingredients(ingredients)))
    return(listed_ingredients)

def clean_ingredients(string_ingredient):
    # ingredient = ingredient.lower()
    ingredient = string_ingredient.replace('%','')
    ingredient = ingredient.replace('(','')
    ingredient = ingredient.replace(')','')
    ingredient = ingredient.replace('*','')
    ingredient = ingredient.replace(';','')
    ingredient = ingredient.replace('.','')
    ingredient = ingredient.replace('{','')
    ingredient = ingredient.replace('}','')
    ingredients = ingredient.split(' ')
    ingredients_no_stop = [word.lower() for word in ingredients if word.lower().split('/') not in stopwords_]
    print('ingredient no stop = ',ingredients_no_stop)
    return(ingredients_no_stop)

# def
# ingredient_only_list = []
# for ingredient in ingredients:
#     resultingredients  = [word for word in ingredient if word.lower() not in stopwords_]
#     ingredient_only_list.append(resultingredients)
