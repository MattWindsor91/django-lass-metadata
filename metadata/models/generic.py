"""Generic metadata base class."""

from django.db import models
from metadata.models import MetadataKey
from people.mixins import CreatableMixin
from people.mixins import ApprovableMixin
from metadata.mixins import EffectiveRangeMixin


class GenericMetadata(ApprovableMixin,
                      CreatableMixin,
                      EffectiveRangeMixin):
    """
    An item of generic metadata.

    NOTE TO IMPLEMENTORS: The final concrete instances of this class
    must have a field named 'element' that foreign key references the
    element of data to which the metadata is to be attached.

    Any further implementors must also include a field named 'value'
    that stores the metadatum value.

    """

    class Meta(EffectiveRangeMixin.Meta):
        abstract = True

    def __unicode__(self):
        """Returns a concise Unicode representation of the metadata.

        """
        return u'{0} -> {1} (ef {2}->{3} on {4})'.format(
            self.key,
            self.value,
            self.effective_from,
            self.effective_to,
            self.element)

    key = models.ForeignKey(
        MetadataKey,
        help_text="""The key, or type, of the metadata entry.""",
        db_column='metadata_key_id')

    @classmethod
    def make_model(cls,
                   target_class,
                   app=None,
                   model_name=None,
                   table=None,
                   id_column=None,
                   fkey_column=None,
                   help_text=None):
        """
        Constructs a metadata model of this metadata model's strand
        type, optionally with the given table and id column.

        """
        if isinstance(target_class, basestring):
            # We got a string in, which is hopefully a model name.
            # This means the target name and the target are equal.
            target_name = target_class
        else:
            # We got something that we hope is a class object in.
            # Its name is just the __name__ param.
            target_name = target_class.__name__

        # The 'fields' dict will contain the fields that we're
        # adding on top of cls for the metadata class we're building.
        fields = {'__module__': __name__}

        # Make a meta class with the correct database table, app label
        # and 'abstract' switched on.
        class Meta(cls.Meta):
            abstract = False
            if table:
                db_table = table
            if app:
                app_label = app
        fields['Meta'] = Meta

        # Default model name is Target-nameThis-type-ofMetadata
        if model_name is None:
            model_name = ''.join((
                target_name,
                cls.__name__
            ))

        # Make the foreign key pointing to the element.
        # - Let's make the dict of arguments to the foreign key class.
        fkey_kwargs = {}
        # - Did the user specify a foreign key?
        if fkey_column:
            fkey_kwargs['db_column'] = fkey_column
        # - Now we can have a foreign key...
        fields['element'] = models.ForeignKey(
            target_class,
            **fkey_kwargs
        )

        # Now dynamically construct the class.
        return cls.__class__(
            model_name,
            (cls,),
            fields
        )
