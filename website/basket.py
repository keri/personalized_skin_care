import pandas as pd 



'''Class that creates new basket, adds to basket, updates basket price and concerns
 	input: budget, list of concerns
    output: basket = dictionary
                    {basket_concerns:{concern1:basket_total(float8)
                                     concern2:basket_total(floate8)
                                     etc},
                     products:list of product dictionary in basket[
                            {concern1:product_total(double precision),
                             concern2:product_total(double precision),
                             etc,
                             asin:text,
                             title:text,
                             imageurl:text,
                             price:double precision,
                             category:text,
                             concern_totals:double precision}]
                     basket_price:double precision}
                             
                             '''

class Basket(object):
	def __init__(self):
		self.basket = {'basket_concerns':{},'basket_price':0,'products':[]}
		self.total_price = 0
		self.concerns =[]
		self.products = []
		self.categories = ['moisturizer','serum','cleanser']
		#self.categories_own = []


	def get_products_in_each_category(self):

		moisturizers = [result for result in self.products if result['category'] == 'moisturizer']
		cleansers = [result for result in self.products if result['category'] == 'cleanser']
		serums = [result for result in self.products if result['category'] == 'serum']
		
		product_categories = {'moisturizer': moisturizers, 'cleanser': cleansers, 'serum' : serums}

		return(product_categories)


	def _get_max_concern_totals(self,temp_df):
		#gets a concern total for each product
		temp_df['concern_totals'] = 0
		for concern in self.concerns:
			temp_df['concern_totals'] = temp_df['concern_totals'].add(temp_df[concern])

		#update the product list with top products that have total concerns over .5
		mask = temp_df['concern_totals'] > .3
		products_over_threshold = temp_df[mask]
		if products_over_threshold.shape[0] < 20: 
			top_products = products_over_threshold.sort_values('concern_totals', ascending=False)
		else:
			top_products = products_over_threshold.sort_values('concern_totals', ascending=False)[:20]

		self.products.extend(top_products.to_dict(orient='records'))

		#getting top 5 and picking randomly
		top_5 = temp_df.sort_values('concern_totals', ascending=False)[:5]
		max_product_for_category = top_5.sample(1).to_dict(orient='records')#returns a list with one value
		return(max_product_for_category[0]) 

	def _update_basket_price(self,product_to_add):
		self.total_price += product_to_add['price']
		# self._update_basket_concerns(product_to_add)
		self.basket['basket_price'] = round(self.total_price,2)

	def create_top_bottom_confidence_dataframe(self,temp):
		top_20 = temp.sort_values('confidence', ascending=False)[:30]
		bottom_rest = temp.sort_values('confidence', ascending=True)[:30]
		random_top = top_20.sample(20)
		random_bottom = bottom_rest.sample(20)
		return(pd.concat([random_top, random_bottom]))


	def add_first_products(self, total_products):
		#check only the products in categories that the user doesn't already have
		for category in self.categories:
			# if category not in self.categories_own:
			temp = [product for product in total_products if product['category'] == f'{category}']
			temp_df = pd.DataFrame(temp)
			temp_df.fillna(value=0,inplace=True)
			bottom_top_df = self.create_top_bottom_confidence_dataframe(temp_df)
			product_to_add = self._get_max_concern_totals(bottom_top_df)
			self.basket['products'].append(product_to_add)
			self._update_basket_concerns(product_to_add)
			self._update_basket_price(product_to_add)


	def new_basket(self,concerns,total_products):
		#self.categories_own = categories_own
		self.total_price = 0
		self.basket = {'basket_concerns':{},'basket_price':0,'products':[]}
		self.concerns = concerns
		#self.products = total_products

		for concern in self.concerns:
			self.basket['basket_concerns'][concern] = 0

		self.add_first_products(total_products)

	def empty_basket(self, concerns):
		self.concerns = concerns
		self.total_price = 0
		self.basket = {'basket_concerns':{},'basket_price':0,'products':[]}
		for concern in self.concerns:
			self.basket['basket_concerns'][concern] = 0


	def add_product(self,product_to_add, concerns, basket):
		self.basket = basket
		self.concerns = concerns

		self.basket['products'].append(product_to_add)
		# self._update_basket_price(product_to_add)
		self.basket['basket_price'] = round(self.total_price,2)
		for concern in self.concerns:
			self.basket['basket_concerns'][concern] += round(product_to_add[concern],2)

	def delete_product(self,product, concerns, basket):
		self.basket = basket
		self.concerns = concerns

		for idx, product_to_del in enumerate (self.basket['products']):
			if product == product_to_del:
				del self.basket['products'][idx]

		self.total_price -= product['price']
		self.basket['basket_price'] = round(self.total_price,2)
		for concern in self.concerns:
			self.basket['basket_concerns'][concern] -= round(product[concern],2)


	def _update_basket_concerns(self,product):
		# print('self.basket = ',self.basket.encode('utf-8'))
		for concern in self.concerns:
			self.basket['basket_concerns'][concern] += round(product[concern],2)

	def get_basket(self):
		return(self.basket)








		
