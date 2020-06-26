from django.db import models
from decimal import Decimal
from pprint import pprint

from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.template.defaultfilters import slugify
from rest_framework.authtoken.models import Token
from django.utils.crypto import get_random_string
import collections
from bs4 import BeautifulSoup 
import json
from celery import shared_task


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"



class MongoClass:
    connection = {}
    @staticmethod
    def connect_to_mongodb():
        import pymongo
        from pymongo import MongoClient
        print('connection obj is ',MongoClass.connection)
        if not MongoClass.connection:
            MongoClass.connection = MongoClient('mongodb://mongoadmin:Mongoadmin_123#@localhost:27017/just_books?authSource=admin', 27017)
        
        db = MongoClass.connection.just_books
        return db

    def mongo_connect(table_name):
        
        db = MongoClass.connect_to_mongodb()

        database_table = 'api_' + table_name

        data = db[database_table]

        response = data.find()
        
        row = []

        for item in response:
            del item['_id']
            row.append(item)

        
        return row

    def latestActiveBatch(table_name):
        db = MongoClass.connect_to_mongodb()
        database_table = 'api_' + table_name
        data = db[database_table]
        response = data.find({'status':True}).sort('updated',-1)
        row = []
        for item in response:
            del item['_id']
            row.append(item)
        return row

    def update_collection_using_id(table_name,id_,data_to_update):
        db = MongoClass.connect_to_mongodb()
        print(db)
        database_table = 'api_' + table_name

        data = db[database_table]

        response = data.update({'id':id_},{'$set':data_to_update})
        row = []

        # for item in response:
        #     del item['_id']
        #     row.append(item)
        

        return response

    def mongo_connect_get_data_table(table_name,bid):
       
        db = MongoClass.connect_to_mongodb()
        print(db)
        database_table = 'api_' + table_name

        data = db[database_table]

        # print(bid)
        batch_id = int(bid)
        response = data.find({'batch_id':batch_id})
        
        row = []

        for item in response:
            del item['_id']
            # print(item)
            row.append(item)

        return row

    def mongo_api_schema(table_name):
        db = MongoClass.connect_to_mongodb()
        

        database_table = '__schema__' 


        data = db[database_table]
        print(data)
        print(table_name)
        response = data.find({'name':table_name})
        print(response)
        row = []

        for item in response:
            del item['_id']
            # print(item)
            row.append(item)

        return row


    def get_data_with_sku(table_name, sku):
        db = MongoClass.connect_to_mongodb()
        
        database_table = 'api_' + table_name

        data = db[database_table]

        response = data.find({'sku':sku})
        
        row = []

        for item in response:
            del item['_id']
            row.append(item)

        return row

    def get_data_batchproduct(table_name,batch_id):
        db = MongoClass.connect_to_mongodb()
     
        database_table = 'api_' + table_name

        data = db[database_table]

        response = data.find({'batch_id':int(batch_id)})
        print('response')
        # pprint(response)
        row = []

        for item in response:
            del item['_id']
            # print(item)
            row.append(item)

        return row


    def get_data_with_conditions_having_list(table_name,listofid,search_for):
        db = MongoClass.connect_to_mongodb()
        

        database_table = 'api_' + table_name

        data = db[database_table]
        
        response = data.find({search_for:{ '$in': listofid } } )
        print('response')
        pprint(response)
        row = []

        for item in response:
            del item['_id']
            # print(item)
            row.append(item)

        return row

    def get_data_(table_name,bpid):
        db = MongoClass.connect_to_mongodb()
        database_table = 'api_' + table_name

        data = db[database_table]
        
        response = data.find({"id":int(bpid)},{'amazon':1,'sku':1,'imageUrl':1,'goodreads':1,'publisher':1,
            'description':1,'author':1})
        print('response')
        # pprint(response)
        row = []

        for item in response:
            del item['_id']
            # print(item)
            row.append(item)

        return row

    # def get_poproduct_data_(table_name,po_id,flag,branch):
    def get_poproduct_data_(table_name,po_id):
        db = MongoClass.connect_to_mongodb()
        database_table = 'api_' + table_name

        data = db[database_table]
        queryObj = {}
        queryObj['po_id'] = int(po_id)

        # //flag is 1 if it is for admin login
        # if flag is not '1':
        #     queryObj['branch'] = int(branch)
        
        print(queryObj)

        response = data.aggregate([
                    {
                        '$match':queryObj
                    },
                    {
                        '$lookup':{
                            'from':'api_retail',
                            'let':{
                                'branch':'$branch'
                            },
                            'pipeline':[
                                {
                                    '$match':
                                    {
                                        '$expr':
                                            {'$eq':['$branch','$$branch']},
                                         
                                    }
                                     
                                }
                            ],
                            'as':'branches'
                        }
                    },
                    
                    {
                        '$project': {
                            "sku":1,
                            "name":1,
                            "mrp":1,
                            "qty":1,
                            "branch":1,
                            "id":1,
                            "created":1,
                            "batch_id":1,
                            "branches.name":1,
                            "branches.id":1,
                            "branches.branch":1
                        }
                    }   
                ])
        print('response')
        # pprint(response)
        row = []

        for item in response:
            del item['_id']
            # print(item)
            row.append(item)

        return row



    def get_data_with_conditions_having_list_and_id(table_name,listofid,search_for,id):
        
        db = MongoClass.connect_to_mongodb()

        database_table = 'api_' + table_name

        data = db[database_table]
        
        response = data.find({search_for:{ '$in': listofid },"po_id":id} )
        print('response')
        pprint(response)
        row = []

        for item in response:
            del item['_id']
            # print(item)
            row.append(item)

        return row    

    def searchingInArrayField(table_name,dataToSearch):
        
        db = MongoClass.connect_to_mongodb()
    
        database_table = 'api_' + table_name
       
        data = db[database_table]
        b_id = int(dataToSearch)

        # response = data.find({'branch_list':{'$elemMatch':{'$eq':b_id}}})
        response = data.aggregate([
                    {
                        '$match':{'branch_list':{'$elemMatch':{'$eq':b_id}}}
                    },
                    {
                        '$lookup':{
                            'from':'api_batch',
                            'let':{
                                'id':'$batch_id'
                            },
                            'pipeline':[
                                {
                                    '$match':
                                    {
                                        '$expr':
                                            {'$eq':['$id','$$id']},
                                    }
                                }
                            ],
                            'as':'batch'
                        }
                    },
                    
                    {
                        '$lookup':{
                            'from':'api_po_product',
                            'let':{
                                'po_id':'$id',
                                'branch':b_id
                            },
                            'pipeline':[
                                {
                                    '$match':
                                    {
                                        '$expr':{
                                            '$and': [
                                                {'$eq':['$po_id','$$po_id']},
                                                {'$eq':['$branch',b_id]}
                                            ]
                                        }
                                    }
                                }
                            ],
                            'as':'po_pro'
                        }
                    },
                    {
                        '$unwind':'$batch'
                    },
                    {
                        '$unwind':'$po_pro'
                    },
                    {
                        
                        '$group':
                        {
                            '_id': {'po_id':'$po_pro.po_id'},
                            'qty': { '$sum': "$po_pro.qty" },
                            'count': { '$sum': 1 },
                            "batchName": { "$first": "$batch.name"},
                            "name":{"$first":"$name"},
                            "id":{"$first":"$id"}
                        }
             
                    }
        ])

        
        row = []

        for item in response:
            del item['_id']
            row.append(item)

        return row   

    def get_qty_ordered_initially_by_po(table_name,po_list,branch):
        db = MongoClass.connect_to_mongodb()
        database_table = 'api_' + table_name
        data = db[database_table]

        response = data.aggregate([
            {
                '$match':{'po_id':{'$in':po_list}}
            },
            {
                '$group':
                {
                    '_id': {'isCurrentBranch':{'$eq':['$branch',int(branch)]}},
                    'totalqty': { '$sum': "$qty" },
                    'count': { '$sum': 1 }
                }
            }
        ])


    def get_data_with_group_and_match(table_name,matchKey,matchValue,sku):
        db = MongoClass.connect_to_mongodb()

        database_table = 'api_' + table_name

        data = db[database_table]
        
        response = data.aggregate([
            {
                '$match':{
                    matchKey:matchValue,
                    "sku":sku
                }
            },
            {
                '$group':{
                    '_id':{
                        'isbn':"$sku"
                    },
                   'totalQty':{
                        '$sum':"$qty"
                    },
                    'sku': {
                        '$push': "$sku"
                    }
                }
            },
        ])
        row = []
        print('response')
        print(response)
        for item in response:
            print(item)
            del item['_id']
            # print(item)
            row.append(item)

        return row 
        
    def findAndModifyCollection(table_name,queryValue):
        db = MongoClass.connect_to_mongodb()
        database_table = 'api_' + table_name

        data = db[database_table]
        response = data.update(
            {
                'po_id':int(queryValue['po']),'branch':int(queryValue['branch']),'sku':queryValue['sku']
            },
            {
                '$inc':{'receivedqty': 1}
            }
        )
        row = []
        print('response')
        # print(response)
        # for item in response:
            # print(item)
            # del item['_id']
            # print(item)
            # row.append(item)

        return response



    def update_one_entry(table_name,queryParam,request):
        db = MongoClass.connect_to_mongodb()
        

        database_table = 'api_' + table_name

        data = db[database_table]
        # response = data.find(queryParam)
        response = data.update({
           
                "po_id":int(queryParam['po_id']),
                "sku":queryParam['sku'],
                "item_number":queryParam['item_number']
            },
            { 
            '$set':{
                'item_number':request['item'],
                'branch':request['branch'],
                'status':'In Dispatch'
            }
        }
    )
        print('response')
        pprint(response)
        row = []

        for item in response:
            # del item['_id']
            print(item)
            row.append(item)

        return row   

    def createBatchProductFromCsv(batch_pro_list,table_name,last_id):
        db = MongoClass.connect_to_mongodb()
        

        database_table = 'api_' + table_name

        data = db[database_table]
        # response = data.find(queryParam)
        response = data.insert_many(batch_pro_list)
        
        schema_data = db['__schema__']
        ress = schema_data.update({
            "name":"api_batchproduct"
        },{
            '$set':{
                'auto.seq':last_id
            }
        })
        print('response')
        print(response)
        row = []

        # for item in response:
            # del item['_id']
            # print(item)
            # row.append(item)

        return 'row' 

    def update_amazonrating_batch_product(table_name,queryParam):
        db = MongoClass.connect_to_mongodb()


        database_table = 'api_' + table_name

        data = db[database_table]
        response = data.update_many({
        
                "sku":queryParam['sku']
            },
            {
                '$set':{ 
                    'amazon':queryParam['amazon'],
                    'imageUrl':queryParam['image'],
                    'goodreads':queryParam['goodreads'],
                    'authorName':queryParam['author'],
                    'description':queryParam['description'],
                    'publisherName':queryParam['publisher']
                }
            }
        )
        print('response')
        pprint(response)

        return 'success'

    def update_goodreads_batch_product(table_name,listofsku):
        db = MongoClass.connect_to_mongodb()
        

        database_table = 'api_' + table_name

        data = db[database_table]
        
        for item in listofsku:
            
            response = data.update_many({'sku': item['sku'] },{
                '$set':
                { 
                    'goodreads':item['goodreads']
                }
            })
            print('response')
            pprint(response)
    

        # for item in response:
        #     del item['_id']
        #     # print(item)
        #     row.append(item)

        return 'success'

    def get_po_for_new_arrivals_using_batch(table_name,batch_id_list):
        db = MongoClass.connect_to_mongodb()
        database_table = 'api_' + table_name

        data = db[database_table]
        
        response = data.aggregate([
        {
            '$match' : {
                'batch_id':{'$in' : batch_id_list}
            }
        },
        {
            '$lookup':{
                'from': "api_retail",
                'localField': "vendor_id",
                'foreignField': "id",
                'as':"vendorDetails"
            }
        },
        {
            '$project': {
                "id":1,
                "qty":1,
                "created":1,
                "batch_id":1,
                "vendor_id":1,
                "name":1,
                "vendorDetails.name":1
            }
        }   

        ])
    
        row = []
        for item in response:
            del item['_id']
            # print(item)
            row.append(item)

        return row        

    def updateAllBranchReqProduct(table_name,branch_list,sku_list,newStatus):
        db = MongoClass.connect_to_mongodb()
        database_table_br_req = 'api_branch_request'
        dataN = db[database_table_br_req]
        br_req_response = dataN.find({'branch':{'$in':branch_list}})
        br_req_id = []
        for item in br_req_response:
            br_req_id.append(int(item['id']))

        print('branch List ',branch_list)
        print('branch List type',type(branch_list[0]))
        print('branch req ids are ', br_req_id)
        print('skus are ', sku_list)
        print('sku  type',type(sku_list[0]))

        database_table = 'api_'+ table_name
        data = db[database_table]
        response = data.update_many(
            {
                'branch_req_id':{'$in':br_req_id},
                'sku':{'$in':sku_list}
            },
            {
                '$set':{
                    'status':newStatus
                }
            })
        print(response)
        return response


    def updateAllBranchReqProUsingPoId(table_name,po_id,sku_list,newStatus):
        db = MongoClass.connect_to_mongodb()
        po_database_table = 'api_po'
        po_data = db[po_database_table]
        po_response = po_data.find({'id':int(po_id)},{'batch_id':1,'_id':0})
        print(po_response)
        batch_id = ''
        for item in po_response:
            batch_id = item['batch_id']
    
        database_table = 'api_'+ table_name
        data = db[database_table]
        response = data.update_many(
            {
                'batch_id':int(batch_id),
                'sku':{'$in':sku_list}
            },
            {
                '$set':{
                    'status':newStatus
                }
            })
        print(response)
        return response

    def get_batch_products_for_placeorder(table_name, batch_id, branch_request_id):
        
        db = MongoClass.connect_to_mongodb()


        database_table = 'api_' + table_name

        data = db[database_table]

        response = data.aggregate([
                    {
                        '$match':{
                            'batch_id':int(batch_id)
                        }
                    },
                    {
                        '$lookup':{
                            'from':'api_branch_request_product',
                            'let':{
                                'sku':'$sku',
                                'batch_id':'$batch_id'
                            },
                            'pipeline':[
                                {
                                    '$match':
                                    {
                                        '$expr':
                                        {
                                            '$and':[
                                                {'$eq':['$sku','$$sku']},
                                                {'$eq':['$batch_id',int(batch_id)]},
                                                {'$eq':['$branch_req_id',int(branch_request_id)]}
                                            ]
                                            
                                        }
                                    }
                                     
                                }
                            ],
                            'as':'ordersPlaced'
                        }
                    },
                    
                    {
                        '$project': {
                            "sku":1,
                            "author":1,
                            "name":1,
                            "mrp":1,
                            "discount":1,
                            "category":1,
                            "batch_id":1,
                            "id":1,
                            "ordersPlaced.sku":1,
                            "ordersPlaced.batch_id":1,
                            "ordersPlaced.qty":1,
                            "ordersPlaced.id":1
                        }
                    }   
                ])
        
        row = []
        for item in response:
            del item['_id']
            # print(item)
            row.append(item)

        return row



