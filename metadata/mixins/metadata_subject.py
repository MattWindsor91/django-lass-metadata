"""In which a mixin that allows attached metadata on a model to be
accessed in a common manner is described.

"""

from django.utils import timezone

from metadata.hooks import QueryFailureError, DEFAULT_HOOKS, run_query
from metadata.models.key import MetadataKey
from metadata.query import INITIAL_QUERY_STATE
from metadata.query import MetadataQuery, EXISTS, VALUE


class MetadataView(object):
    """
    A dictionary view abstraction over the metadata system,
    treating each strand of metadata in a metadata subject as a
    separate key in a dictionary.

    """

    class StrandView(object):
        """
        An intermediary class that represents a strand of metadata
        as a dictionary.

        """
        def __init__(self, subject, date, strand, hooks):
            """
            Initialises the strand view.

            :param subject: see MetadataView.__init__

            :param date: see MetadataView.__init__

            :param strand: The strand of metadata (for example 'text',
                'images' etc) that this view is operating on

            :param hooks: The set of metadata hooks to use to retrieve
                metadata.

            """
            self.query = lambda key, query_type: MetadataQuery(
                subject,
                date,
                key,
                strand,
                query_type
            )
            self.run_q = lambda query: run_query(query, hooks)

        def __contains__(self, key):
            """
            Checks to see if the given metadata key is in this
            strand.

            """
            return self.run(key, EXISTS)

        def __getitem__(self, key):
            """
            Attempts to get a metadatum in the current strand.

            """
            return self.run(key, VALUE)

        def get(self, key, default=None):
            try:
                val = self[key]
            except KeyError:
                val = default
            return val

        def run(self, key, query_type):
            """
            Wrapper over query running.

            """
            try:
                q = self.query(key, query_type)
            except MetadataKey.DoesNotExist:
                # 'key' turns out not to exist
                # What we do here is based on the query type
                # - if we can get away with returning the initial
                # query state then we will.
                result = INITIAL_QUERY_STATE[query_type]
                if result is None:
                    # Sounds like we can't return anything without
                    # a key...
                    raise KeyError(
                        'Key {0} is not a valid metadata key'.format(
                            key
                        )
                    )
            else:
                try:
                    result = self.run_q(q)
                except QueryFailureError:
                    raise KeyError(
                        'No metadata found for {0}.'.format(key)
                    )
            return result

    def __init__(self, subject, date, hooks):
        """Initialises the metadata view.

        :param subject: The object whose metadata is being presented
            as a dictionary.

        :param date: The date representing the period of time used to
            decide what constitutes "active" metadata.

        :param hooks: The set of metadata hooks used to find metadata.

        """
        self.subject = subject
        self.date = date
        self.hooks = hooks

    def __call__(self, date=None):
        """
        Backwards compatibility for any code that calls metadata(),
        or metadata(date).

        New code should use metadata as a field, or call
        metadata_at(date).

        """
        return self if not date else self.__class__(
            self.subject,
            date,
            self.hooks
        )

    def __contains__(self, strand):
        """Checks to see if a named strand is present."""
        return (strand in self.subject.metadata_strands())

    def __getitem__(self, strand):
        """Attempts to get a view for a metadata strand."""
        if not self.__contains__(strand):
            raise KeyError('No such metadata strand here.')
        return MetadataView.StrandView(
            self.subject,
            self.date,
            strand,
            self.hooks
        )


class MetadataSubjectMixin(object):
    """Mixin granting the ability to access metadata.

    """

    ## MANDATORY OVERRIDES ##

    def metadata_strands(self):
        """
        Returns a dictionary of related sets that provide the
        metadata strands.

        These should usually be organised along type lines, for
        example {'text': textual_metadata_set,
        'images': image_metadata_set, etc...}.

        This should invariably be overridden in mixin users.

        """
        raise NotImplementedError(
            'Must implement metadata_strands.')

    ## OPTIONAL OVERRIDES ##

    def metadata_hooks(self):
        """
        Returns an iterable of metadata hooks.

        Metadata hooks are functions taking a date, metadata
        strand, key and a boolean specifying whether or not to peek
        instead of returning a value, and returning a metadata
        value, or raising :class:`KeyError` if no such value exists.

        The default behaviour is to return
        :data:`metadata.hooks.DEFAULT_HOOKS`.
        """
        return DEFAULT_HOOKS

    def metadata_parent(self):
        """
        Returns an object that metadata should be inherited from
        if not assigned for this object.

        This can return None if no inheriting should be done.

        """
        return None

    ## MAGIC METHODS ##

    def __getattr__(self, name):
        """
        Attribute retrieval hook that intercepts calls for *metadata*
        and reroutes them to *metadata_at*, as well as attempting to
        route calls for items to the first matching metadatum in
        the current strands.

        """
        result = None
        result_def = False

        # Some slightly heuristic-y checks to make sure that we
        # don't enter an infinite getattr loop
        about_to_recurse = (
            name.endswith('metadata_set')
            or name == 'range_start'
            or name.startswith('_')
        )
        if about_to_recurse:
            raise AttributeError

        result, result_def = self.getattr_metadata(name)

        if not result_def:
            raise AttributeError
        return result

    ## OTHER FUNCTIONS ##

    def getattr_metadata(self, name):
        """
        Hook for __getattr__ to check the subject's metadata sets.

        You should almost never need to call this outside of
        __getattr__.

        """
        now = (
            timezone.now()
            if not hasattr(self, 'range_start')
            else self.range_start()
        )
        result = None
        result_def = False

        if name == 'metadata':
            result = self.metadata_at(now)
            result_def = True
        elif name in self.metadata_strands():
            result = self.metadata_at(now)[name]
            result_def = True
        else:
            for strand in self.metadata_strands():
                md = self.metadata_at(now)[strand]
                if name in md:
                    result = md[name]
                    result_def = True
                    break
        return result, result_def

    def metadata_at(self, date, hooks=None):
        """
        Returns a dict-like object that allows the strands of
        metadata active on this item at the given time.

        The result is two-tiered and organised first by metadata
        strand and then by key.

        If ``inherit_function`` is specified, it will be supplied
        a date, strand and key in the event that a key is accessed
        that does not appear in the metadata strand for this subject
        on that date, and should return either a metadatum inherited
        by this subject in its place or raise :class:`KeyError`.

        """
        return MetadataView(
            self,
            date,
            (self.metadata_hooks() if not hooks else hooks)
        )
