=====
Usage
=====

More documentation will hopefully be added to this later.  Always
check the API auto-docs for the latest insights into how to use this
module.


How can I add metadata to a model?
==================================

Adding metadata requires the following steps:

1) Inherit your subject model from
   :class:`metadata.mixins.MetadataSubjectMixin`.  This pulls in the
   nice frontend code to allow metadata to be accessed in a mostly
   transparent way.
2) *(Optional)*.  Override the
   :meth:`metadata.mixins.MetadataSubjectMixin.metadata_parent`
   function in your subject to return a model instance whose metadata
   should be inherited by this model when an attempt to access
   nonexistent metadata (or any multiple-value metadata) happens.
   For more fine-grained control over metadata inheritance, try
   experimenting with the inheritance function system.
3) For each strand you want to attach, derive a model from the
   appropriate subclass of
   :class:`metadata.models.GenericMetadata` using the 
   :meth:`metadata.models.GenericMetadata.make_model` function.
4) Override the
   :meth:`metadata.mixins.MetadataSubjectMixin.metadata_strands`
   function in your subject to provide a dict mapping strand names to
   the related sets corresponding to the models you just created.
   (See the Django documentation for more information about related
   sets.)

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
