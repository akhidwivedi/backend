from rest_framework.serializers import (     CharField,EmailField,
	HyperlinkedIdentityField,
	ModelSerializer,
	SerializerMethodField,
	ValidationError,


	)

from pprint import pprint

from rest_framework import serializers
from rest_framework import fields, serializers

from api.models import (BPFieldMapper, BatchProduct, Product,  Category, Profile, Branch_Request, Batch, Branch_Request_Product,
                                    PO_GR, User, GroupTaxName, Document, Retail,PO,PO_Product
                                    # BranchRequest, BranchRequestedProduct,MetaData
                                    )

class SignUpUserSerializer(serializers.ModelSerializer):
  
  class Meta:
    model=User
    # fields='__all__'
    fields=[
        'id',
        # 'username',
        'first_name',
        'last_name',
        'password',
        'email'
    ]
    extra_kwargs = {'password': {'write_only': True}}
  
  def create(self, validated_data):
    user = User(
        email=validated_data['email'],
        username=validated_data['email'],
        password=validated_data['password'],
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name']
    )
 
    user.set_password(validated_data['password'])
    user.save()
    return user


class UserSerializer(serializers.ModelSerializer):
  # date_joined = serializers.DateTimeField(format=None, input_formats=None)
  # last_login = serializers.DateTimeField(format=None, input_formats=None)
  class Meta:
      model=User
      fields=[
        'id',
        'username',
        'password',
        'first_name',
        'last_name',
        'email',
        # 'wallet'
        # 'date_joined',
        # 'last_login',
      ]


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name',)

    def name(self, object):
      return self.name    


class ChangeProfileMobileNumSerializer(serializers.ModelSerializer):
    contact_num = serializers.CharField(required=True, max_length=10)
    
    class Meta:
        model = Profile
        fields = ('contact_num',)

        
class BranchRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch_Request
        fields = ('id', 'name','batch','vendor','desc')

    def name(self, object):
      return self.name

class BranchRequestSerializerNew(serializers.ModelSerializer):
  batchname = serializers.SerializerMethodField()
  retailername = serializers.SerializerMethodField()
  class Meta:
      model = Branch_Request
      fields = ('id','created','updated','network','retail','retailername','user','batch','branch','batchname')

  def get_batchname(self,object):
    
    return object.batch.name

  def get_retailername(self,object):
    print(object.retail)
    return object.retail.name

  def __str__(self):
      return str(self.batch.name)
  
  def create(self, validated_data):
      
    return Branch_Request.objects.create(**validated_data)

class BranchRequestSerializerUpdate(serializers.ModelSerializer):
  batchname = serializers.SerializerMethodField()
  retailername = serializers.SerializerMethodField()
  class Meta:
      model = Branch_Request
      fields = ('id','created','updated','network','retail','retailername','user','batch','branch','batchname')

  def get_batchname(self,object):
    
    return object.batch.name

  def get_retailername(self,object):
    print(object.retail)
    return object.retail.name

  def __str__(self):
      return str(self.batch.name)

  def get_or_create(self, validated_data):
      
    return Branch_Request.objects.create(**validated_data,defaults={'created':datetime.now,'updated':datetime.now})


class PO_Gr_Serializer(serializers.ModelSerializer):
  class Meta:
    model = PO_GR
    fields = ('__all__')

  def returnId(self,object):
    return self.id

  def create(self, validated_data):
      
    return PO_GR.objects.create(**validated_data)

class PO_GR_Catalogue_Serializer(serializers.ModelSerializer):
  batchName = serializers.SerializerMethodField()
  class Meta:
    model = PO_GR
    fields = ('item_number','sku','branch','status','created','batchName')

  def returnId(self,object):
    return self.id

  def get_batchName(self,obj):
    return obj.batch.name

class UserNameSerializer(serializers.ModelSerializer):
  class Meta:
      model=User
      fields=(
        'id',
        'first_name',
        'last_name'
      
      )

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ("type_user",
                  "user",
                  'registered_company',
                  'registered_address',
                  'other_address',
                  'contact_num',
                  'pan',
                  'tan',
                  'gst',
                  'approved',
                  'verify_mobile',
                  'admin_note',
                  'profile_status',
                  )
    
    # def get_user(self, obj):
    #   return obj.user.username        

class RetailerListSerializer1(serializers.ModelSerializer):
  # user = UserNameSerializer()
  class Meta:
    model = Retail
    fields = ('__all__')
      
