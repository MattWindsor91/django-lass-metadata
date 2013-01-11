"""
The :class:`Package` model and related stuff.

"""

from django.conf import settings
from django.db import models

from lass_utils.models import Type
from lass_utils.mixins import AttachableMixin, EffectiveRangeMixin

from people.mixins import CreatableMixin, ApprovableMixin

from metadata.mixins import MetadataSubjectMixin

# These need to be imported directly due to cyclic dependencies
from metadata.models.text import TextMetadata
from metadata.models.image import ImageMetadata


class Package(Type,
              MetadataSubjectMixin):
    """
    A 'package' is an object that can be applied to an
    object to provide an overridable, default set of metadata.

    """

    if hasattr(settings, 'PACKAGE_DB_ID_COLUMN'):
        id = models.AutoField(
            primary_key=True,
            db_column=settings.PACKAGE_DB_ID_COLUMN
        )

    def metadata_strands(self):
        return {
            'text': self.packagetextmetadata_set,
            'image': self.packageimagemetadata_set,
        }

    @classmethod
    def make_foreign_key(cls):
        """
        Shortcut for creating a field that links to a package.

        """
        _FKEY_KWARGS = {}
        if hasattr(settings, 'PACKAGE_DB_FKEY_COLUMN'):
            _FKEY_KWARGS['db_column'] = settings.PACKAGE_DB_FKEY_COLUMN
        return models.ForeignKey(
            cls,
            help_text='The package associated with this item.',
            **_FKEY_KWARGS
        )

    class Meta(object):
        if hasattr(settings, 'PACKAGE_DB_TABLE'):
            db_table = settings.PACKAGE_DB_TABLE

        app_label = 'metadata'


PackageTextMetadata = TextMetadata.make_model(
    Package,
    'metadata',
    'PackageTextMetadata',
    getattr(
        settings, 'PACKAGE_TEXT_METADATA_DB_TABLE',
        None
    ),
    getattr(
        settings, 'PACKAGE_TEXT_METADATA_DB_ID_COLUMN',
        None
    ),
    help_text='The package associated with this textual metadata.',
    fkey=Package.make_foreign_key(),
)


PackageImageMetadata = ImageMetadata.make_model(
    Package,
    'metadata',
    'PackageImageMetadata',
    getattr(
        settings, 'PACKAGE_IMAGE_METADATA_DB_TABLE',
        None
    ),
    getattr(
        settings, 'PACKAGE_IMAGE_METADATA_DB_ID_COLUMN',
        None
    ),
    help_text='The package associated with this image metadata.',
    fkey=Package.make_foreign_key(),
)


class PackageEntry(AttachableMixin,
                   EffectiveRangeMixin,
                   CreatableMixin,
                   ApprovableMixin):
    """
    An attachable that allows zero or more packages to be assigned to
    an arbitrary model for use in its metadata resolution.

    """

    package = Package.make_foreign_key()

    class Meta(Type.Meta):
        abstract = True
