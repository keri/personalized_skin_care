'''Class that updates basket with ability to delete, add products'''
'''input:	product dictionary with:
			price
			concern with value for each concern
			category
			title
			imageurl
			asin
	return:
			basket dictionary 
			products: product list of product dictionaries
			price: price - float total
			basket_concerns: dictionary of concerns total concern values for basket
	'''

class Basket(object):
	def __init__(self):
		# self.basket = {'basket_concerns':{},'price':0,'products':[]}
		# self.total_price = 0
		# self.concerns = []
		self.basket = {'basket_concerns':{},'basket_price':0,'products':[]}
		self.total_price = 0
		self.concerns =[]
		self.products = []
		self.categories = ['moisturizer','serum','cleanser']
		self.categories_own = []

	def get_products_in_each_category(self):

		moisturizers = [result for result in self.products if result['category'] == 'moisturizer']
		cleansers = [result for result in self.products if result['category'] == 'cleanser']
		serums = [result for result in self.products if result['category'] == 'serum']
		
		
		product_categories = { 'moisturizer': moisturizers, 'cleanser': cleansers, 'serum' : serums }

		return(product_categories)

	def get_basket_concerns(basket, concerns):
	    basket_concerns = {}
	    for concern in concerns:
	        concern_total = (basket[0][concern] + basket[1][concern] +
	                        basket[2][concern])
	        basket_concerns[concern] = concern_total
	    return(basket_concerns)

	def _check_concern_totals(self,temp_df):
			temp_df['concern_totals'] = 0
			for concern in self.concerns:
				temp_df['concern_totals'] = temp_df['concern_totals'].add(temp_df[concern])
			max_product_for_category = temp_df.loc[temp_df['concern_totals']==max(temp_df['concern_totals'])].to_dict(orient='records')
			return(max_product_for_category[0]) 

	def _update_basket_price(self,product_to_add):
		self.total_price += product_to_add['price']
		# self._update_basket_concerns(product_to_add)
		self.basket['basket_price'] = round(self.total_price,2)


	def add_first_products(self):
		#check only the products in categories that the user doesn't already have
		# for category in self.categories:
		# 	if category not in self.categories_own:
		# 		temp = [product for product in self.products if product['category'] == f'{category}']
		# 		temp_df = pd.DataFrame(temp)
		# 		temp_df.fillna(value=0,inplace=True)
		# 		#gets the poroduct with the highest value for all of the concerns the user picked
		# 		product_to_add = self._check_concern_totals(temp_df)
		# 		self.basket['products'].append(product_to_add)
		# 		self._update_basket_concerns(product_to_add)
		# 		self._update_basket_price(product_to_add)

		baskets =  list(itertools.product(moisturizers, serums, cleansers))
	    basket_dictionary = {}

	    '''scales to any number of concerns the user chooses. Adds up total for each concern for each basket
	        and appends to final list that comtains each basket as an element'''
	    combo_idx = 0
	    basket_count = 0

	    for combination in baskets:
	        basket_price = get_basket_price(combination)
	        basket_concerns = get_basket_concerns(combination, concerns)

	        if all(i >= .9 for i in basket_concerns.values()):
	            temp_basket = {}
	            temp_basket['products'] = baskets[combo_idx]
	            temp_basket['basket_concerns'] = basket_concerns
	            temp_basket['price'] = round(basket_price,2)
	            basket_dictionary[basket_count] = temp_basket
	            basket_count += 1
	        elif all(i >= .7 for i in basket_concerns.values()):
	            temp_basket = {}
	            temp_basket['products'] = baskets[combo_idx]
	            temp_basket['basket_concerns'] = basket_concerns
	            temp_basket['price'] = round(basket_price,2)
	            basket_dictionary[basket_count] = temp_basket
	            basket_count += 1
	        elif any(i >= .9 for i in basket_concerns.values()):
	            temp_basket = {}
	            temp_basket['products'] = baskets[combo_idx]
	            temp_basket['basket_concerns'] = basket_concerns
	            temp_basket['price'] = round(basket_price,2)
	            basket_dictionary[basket_count] = temp_basket
	            basket_count += 1
	        elif any(i >= .7 for i in basket_concerns.values()):
	            temp_basket = {}
	            temp_basket['products'] = baskets[combo_idx]
	            temp_basket['basket_concerns'] = basket_concerns
	            temp_basket['price'] = round(basket_price,2)
	            basket_dictionary[basket_count] = temp_basket
	            basket_count += 1
	        else:
	            temp_basket = {}
	            temp_basket['products'] = baskets[combo_idx]
	            temp_basket['basket_concerns'] = basket_concerns
	            temp_basket['price'] = round(basket_price,2)
	            basket_dictionary[basket_count] = temp_basket
	            basket_count += 1
	        combo_idx += 1
	    return(basket_dictionary, moisturizers, serums, cleansers)


	def new_basket(self,concerns,total_products,categories_own=[]):
		self.categories_own = categories_own
		self.total_price = 0
		self.basket = {'basket_concerns':{},'basket_price':0,'products':[]}
		self.concerns = concerns
		self.products = total_products

		for concern in self.concerns:
			self.basket['basket_concerns'][concern] = 0

		self.add_first_products()

	def empty_basket(self, concerns):
		self.concerns = concerns
		self.total_price = 0
		self.basket = {'basket_concerns':{},'basket_price':0,'products':[]}
		for concern in self.concerns:
			self.basket['basket_concerns'][concern] = 0
		print('empty basket = ',self.basket)	


	def add_product(self,product_to_add, concerns, basket):
		self.basket = basket
		self.concerns = concerns
		print('concerns in add product = ', self.concerns)

		self.basket['products'].append(product_to_add)
		# self._update_basket_price(product_to_add)
		self.basket['basket_price'] = round(self.total_price,2)

		print(product_to_add)
		for concern in self.concerns:
			self.basket['basket_concerns'][concern] += round(product_to_add[concern],2)

	def delete_product(self,product, concerns, basket):
		self.basket = basket
		self.concerns = concerns
		print('concerns in delete product = ', self.concerns)

		for idx, product_to_del in enumerate (self.basket['products']):
			if product == product_to_del:
				del self.basket['products'][idx]

		self.total_price -= product['price']
		self.basket['basket_price'] = round(self.total_price,2)
		for concern in self.concerns:
			self.basket['basket_concerns'][concern] -= round(product[concern],2)


	def _update_basket_concerns(self,product):
		print('self.basket = ',self.basket)
		for concern in self.concerns:
			self.basket['basket_concerns'][concern] += round(product[concern],2)

	def get_basket(self):
		return(self.basket)












# 	def create_basket(self,concerns):
# 		self.concerns = concerns
# 		for concern in self.concerns:
# 			self.basket['basket_concerns'][concern] = 0

# 	def new_basket(self):
# 		self.basket = {'basket_concerns':{},'price':0,'products':[]}


# 	def add_product(self,product):
# 		self.basket['products'].append(product)
# 		self.total_price += product['price']
# 		self._update_concerns(product)
# 		self.basket['price'] = round(self.total_price,2)

# 	def delete_product(self,product):
# 		products = self.basket['products']
# 		products.remove(product)
# 		self.total_price -= product['price']
# 		self.basket['products'] = products
# 		self.basket['price'] = self.total_price

# 	def _update_concerns(self,product):
# 		for concern in self.concerns:
# #			self.basket['basket_concerns'][concern] = 0
# #			for product in self.basket['products']:
# 			self.basket['basket_concerns'][concern] += product[concern]

# 	def get_basket(self):
# 		return(self.basket)






		
