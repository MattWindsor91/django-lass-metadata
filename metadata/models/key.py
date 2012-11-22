"""The MetadataKey model, which forms the key in the metadata
key-value storage system.

"""
from django.conf import settings
from django.db import models

from metadata.models import Type


METADATA_KEY_DB_TABLE = getattr(
    settings,
    'METADATA_KEY_DB_TABLE',
    'metadata_key'
)

METADATA_KEY_DB_ID_COLUMN = getattr(
    settings,
    'METADATA_KEY_DB_ID_COLUMN',
    'metadata_key_id'
)


class MetadataKey(Type):
    """A metadata key, which defines the semantics of a piece of
    metadata.

    """

    allow_multiple = models.BooleanField(
        default=False,
        help_text="""If True, multiple instances of this metadata key
            can be active at the same time (e.g. arbitrary tags).

            """)
    id = models.AutoField(
        primary_key=True,
        db_column=METADATA_KEY_DB_ID_COLUMN
    )

    class Meta(Type.Meta):
        db_table = METADATA_KEY_DB_TABLE
        app_label = 'metadata'
