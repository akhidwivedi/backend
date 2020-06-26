from django.shortcuts import render
# add user return id with token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.utils.crypto import get_random_string
from datetime import datetime
from collections import OrderedDict
# import settings
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework import status

from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination

from rest_framework.decorators import api_view

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser 
# from settings import * 
from celery import shared_task

from django.views.generic import View
from django.utils import timezone
from .models import *
from .render import Render

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView, 
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
    )
from decimal import *
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.decorators import api_view
from rest_framework.authentication import (TokenAuthentication, SessionAuthentication, BasicAuthentication,)
from num2words import num2words

from rest_framework import generics
from rest_framework.response import Response

from pprint import pprint
from drf_multiple_model.views import ObjectMultipleModelAPIView

from api.models import (BatchProduct , Branch_Request_Product, Product, Profile, Category, Branch_Request, Batch ,
                         PO_GR,BPFieldMapper,Retail,PO,PO_Product,Network,
                        # BranchRequest, BranchRequestedProduct,
                        )

from django.contrib.auth.models import User
from django.conf import settings

from api.methods import ( ExportCsvMixin, MongoClass, CollectionsMethod, ScrapeDataFromAmazon ) 


from api.serializers import (ChangeProfileMobileNumSerializer, RetailerListSerializer1,

    ProfileSerializer, Branch_Request_ProductSerializer, BatchProductSerializer,PO_Gr_Serializer,
                         ProductSerializer, CategorySerializer, BranchRequestSerializer, BatchSerializer,
                         BranchRequestSerializerNew, Branch_Request_ProductSerializerNew,BPFieldMapperSerializer,BPFieldMapperSerializerNew,
                         RetailerListSerializer,PO_Serializer,PO_Product_Serializer,PO_GR_Catalogue_Serializer,BatchProductSerializer1,
                         VendorListSerializer,BranchRequestSerializerUpdate,
                        #  BranchRequestedProductSerializer, BranchRequestSerializer
                         ) 
import csv
import requests
import urllib
import pandas as pd
import ast,json        
from api.tasks import (add,crawl_data_update_batchProduct,get_data_from_goodreads_amazon_,
                        update_branch_request_products_by_batch_id,
                        update_branch_request_products_by_po_id,sendMail)

# Create your views here.
class CustomObtainAuthToken(ObtainAuthToken):
    permission_classes = ((AllowAny,))

    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        
        uid=token.user_id
        print('user id is ',uid)
        user_type = list(Profile.objects.filter(user=uid).values('type_user', 'approved','network','retailer','branch'))
        print(user_type[0])
        if (len(user_type)==0):
            u_type="Please Create User Profile"
        
        if (len(user_type)>0):
            for utype in user_type:
                print(utype)
                u_type = utype.get('type_user')
                network = utype.get('network')
                approved = utype.get('approved')
                branch = utype.get('branch')
                retail = utype.get('retailer')
                # print(utype)
                # u_type = user_type[0]
     
        return Response({ 
                    'token': token.key, 
                    'id': token.user_id,
                    'network': network, 
                    'user_type': u_type,
                    'approved':approved,
                    'branch':branch,
                    'retail':retail
                })



class ProfileListApiView(ListAPIView):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self, *args, **kwargs):

        pk = self.request.GET.get("id")
        if pk:
            return Profile.objects.filter(id=pk)
        else:
            return Profile.objects.all()

    # def get(self, request, format=None):
    #     profile = Profile.objects.all()
    #     serializer = ProfileSerializer(profile, many=True)

    #     return Response(serializer.data)

 
    def post(self, request, format=None):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.utils.crypto import get_random_string

class UpdateUserProfile(APIView):
    """ update user profile by pasing params>> ?user_id as uid
    """

    permission_classes=((AllowAny, ))
    serializer_class = ProfileSerializer
    lookup_url_kwarg = 'uid'
        
    def get(self, request, *args, **kwargs):
        uid=self.kwargs['uid']

        profile_qs = Profile.objects.filter(user_id=uid)
        serializer_class = ProfileSerializer(profile_qs, many=True)
        return Response(serializer_class.data)       

    def post(self, request, *args, **kwargs):
        uid=self.kwargs['uid']
        qs = Profile.objects.filter(user_id=uid)
        
        serializer = ProfileSerializer(qs[0], data=request.data)

        if serializer.is_valid():
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
   
        ph_num = list(Profile.objects.filter(user_id=uid).values_list('contact_num', flat=True))
        cust_num = ph_num[0]

        # print mob

        verify_mob_code = list(Profile.objects.filter(user_id=uid).values_list('verify_mob_code', flat=True))
        code = verify_mob_code[0]
        # print code
        
        message = ("This Is Your One Time Verification Code" + ' ' + code)
        
        if Profile.objects.filter(user_id=uid, verify_mobile=False):
            sendsms_test(cust_num, message)

        s = LogEntry.objects.log_action(
                            user_id=uid,
                            content_type_id=ContentType.objects.get_for_model(Profile).pk,
                            object_id=Profile.objects.values_list('id', flat=True).last(),
                            object_repr=unicode(Profile.objects.only('type_user').last()),
                            action_flag=CHANGE,
                            change_message='Profile change'
                        )
        return Response(response[0])




class ApproveProfileViewByAdminAPI(APIView):
    """ admin make approved for all user (supplier/agent)\n 
        by passing params ?userId"""

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        
        if (settings.USER_IS_STAFF==self.request.user.is_staff):
                        
            approved = self.request.data.get('approved')
            user_id = self.request.data.get('user_id')
            admin_note = self.request.data.get('admin_note')
            profile_status = self.request.data.get('profile_status')


            if ((approved.title())=="True") | ((approved.title())=="False"):

                    queryset = Profile.objects.filter(
                                            user_id=user_id
                                            ).update(
                                            approved=approved.title(),
                                            verify_mobile=approved.title(),
                                            verify_email=approved.title(),
                                            profile_status=profile_status,
                                            admin_note=admin_note                                            
                                            )

                    response = Profile.objects.filter(
                                        user_id__exact=user_id
                                        )
                    serializer = ProfileSerializer(response, many=True)
                    return Response(serializer.data[0])
                        
        else:
            return Response({"detail": "only admin has permissions to access data" 
                            },status=status.HTTP_400_BAD_REQUEST
                            )
            

