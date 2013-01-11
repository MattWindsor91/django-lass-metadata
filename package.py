"""Generic metadata base class."""

from django.conf import settings
from django.db import models

from metadata.models import MetadataKey
from people.mixins import CreatableMixin
from people.mixins import ApprovableMixin

from lass_utils.mixins import AttachableMixin
from lass_utils.mixins import EffectiveRangeMixin


class GenericMetadata(ApprovableMixin,
                      AttachableMixin,
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
        """
        Returns a concise Unicode representation of the metadata.

        """
        return u'{0} -> {1} (ef {2}->{3} on {4})'.format(
            self.key,
            self.value,
            self.effective_from,
            self.effective_to,
            self.element
        )

    kwargs = {}
    if hasattr(settings, 'METADATA_DB_KEY_COLUMN'):
        kwargs['db_column'] = settings.METADATA_DB_KEY_COLUMN

    key = models.ForeignKey(
        MetadataKey,
        help_text="""The key, or type, of the metadata entry.""",
        **kwargs
    )