class CollectionsMethod:
    
    def CountFrequency(arr):
        return collections.Counter(arr)  

    @staticmethod
    def amt2words(amount, currency='rupee', change='paise', precision=2):
        from num2words import num2words
        print(type(amount))
        change_amt_ =  (amount - int(amount))
        change_amt = round(change_amt_,2)
        words = '{main_amt} {main_word}'.format(
            main_amt=num2words(int(amount)),
            main_word=currency,
        )
        if change_amt > 0:
            words += ' and {change_amt} {change_word}'.format(
            change_amt=num2words(change_amt),
            change_word=change,
        )
        return words

class ScrapeDataFromAmazon:
    
    def __init__(self):
        import pymongo
        from pymongo import MongoClient
        with open('config.json', 'r') as fp:
            self.config_dct = json.load(fp)
            try:
                self.client = MongoClient('101.53.137.161', 27017)
                print('connected to mongodb')
            except Exception as e:
                print('exception occured while connecting to database',e)

    def crawler(self,url,sku):
        import requests
        import json
        import re
        result = {}
        # print(self.config_dct["target_url"])

        try:
            req = requests.get(url)
            print(req.text)
            soup = BeautifulSoup(req.text, 'lxml')

            # anchors = soup.find_all('img')
            imge = soup.find("div",{"class":"a-column a-span12 a-text-center"})
            ratingDiv = soup.find("div", {"class":"a-column a-span5 a-span-last"})
            # print('image is')
            imageUrl = imge.find('img').get('src')
            # print(imageUrl)
            amazonRating = ratingDiv.find('span',{"class":"a-icon-alt"}).text
                
            # print(amazonRating)
            result['status'] = True
            result['ISBN'] = sku
            result['image'] = imageUrl
            result['Amazon Rating'] = amazonRating

        except Exception as e:
            print('Exception in crawler for crawling: ', e)
            result['status'] = False
            result['ISBN'] = sku
            result['Amazon Rating'] = 'Not Available'
            result['image'] = 'Not Available'

        self.client.close()
       
        return result


    def get_goodreads_rating(self,sku):
        import requests
        print(sku)
    
        api_key = self.config_dct['goodreads_key']
        url = "https://www.goodreads.com/book/review_counts.json?key="+api_key+"&isbns="+sku
        # +sku_csv
        data = requests.get(url,sku)
        datanew = json.loads(data.text)
        self.client.close()
           
        return datanew

    def get_data_from_goodreads(self,sku):
        import requests
        print(sku)
    
        api_key = self.config_dct['goodreads_key']
        product_data = {}
        url = f"https://www.goodreads.com/search/index.xml?key={api_key}&q={sku}"
        try:
            req = requests.get(url)
            soup = BeautifulSoup(req.text, 'lxml')
            pro_title = soup.find("title")
            if(pro_title == None):
                product_data['publisher'] = "Not Available"
                product_data['description'] = "Not Available"
                product_data['goodreads'] = "Not Available"
                product_data['author'] = "Not Available"
                print("None find")
            else:   
                idOfBook = pro_title.find_previous_sibling("id").text
                print(idOfBook)

                newUrl = f"https://www.goodreads.com/book/show.xml?key={api_key}&id={idOfBook}"
                req = requests.get(newUrl)
                soup = BeautifulSoup(req.text, 'lxml')
            
                product_data['publisher'] = soup.find("publisher").text
                product_data['description'] = soup.find("description").text
                product_data['goodreads'] = soup.find("average_rating").text
                authors = soup.find_all("author")
            
                authorName = ''
                authorId  = ''
                for author in authors:
                    authorName += author.find("name").text + ","
                    authorId =  author.find("id").text

                product_data['author'] = authorName.rstrip(",")
        
        except Exception as e:
            print('Exception in crawler for crawling: ', e)
            product_data['publisher'] = 'Not Available'
            product_data['description']= 'Not Available'
            product_data['goodreads'] = 'Not Available'
            product_data['author'] = 'Not Available'
        

        self.client.close()

        return product_data
        
           

    def getBatchProductsFromXml(self,file):
        soup = BeautifulSoup(file, 'lxml')
        self.client.close()
        return soup


class BackgroundJobs:
    
    @shared_task
    def crawl_amazon_api():
        import requests
        print(sku)
    
        # api_key = self.config_dct['goodreads_key']
        api_key = "6lIPd7Zb7CA5TNqTHRA"
        sku = "9780263933970"
        url = "https://www.goodreads.com/book/review_counts.json?key="+api_key+"&isbns="+sku
        # +sku_csv
        data = requests.get(url)
        datanew = json.loads(data.text)

        # self.client.close()
        print('crawling finished data is')
        print(datanew)
        # return datanew