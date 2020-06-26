from __future__ import absolute_import

from celery import shared_task
from api.methods import (  MongoClass,  ScrapeDataFromAmazon ) 


@shared_task
def add(x, y):
    return x + y

@shared_task
def crawl_data_update_batchProduct(sku_csv):
    
    obj = ScrapeDataFromAmazon()
    update_batch_pro = {}
    sku_list = sku_csv.split(',')
    sku_goodreads_list = []
    for sku in sku_list:
        url = "https://www.amazon.in/s?url=search-alias%3Daps&field-keywords="+sku
        crawled_data = obj.crawler(url,sku)
        update_batch_pro['amazon'] = crawled_data['Amazon Rating']
        update_batch_pro['image'] = crawled_data['image']
        update_batch_pro['sku'] = sku

        print(update_batch_pro)
        data = MongoClass.update_amazonrating_batch_product('batchproduct',update_batch_pro)
    
    dataToSend = obj.get_goodreads_rating(sku_csv)
    for item in dataToSend['books']:
        sku_goodreads_list.append({
            'sku':item['isbn13'],
            'goodreads':item['average_rating']
        })

    msg_res = MongoClass.update_goodreads_batch_product('batchproduct',sku_goodreads_list)
    
    return sku_goodreads_list

@shared_task
def get_data_from_goodreads_amazon_(sku_csv):
    obj = ScrapeDataFromAmazon()
    update_batch_pro = {}
    sku_list = sku_csv.split(',')
    sku_goodreads_data = []
    for sku in sku_list:
        url = "https://www.amazon.in/s?url=search-alias%3Daps&field-keywords="+sku
        amazon_data = obj.crawler(url,sku)
        update_batch_pro['amazon'] = amazon_data['Amazon Rating']
        update_batch_pro['image'] = amazon_data['image']
        update_batch_pro['sku'] = sku

        goodreads_data = obj.get_data_from_goodreads(sku)
        update_batch_pro.update(goodreads_data)
        data = MongoClass.update_amazonrating_batch_product('batchproduct',update_batch_pro)
    
    
    return update_batch_pro


@shared_task
def update_branch_request_products_by_batch_id(table_name,branch_list,sku_list,newStatus):
    print('going to update all br_req_pro for these branches ',branch_list)
    data = MongoClass.updateAllBranchReqProduct(table_name,branch_list,sku_list,newStatus)
    print('response of update query for status of br_re_pro is ',data)
    return 'data'

@shared_task
def update_branch_request_products_by_po_id(table_name,po_id,sku_list,newStatus):
    print('going to update all br_req_pro for this po id ',po_id)
    data = MongoClass.updateAllBranchReqProUsingPoId(table_name,po_id,sku_list,newStatus)
    print('response of update query for status of br_re_pro is ',data)
    return 'data'

@shared_task
def sendMail(dataToPost):
    import requests
    import json 
    url = "http://101.53.139.41:8083/wishbooks/wishbookMail"
    
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache"
    }
    try:
        response = requests.request("POST", url, data=json.dumps(dataToPost), headers=headers)
        print(response.text)
        return True
    except Exception as e:
        return False