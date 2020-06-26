from djongo import models

# from django.db import models
from decimal import Decimal

from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.template.defaultfilters import slugify
from rest_framework.authtoken.models import Token
from django.utils.crypto import get_random_string
from django import forms
# Create your models here.


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'media/document_{0}/{1}'.format(instance.user.username, filename)

def product_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'media/Image_{0}/{1}'.format(instance.user.username, filename)

def product(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'product_{0}/{1}'.format(instance.user.username, filename)


class Category(models.Model):
	name = models.CharField(max_length=255, blank=True, null=True)
	image = models.ImageField(upload_to='media', null=True)
	active = models.BooleanField(default=False)
       
	def __str__(self):
	    return str(self.name)




class Network(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='Network_Admin',on_delete=models.DO_NOTHING, null=True )
    network_company = models.CharField(max_length=100, blank=True, null=True )
    registered_address = models.CharField(max_length=100, blank=True, null=True )
    other_address = models.CharField(max_length=100, blank=True, null=True )
    contact_num = models.CharField(max_length=10, blank=True, null=True,)
    pan = models.CharField(max_length=256, blank=True, null=True)
    tan = models.CharField(max_length=256, blank=True, null=True)
    gst = models.CharField(max_length=256, blank=True, null=True)
    approved = models.BooleanField(default=False)



class GroupTaxName(models.Model):

	group_name = models.CharField(max_length=30, blank=True, null=True)
	visible_name = models.CharField(max_length=30, null=True, blank=True)
	cgst = models.CharField(max_length=30, null=True, blank=True)
	sgst = models.CharField(max_length=30, null=True, blank=True)
	cgst_percentage = models.DecimalField(max_digits=40,decimal_places=2,default=Decimal(('0.0')))
	sgst_percentage = models.DecimalField(max_digits=40,decimal_places=2,default=Decimal(('0.0')))

	 
	def __str__(self):
	    return str(self.group_name)





class Retail(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='Retail_Admin',on_delete=models.DO_NOTHING,  null=True )
    network_company = models.CharField(max_length=100, blank=True, null=True )
    registered_address = models.CharField(max_length=100, blank=True, null=True )
    other_address = models.CharField(max_length=100, blank=True, null=True )
    contact_num = models.CharField(max_length=10, blank=True, null=True,)
    approved = models.BooleanField(default=False)
    vendor = models.BooleanField(default=False) 
    name =  models.CharField(max_length=100, blank=True, null=True )
    branch = models.PositiveIntegerField(blank= True,null=True,default='')
    discount = models.PositiveSmallIntegerField(blank=True, default='')



class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ('Supplier', 'Supplier'),
        ('Retailer', 'Retailer'),
        ('NetworkAdmin', 'NetworkAdmin'),
        ('RetailAdmin', 'RetailAdmin'),
        ('Branch','Branch'),
        ('Admin', 'Admin'),
        ('Blank', 'Blank'),
    )

    ProfileStatus__CHOICES = (
        ('Approved', 'Approved'),
        ('Suspend', 'Suspend'),
        ('Hold', 'Hold'),
        ('Rejected', 'Rejected'),
        )

    type_user = models.CharField(max_length=50,choices=USER_TYPE_CHOICES,  default='Blank', null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='end_user_data',on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    contact_num = models.CharField(max_length=10, blank=True, null=True,)
    approved = models.BooleanField(default=False)
    
    verify_code = models.CharField(max_length=40, blank=True)
    verify_email = models.BooleanField(default=False, blank=True)
    verify_email_datetime = models.DateTimeField(default=datetime.now)

    verify_mob_code = models.CharField(max_length=40, blank=True)
    verify_mobile = models.BooleanField(default=False, blank=True)
    verify_mobile_datetime = models.DateTimeField(default=datetime.now)
    verify_changeNum_code = models.CharField(max_length=6, blank=True, null=True)
    profile_status = models.CharField(max_length=50,choices=ProfileStatus__CHOICES, default='Suspend', null=True)
    admin_note = models.CharField(max_length=500, blank=True, null=True)
    network = models.ForeignKey(Network, null=True, on_delete=models.DO_NOTHING)
    retailer = models.ForeignKey(Retail, null=True, on_delete=models.DO_NOTHING)
    branch = models.PositiveIntegerField(null=True,blank=True)

    
    def __unicode__(self):  
        return str(self.user.first_name + ' ' + self.user.last_name )

    def __str__(self):
        return str(self.user.first_name + ' ' + self.user.last_name )

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_user_profile(sender, instance, created, **kwargs):
    if  created:
        Profile.objects.create(user=instance,
                verify_code=get_random_string(length=40), 
                verify_mob_code=get_random_string(length=40)
            )


class Document(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    pan = models.ImageField(upload_to=user_directory_path,  blank=True, null=True)
    shop = models.ImageField(upload_to=user_directory_path,  blank=True, null=True)
    photography = models.ImageField(upload_to=user_directory_path,  blank=True, null=True)
    cheque = models.ImageField(upload_to=user_directory_path,  blank=True, null=True)
    licence = models.ImageField(upload_to=user_directory_path,  blank=True, null=True)

class Product(models.Model):

    product_status = (
        ('Active', 'Active'),
        ('InActive', 'InActive'),
        ('Draft', 'Draft'),
        ('UnderMaintenance', 'Maintenance'),
    )

    category  = models.ForeignKey(Category, null=True, on_delete=models.DO_NOTHING)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)
    gst_slab = models.ForeignKey(GroupTaxName, null=True, on_delete=models.DO_NOTHING)    
    supplier_status = models.CharField(max_length=30, choices=product_status, default='InActive')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, default='')
    sku = models.CharField(max_length=255, blank=True, default='', unique=True,)
    supplier_name = models.CharField(max_length=100, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    active = models.BooleanField(blank=True, default=False)
    

    #def save(self, *args, **kwargs):
        #super(Product, self).save(*args, **kwargs)

@receiver(post_save, sender=Product)
def active_product(sender, instance=None, created=False, **kwargs):
    if created:
        product_status = Product.objects.get(id=instance.id).product_status
        print("product_status", product_status)

        if (product_status=='Active'):
            Product.objects.filter(
                    id=instance.id
                    ).update(
                    active=True
                    )
        else:
            if (product_status=="InActive"):
                Product.objects.filter(
                    id=instance.id
                    ).update(
                    active=False
                    )

class Batch(models.Model):
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.DO_NOTHING)
    # network = models.ForeignKey(Network, null=True, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255, blank=True, default='')
    description = models.CharField(max_length=255, blank=True, default='')
    status = models.BooleanField(blank=True, default=False)
    delete = models.BooleanField(blank=True,default=False)
    po_type =  models.CharField(max_length=255, blank=True, default='')


