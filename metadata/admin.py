"""
Administration system hooks for the `metadata` application.

"""

from django.contrib import admin

from metadata.admin_base import TextMetadataInline
from metadata.admin_base import ImageMetadataInline

from metadata.models import MetadataKey
from metadata.models import PackageTextMetadata, PackageImageMetadata
from metadata.models import Package


## MetadataKey ##

class MetadataKeyAdmin(admin.ModelAdmin):
    """
    An adminstration snap-in for maintaining the list of metadata
    keys.

    """
    list_display = ('name', 'description', 'allow_multiple')


## Package ##

class PackageTextMetadataInline(TextMetadataInline):
    model = PackageTextMetadata


class PackageImageMetadataInline(ImageMetadataInline):
    model = PackageImageMetadata


class PackageAdmin(admin.ModelAdmin):
    """
    An administration snap-in for maintaining the list of packages.

    """
    list_display = ('name', 'description', 'weight')
    inlines = [PackageTextMetadataInline, PackageImageMetadataInline]


## Registration ##

def register(site):
    """
    Registers the metadata admin hooks with an admin site.

    """
    site.register(MetadataKey, MetadataKeyAdmin)
    site.register(Package, PackageAdmin)
