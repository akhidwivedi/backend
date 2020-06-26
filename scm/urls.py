"""example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, routers
from rest_framework.authtoken.views import ObtainAuthToken
from django.conf import settings
from django.conf.urls.static import static

from api.views import ( Pdf, ManualBPListAPIView, ProfileListApiView, UpdateUserProfile, ChangeProfileMobileNumAPI,TestGetOrCreate,
    ApproveProfileViewByAdminAPI, BatchUpdateAPIView, BatchDeleteAPIView,LatestActiveBatchAPIView,POListForCatalogueAPIView,
    BatchListByDonationAPIView,CatalogueUsingBatchAPIView,BranchRequestProductByBatchAPIView,BatchProductsListAsPerBranchRequest,
    BatchProductDetailAPIView, BatchProductListbyIdAPIView, BPListAPIView,BranchRequestListAPIView,UpdateOrderPlacedAPIView,
        BatchProductListAPIView, PO_ProductDetailAPIView, PO_ProductListAPIView, PO_ProductListbyBatchAPIView, 
        CustomObtainAuthToken, ProductDetailAPIView, ProductListAPIView, BatchListAPIView, ActiveBatchListAPIView,BatchDetailAPIView,
        BatchUpdateAPIView, PlaceOrderAPIView,CatalogueUpdateGrAndPo_ProAPIView,GetAllBranchesAPIView,UpdateBatchProDiscountByVendor,
        BranchRequestProductAPIView,BranchRequestByBatchAPIView,BranchRequestForBranchAPIView,GeneratePOAPIView,BPFieldMapperAPIView,RetailListAPIView,VendorListAPIView,
        CreatePOUsingFile,PO_ProductAPIView,POListApiView,POListByVendorApiView,PO_GRListAPIView,GetBranchesForCatalogue,CreatePoGrAPIView,
        GenerateReportForCatalogueDBook,CreatePOListAPIView,BatchProductModalView,PO_product_by_po,PO_product_by_po_pdf,
        CreateBatchAndBatchProductsViaFile,CreateBpFields,PoProductUpdateName,GetNewArrivalsPoList,CreatePoForNewArrivals,
        DonatedProductsList,InboundPoListApiView)

from django.conf import settings
# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^api/v1/token/', ObtainAuthToken.as_view()),

    
    
    # url(r'^api/v1/token/', CustomObtainAuthToken.as_view()),
    url(r'^api/v1/profile/$', ProfileListApiView.as_view()),

    url(r'^api/v1/signupuserprofile/(?P<uid>\d+)/', UpdateUserProfile.as_view()),
    url(r'^api/v1/ChangeProfileMobileNum/$', ChangeProfileMobileNumAPI.as_view()),
    url(r'^admin/api/v1/ApproveProfile/', ApproveProfileViewByAdminAPI.as_view()),

    url(r'^api/v1/po__pdf/(?P<id>\d+)/$', Pdf.as_view()),

    # path('admin/', admin.site.urls),
    url(r'^drf/', include(router.urls)),
    #url(r'^docs/', include(rest_framework_docs.urls)),
    #url(r'^', include(router.urls)),
    #url(r'^docs/', include_docs_urls(title='My API title')), 
    #url(r'^docs/', include('rest_framework_docs.urls'), name='docs'),

    url(r'^', admin.site.urls),

    # url(r'^admin/', admin.site.urls),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    url(r'^api/v1/products/(?P<id>\d+)/$', ProductDetailAPIView.as_view()),
    url(r'^api/v1/products/$', ProductListAPIView.as_view()),
    url(r'^api/v1/createMappers/$', CreateBpFields.as_view()),
    

    url(r'^api/v1/batchproducts/(?P<id>\d+)/$', BatchProductDetailAPIView.as_view()),
    url(r'^api/v1/batchproducts/$', BatchProductListAPIView.as_view()),
    url(r'^api/v1/createBatch/$', CreateBatchAndBatchProductsViaFile.as_view()),
    
    url(r'^api/v1/batchstatus/(?P<id>\d+)/$', BatchUpdateAPIView.as_view()),
    url(r'^api/v1/latestActiveBatch/(?P<uid>\d+)/$', LatestActiveBatchAPIView.as_view()),


    url(r'^api/v1/batchproductsbyid/(?P<bid>\d+)/$', BPListAPIView.as_view()),
    
    url(r'^api/v1/manualbatchproduct/(?P<bid>\d+)/$', ManualBPListAPIView.as_view()),

    url(r'^api/v1/placeOrderForBatchProducts/(?P<bid>\d+)/(?P<uid>\d+)/$', BatchProductsListAsPerBranchRequest.as_view()),

#         axios.get(url+`placeOrderForBatchProducts/${item.id}/`, authHeader)
# BatchProductsListAsPerBranchRequest
    # url(r'^api/v1/po_product/(?P<bid>\d+)/$', PO_ProductListbyBatchAPIView.as_view()),    
    url(r'^api/v1/po_product/(?P<id>\d+)/$', PO_ProductDetailAPIView.as_view()),

    url(r'^api/v1/placeOrder/$', PlaceOrderAPIView.as_view()),
    url(r'^api/v1/updatePlaceOrder/$',UpdateOrderPlacedAPIView.as_view()),

    url(r'^api/v1/po_product/$', PO_ProductListAPIView.as_view()),
    url(r'^api/v1/po_product_by_poid/(?P<id>\d+)/$', PO_product_by_po.as_view()),
    url(r'^api/v1/po_product_by_poid_for_pdf/(?P<id>\d+)/$', PO_product_by_po_pdf.as_view()),

    url(r'^api/v1/batch/(?P<id>\d+)/$', BatchDetailAPIView.as_view()),
    url(r'^api/v1/batch/$', BatchListAPIView.as_view()),
    url(r'^api/v1/getActiveBatch/$', ActiveBatchListAPIView.as_view()),

    url(r'^api/v1/donationBatchList/$', BatchListByDonationAPIView.as_view()),
    url(r'^api/v1/batchdelete/(?P<id>\d+)/$', BatchDeleteAPIView.as_view()),
    
    url(r'^api/v1/test/$', TestGetOrCreate.as_view()),
    url(r'^api/v1/getAllBranchRequestList/$', BranchRequestListAPIView.as_view()),

    url(r'^api/v1/getAllBranchRequestList/(?P<bid>\d+)/$', BranchRequestByBatchAPIView.as_view()),
    url(r'^api/v1/getBranchRequestList/(?P<batchid>\d+)/(?P<branch>\d+)/$', BranchRequestForBranchAPIView.as_view()),

    url(r'^api/v1/branchRequestedProduct/(?P<id>\d+)/$', BranchRequestProductAPIView.as_view()),
    url(r'^api/v1/generatePO/(?P<bid>\d+)/$', GeneratePOAPIView.as_view()),
    url(r'^api/v1/getFieldmap/$', BPFieldMapperAPIView.as_view()),
    url(r'^api/v1/getVendorMetadata/$', RetailListAPIView.as_view()),

    url(r'^api/v1/getVendorDetails/$', VendorListAPIView.as_view()),

    url(r'^api/v1/createPoUsingFile/$', CreatePOUsingFile.as_view()),
    # url(r'^api/v1/get_po_product_list/(?P<po_id>\d+)/$', PO_ProductAPIView.as_view()),

    # url(r'^api/v1/get_po_product_list/(?P<po_id>\d+)/(?P<flag>\d+)/(?P<branch>\d+)/$', PO_ProductAPIView.as_view()),
    url(r'^api/v1/get_po_product_list/(?P<po_id>\d+)/$', PO_ProductAPIView.as_view()),
    
    url(r'^api/v1/get_all_po_list/$', POListApiView.as_view()),
    url(r'^api/v1/get_all_po_list_for_catalogue/$', POListForCatalogueAPIView.as_view()),
    url(r'^api/v1/get_po_list_by_vendor/(?P<id>\d+)/$', POListByVendorApiView.as_view()),
    url(r'^api/v1/get_inbound_po_list/(?P<branch>\d+)/$', InboundPoListApiView.as_view()),
    # get_inbound_po_list

    url(r'^api/v1/getAllNewArrivalsPo/$', GetNewArrivalsPoList.as_view()),
    url(r'^api/v1/createPoForNewArrivals/$',CreatePOListAPIView.as_view()),
    # url(r'^api/v1/create_gr/$', PO_GRListAPIView.as_view()),
    url(r'^api/v1/getBranch/(?P<po_id>\d+)/(?P<sku>\d+)/$', GetBranchesForCatalogue.as_view()),
    url(r'^api/v1/getAllBranches/$', GetAllBranchesAPIView.as_view()),
    url(r'^api/v1/creategr/$', CreatePoGrAPIView.as_view()),
    url(r'^api/v1/createPoWithoutFile/$', CreatePOListAPIView.as_view()),
    url(r'^api/v1/createCatalogue/$', CatalogueUpdateGrAndPo_ProAPIView.as_view()),
    url(r'^api/v1/createCatalogueUsingBatch/$', CatalogueUsingBatchAPIView.as_view()),
    url(r'^api/v1/generateReport/(?P<batchId>\d+)/$', GenerateReportForCatalogueDBook.as_view()),
    url(r'^api/v1/branch_request_product_using_batch_id/(?P<batchId>\d+)/$', BranchRequestProductByBatchAPIView.as_view()),
    # url(r'^api/v1/testcrawler/(?P<batchid>\d+)/$', TestAmazonCrawler.as_view()),
    url(r'^api/v1/getDataForPlaceOrderViewModal/(?P<batch_id>\d+)/$', BatchProductModalView.as_view()),
    url(r'^api/v1/updateNamePOPro/$', PoProductUpdateName.as_view()),
    url(r'^api/v1/updateBatchProOnSelectionVendor/$', UpdateBatchProDiscountByVendor.as_view()),
    url(r'^api/v1/getDonatedProducts/(?P<batchId>\d+)/(?P<branchId>\d+)/$',DonatedProductsList.as_view()),
    # url(r'^api/v1/getGoodReads/(?P<id>\d+)/$',GoodReadsRatingAPIView.as_view()),

    # url(r'^api/v1/getBranchRequest/$', BranchRequestAPIView.as_view()),
    # url(r'^api/v1/getBranchRequestProduct/$', BranchRequestProductAPIView.as_view()),
    #url(r'^jet/v1/', include('jet.urls', 'jet')),  # Django JET URLS
    #url(r'^jet/v1/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    #url(r'^admin/', include(admin.site.urls)),    



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
