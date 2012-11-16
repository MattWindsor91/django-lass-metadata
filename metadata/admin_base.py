"""Base admin classes for metadata administration."""

from django.contrib import admin


class MetadataAdmin(admin.ModelAdmin):
    """Base class for metadata admin-lets."""

    date_hierarchy = 'effective_from'
    list_display = (
        'element',
        'key',
        'value',
        'creator',
        'approver',
        'effective_from',
        'effective_to',
    )


class MetadataInline(admin.TabularInline):
    """Base inline class for metadata inline admin-lets."""

    # Doing this makes the siteadmin virtually unuseable without JS,
    # but closes an annoying bug that causes the extra fields to
    # demand being filled in due to having their times populated.
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Provides a form field for foreign keys.

        Overrides the normal inline so that submitter and approver
        are set, by default, to the currently logged in user.

        """
        is_user_field = (
            db_field.name == 'creator'
            or db_field.name == 'approver'
        )
        if is_user_field:
            kwargs['initial'] = request.user.id
        return super(MetadataInline, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )
