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

Metadata
--------

.. automodule:: metadata.models.data
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
from metadata.models.key import MetadataKey
from metadata.models.data import Metadata
from metadata.models.generic import GenericMetadata
from metadata.models.image import ImageMetadata
