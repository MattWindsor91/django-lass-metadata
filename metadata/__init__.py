"""
=========================================================
`metadata` - the LASS metadata and common patterns system
=========================================================

The `metadata` app contains code designed to cover generic patterns
in the LASS system.

One of these, and the namesake of the app, is the generic metadata
system, which allows objects in the LASS model set to contain
key-value stores of textual, image-based and other formats of
metadata by inheriting a mixin and providing a subclass of the
standard metadata models.

The `metadata` app also includes several models, mixins and utility
functions covering other commonly used patterns.

Metadata system
===============

Most of the `metadata` app is dedicated to the URY *metadata system*,
which allows various different *strands* of data (generally text,
but also image-based and other formats) to be attached to items.

LASS uses the metadata system, for example, to provide shows with
names and descriptions that have full recorded history and hooks for
an approval system.  It is also used to associate images (thumbnails
and player insets) with podcasts.

Strands
-------

Each model can have zero or more `strands` of metadata attached to
it.  Each strand is its own model (see below for more information on
how to create a metadata provider model), and represents a specific
collection of metadata on objects in the subject model.

Strands are indexed by name; an entire strand (as a dictionary-like
object) can be retrieved from an implementor of
`MetadataSubjectMixin` with ``object.metadata('strand-name')``.
Generally, there will be a ``text`` strand containing all textual
metadata, and an ``images`` strand containing thumbnail images and
other related pictorial metadata.

Implementation
--------------

All metadata strands are implemented as key-value stores, the key
store being implemented as one unified model for simplicity reasons
and the value stores being separate for each strand for each model.

Two classes (`metadata.mixins.MetadataSubjectMixin` and
`metadata.models.GenericMetadata`) provide the core framework for
defining a metadata subject and a metadata strand.  There are
descendents of `GenericMetadata` available for specific commonly used
strand types.

Examples
--------

In the LASS project, examples of how to use the metadata system can
be found in `schedule.models.show`, `uryplayer.models.podcast` and
`people.models.role`.

Models
======

.. automodule:: metadata.models
    :deprecated:
    :members:
    :undoc-members:
    :show-inheritance:

Mixins
======

.. automodule:: metadata.mixins
    :deprecated:
    :members:
    :undoc-members:
    :show-inheritance:

Misc
====

Administration hooks
--------------------

.. automodule:: metadata.admin
    :deprecated:
    :members:
    :undoc-members:
    :show-inheritance:

tests
-----

.. automodule:: metadata.tests
    :deprecated:
    :members:
    :undoc-members:
    :show-inheritance:

admin_base
----------

.. automodule:: metadata.admin_base
    :deprecated:
    :members:
    :undoc-members:
    :show-inheritance:
"""
