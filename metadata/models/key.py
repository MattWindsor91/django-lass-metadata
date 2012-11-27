"""
The MetadataKey model, which forms the key in the metadata
key-value storage system.

"""
from django.conf import settings
from django.db import models

from lass_utils.models import Type


class MetadataKey(Type):
    """A metadata key, which defines the semantics of a piece of
    metadata.

    """

    allow_multiple = models.BooleanField(
        default=False,
        help_text="""If True, multiple instances of this metadata key
            can be active at the same time (e.g. arbitrary tags).

            """)
    if hasattr(settings, 'METADATA_KEY_DB_ID_COLUMN'):
        id = models.AutoField(
            primary_key=True,
            db_column=settings.METADATA_KEY_DB_ID_COLUMN
        )

    class Meta(Type.Meta):
        if hasattr(settings, 'METADATA_KEY_DB_TABLE'):
            db_table = settings.METADATA_KEY_DB_TABLE
        app_label = 'metadata'
