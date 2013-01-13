=================
Metadata packages
=================

Sometimes you need to be able to apply entire collections of metadata
to an item at a single time, or be able to link some metadata into one
unit that you can update across a large amount of items of different
types.

One example of where this might be useful is branding.  If you have a
certain brand that you want to apply to, say, a range of podcasts, you
could manually set those podcasts up to have a consistent set of
images, stock titles and descriptions, and so on.  This is quite
tedious and any changes made later won't automatically propagate to
existing podcasts.

This is where *metadata packages* come in.  Packages are metadata
subject items that live in the
:py:class:`metadata.models.package.Package` model, which can be
attached in a many-to-many relationship to your models using the
:py:class:`metadata.models.package.PackageEntry` attachable.  (See the
`django-lass-utils documentation <http://django-lass-utils.rtfd.org>`_
for information about how to use attachables.) 

Using as a fallback for metadata subjects
=========================================

The default :ref:`hooks <hooks>` set can automatically try getting
metadata from a metadata package if no item-specific metadata exists.
Creating a method ``packages`` on the subject class that returns the
reverse set of a package entry attachable will enable this.  See the
unit tests for an example.

Querying a package for metadata
===============================

:py:class:`metadata.models.package.Package` implements
:py:class:`metadata.mixins.MetadataSubjectMixin`, so the
:ref:`standard interface <subjects>` for retrieving metadata works on
them.