from django.utils.crypto import get_random_string

class ChangeProfileMobileNumAPI(ListAPIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    serializer_class = ChangeProfileMobileNumSerializer
    queryset = Profile.objects.all()
    
    def post(self, request):
        contact_num = self.request.data.get('contact_num', None)

        print('contact_num', contact_num)
        print('user_id', self.request.user.id)

        queryset = Profile.objects.filter(user_id=self.request.user.id).update(
                            verify_changeNum_code=get_random_string(length=6, 
                                                    allowed_chars='123456789')) 
        

        verify_code = list(Profile.objects.filter(user_id=self.request.user.id
                                            ).values_list('verify_changeNum_code', flat=True))
        change_cust_num = verify_code[0]

        print('change_cust_num', change_cust_num)

        message = ("This Is Your One Time Verification Code" + ' ' + change_cust_num)
        sendsms_test(contact_num, message)
        
        return Response({"detail": "OTP has been sent to your Mobile number."}, status=status.HTTP_201_CREATED)
        
    def get(self, request):
        otp = self.request.query_params.get('OTP', None)
        contact_num = self.request.query_params.get('contact_num', None)

        if otp is None:
            return Response({"detail": "pass ?OTP and contact_num is needed"})
        
        else:
            
            if Profile.objects.filter(user_id=self.request.user.id, 
                                    verify_changeNum_code=otp).exists():

                queryset = Profile.objects.filter(user_id=self.request.user.id).update(
                            contact_num=contact_num) 
        

                return Response({"detail": "You have successfully changed your mobile number"})

            else:
                return Response({"detail": "Please Enter a valid OTP to change your Mobile Num" })        

class ProductDetailAPIView(ObjectMultipleModelAPIView):
    objectify = True
    lookup_url_kwarg = 'id'

    def get_queryList(self):
        pk = self.kwargs['id']
        
        queryList = (
            (Product.objects.filter(id =pk), ProductSerializer, 'product_data'),
        )
        
        return queryList




class BPListAPIView(ListAPIView):
    permission_classes = ((AllowAny,))

    queryset = BatchProduct.objects.all()
    serializer_class = BatchProductSerializer
    lookup_url_kwarg = 'bid'

    def get(self, request, *args, **kwargs):

        bid=self.kwargs['bid']
        batch_products = BatchProduct.objects.filter(batch_id=bid)
        serializer_class = BatchProductSerializer(batch_products, many=True)

        return Response(serializer_class.data)



class ManualBPListAPIView(ListAPIView):
    permission_classes = ((AllowAny,))
    lookup_url_kwarg = 'bid'
    def get(self, request, *args, **kwargs):
        bid=self.kwargs['bid']
        print(bid)
        data = MongoClass.mongo_connect_get_data_table('batchproduct',bid)
        return Response(data)

class HandlePlaceOrderGetApi:
    def getProdcts(self,batch_id,user_id):
        try:
            print('inside try block')
            branch_request = Branch_Request.objects.get(batch=int(batch_id),user=int(user_id))
            print(branch_request)
            print(branch_request.id)
            branch_request_id = branch_request.id
            data = MongoClass.get_batch_products_for_placeorder('batchproduct',batch_id , branch_request_id)
            return data

        except Exception as e:
            print('inside Catch block')
            print(batch_id)
            data = MongoClass.get_data_batchproduct('batchproduct',batch_id)
            # print(data)
            return data
        

class BatchProductsListAsPerBranchRequest(ListAPIView):
    def get(self,request,*args,**kwargs):
        batch_id = self.kwargs['bid']
        user_id = self.kwargs['uid']
        print(batch_id)
        obj = HandlePlaceOrderGetApi()
        data = obj.getProdcts(batch_id,user_id)
        dataToSend = {'products':data,'status':True,'batch_id':batch_id}
        return Response(dataToSend,status.HTTP_200_OK)


class BatchProductDetailAPIView(ObjectMultipleModelAPIView):
    objectify = True
    lookup_url_kwarg = 'id'

    def get_queryList(self):
        pk = self.kwargs['id']
        
        queryList = (
            (Product.objects.filter(id =pk), ProductSerializer, 'product_data'),
        )
        
        return queryList



class PO_ProductDetailAPIView(ObjectMultipleModelAPIView):
    
    objectify = True
    lookup_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['id']
        print(pk)
        po_products = Branch_Request_Product.objects.filter(po=pk)
        serializer_class = Branch_Request_ProductSerializer(po_products, many=True)
       
        return Response(serializer_class.data)

class BatchDetailAPIView(ObjectMultipleModelAPIView):
    objectify = True
    lookup_url_kwarg = 'id'

    def get_queryList(self):
        pk = self.kwargs['id']
        
        queryList = (
            (Batch.objects.filter(id =pk), BatchSerializer, 'product_data'),
        )
        
        return queryList

# class BatchUpdateAPIView(UpdateAPIView):
    
#     def put(self,request):
#         print(request.data['id'])
#         currentBatch = Batch.objects.get(id=request.data['id'])
#         pprint(currentBatch.status)
#         print(type(currentBatch.status))
#         if(currentBatch.status == 'True'):
#             updatedActive = False
#         else:
#             updatedActive = True
        
#         serializer = BatchSerializer(currentBatch, {'active':updatedActive})
#         serializer.is_valid()
#         serializer.save()
#         print(serializer.data)
#         return Response(serializer.data)

class BatchDeleteAPIView(UpdateAPIView):
    def put(self,request,id):
       lookup_url_kwarg = 'id' 
       batch_id = self.kwargs['id']

       currentBatch = Batch.objects.get(id=batch_id)
       print(currentBatch)
       updatedActive = 1
       serializer = BatchSerializer(currentBatch, {'delete':updatedActive})
       serializer.is_valid()
       serializer.save()
       print(serializer.data)

       #return serializer.data[0]

       return Response(serializer.data)
        

class LatestActiveBatchAPIView(UpdateAPIView):
    def get(self,request,*args, **kwargs):
       batch = MongoClass.latestActiveBatch('batch') 
    #    print(batch[0]['id'])
       user_id = self.kwargs['uid']
       try:
           batch_id = batch[0]['id'] 
           obj = HandlePlaceOrderGetApi()
           data = obj.getProdcts(batch_id,user_id)
           apiResponse = {'products':data,'status':True,'batch_id':batch_id}
           return Response(apiResponse,status.HTTP_200_OK)
       except Exception as e:
           apiResponse = {'products':'No active batches present','status':False}
           return Response(apiResponse,status.HTTP_200_OK) 



class BatchUpdateAPIView(UpdateAPIView):
   
   def put(self,request, id):
       lookup_url_kwarg = 'id' 
       batch_id = self.kwargs['id']

       currentBatch = Batch.objects.get(id=batch_id)
       print(currentBatch)
       updated = datetime.now()
       if(currentBatch.status == 1):
           updatedActive = 0
       else:
           updatedActive = 1
       serializer = BatchSerializer(currentBatch, {'status':updatedActive,'updated':updated})
       serializer.is_valid()
       serializer.save()
       batchId = serializer.data['id']
       
       batchProducts = BatchProduct.objects.filter(batch_id=batchId).update(status=updatedActive,updated=updated)
       
       print(serializer.data)

       #return serializer.data[0]

       return Response(serializer.data)


class ProductListAPIView(ListAPIView):

    authentication_classes = (TokenAuthentication,)
        
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
   
    def get(self, request, format=None):
        snippets = Product.objects.all()
        serializer_class = ProductSerializer(snippets, many=True)
        return Response(serializer_class.data)

  
    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            print("=============")
            pprint(serializer.validated_data)
            print("=============") 
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class BatchProductListAPIView(ListAPIView):

    authentication_classes = (TokenAuthentication,)
        
    permission_classes = (IsAuthenticated,)
    queryset = BatchProduct.objects.all()
    serializer_class = BatchProductSerializer
   
    def get(self, request, format=None):
        snippets = BatchProduct.objects.all()
        
        print("=============")
        pprint(snippets)
        print("=============")

        serializer_class = BatchProductSerializer(snippets, many=True)
        
        return Response(serializer_class.data)

  
    def post(self, request, format=None):
        serializer = BatchProductSerializer(data=request.data)
        

        if serializer.is_valid(raise_exception=True):
            print("=============")
            pprint(serializer.validated_data)
            print("=============") 
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BatchProductListbyIdAPIView(ListAPIView):

    authentication_classes = (TokenAuthentication,)
        
    permission_classes = (IsAuthenticated,)
    queryset = BatchProduct.objects.all()
    serializer_class = BatchProductSerializer
   
    def get(self, request, format=None):
        snippets = BatchProduct.objects.all()
        
        print("=============")
        pprint(snippets)
        print("=============")

        serializer_class = BatchProductSerializer(snippets, many=True)
        
        return Response(serializer_class.data)

  
    def post(self, request, format=None):
        serializer = BatchProductSerializer(data=request.data)
        

        if serializer.is_valid(raise_exception=True):
            print("=============")
            pprint(serializer.validated_data)
            print("=============") 
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PO_ProductListAPIView(ListAPIView):

    authentication_classes = (TokenAuthentication,)
        
    permission_classes = (IsAuthenticated,)
    queryset = Branch_Request_Product.objects.all()
    serializer_class = Branch_Request_ProductSerializer
   
    def get(self, request, format=None):
        snippets = Branch_Request_Product.objects.all()
        serializer_class = Branch_Request_ProductSerializer(snippets, many=True)
        return Response(serializer_class.data)

  
    def post(self, request, format=None):
        
        print("=====request.data========")
        pprint(request.data)
        print("=========request.data====")    

        serializer = Branch_Request_ProductSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            print("=============")
            pprint(serializer.validated_data)
            print("=============") 
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PO_ProductListbyBatchAPIView(ListAPIView):

    objectify = True
    lookup_url_kwarg = 'bid'

    def queryset(self):
        bid = self.kwargs['bid']
        
        queryList = (
            (Branch_Request_Product.objects.filter(batch=bid), Branch_Request_ProductSerializer, 'product_data'),
        )
        
        return queryList


class BatchListAPIView(ListAPIView):

    authentication_classes = (TokenAuthentication,)
        
    permission_classes = (IsAuthenticated,)
    queryset = Batch.objects.filter(delete=False)
    serializer_class = BatchSerializer
   
    def get(self, request, format=None):
        snippets = Batch.objects.filter(delete=False,po_type='branchOrdering')
        serializer_class = BatchSerializer(snippets, many=True)
        return Response(serializer_class.data)


    def post(self, request, format=None):
        serializer = BatchSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            print("=============")
            pprint(serializer.validated_data)
            print("=============") 
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActiveBatchListAPIView(ListAPIView):
    
    authentication_classes = (TokenAuthentication,)
        
    permission_classes = (IsAuthenticated,)
    queryset = Batch.objects.filter(delete=False)
    serializer_class = BatchSerializer
   
    def get(self, request, format=None):
        snippets = Batch.objects.filter(delete=False,po_type= 'branchOrdering',status=True)
        serializer_class = BatchSerializer(snippets, many=True)
        return Response(serializer_class.data)

class CategoryListAPIView(ListAPIView):
    permission_classes = ((AllowAny,))

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, format=None):
        queryset = Category.objects.all()
        serializer_class = CategorySerializer(queryset, many=True)
        return Response(serializer_class.data)       
    
    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BranchRequestListAPIView(ListAPIView):
    permission_classes = ((AllowAny,))

    queryset = Branch_Request.objects.all()
    # serializer_class = BranchRequestSerializer

    def get(self, request, format=None):
        queryset = Branch_Request.objects.all()
        pprint(queryset)
        serializer_class = BranchRequestSerializerNew(queryset, many=True)
        return Response(serializer_class.data)       
    
    def post(self, request, format=None):
        serializer = BranchRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaceOrderAPIView(ListAPIView):
    serializer_class = BranchRequestSerializerNew

    def post(self, request, format=None):
        data = request.data
        print(data['po'])
        branch_products = request.data['po_products']
        branch_req_products = []
        br_req_data = data['po']    
        obj, created = Branch_Request.objects.get_or_create(user=User(br_req_data['user']),
            batch=Batch(br_req_data['batch']),network=Network(br_req_data['network']),
            retail=Retail(br_req_data['retail']),branch=int(br_req_data['branch']))
        # obj.value = request.data['po']
        # obj.save()
        print(created)
        br_req_id = obj.id
        print(br_req_id)
        for products in branch_products:
            print(type(products['batch_id']))
            branch_req_products.append(Branch_Request_Product(
                branch_req= Branch_Request(br_req_id),
                sku=products['sku'],product=BatchProduct(products['id']),discount=products['disc'],
                qty=products['qty'],mrp=products['mrp'],name=products['name'], 
                subTotal = products['subTotal'], batch = Batch(products['batch_id'])))

        branch_pro = Branch_Request_Product.objects.bulk_create(branch_req_products)
        # pprint(branch_pro)
        
        return Response('Created', status =status.HTTP_201_CREATED)


