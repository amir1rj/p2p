from django.contrib import admin

from vendor.models import Vendor, VendorImage


class VendorImageInline(admin.TabularInline):
    model = VendorImage
    extra = 1

# Register your models here.


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ["user", "description", "status"]
    list_editable = ["status"]
    inlines = [VendorImageInline]
