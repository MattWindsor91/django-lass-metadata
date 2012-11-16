"""
Administration system hooks for the `metadata` application.

"""

from metadata.models import MetadataKey
from django.contrib import admin


## MetadataKey ##

class MetadataKeyAdmin(admin.ModelAdmin):
    """
    An adminstration snap-in for maintaining the list of metadata
    keys.

    """
    list_display = ('name', 'description', 'allow_multiple')


admin.site.register(MetadataKey, MetadataKeyAdmin)