class TestGetOrCreate(ListAPIView):
    def post(self,request,format=None):
    
        return Response("success",status.HTTP_200_OK)

class UpdateOrderPlacedAPIView(ListAPIView):

    def post(self, request, format=None):
        br_req_pro_id = request.data['br_req_pro_id']
        newOrderedQty = request.data['newQty']
        try:
            data = Branch_Request_Product.objects.filter(id=br_req_pro_id).update(qty=newOrderedQty)
        except Exception as e:
            print(e)
            dict_obj = {
                "detail":"Error updating the ordered quantity"
            }
            return Response(dict_obj,status.HTTP_400_BAD_REQUEST)    

        return Response('New Quantity Updated', status =status.HTTP_201_CREATED)

class BranchRequestProductAPIView(ListAPIView):
    objectify=True
    lookup_url_kwarg = 'id'
    serializer_class = Branch_Request_ProductSerializer

    def get(self, request, *args, **kwargs):
        bid=self.kwargs['id']
        
        data = Branch_Request.objects.filter(id=bid)
        serializer = BranchRequestSerializerNew(data, many =True)
        # branch_req_id = serializer.data[0]['id']

        pro_data = Branch_Request_Product.objects.filter(branch_req=bid)
        returnData = {}
        returnData['branch_request'] = serializer.data
        returnData['branch_request_product'] = Branch_Request_ProductSerializer(pro_data,many=True).data
        # serializer.is_valid()
        return Response(returnData,status = status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = Branch_Request_ProductSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            # pprint(serializer.data)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BranchRequestByBatchAPIView(ListAPIView):
    objectify = True
    lookup_url_kwarg = 'bid'

    def get(self,request,*args,**kwargs):
        batch_id = self.kwargs['bid']
        data = Branch_Request.objects.filter(batch=batch_id)
        serializer = BranchRequestSerializerNew(data,many=True)
        return Response(serializer.data,status.HTTP_200_OK)


class BranchRequestForBranchAPIView(ListAPIView):
    objectify = True
    lookup_url_kwarg = 'batchid'

    def get(self,request,*args,**kwargs):
        batch_id = self.kwargs['batchid']
        branch = self.kwargs['branch']
        data = Branch_Request.objects.filter(batch=batch_id,branch=branch)
        serializer = BranchRequestSerializerNew(data,many=True)
        return Response(serializer.data,status.HTTP_200_OK)

class GeneratePOAPIView(ListAPIView):
    objectify = True
    lookup_url_kwarg = 'bid'

    def get(self, request, *args, **kwargs):
        batch_id = self.kwargs['bid']
        print(batch_id)
        
        data = Branch_Request_Product.objects.filter(batch=batch_id)
        serializer = Branch_Request_ProductSerializerNew(data, many=True)
        print(len(serializer.data))
        if len(serializer.data) == 0:
            errorMessage = {}
            errorMessage['msg'] = 'Requests are yet to be received for this batch'       
            return Response(errorMessage, status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.data,status.HTTP_200_OK)

class BPFieldMapperAPIView(ListAPIView):

    def get(self,request,format=None):
        data = BPFieldMapper.objects.all()
        serializer = BPFieldMapperSerializer(data,many=True)
        return Response(serializer.data,status.HTTP_200_OK)

class RetailListAPIView(ListAPIView):

    def get(self,request,format=None):
        data= Retail.objects.filter(vendor=True)
        serializer = RetailerListSerializer(data,many=True)
        print('vendor are')
        print(serializer.data)
        return Response(serializer.data,status.HTTP_200_OK)

class VendorListAPIView(ListAPIView):
    
    def get(self,request,format=None):
        data= Retail.objects.filter(vendor=True)
        serializer = VendorListSerializer(data,many=True)
        print('vendor are')
        print(serializer.data)
        return Response(serializer.data,status.HTTP_200_OK)


class CreatePOUsingFile(ListAPIView):

    def post(self,request,format=None):
        import pandas as pd
        csv_file = request.FILES['csv']
        if not csv_file.name.endswith('.csv'):
            return Response('Please upload a .csv file',status.HTTP_406_NOT_ACCEPTABLE)
        df = pd.read_csv(csv_file)
        poFileDict = df.to_dict('records')
        po_products_arr = []
        vendor = request.data['vendor']
        vendorDiscount = request.data['vendorDiscount']
        vendorData = Retail.objects.get(id=vendor)
        serializer = RetailerListSerializer(vendorData,many=False)
        retailer_name = serializer.data['name']
        po_name = retailer_name+" "+ request.data['created']
        (batch,discount,po_id,i,totalqty,totalAmtForPo,discAmt,netTotal) = '','','',0,0,0,0,0
        
        fs = FileSystemStorage(location='uploads/')
        filename = fs.save(csv_file.name, csv_file)
        
        poObject = PO.objects.create(vendor = Retail(vendor), qty = 0, name = po_name, totalAmount = 0)
        po_id = poObject.id
        branch_list = []
        sku_list = []
        for item in poFileDict:
            qty = int(item.get('COUNT'))
            mrp = float(item.get('PRICE')) 
            batch = int(item.get('BATCH')) 
            name = item.get('TITLE')
            branch = int(item.get('BRANCH'))
            sku = item.get('ISBN')
            sku_list.append(str(sku))
            if branch in branch_list:
                pass
            else:
                branch_list.append(branch)
            print(branch_list)
            try:
                discount = float(item.get('DISCOUNT'))
            except Exception as e:
                discount = float(vendorDiscount)

            totalqty += qty  
            discAmt = mrp * discount/100
            netTotal = qty * (mrp - discAmt)
            totalAmtForPo += netTotal
            po_products_arr.append(PO_Product(po=PO(po_id),sku= sku,
            qty=qty,mrp=mrp, batch=Batch(batch),branch=int(item.get('BRANCH')),name=name,
            discount=discount,discountAmount=discAmt,netTotal=netTotal))

        data = {}
        data['batch_id'] = batch
        data['qty'] = totalqty
        data['totalAmount'] = totalAmtForPo
        data['branch_list'] = branch_list
        newPO = MongoClass.update_collection_using_id('po',po_id,data)
        # newPO = PO.objects.filter(id=po_id).update(batch=batch,qty=totalqty,totalAmount=totalAmtForPo)
        pprint(newPO)
        po_pro_obj = PO_Product.objects.bulk_create(po_products_arr)
        print(po_pro_obj)
        print('starting backgrounf job')          
        updateInBackground = update_branch_request_products_by_batch_id.delay('branch_request_product',
        branch_list,sku_list,'Ordered')
        return Response("success",status.HTTP_200_OK)

        
class PO_ProductAPIView(ListAPIView):
    def get(self,request,*args,**kwargs):
        po_id = self.kwargs['po_id']
        # isNetworkAdmin = self.kwargs['flag']
        # print(isNetworkAdmin)
        # print(type(isNetworkAdmin))
        # branch = self.kwargs['branch']
        # data = MongoClass.get_poproduct_data_('po_product',po_id,isNetworkAdmin,branch)
        data = MongoClass.get_poproduct_data_('po_product',po_id)
            
        return Response(data,status.HTTP_200_OK)

class POListApiView(ListAPIView):
    def get(self,request,format=None):
        data = PO.objects.all()
        for element in data:
            print(element.vendor)
        serializer = PO_Serializer(data,many=True)
        return Response(serializer.data,status.HTTP_200_OK)


class POListForCatalogueAPIView(ListAPIView):
    def get(self,request,format=None):
        data = PO.objects.filter(received=True)
        for element in data:
            print(element.vendor)
        serializer = PO_Serializer(data,many=True)
        return Response(serializer.data,status.HTTP_200_OK)


class POListByVendorApiView(ListAPIView):
    def get(self,request,*args,**kwargs):
        vendor_id = self.kwargs['id']
        print(vendor_id)
        data = PO.objects.filter(vendor=vendor_id)
        serializer = PO_Serializer(data,many=True)
        return Response(serializer.data,status.HTTP_200_OK)

class InboundPoListApiView(ListAPIView):
    def get(self,request,*args,**kwargs):
        branch_id = self.kwargs['branch']
        print(branch_id)
        data = MongoClass.searchingInArrayField('po',branch_id)
        print('data is ',data)
        return Response(data,status.HTTP_200_OK)


class PO_GRListAPIView(ListAPIView):
    def post(self, request, format=None):
        po_gr_arr = []
        response = request.data
        sku_arr = []
        po_id = ''
        count = []
        for item in response:
            po_id = item['pid']
            sku_arr.append(item['sku'])
            count.append(item['count'])
            i = 0
            po_data = PO_Product.objects.filter(po=po_id,sku=sku_arr[i])
            while i < int(item['count']):
                po_gr_arr.append(PO_GR(sku=item['sku'],invoice_num=item['inv_num'],
                invoice_amt=item['inv_amt'],po=PO(item['pid'])))
               
                i = i+1

        
        print(sku_arr)
        data = PO_GR.objects.bulk_create(po_gr_arr)

        for i in range(0,len(sku_arr)):
            print(sku_arr[i])    
            print(count[i])    
            data = PO_Product.objects.filter(po=po_id,sku=sku_arr[i]).update(receivedqty=count[i])

        
        # sku_count_dict = CollectionsMethod.CountFrequency(sku_arr)

        # print(sku_count_dict)

        # for key, value in sku_count_dict.items():
            # data = PO_Product.objects.filter(po=po_id,sku=key).update(receivedqty=sku_count_dict[key])
            

        return Response('success',status.HTTP_200_OK)

    def put(self,request):
        print(request.data)
        return Response('on',status.HTTP_200_OK)

class CreatePoGrAPIView(ListAPIView):
    def post(self,request,format=None):
        po_desc = request.data['po_desc']
        sku_count_list = request.data['sku_count_arr']
        sku_list = []
        receive_qty_arr = []
        for item in sku_count_list:
            sku_list.append(item['sku'])
            receive_qty_arr.append(item['count'])
            
        po_products_list = []
        rec_qty = {}
        po_gr_arr = []
        po_id = po_desc['po_id']
        print(f"po_id is {po_id}")
        error = {}
        for item in range(0, len(sku_list)):
            po_pro = MongoClass.get_data_with_group_and_match('po_product','po_id',int(po_desc['po_id']),sku_list[item])
            print(po_pro)

            # error = {}
            # print(receive_qty_arr[item])
            if(len(po_pro) > 0):
                if int(receive_qty_arr[item]) > po_pro[0]['totalQty']:
                    
                    error['error_desc'] = sku_list[item] + " received quantity is more than ordered"
                    return Response(error,status.HTTP_400_BAD_REQUEST)
                else:
                    rec_qty['received'] = receive_qty_arr[item]
                    po_pro[0]['rec'] = receive_qty_arr[item]
                    po_products_list.append(po_pro)
            else:
                error['error_desc'] = sku_list[item] + " this item was not ordered in the selected PO"
                return Response(error,status.HTTP_400_BAD_REQUEST)
                
        

        for item in range (0, len(po_products_list)):
            sku = po_products_list[item][0]['sku'][0]
            po_id = po_desc['po_id']
            received = po_products_list[item][0]['rec']
            # print(received)
            i = 0
            while i < int(received):
                # print (i)
                po_gr_arr.append(PO_GR(sku=sku,invoice_num=po_desc['inv_num'],
                    invoice_amt=po_desc['inv_amt'],po=PO(po_id)))
                i=i+1
        

        data = PO_GR.objects.bulk_create(po_gr_arr)
        updatePo = PO.objects.filter(id=int(po_id)).update(received=True)
        # updateInBackground = update_branch_request_products_by_po_id.delay('branch_request_product',po_id,sku_list,'Purchased')

        return Response('success',status.HTTP_200_OK)

class GetAllBranchesAPIView(ListAPIView):
    
    def get(self,request,format=None):
        branches = Retail.objects.all()
        serializer = RetailerListSerializer1(branches,many=True)
        return Response(serializer.data,status.HTTP_200_OK)

class GetBranchesForCatalogue(ListAPIView):
    def get(self,request,*args,**kwargs):
        po_id = self.kwargs['po_id']
        sku = self.kwargs['sku']
        
        branches = PO_Product.objects.filter(po=po_id,sku=sku)
        serializer = PO_Product_Serializer(branches,many=True)
        branchid_list = []
        
        for item in serializer.data:
            # print('item')
            # print(item)
            branchid_list.append(item['branch'])
        
        print(branchid_list)
        search_for = 'branch'

        data = MongoClass.get_data_with_conditions_having_list('retail',branchid_list,search_for)
        print(data)
        # serialize = RetailerListSerializer(data,many=True)
        return Response(data,status.HTTP_200_OK)

class PO_product_by_po(ListAPIView):
    def get(self,request,*args,**kwargs):
        po_id = self.kwargs['id']
        data = PO_Product.objects.filter(po=po_id)
        serializer = PO_Product_Serializer(data,many=True)

        return Response(serializer.data,status.HTTP_200_OK)
        # PO_Product_Serializer


class Pdf(ListAPIView):

    def get(self,request,*args,**kwargs):
        po_id = self.kwargs['id']
        data = PO_Product.objects.filter(po=po_id)

        data_po = PO.objects.get(id=po_id)

        data_po_filter = PO.objects.filter(id=po_id)


        serializer_po = PO_Serializer(data_po_filter,many=True)

        po_data = serializer_po.data


        # for item in po_data[0]:
        #     print("---------===")
        #     print(item)            


        serializer = PO_Product_Serializer(data,many=True)
        sales = serializer.data
        print(po_data[0]['totalAmount'])
        print(type(po_data[0]['totalAmount']))
        amount = float(po_data[0]['totalAmount'])

        amountInteger = int (float(po_data[0]['totalAmount']))

        # totalAmountInWords = num2words(amountInteger,ordinal=True)

        totalAmountInWords = CollectionsMethod.amt2words(amountInteger) 
        print(totalAmountInWords)
        dict_data = {
            'sales': sales,
            'name' : po_data[0]['name'],
            'created' : po_data[0]['created'],
            'totalAmount' : po_data[0]['totalAmount'],
            'totalAmountInWords' : totalAmountInWords.title(),
            'vendorname' : po_data[0]['vendorName'],

        }

        # print("---==000==")
        # pprint(dict_data)
        # print("---==000==")

        import os
        cwd = os.getcwd()

        

        return Render.render( 'pdf.html', dict_data)

        #return Render.render('pdf.html', serializer.data)


class PO_product_by_po_pdf(ListAPIView):
    def get(self,request,*args,**kwargs):
        po_id = self.kwargs['id']
        data = PO_Product.objects.filter(po=po_id)
        serializer = PO_Product_Serializer(data,many=True)

        return Response(serializer.data,status.HTTP_200_OK)

class CatalogueUpdateGrAndPo_ProAPIView(ListAPIView):
    def post(self,request, format=None):
        request_data = request.data
        item_no = request_data['item']
        sku = request_data['sku']
        branch = request_data['branch']
        po = request_data['po']
        queryParams = {'po_id':po, 'sku':sku, 'item_number':"0"}
        # print(queryParams)
        branch_list = []
        sku_list = []
        sku_list.append(sku)
        branch_list.append(int(branch))
        data = MongoClass.update_one_entry('po_gr',queryParams,request_data)

        if not data:
            response_msg = 'The item '+sku+' is not received yet'
            return Response({'msg':response_msg},status.HTTP_400_BAD_REQUEST)
        po_pro = MongoClass.findAndModifyCollection('po_product',request_data)
        print(po_pro)
        # print(data)
        updateInBackground = update_branch_request_products_by_batch_id.delay('branch_request_product',branch_list,sku_list,'Jacketting in Progress')
        return Response('success',status.HTTP_200_OK)


class BatchListByDonationAPIView(ListAPIView):
    
    authentication_classes = (TokenAuthentication,)
        
    permission_classes = (IsAuthenticated,)
    queryset = Batch.objects.filter(delete=False,po_type="donation/gift")
    serializer_class = BatchSerializer
   
    def get(self, request, format=None):
        snippets = Batch.objects.filter(delete=False,po_type="donation/gift")
        serializer_class = BatchSerializer(snippets, many=True)
        return Response(serializer_class.data,status.HTTP_200_OK)


    def post(self, request, format=None):
        created = request.data['created']
        batch_dict = {}
        batch_dict['name'] = request.data['name']
        batch_dict['description'] = request.data['description']
        batch_dict['po_type'] = request.data['po_type']
        batch_dict['user'] = request.data['user']
        batch_dict['status'] = True
        try:
            batch_dict['created'] = datetime(*map(int, created.split('-')))
        except Exception as e:
            batch_dict['created'] = datetime.now()

        print(batch_dict['created'])
        print(type(batch_dict['created']))

        serializer = BatchSerializer(data=batch_dict)
        
        if serializer.is_valid(raise_exception=True):
            print("=============")
            pprint(serializer.validated_data)
            print("=============") 
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CatalogueUsingBatchAPIView(ListAPIView):
    def post(self,request,format=None):
        item_no = request.data['item']
        sku = request.data['sku']
        branch = request.data['branch']
        batch = request.data['batch']
        po_gr = PO_GR.objects.create(item_number=item_no,sku=sku,branch=branch,batch=Batch(batch),status='In Dispatch')
        print(po_gr)
        return Response('Item Catalogued',status.HTTP_200_OK)

class GenerateReportForCatalogueDBook(ListAPIView):
    def get(self,request,*args,**kwargs):
        batchId = self.kwargs['batchId']
        po_gr_data = PO_GR.objects.filter(batch=batchId)
        serializer = PO_GR_Catalogue_Serializer(po_gr_data,many=True)
        return Response(serializer.data,status.HTTP_200_OK)


class BranchRequestProductByBatchAPIView(ListAPIView):
    objectify=True
    lookup_url_kwarg = 'batchId'
    serializer_class = Branch_Request_ProductSerializer

    def get(self, request, *args, **kwargs):
        bid=self.kwargs['batchId']
        print('batch ids is ')
        print(bid)
        pro_data = Branch_Request_Product.objects.filter(batch=bid)
        serializer = Branch_Request_ProductSerializerNew(pro_data, many =True)
        return Response(serializer.data,status = status.HTTP_200_OK)


class CreatePOListAPIView(ListAPIView):

    def post(self,request,format=None):
        po_products_arr = request.data['po_product']
        po_data = request.data['po']
        po_products = []
        updateBranchReqPro = request.data['updateBranchReqPro']
        batchId = int(po_data['batch'])
        vendorId = int(po_data['vendor'])
        print(vendorId)
        print('===')
        print(batchId)
        totalqty = 0
        retailer = Retail.objects.get(id=vendorId)
        totalAmtForPo = 0
        discAmt = 0
        netTotal = 0
        retailer_name = retailer.name
        po_name = retailer_name+" "+ po_data['created']
        poObject = PO.objects.create(vendor=Retail(vendorId), batch=Batch(batchId),qty=0,name=po_name,totalAmount=0)
        po_id = poObject.id
        branch_list = []
        sku_list = []
        for item in po_products_arr:
            qty = int(item['qty'])
            # print(qty)
            sku = item['sku']
            sku_list.append(sku)
            name = item['name']
            discount = float(item['discount'])
            # print(sku)
            mrp = float(item['mrp'])
            discAmt = mrp * discount/100
            netTotal = qty * (mrp - discAmt)
            totalAmtForPo += netTotal
            # print(mrp)
            branch = int(item['branch'])
            if branch in branch_list:
                pass
            else:
                branch_list.append(branch)

            totalqty += qty  
            po_products.append(PO_Product(po=PO(po_id),sku=sku,
                qty=qty,mrp=mrp, batch=Batch(batchId),branch=branch,name=name,
                discount=discount,discountAmount=discAmt,netTotal=netTotal))

        data = {}
        data['qty'] = totalqty
        data['totalAmount'] = totalAmtForPo
        data['branch_list'] = branch_list
        newPO = MongoClass.update_collection_using_id('po',po_id,data)
        # newPO = PO.objects.filter(id=po_id).update(qty=totalqty,totalAmount=totalAmtForPo)
        # pprint(newPO)
        po_pro_obj = PO_Product.objects.bulk_create(po_products)
        # print(po_pro_obj)
        print(type(updateBranchReqPro))
        print(updateBranchReqPro)
        if updateBranchReqPro:
            updateInBackground = update_branch_request_products_by_batch_id.delay('branch_request_product',
            branch_list,sku_list,'Ordered')
        else:
            pass
        return Response("success",status.HTTP_200_OK)



class BatchProductModalView(ListAPIView):
    def get(self,request,*args,**kwargs):
        batch_pro_id = kwargs['batch_id']

        data = MongoClass.get_data_('batchproduct',batch_pro_id)
        print(data)
        return Response(data, status.HTTP_200_OK)


class CreateBatchAndBatchProductsViaFile(ListAPIView):
    def post(self,request,format=None):
        
        csv = request.FILES['csv']
        name = request.data['name']
        po_type = request.data['po_type']
        description = request.data['description']
        user = int(request.data['user'])
        created = request.data['created']
        endDate = request.data['endDate']
        network = int(request.data['network'])
        updated = ''
        data = ''
        statuss = False
        response_data = {}

        if not csv.name.endswith('.csv'):
            return Response('Please upload a .csv file ',status.HTTP_406_NOT_ACCEPTABLE)
        
        df = pd.read_csv(csv)
        csv_header = df.columns

        try:
            strdate =datetime(*map(int, created.split('-')))
            created = strdate
            updated = strdate
        except Exception as e:
            created = datetime.now()
            updated = created

        # print(batch_id)
        try:
            data = BPFieldMapper.objects.filter(network=1)
            serializer = BPFieldMapperSerializerNew(data,many=True)
            field_mapper_arr = serializer.data

            user_sys_dict = {}
            # print(sku_list[0])
            # creating a dictionary having user_key and sys_key
            for item in field_mapper_arr:
                user_sys_dict.update({
                    item['user_key'].lower():item['sys_key']
                })
            
            new_header_list = {}
            for item in csv_header:
                nKey = ''
                try:
                    nKey = user_sys_dict[item.lower()].lower()
                except Exception as e:
                    nKey = item.lower()
                new_header_list.update({item:nKey})

            df.rename(columns=new_header_list, inplace=True)
            records = df.to_dict('records')

            data = Batch.objects.create(name=name,user=User(user),description=description,status=statuss,po_type=po_type,created=created,updated=updated)

            batch_id = int(data.id)
            # batch_id=1
            # print(records)
            batch_products_arr = []

            batch_pro_seq = MongoClass.mongo_api_schema('api_batchproduct')
          
            last_id = batch_pro_seq[0]['auto']['seq']
            sku_list = []

            for item in records:
                obj = item
                obj['sku'] = str(item.get('sku'))
                # print('sku is ',obj['sku'])
                sku_list.append(obj['sku'])
                # print(item.get('sku'))
                # print(type(item.sku))
                last_id += 1

                obj.update({'batch_id':batch_id,'user_id':user,'id':last_id,'created':created,'updated':updated,
                'network_id':network,'category_id':1,'gst_slab_id':1,'supplier_status':'Active','status':True})

                batch_products_arr.append(obj)

            print(po_type)
            if po_type == "branchOrdering":
                pass
            else:
                try:
                    print('inside requset try ')
                    url = "http://101.53.139.41:11300/v1/api/doesIsbnsExist"

                    payload = {}
                    # payload['isbns[]'] = sku_list
                    headers = {
                        'content-type': "application/x-www-form-urlencoded"
                        }
                    
                    tu = {"isbns[]":sku_list}
                    dataToPost = urllib.parse.urlencode(tu,True)
                    # print('data to oise is ',dataToPost)
                    response = requests.request("POST", url, data=dataToPost, headers=headers)
                    
                    # response_data['batchId'] = batch_id,
                    api_response = json.loads(response.text)

                    # api_response = ast.literal_eval(ddd)
                    print(api_response.get('status'))
                    if api_response['status']:
                        if len(api_response['successObject']['false']) > 0:
                            response_data['status'] = True
                            response_data['isIsbnValid'] = False
                            response_data['invalidIsbn'] = api_response['successObject']['false']
                            Batch.objects.filter(id=batch_id).delete()
                            return Response(response_data,status.HTTP_200_OK)    
                        else:
                            print('response from validate isbn is fine al isbn are valid procees nor')
                            pass
                    else:
                        response_data['status'] = False,
                        response_data['message'] = api_response['errorDescription']
                        Batch.objects.filter(id=batch_id).delete()
                        return Response(response_data,status.HTTP_500_INTERNAL_SERVER_ERROR)    
                
                except Exception as e:
                    print('inside requset exception ',e)

                    response_data['status'] = False,
                    response_data['message'] = 'unable to validate isbn, Server is not responding'
                    Batch.objects.filter(id=batch_id).delete()
                    return Response(response_data,status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            sku_csv = ','.join(sku_list)
            
            # inserting batch products in database
           
            d = MongoClass.createBatchProductFromCsv(batch_products_arr,'batchproduct',last_id)
            if po_type == "branchOrdering":
                print('ratings will be updated in background')
                
                dataToPost = {}
                dataToPost['to'] = "avinash@justbooksclc.com"
                dataToPost['from'] = "operations@justbooksclc.com"
                dataToPost['subject'] = "New Releases"
                dataToPost['body'] = f"We have uploaded Releases for this Month on MIS Portal with Batch Name {name}. <br/><br/> Please order books before {endDate}. Note: Super Lead title will be arranged on priority."
                dataToPost['cc'] = "ashish@freenet.zone"
                dataToPost['sender'] = "Prashanth.R" 

                sendmail = sendMail.delay(dataToPost)
                insertRatingsInBackground = get_data_from_goodreads_amazon_.delay(sku_csv)
            else:
                print('no background task for ratings') 
                
            response_data['batchId'] = batch_id,
            response_data['message'] = "success"
            response_data['isIsbnValid'] = True
            response_data['status'] = True
            
            return Response(response_data, status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            Batch.objects.filter(id=batch_id).delete()
            BatchProduct.objects.filter(batch=batch_id).delete()
            return Response('Internal Server Error',status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # if not csv_file.name.endswith('.csv'):
            # return Response('Please upload a .csv file',status.HTTP_406_NOT_ACCEPTABLE)


        
class CreateBpFields(ListAPIView):
    serializer_class =BPFieldMapperSerializer 
    def get(self,request,format=None): 
        # d = BPFieldMapper.objects.all()
        # serializer =BPFieldMapperSerializer(d)a
        print('====================')
        obj = CheckAmazonSimpleAPI()
        # print(data)
        return Response('data',status.HTTP_200_OK)

    def post(self,request,format=None):
        data = request.data
        bdata = BPFieldMapper.objects.create(network=Network(data['network']),
        user=User(data['user']),sys_key=data['sys_key'],
        user_key=data['user_key'])
        print(bdata)
        return Response('success',status.HTTP_200_OK)



class ChecKAmazonsimpleAPI():
    def __init__(self):
        from amazon.api import AmazonAPI
        self.dict_keys = {
            'secret-key':'0CA+6/lUnkcrvs86MBvBxULINgoZfMJRatYdrWT9',
            'access-key':'AKIAJEXEOBPXQDT43C3A',
            'AssociateTag':'gobuzzmobi-21'
        }
        print(self.dict_keys['access-key'])
        self.amazon = AmazonAPI(self.dict_keys['access-key'],self.dict_keys['secret-key'], self.dict_keys['AssociateTag'])
    
    def tester(self):
        print(self.amazon)
        self.product = self.amazon.search(Keywords = "Grey", SearchIndex = "Books")
        #  self.amazon.lookup(IdType='ISBN',ItemId='9780263933949')
        return self.product


class PoProductUpdateName(ListAPIView):
    def post(self,request,format=None):
        sku = request.data['sku']
        print(sku)
        data = MongoClass.get_data_with_sku('batchproduct',sku)
        pprint(data)
        name = ''
        for item in data:
            name = item['name']
        # serializer = BatchProductSerializer(data,many=True)
        # name = ''
        # pprint(serializer.data)
        # for item in serializer.data:
        #     name = serializer.data['name']     
        data  = PO_Product.objects.filter(sku=sku).update(name=name)   
        return Response('success',status.HTTP_200_OK)

class GetNewArrivalsPoList(ListAPIView):
    def get(self,request,*args,**kwargs):
        batch_data = Batch.objects.filter(po_type="newArrivals")
        serializer = BatchSerializer(batch_data,many=True)
        batch_id = []
        for item in serializer.data:
            batch_id.append(item['id'])

        po_data = MongoClass.get_po_for_new_arrivals_using_batch('po',batch_id)
        return Response(po_data,status.HTTP_200_OK)

class CreatePoForNewArrivals(ListAPIView):
    def post(self,request,format=None):

        return Response('success',status.HTTP_200_OK)


class UpdateBatchProDiscountByVendor(ListAPIView):
    def post(self,request,format=None):
        discount = int(request.data['discount'])
        batch_id = request.data['batch_id']

        data = BatchProduct.objects.filter(batch=batch_id).update(discount=discount)
        return Response('success',status.HTTP_200_OK)

class DonatedProductsList(ListAPIView):
    def get(self,request,*args,**kwargs):
        batch_id = self.kwargs['batchId']
        branch_id = self.kwargs['branchId']
        branch = Retail.objects.filter(branch=branch_id)
        branchSerializer = RetailerListSerializer(branch,many=True)
        print(branchSerializer.data)
        donated_pro = PO_GR.objects.filter(batch_id=batch_id,branch=branch_id)
        serializer = PO_GR_Catalogue_Serializer(donated_pro,many=True)
        return Response({
                'products':serializer.data,
                'branchName':branchSerializer.data
            } ,status.HTTP_200_OK)