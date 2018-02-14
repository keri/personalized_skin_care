import numpy as np
import pandas as pd

def cosine_similarity(row,new_product_vec):
    similarity = (1 - spatial.distance.cosine(row, new_product_vec))
    if similarity > 0:
        return similarity
    else:
        return 0


def find_product_aoc(X,new_product_vec):
'''returns a dictionary of cosine similarities with the area of concern'''
    
    similarity_dict = {
                       'scent':cosine_similarity(X[0],new_product_vec),
                       'dry':cosine_similarity(X[1],new_product_vec), 
                       'oily':cosine_similarity(X[2],new_product_vec), 
                       'combination':cosine_similarity(X[3],new_product_vec), 
                       'anti-aging':cosine_similarity(X[4],new_product_vec), 
                       'psoriasis':cosine_similarity(X[5],new_product_vec),
                       'lightening':cosine_similarity(X[6],new_product_vec), 
                       'sensitive':cosine_similarity(X[7],new_product_vec), 
                       'large-pores':cosine_similarity(X[8],new_product_vec), 
                       'circles-under-eyes':cosine_similarity(X[9],new_product_vec),
                       'uneven-skintone':cosine_similarity(X[10],new_product_vec), 
                       'night_cream':cosine_similarity(X[11],new_product_vec), 
                       'sun_screen':cosine_similarity(X[12],new_product_vec)
                       }
    return similarity_dict