class BPFieldMapper(models.Model):

    system_fields = (
        ('sku', 'sku'),
        ('name', 'name'),
        ('mrp', 'mrp'),
        ('discount', 'discount'),
        ('leadType', 'leadType'),
        ('circulation', 'circulation'),
        ('copies_purchased', 'copies_purchased'),
        ('category', 'category'),
        ('release', 'release'),
        ('author_rating','author_rating'),
        ('author','author'),
        ('goodreads','goodreads'),
        ('publisher','publisher'),
        ('others','others')
    )

    network = models.ForeignKey(Network, null=True, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.DO_NOTHING)
    sys_key = models.CharField(max_length=30, choices=system_fields, default='Active')
    user_key = models.CharField(max_length=255, blank=True, default='')
            

class BatchProduct(models.Model):
    product_status = (
        ('Active', 'Active'),
        ('InActive', 'InActive'),
        ('Draft', 'Draft'),
        ('UnderMaintenance', 'Maintenance'),
    )
    batch_status = (
        ('Ordered','Ordered')
    )
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)
    category  = models.ForeignKey(Category, null=True, on_delete=models.DO_NOTHING)
    gst_slab = models.ForeignKey(GroupTaxName, null=True, on_delete=models.DO_NOTHING)    
    supplier_status = models.CharField(max_length=30, choices=product_status, default='Active')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    network = models.ForeignKey(Network, null=True, on_delete=models.DO_NOTHING)
    batch = models.ForeignKey(Batch, null=True, on_delete=models.CASCADE)
    sku = models.CharField(max_length=255, blank=True, default='' )
    name = models.CharField(max_length=255, blank=True, default='')
    mrp = models.PositiveSmallIntegerField(blank=True, default='')
    discount = models.PositiveSmallIntegerField(blank=True, default='')
    qty = models.PositiveSmallIntegerField(blank=True, default=''),
    status = models.BooleanField(blank=True,default=True)


    

