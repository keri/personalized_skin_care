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
		self.basket = {'basket_concerns':{},'price':0,'products':[]}
		self.total_price = 0
		self.concerns = []

	def create_basket(self,concerns):
		self.concerns = concerns
		for concern in self.concerns:
			self.basket['basket_concerns'][concern] = 0

	def new_basket(self):
		self.basket = {'basket_concerns':{},'price':0,'products':[]}


	def add_product(self,product):
		self.basket['products'].append(product)
		self.total_price += product['price']
		self._update_concerns(product)
		self.basket['price'] = round(self.total_price,2)

	def delete_product(self,product):
		products = self.basket['products']
		products.remove(product)
		self.total_price -= product['price']
		self.basket['products'] = products
		self.basket['price'] = self.total_price

	def _update_concerns(self,product):
		for concern in self.concerns:
#			self.basket['basket_concerns'][concern] = 0
#			for product in self.basket['products']:
			self.basket['basket_concerns'][concern] += product[concern]

	def get_basket(self):
		return(self.basket)






		
