"""In which a mixin that allows attached metadata on a model to be
accessed in a common manner is described.

"""

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from metadata.models.key import MetadataKey


class MetadataView(object):
    """A dictionary view abstraction over the metadata system,
    treating each strand of metadata in a metadata subject as a
    separate key in a dictionary.

    """

    class StrandView(object):
        """An intermediary class that represents a strand of metadata
        as a dictionary.

        """
        def __init__(self, subject, date, strand):
            """Initialises the strand view.

            Keyword arguments:
            subject - see MetadataView.__init__
            date - see MetadataView.__init__
            strand - the strand of metadata (for example 'text',
                'images' etc) that this view is operating on

            """
            self.subject = subject
            self.strand = strand
            self.date = date

        def __getitem__(self, key):
            """Attempts to get a metadatum in the current
            strand.

            """
            return self.subject.metadatum_at_date(
                date=self.date,
                key=key,
                strand=self.strand)

    def __init__(self, subject, date):
        """Initialises the metadata view.

        Keyword arguments:
        subject - the object whose metadata is being presented as a
            dictionary
        date - the date representing the period of time used to
            decide what constitutes "active" metadata

        """
        self.subject = subject
        self.date = date

    def __getitem__(self, strand):
        """Attempts to get a view for a metadata strand."""
        if strand not in self.subject.metadata_strands():
            raise KeyError('No such metadata strand here.')
        return MetadataView.StrandView(
            self.subject,
            self.date,
            strand)


class MetadataSubjectMixin(object):
    """Mixin granting the ability to access metadata.

    """

    # Don't forget to override this!
    def metadata_strands(self):
        """Returns a dictionary of related sets that provide the
        metadata strands.

        These should usually be organised along type lines, for
        example {'text': textual_metadata_set,
        'images': image_metadata_set, etc...}.

        This should invariably be overridden in mixin users.

        """
        raise NotImplementedError(
            'Must implement metadata_strands.')

    # Also override this, if relevant
    def metadata_parent(self):
        """Returns an object that metadata should be inherited from
        if not assigned for this object.

        This can return None if no inheriting should be done.

        """
        return None

    ## COMMON METADATA KEYS ##

    def title(self):
        """Provides the current title of the item.

        The title is extracted from the item metadata.

        """
        return self.current_metadatum('title')

    def title_image(self):
        """Provides the path (within the image directory) of an
        image that can be used in place of this item's 'title'
        metadatum in headings, if such an image exists.

        This is extracted from the item metadata.

        """
        return self.current_metadatum('title_image')

    def description(self):
        """Provides the current description of the item.

        The description is extracted from the item metadata.

        """
        return self.current_metadatum('description')

    def metadata(self, date=None):
        """Returns a dictionary-style view of the metadata that
        can be used to access it in templates.

        The result is two-tiered and organised first by metadata
        strand and then by key.

        """
        return MetadataView(self, date if date else timezone.now())

    def metadatum_at_date(self,
                          date,
                          key,
                          strand='text',
                          inherit=True):
        """Returns the value of the given metadata key that was
        in effect at the given date.

        The value returned is the most recently effected value
        that is approved and not made effective after the given
        date.

        If no such item exists, and inherit is True, the metadatum
        request will propagate up to the parent if it exists.

        """
        key_id = MetadataKey.get(key).id
        try:
            result = self.metadata_strands()[strand].filter(
                key__pk=key_id,
                effective_from__lte=date).order_by(
                    '-effective_from').latest().value
        except ObjectDoesNotExist:
            if inherit is True and self.metadata_parent() is not None:
                result = self.metadata_parent().metadatum_at_date(
                    date,
                    key,
                    strand,
                    inherit)
            else:
                result = None
        return result

    def current_metadatum(self, key, strand='text', inherit=True):
        """Retrieves the current value of the given metadata key.

        The current value is the most recently effected value that
        is approved and not in the future.

        If no such item exists, and inherit is True, the metadatum
        request will propagate up to the parent if it exists.

        """
        return self.metadatum_at_date(
            timezone.now(),
            key,
            strand,
            inherit)
