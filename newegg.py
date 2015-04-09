__author__ = 'georgeventura'

import requests
import json


class Newegg(object):

    def __init__(self):
        self.url = 'http://www.ows.newegg.com'
        self.session = requests.Session()
        self.headers = {'User-Agent': 'Newegg iPhone App / 4.4.0'}
        self.path = []
        self.sub_category = []
        self.product_list = []
        self.end = 0

    # Retrieves main categories, returns JSON object
    def _get_main_cat(self):
        try:
            url_suffix = '/Stores.egg/ShopAllNavigation'
            response = requests.get(self.url + url_suffix, headers=self.headers)
            response = json.loads(response.content)

            return response
        except:
            print "error"

    def walker(self, path):
        #   Split path directory ex: [Computer Hardware/Memory]
        category = path.split('/')
        #   Subtract 1 since we use get_stores() to go up 1 level
        levels = len(category)-1
        count = 0
        stores = self._get_main_cat()
        target = []
        while count < levels:
            for store in stores:
                #   Cycle through store categories until we get a match
                if store['Description'] == category[count]:
                    parameters = ""
                    for key, value in store.iteritems():
                        #   Concatenate GET request parameters
                        parameters += key + '=' + str(value) + '&'
                    try:
                        url_suffix = '/Stores.egg/StoreNavigation?'
                        child_stores = requests.get(self.url +
                                                    url_suffix +
                                                    parameters,
                                                    headers=self.headers)
                        count += 1
                        stores = json.loads(child_stores.content)[0]
                        stores = stores['NavigationItemList']
                        target = store
                        if count == levels:
                            self.sub_category = stores
                        for sub_category in stores:
                            if sub_category['Description'] == category[count]:
                                # check to see if this is end category (-1 are subcategories)
                                if int(sub_category['SubCategoryId']) != -1:
                                    self.end = 1
                                    print sub_category['Description'] + ' ' + \
                                       'end directory'
                                    self.query(sub_category)
                                    return
                        #if target[]
                        self.end = 0
                        break
                        stores = json.loads(child_stores.content)
                        print stores
                    except:
                        print "error getting child"

        '''for tag in target:
            print tag['Description']'''

    #   Retreives product item list in the queried category
    def query(self, category):

        # POST data for query
        store_id = category['StoreId']
        sub_category_id = category['SubCategoryId']
        node_id = category['NodeId']
        category_id = category['CategoryId']
        store_type = category['StoreType']
        n_value = category['NValue']
        brand_id = category['BrandId']
        page_number = category['CategoryId']

        response = self.query_list(store_id, sub_category_id, node_id,
                                   category_id, store_type, n_value,
                                   brand_id, page_number)

        if response.status_code == 200:
            None
        print response
        self.reterive_products(response)

    def get_pretty_product_details(self, product):
        return {'Item': product['Title'],
                'inStock': product['Instock'],
                'FinalPrice': product['FinalPrice'],
                'isFreeShipping': product['IsFreeShipping'],
                'ItemNumber': product['ItemNumber'],
                'TotalReviews': (product['ReviewSummary'])['TotalReviews'],
                'ShippingText': product['ShippingText']}


    # organize data to a more usable form
    def reterive_products(self, response):
        item_list = json.loads(response.content)
        item_list = item_list['ProductGroups']
        item_list = (item_list[0])['ProductDeals']
        self.product_list = item_list

    # Parse to get selected product by it's ItemNumber and return
    # product details. In JSON format.
    def get_product_details(self, item_number):
        if len(self.product_list) != 0:
            for product in self.product_list:
                if item_number == product['ItemNumber']:
                    return self.get_pretty_product_details(product)

    # Gets list of products in specified category.
    # SubCategoryId is unique variable which differentiates
    # between product categories.
    def query_list(self, store_id, sub_category_id, node_id, category_id,
                   store_type, n_value, brand_id, page_number):
        payload = {
                  "InnerKeyWord": "",
                  "MinPrice": "",
                  "StoreId": store_id,
                  "Sort": "FEATURED",
                  "SearchProperties": [],
                  "BrandList": [],
                  "SubCategoryId": sub_category_id,
                  "NodeId": node_id,
                  "CategoryId": category_id,
                  "ProductType": [],
                  "KeyWord": "",
                  "StoreType": store_type,
                  "NValue": str(n_value),
                  "BrandId": brand_id,
                  "MaxPrice": "",
                  "PageNumber": page_number,
                  "ModuleParams": ""
                }

        try:
            suffix_url = '/Search.egg/Query'
            return requests.post(self.url + suffix_url,
                                data=json.dumps(payload), headers=self.headers)

        except:
            print 'error getting items'

    def print_req_category(self):
        if self.end == 0:
            if len(self.sub_category) != 0:
                for category in self.sub_category:
                    print category['Description']
        elif self.end == 1:
            if len(self.product_list) != 0:
                for product in self.product_list:
                    print product['ItemNumber'] + ' - ' + product['Title']

    def get_storeId(self, store_name):
        for store in self._get_main_cat():
            if store['Description'] == store_name:
                print store['StoreId']

newegg = Newegg()

print newegg._get_main_cat()
newegg.walker('Computer Hardware/Computer Cases/')
newegg.print_req_category()
#details = newegg.get_product_details(raw_input('Select Item Using product id:'))
#print json.dumps(details, indent=4, sort_keys=True)
#print details
#newegg.print_product_list()

