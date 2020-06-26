from django.contrib import admin
from django.contrib.auth.models import Group

# Register your models here.

from .models import (BPFieldMapper,
	BatchProduct, Batch, Product, Profile, Category, GroupTaxName, Network, Retail, Branch_Request, Branch_Request_Product, 
	# BranchRequest, BranchRequestedProduct
	)

#from .methods import (ExportCsvMixin, ProductUpload)
from .methods import (ExportCsvMixin)


import csv
import sys
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.urls import path, reverse

from django import forms


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


class ImportCsvMixin:

    pass


class ProductForm(forms.ModelForm):
    category_name = forms.CharField()

    class Meta:
        model = Product
        exclude = ["category"]

class CategoryChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "Category: {}".format(obj.name)


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


#@admin.register(Product)

class HeroAdmin(admin.ModelAdmin, ExportCsvMixin):

    change_list_template = "entities/heroes_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            reader = csv.reader(csv_file)
            # Create Hero objects from passed in data
            # ...
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/csv_form.html", payload
        )





class RetailAdmin(admin.ModelAdmin):
	list_display = ("id",
					"network_company",
					"registered_address",
	                'contact_num',
	                'approved',
	                )

	list_filter = ('user', 'approved',)
	search_fields = ('user__username',
					 'network_company',
					 'contact_num',
					 
					)

	ordering = ('-id',)	



class NetworkAdmin(admin.ModelAdmin):
	list_display = ("id",
					"network_company",
					"registered_address",
	                'contact_num',
	                'approved',
	                )

	list_filter = ('user', 'approved',)
	search_fields = ('user__username',
					 'network_company',
					 'contact_num',
					 
					)

	ordering = ('-id',)	


class BPFieldMapperAdmin(admin.ModelAdmin):
	list_display =('id',
			      'user',
			      'network',
			      'sys_key',
			      'user_key',
			    )

	ordering = ('-id', )
	list_filter = ('network', "user__username")
	search_fields =(  
				   'user',
			      'network',
			      'sys_key',
			      'user_key',
			      )

	


class BatchProductsAdmin(admin.ModelAdmin):
	list_display =('id',
			      'user',
			      'gst_slab',
			      'name',
			      'category',
			      
			    )

	ordering = ('-id', )
	list_filter = ('name', "user__username")
	search_fields =(  
					  'user',
			      'gst_slab',
			      'name',
			      'category',
			      
			      )



class ProductsAdmin(admin.ModelAdmin):
	list_display =('id',
			      'user',
			      'gst_slab',
			      'name',
			      'category',
			      
			    )

	ordering = ('-id', )
	list_filter = ('name', "user__username")
	search_fields =(  
					  'user',
			      'gst_slab',
			      'name',
			      'category',
			      
			      )


class BatchAdmin(admin.ModelAdmin):
	list_display =('id',
			      'user',
			      'description',
			      'name',
			      'status',
			      
			    )

	ordering = ('-id', )
	list_filter = ('name', "user__username")
	search_fields =(  
				  'user',
			      'description',
			      'name',
			      'status',
			      
			      )



class CategoryAdmin(admin.ModelAdmin):
	list_display =('id', 'name', 'image')
	ordering = ('-id',)



class ProfileAdmin(admin.ModelAdmin):
	list_display = ("id",
					"type_user",
					"user",
	                'contact_num',
	                'approved',
	                )

	list_filter = ('user', 'approved',)
	search_fields = ('user__username',
					 'type_user',
					 'contact_num',
					 
					)

	ordering = ('-id',)	


class GroupTaxNameAdmin(admin.ModelAdmin):
	list_display = ('id', 'group_name', 'visible_name', 
					'cgst', 'sgst', 'sgst_percentage', 
					'cgst_percentage'  
				)

	ordering = ('id',)

class PurchaseOrderProducts(admin.ModelAdmin):
	list_display = ('id','name','mrp','sku','status',
					'qty','discount',
					'batch','branch_req','product'
				)
	
	ordering = ('id',)

class PurchaseOrder(admin.ModelAdmin):
	list_display = ('id','created','updated',
					'network','retail','user'	
				)
	
	ordering = ('id',)


admin.site.register(Product, ProductsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(GroupTaxName, GroupTaxNameAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Retail, RetailAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(BatchProduct, BatchProductsAdmin)
admin.site.register(BPFieldMapper, BPFieldMapperAdmin)
admin.site.register(Branch_Request, PurchaseOrder)
admin.site.register(Branch_Request_Product,PurchaseOrderProducts)
# admin.site.register([BranchRequest,BranchRequestedProduct])
#admin.site.register(ProductUpload, HeroAdmin)


