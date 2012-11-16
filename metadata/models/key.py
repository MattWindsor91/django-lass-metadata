"""The MetadataKey model, which forms the key in the metadata
key-value storage system.

"""
from django.db import models
from metadata.models import Type
from urysite import model_extensions as exts


class MetadataKey(Type):
    """A metadata key, which defines the semantics of a piece of
    metadata.

    """

    class Meta(Type.Meta):
        db_table = 'metadata_key'  # in schema 'metadata'
        app_label = 'metadata'

    allow_multiple = models.BooleanField(
        default=False,
        help_text="""If True, multiple instances of this metadata key
            can be active at the same time (e.g. arbitrary tags).

            """)

    id = exts.primary_key_from_meta(Meta)
