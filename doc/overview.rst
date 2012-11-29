========
Overview
========

In which the purpose of this app is explained, alongside pointers as
to how to use it to add metadata to arbitrary models.

In short
========

This package provides metadata services that can be attached to
existing models to add key-value metadata.  It is used in the URY
LASS project to store show names, descriptions, thumbnails and other
such data.

What is metadata?
=================

The ``django-lass-metadata`` system defines *metadata* as a key-value
map whereby the same keys can be mapped to different values
in different models.  The keys are typically referred to by a string,
but are themselves contained in a global model alongside some
additional properties each key has.

Each collection of metadata attached to a model is known as a
*metadata strand*, and is homogeneous (that is, every value inside it
is of the same type).

Each strand is its own model, but the package provides convenience
functions for spawning new models for 
This package provides both a generic metadata abstract model that can
be used to define these homogeneous strand models, as well as
predefined versions for textual and image-based metadata.

Keys are global
---------------

As mentioned before, there is only one key repository shared by all
models; this was a design decision primarily for simplicity, but has
the result of promoting a common language or taxonomy for all objects
inside a domain.

Metadata has history
--------------------

Metadata has an *effective range*, which means that it can be set to
come into and go out of force at given date-times.  This allows the
metadata system to track history of metadata, instead of just holding
the current state.

Metadata has approvers and creators
-----------------------------------

Metadata also tracks who created it, and (optionally) who approved it
for usage.

How can I access metadata?
==========================

By default, the metadata of a subject model can be accessed through
the :attr:`MetadataSubjectMixin.metadata` pseudo-field, which
retrieves a dict-like object of all active metadata strands on that
field.  A method :meth:`MetadataSubjectMixin.metadata_at()` allows
finer-grained control over this object, including overriding the
current reference date (to look at historical or future metadata).

Each strand can then also be accessed like a dict, with metadata
accessed via its key's name, ID or the key object itself as the dict
key.

The first strand defined on a model is special: it by default serves
as the fallback for any attribute requests on the subject itself.
This allows you to specify, for example, ``foo.title`` instead of
``foo.metadata['text']['title']``, and should help with migration to
the metadata system from discrete fields.
