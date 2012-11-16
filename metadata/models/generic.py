"""Generic metadata base class."""

from django.db import models
from metadata.models import MetadataKey
from people.mixins import CreatableMixin
from people.mixins import ApprovableMixin
from metadata.mixins import EffectiveRangeMixin


class GenericMetadata(ApprovableMixin,
                      CreatableMixin,
                      EffectiveRangeMixin):
    """An item of generic metadata.

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
