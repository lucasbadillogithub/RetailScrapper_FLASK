from flask import Flask, render_template, request, flash
from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
from pathlib import Path 
import os
from datetime import date
import time


class Exito:
    def __init__(self,search_term):
        self.search_term = search_term
        self.today = date.today()
        self.page = 1
        self.i=0
        self.headers = {
             "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
             "Accept-Encoding":"gzip, deflate, br",
             "Accept-Language":"en-US,en;q=0.5",
             "Connection":"keep-alive",
             "Host":"www.exito.com",
             "Sec-Fetch-Dest":"document",
             "Sec-Fetch-Mode":"navigate",
             "Sec-Fetch-Site":"cross-site",
             "Upgrade-Insecure-Requests":"1",
             "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0"
         }
        
    
    def set_url(self):
        return f'https://www.exito.com/{self.search_term}?_q={self.search_term}&map=ft&page={self.page}&__pickRuntime=appsEtag%2CqueryData%2Csettings&__device=desktop'
    
    def make_request(self):
        url = self.set_url()
        return requests.request("GET",url,headers=self.headers)
    
    def get_data(self):
        self.data = self.make_request().json()
        
    def save_path(self): # ,name
        filepath = Path(f'search/img/create.jpg')  
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath = Path(f'search/{self.search_term}/{self.today}/csv/{self.search_term}-{self.today}.csv')  
        filepath.parent.mkdir(parents=True, exist_ok=True)  
                
    def download(self,url,imageId,itemId):
        filepath = self.save_path()
        with open(f'search/img/{itemId}-{imageId}.jpg',"wb") as f:
            f.write(requests.request(method="GET",url=url,headers=self.headers).content)
            
        
            
    def Scrapper(self, items=21):
        products_list = []
        sellers_list = []
        seller_conditions_list = []
        seller_effects_list = []
        item_categoria = []
        items_matched = items
        pages_matched = 200
        i = 0
        exit = False
        while exit == False:
            try:
                url = self.set_url()
                self.page += 1
                get_request = self.make_request()
                self.get_data()
                data_dict = json.loads(self.data['queryData'][0]['data'])
                products = data_dict['productSearch']['products']            
                for item in products:
                    len_categorie = len(item.get('categories'))
                    multiplicator = 5 - len_categorie
                    complementList = ['//']*multiplicator 
                    item_categoria =   item.get('categories')
                    item_categoria.reverse()
                    item_categoria.extend(complementList)
                    imageId = item.get('items')[0].get('images')[0].get('imageId')
                    itemId =  item['items'][0]['itemId']
                    imageUrl = item.get('items')[0].get('images')[0].get('imageUrl')
                    base_list=[(item.get('cacheId'))
                               ,self.today 
                               ,self.search_term
                               ,self.page
                               ,i
                               ,(item.get('productReference') )
                               ,(item.get('brand') )
                               ,item['priceRange']['listPrice']['highPrice']
                               ,(item['items'][0]['itemId'])
                               ,(item['items'][0]['name'])
                               ,(item['items'][0]['nameComplete'])
                               ,(item['items'][0]['complementName'])
                               ,(item['items'][0]['ean'])
                               ,(item['items'][0]['measurementUnit'])
                               ,(item.get('items')[0].get('unitMultiplier'))
                               ,(len(item.get('categories')) ) 
                               ,item.get('categories') # item_categoria[0]
                               ,(item.get('items')[0].get('images')[0].get('imageId'))
                               ,(imageUrl)
                              ]


                    filepath = Path(f'search/img/{itemId}-{imageId}.jpg')  
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    with open(f'search/img/{itemId}-{imageId}.jpg',"wb") as f:
                        f.write(requests.get(imageUrl).content)

                    products_list.append(base_list)
                    
                    s = 0
                    ## SELLER
                    sellers = item.get('items')[0].get('sellers')
                    for seller in sellers:
                        base_list_seller = [(itemId)
                                            ,seller.get('sellerId')
                                            ,seller.get('sellerName')
                                            ,seller.get('commertialOffer').get('Price')      
                                            ,seller.get('commertialOffer').get('ListPrice')  
                                            ,seller.get('commertialOffer').get('spotPrice')  
                                            ,seller.get('commertialOffer').get('PriceWithoutDiscount')  
                                          ] 

                        s+=1
                        sellers_list.append(base_list_seller)

                        t = 0
                        ## Teaser
                        teasers = seller.get('commertialOffer').get('teasers')
                        for teaser in teasers:
                            e =0
                            ### Effects Parameters
                            effectsParameters = teaser.get('effects').get('parameters')
                            for effectParamter in effectsParameters:
                                base_list_teaser_effect_par = [itemId
                                                               ,seller.get('sellerId')    
                                                               ,teaser.get('name')
                                                               ,effectParamter.get('name')  
                                                               ,effectParamter.get('value')  
                                                              ]

                                # Store seller in external list
                                seller_effects_list.append(base_list_teaser_effect_par)
                                
                                e+=1


                            c = 0
                            ### conditions parameters here we find list or restricted bins name = 'RestrictionsBins'
                            parameters = teaser.get('conditions').get('parameters')
                            for parameter in parameters:
                                base_list_teaser_condition_par = [itemId
                                                                   ,seller.get('sellerId')    
                                                                   ,teaser.get('name')
                                                                   ,parameter.get('name')
                                                                   ,parameter.get('value')
                                                                  ]

                                seller_conditions_list.append(base_list_teaser_condition_par) # Store in external list

                                c+=1


                            t+=1

                    if i == items_matched:
                        print('reach ITEMS limit!')
                        exit = True
                        break
                    i += 1

                if self.page == pages_matched:
                    exit = True
                    print('reach PAGE limit!')
                    break

                time.sleep(5)

            except:
                exit =True
                print('Error!')

        ##--0ut of while sentences--------------------- STORE DATA ------------------------------------------
        # Columns name
        products_columns = ['cacheId'
                            ,'execution_date'
                            ,'search_term'
                            ,'page'
                            ,'i'
                            ,'productReference'
                            ,'brand'
                            ,'base_price'
                            ,'itemId'
                            ,'name'
                            ,'nameComplete'
                            ,'complementName'
                            ,'EAN'
                            ,'measurementUnit'
                            ,'unitMultiplier'
                            ,'len_categorie'
                            ,'categorie'
                            ,'imageId'
                            ,'imageUrl'
                           ]
        products_df = pd.DataFrame(products_list, columns =products_columns)


        sellers_columns = ['itemId'
                            ,'sellerId'
                            ,'sellerName'
                            ,'Price'
                            ,'ListPrice'
                            ,'spotPrice'
                            ,'PriceWithoutDiscount'
                         ]
        sellers_df = pd.DataFrame(sellers_list, columns = sellers_columns)

        seller_effects_columns = ['itemId'
                                    ,'sellerId'
                                    ,'teaser_name'
                                    ,'effects_name'
                                    ,'effects_value'
                                 ]

        seller_effects_df = pd.DataFrame(seller_effects_list, columns = seller_effects_columns)

        seller_conditions_columns = ['itemId'
                                     ,'sellerId'
                                     ,'teaser_name'
                                    ,'condition_name'
                                    ,'condition_value'
                                    ]

        seller_conditions_df = pd.DataFrame(seller_conditions_list, columns = seller_conditions_columns)

        print('Success!')

        ### Store Data Frame into CSV
        to_csv = ['products_df','sellers_df','seller_effects_df','seller_conditions_df']

        for file in to_csv:
            filepath = Path(f'search/{self.search_term}/{self.today}/csv/{self.search_term}-{self.today}-{file}.csv')  
            filepath.parent.mkdir(parents=True, exist_ok=True)  
            code = f"{file}.to_csv(filepath, sep ='\t')"
            exec(code)

        self.i = i
        print('items: '+str(i) + '| pages: '+ str(self.page))
        return self.i


app = Flask(__name__)
app.secret_key = "manbearpig_MUDMAN888"

@app.route("/hello")
def index():
    flash("looking for something?")
    return render_template("index.html")

@app.route("/search", methods=["POST","GET"])
def search():
    num_matches = request.form['num_matches']
    scrapper = Exito(str(request.form['search_term']))
    products = scrapper.Scrapper(int(num_matches))  
    flash(str(request.form['search_term']) + " fetched " + str(products) + "from "+str(request.form['num_matches']) )
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)