class RetailerListSerializer(serializers.ModelSerializer):

  username = serializers.SerializerMethodField()
  email = serializers.SerializerMethodField()
  class Meta:
    model = Retail
    fields = ('id','username','vendor','email','name','discount')

  def get_username(self,obj):
    return obj.user.first_name    
  
  def get_email(self,obj):
    return obj.user.email
        

class VendorListSerializer(serializers.ModelSerializer):

  # email = serializers.SerializerMethodField()
  class Meta:
    model = Retail
    fields = ('id','contact_num','vendor','name','discount')


        
class PO_Serializer(serializers.ModelSerializer):
  vendorName = serializers.SerializerMethodField()
  poType = serializers.SerializerMethodField()
  batchName = serializers.SerializerMethodField()

  class Meta:           
    model = PO
    fields = ('id','qty','created','batch','vendor','vendorName','name','poType','totalAmount','batchName')

  def create(self,validated_data):
    return PO.objects.create(**validated_data)

  def get_vendorName(self,obj):
    return obj.vendor.name

  def get_poType(self,obj):
    return obj.batch.po_type

  def get_batchName(self,obj):
    return obj.batch.name

class PO_Product_Serializer(serializers.ModelSerializer):
  # branchname = serializers.SerializerMethodField()
  class Meta:
    model = PO_Product
    fields = ('__all__')




class Branch_Request_ProductSerializer(serializers.ModelSerializer):

  class Meta:
    model = Branch_Request_Product
    fields =( '__all__')

  def create(self, validated_data):
      
      return Branch_Request_Product.objects.create(**validated_data)

class Branch_Request_ProductSerializerNew(serializers.ModelSerializer):
  branch = serializers.SerializerMethodField()
  branchName = serializers.SerializerMethodField()
  class Meta:
    model =Branch_Request_Product
    fields = ('sku','qty','mrp','status','product','name','discount','branch','branchName')  

  def get_branch(self,object):
    return object.branch_req.branch    

  def get_branchName(self,object):
    return object.branch_req.retail.name    

class ProductSerializer(serializers.ModelSerializer):

  class Meta:
    model = Product
    fields =( '__all__')

  def create(self, validated_data):
      
      return Product.objects.create(**validated_data)


class BPFieldMapperSerializer(serializers.ModelSerializer):

  class Meta:
    model = BPFieldMapper
    fields =('__all__')

  def create(self, validated_data):
      
      return BPFieldMapper.objects.create(**validated_data)
      

class BPFieldMapperSerializerNew(serializers.ModelSerializer):
  class Meta:
      model = BPFieldMapper
      fields = ['user_key','sys_key']

class BatchProductSerializer(serializers.ModelSerializer):

  class Meta:
    model = BatchProduct
    fields =( '__all__')

  def create(self, validated_data):
      
      return BatchProduct.objects.create(**validated_data)

class BatchProductSerializer1(serializers.ModelSerializer):
    
  class Meta:
    model = BatchProduct
    fields =['id','sku']

    def get_id(self,obj):
        return obj.id


class BatchSerializer(serializers.ModelSerializer):

  class Meta:

    model = Batch
    fields =( '__all__')

  def create(self, validated_data):
      
      return Batch.objects.create(**validated_data)
        




class UpdateProductSlotsSerializer(serializers.ModelSerializer):
    class Meta:
      model = Product
      fields = [
          'user',
          'name',
          'category',
          'shared_private',
          'overview', 
          'inclusions', 
          'exclusions', 
          'highlights', 
          'requirments', 
          'cancellation_policy', 
          'active', 
          'supplier_status', 
          'max_booking', 
          'setting_contact_name',
          'setting_contact_number', 
          'setting_all_booking_fields', 
          'setting_travellers_name',
          'setting_travellers_age', 
          'setting_travellers_sex', 
          'setting_travellers_rap_number',
          'setting_travellers_nationality', 
          'setting_medical_condtion', 
          'setting_booking_agent_name'
      ]


class ManageProductSerializer(serializers.ModelSerializer):
    
    category = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'admin_status', 'supplier_status', 'category', )

    def get_category(self, object):
      return object.category.name
    


class VisibleInProductSerializer(serializers.ModelSerializer):
  category = serializers.SerializerMethodField()

  class Meta:
    model = Product
    fields = (
          'id',
          'name',
          'image_1',
          'image_2',
          'image_3',
          'display_price',
          'adult_price',
          'infant_price',
          'child_price',
          'supplier_name',
          'duration_days',
          'duration_hours',
          'duration_minutes',
          'duration_date_time',
          'category',
          'inclusions',
          'exclusions',
          'cancellation_policy',
          'overview',
          'age_requirements',

    )

  def get_category(self, object):
      return object.category.name
    


 
