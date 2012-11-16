"""
Models for the URY text metadata system.

To add metadata to a model, create a subclass of 'Metadata' for that
model, descend the model from 'MetadataSubjectMixin', and fill out
the methods identified in those two classes.

"""

# IF YOU'RE ADDING CLASSES TO THIS, DON'T FORGET TO ADD THEM TO
# __init__.py

from django.db import models
from metadata.models.generic import GenericMetadata


class Metadata(GenericMetadata):
    """Abstract base for items of textual metadata."""

    class Meta(GenericMetadata.Meta):
        abstract = True

    # REMEMBER TO ADD THIS TO ANY DERIVING CLASSES!
    # id = exts.primary_key_from_meta(Meta)

    value = models.TextField(
        help_text="""The value of this metadata entry.""",
        db_column='metadata_value')
