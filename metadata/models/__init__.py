"""
The `metadata` module contains several model definitions under
`metadata.models`.

Metadata system models
======================

MetadataKey
-----------

.. automodule:: metadata.models.key
    :deprecated:
    :members:
    :undoc-members:
    :show-inheritance:

GenericMetadata
---------------

.. automodule:: metadata.models.generic
    :deprecated:
    :members:
    :undoc-members:
    :show-inheritance:

TextMetadata
------------

.. automodule:: metadata.models.text
    :deprecated:
    :members:
    :undoc-members:
    :show-inheritance:

ImageMetadata
-------------

.. automodule:: metadata.models.image
    :deprecated:
    :members:
    :undoc-members:
    :show-inheritance:

Other models
============

Type
----

.. automodule:: metadata.models.type
    :deprecated:
    :members:
    :undoc-members:
    :show-inheritance:

"""

# Import all models, in an order such that models only depend on
# models further up the list
from metadata.models.type import Type
Type = Type

from metadata.models.key import MetadataKey
MetadataKey = MetadataKey

from metadata.models.generic import GenericMetadata
GenericMetadata = GenericMetadata

from metadata.models.package import Package, PackageEntry
Package = Package
PackageEntry = PackageEntry
from metadata.models.package import PackageTextMetadata
PackageTextMetadata = PackageTextMetadata
from metadata.models.package import PackageImageMetadata
PackageImageMetadata = PackageImageMetadata

from metadata.models.text import TextMetadata
TextMetadata = TextMetadata

from metadata.models.image import ImageMetadata
ImageMetadata = ImageMetadata