class ProductNameIDSerializer(serializers.ModelSerializer):
    class Meta:
      model = Product
      fields = ('id', 'name')

class UserProductNameSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = ( 'id', 'name')

class AdminNestedProductSlotsSerializer(serializers.ModelSerializer):
    
    category_name = serializers.SerializerMethodField()
    
    supplier_name = serializers.SerializerMethodField()
    supplier_code = serializers.SerializerMethodField()
      
    class Meta:
        model = Product
        fields = ('id', 
                  'name', 
                  'category', 
                  'category_name', 
                  'location_name', 
                  'admin_status',
                  'supplier_status',
                  'supplier_name',
                  'supplier_code', 
                  'slot'
                  # 'location_id', 
                  )

    def get_category_name(self, object):
      return object.category.name

    def get_category_name(self, object):
      return object.category.name

    def get_supplier_code(self, obj):

      supplier_details = Profile.objects.filter(user_id=obj.user_id
                                            ).values('userID')
      UserID = supplier_details.first()
      return UserID

    def get_supplier_name(self, obj):                
      supplier_details = User.objects.filter(id=obj.user_id
                                            ).values('first_name', 'last_name')
      name = supplier_details.first()
      return name

class ProductItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
          '__all__'
      )


class ListProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ( '__all__' )
        
    
    def get_gst_slab(self, obj):
      return obj.gst_slab.group_name

    

class DocumentUploadSerializer(serializers.ModelSerializer):
  
  class Meta:
      model = Document
      fields = ('id', 
                'user', 
                'pan', 
                'shop', 
                'photography', 
                'cheque', 
                'licence'
                )


class ChangePasswordSerializer(serializers.ModelSerializer):
    
    change_password1 = serializers.CharField(required=True)
    change_password2 = serializers.CharField(required=True)
    
    class Meta:
      model=User
      fields = ('change_password1' ,'change_password2')


class GroupTaxNameSerializer(serializers.ModelSerializer):
    class Meta:
      model=GroupTaxName
      fields= '__all__'



class PasswordResetRequestSerializer(serializers.ModelSerializer):
    email = serializers.CharField(label ="email", max_length=30)
    class Meta:

        model = User
        fields = ("email", )


class PasswordResetSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(label ="password", max_length=30)
    password2 = serializers.CharField(label ="password", max_length=30)

    class Meta:

        model = User
        fields = ("password1", 'password2',)



class LastProductCreatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", )




from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class PermissionSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Permission
    fields = '__all__'



class GroupSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Group
    fields = '__all__'



class NewSignUpViewSerializer(serializers.ModelSerializer):
  name = serializers.SerializerMethodField()
  email = serializers.SerializerMethodField()
  created_at = serializers.SerializerMethodField()
  
  class Meta:
    model = Profile
    fields = ("created_at", 
              'name', 
              'email',
              'contact_num',
              'type_user',
              'user_id',
              ) 

  def get_name(self, obj):
    return (obj.user.first_name + ' ' + obj.user.last_name)  

  def get_email(self, obj):
    return obj.user.username

  def get_created_at(self, obj):
    return obj.user.date_joined


class ProfileUsernameSerializer(serializers.ModelSerializer):
  first_name = serializers.SerializerMethodField()
  last_name = serializers.SerializerMethodField()
  class Meta:
    model=Profile
    fields = ('user_id', 'type_user', 'first_name', 'last_name', 'userID')

  def get_first_name(self, obj):
      return obj.user.first_name
  
  def get_last_name(self, obj):
      return obj.user.last_name


class ActiveProductListSerializer(serializers.ModelSerializer):

  class Meta:
    model = Product
    fields = '__all__'

# class BranchRequestSerializer(serializers.ModelSerializer):
#   class Meta:
#     model=BranchRequest
#     fields = '__all__'

# class BranchRequestedProductSerializer(serializers.ModelSerializer):
#   class Meta:
#     model = BranchRequestedProduct
#     fields= '__all__'

#   def create(self,validated_data):
#     pprint(validated_data)
#     # meta_data = MetaData(validated_data['meta'])
#     return BranchRequestedProduct.objects.create(**validated_data)