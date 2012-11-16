"""
Models for the URY image metadata system.

To add metadata to a model, create a subclass of 'ImageMetadata' for
that model, descend the model from 'ImageMetadataSubjectMixin', and
fill out the methods identified in those two classes.

"""

# IF YOU'RE ADDING CLASSES TO THIS, DON'T FORGET TO ADD THEM TO
# __init__.py

from django.db import models
from metadata.models.generic import GenericMetadata


class ImageMetadata(GenericMetadata):
    """
    Abstract base class for usages of images as metadata.

    """

    value = models.ImageField(
        upload_to=(lambda instance, filename:
                   'image_meta/{0}/{1}'.format(
                       instance.__class__.__name__,
                       filename)),
        help_text='The image associated with this metadata entry.')

    class Meta(GenericMetadata.Meta):
        abstract = True

    # REMEMBER TO ADD THIS TO ANY DERIVING CLASSES!
    # id = exts.primary_key_from_meta(Meta)
