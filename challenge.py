import urllib2
import json
import pprint

pages = {}
product_variants = {}

# you can change this to solve the problem for any product types - you can
# even try it with more than 2 product types!
product_types = ['Computer', 'Keyboard']

# # ========================================================= # #

# pull all the data from the API into JSON objects, one object for each page

for i in xrange(5):
	response = urllib2.urlopen('http://shopicruit.myshopify.com/products.json?page={}'.format(i+1))
	pages[i+1] = json.loads(response.read())

# # ========================================================= # #

# goes through all the pages we just downloaded and returns a list of every
# single product (including all its variants) of the given type

# here we change the format into a nicer format. each product of the type we
# care about is represented as a tuple:

# (title, variant title, cost in $, mass in grams)

# and a list of these tuples is returned.

def get_all_variants(product_type):
	output = []
	for page in pages:
		for product in pages[page]['products']:
			if product['product_type'] == product_type:
				output.extend(map(lambda x: (product['title'], x['title'], x['price'], x['grams']),product['variants']))
	return output

# # ========================================================= # #

# goes through a list of product variants and returns the cheapest one

def get_cheapest_variant(variant_list):
	min_cost = None
	cheapest_variant = None
	for variant in variant_list:
		if not min_cost or float(variant[2]) < min_cost:
			min_cost = float(variant[2])
			cheapest_variant = variant
	return cheapest_variant

# # ========================================================= # #

# recursive function that finds cheapest possible sets of unused products.
# this function is the workhorse of the script.

# set_list is an accumulator, slowly building up the list of sets (in this
# case, computer-keyboard pairs). as we build this accumulator, the
# product_variants dict's values slowly shrink as we remove item types.

# essentially we loop through all the products of the given types, find the
# cheapest item of each product type, and add it to the set. at the same time
# as we add the cheapest item to the set, we remove it from the product list
# (to ensure we don't take duplicate items).

# we then recursively call the function (with our
# updated product list) to find the next cheapest item set,
# continuing until there is a product with no items left (meaning we can
# no longer create more sets without duplicates) and then terminate.

def build_sets_helper(product_variants, set_list):

	for product_type in product_variants:
		if not product_variants[product_type]:
			return set_list

	current_set = []

	for product_type in product_variants:
		cheapest_item = get_cheapest_variant(product_variants[product_type])
		current_set.append(cheapest_item)
		product_variants[product_type].remove(cheapest_item)

	set_list.append(current_set)

	return build_sets_helper(product_variants, set_list)

# wrapper to avoid having to pass an empty list to initialize the accumulator

def build_sets(product_variants):
	return build_sets_helper(product_variants, [])

# # ========================================================= # #

# first, we use get_all_variants to get all the items we care about from the API

for product_type in product_types:
	product_variants[product_type] = get_all_variants(product_type)

# we call build_sets to find the cheapest computer-keyboard pairs satisfying
# the requirements

product_sets = build_sets(product_variants)

# now we just find the total cost and mass of the sets we chose

total_cost = 0
total_mass = 0

for product_set in product_sets:
	for product in product_set:
		total_cost += float(product[2])
		total_mass += float(product[3])

# # ========================================================= # #

print 'Here\'s all the sets Alice should buy:\n'
pprint.pprint(product_sets)
print '\nTotal number of items is {}.'.format(len(product_sets))
print 'Total cost is ${}.'.format(total_cost)
print 'Total mass is {} grams. ({} kilograms.)'.format(total_mass, total_mass/1000)