class Branch_Request(models.Model):
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)
    network  = models.ForeignKey(Network, null=True, on_delete=models.DO_NOTHING)
    retail = models.ForeignKey(Retail, null=True , on_delete = models.DO_NOTHING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, null=True, on_delete=models.DO_NOTHING)
    branch = models.PositiveIntegerField(null=True,blank=True)
    # name = models.CharField(max_length=255, blank=True, default='')
    # description = models.CharField(max_length=255, blank=True, default='')


    
class Branch_Request_Product(models.Model):
    
    STATUS__CHOICES = (
        ('Inprocess', 'Inprocess'),
        ('Requested', 'Requested'),
        ('Delivered', 'Delivered'),
        ('Ordered', 'Ordered'),
        ('Purchased', 'Purchased'),
        ('Jacketting In Progress', 'Jacketting In Progress'),
        )

    sku = models.CharField(max_length=255, blank=True, default='' )
    name = models.CharField(max_length=255, blank=True, null=True)
    mrp = models.PositiveSmallIntegerField(blank=True, default='')
    qty = models.PositiveSmallIntegerField(blank=True, default='')
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, null = True, on_delete = models.DO_NOTHING)
    discount = models.PositiveSmallIntegerField(blank=True, default='')
    status = models.CharField(max_length=50,choices=STATUS__CHOICES, default='Requested', null=True)
    # retailer = models.ForeignKey(Retail, null=True, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(BatchProduct,null=True, on_delete = models.DO_NOTHING)
    subTotal = models.PositiveSmallIntegerField(blank=True,default = '')
    branch_req = models.ForeignKey(Branch_Request,null=True, on_delete = models.DO_NOTHING)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)


class PO(models.Model):
    batch = models.ForeignKey(Batch,null=True,on_delete=models.DO_NOTHING)
    vendor = models.ForeignKey(Retail, null= True, on_delete = models.DO_NOTHING)
    qty = models.PositiveSmallIntegerField(blank=True, default='')
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)
    received = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, default='' )
    totalAmount = models.DecimalField(blank=True, default='',max_digits=8,decimal_places=2)


class PO_Product(models.Model):
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)
    sku = models.CharField(max_length=255, blank=True, default='' )
    qty = models.PositiveSmallIntegerField(blank=True, default='')
    mrp = models.PositiveSmallIntegerField(blank=True, default='')
    branch =models.PositiveIntegerField(null=True,blank=True)
    batch = models.ForeignKey(Batch,null=True,on_delete=models.DO_NOTHING)
    po =  models.ForeignKey(PO,null=True,on_delete=models.DO_NOTHING)
    receivedqty = models.PositiveSmallIntegerField(blank=True, default=0)
    name = models.CharField(max_length=255, blank=True, default='' )
    discount = models.PositiveSmallIntegerField(blank=True, default=0)
    discountAmount = models.DecimalField(blank=True, default=0,max_digits=8,decimal_places=2)
    netTotal = models.DecimalField(blank=True, default=0,max_digits=8,decimal_places=2)



class PO_GR(models.Model):
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)
    sku = models.CharField(max_length=255, blank=True, default='' )
    invoice_num = models.CharField(max_length=50,blank=False, null=True)
    invoice_amt = models.CharField(max_length=50,blank=False, null=True)
    po = models.ForeignKey(PO,null=True, on_delete= models.DO_NOTHING)
    item_number = models.CharField(max_length=255, blank=True, default=0)
    branch = models.PositiveIntegerField(null=True,blank=True,default=0)
    status = models.CharField(max_length=255, blank=True, default='')
    batch = models.ForeignKey(Batch,null=True, on_delete= models.DO_NOTHING)


