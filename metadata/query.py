"""
In which a *metadata query* is defined.

"""

from django.utils import timezone

from metadata.models.key import MetadataKey

VALUE = 0
EXISTS = 1
COUNT = 2
QUERY_TYPES = [VALUE, EXISTS, COUNT]

INITIAL_QUERY_STATE = {
    VALUE: None,
    EXISTS: False,
    COUNT: 0
}


class MetadataQuery(object):
    """
    An object that holds together all state required for a query
    for metadata on a metadata subject to be run.

    For running a metadata query, see the :mod:`metadata.hooks`
    module.

    Generally, however, most code shouldn't need to use metadata
    queries directly.  A sugary frontend is provided by
    :class:`metadata.mixins.MetadataSubjectMixin`.

    """
    def __init__(self,
                 subject,
                 date,
                 key,
                 strand='text',
                 query_type=VALUE):
        """
        Initialises a metadata query.

        :param subject: The object to whom the sought-after metadata
            is attached.  Need not, but ought to, inherit from
            :class:`metadata.mixins.MetadataSubjectMixin`.
        :type subject: :class:`object`

        :param date: The date that the metadata must have been active
            within.
        :type date: :class:`datetime.datetime`

        :param key: The key, or a string or primary key
            representation thereof, used to index the metadata.
        :type key: string, integer or
            :class:`metadata.models.key.MetadataKey`

        :param strand: The name of the metadata strand being
            requested.
        :type strand: string

        :param query_type: The type of metadata query to carry out
            (see above).
        :type query_type: Any of the items in :data:`QUERY_TYPES`.

        """
        if query_type not in QUERY_TYPES:
            raise ValueError(
                'Invalid query type.'
            )

        self.subject = subject
        self._date = date
        self.strand = strand
        self.key = MetadataKey.get(key)
        self.query_type = query_type

        self.construct_date = timezone.now()

    ##################################################################
    # Functions for manipulating query running results

    def initial_state(self):
        """
        Returns the value that should be the initial state of any
        running of this query.

        """
        return INITIAL_QUERY_STATE[self.query_type]

    def join(self, old, new):
        """
        Join two successful query runnings in a way that satisfies
        the query's requirements.

        The old state is given precedence so, for example, trying to
        join two results for a value query on a single-value key
        will return the old state only.

        :param old: the old answer to this query
        :param new: the new answer to this query
        """
        mul = self.key.allow_multiple

        if self.query_type == VALUE:
            result = old if not mul else old | new
        elif self.query_type == EXISTS:
            result = old or new
        elif self.query_type == COUNT:
            s = old + new
            result = s if mul else max(1, s)
        else:
            raise ValueError(
                'Unsupported query type {}'.format(
                    self.query_type
                )
            )
        return result

    def satisfied_by(self, result):
        """
        Given an intermediate result of a metadata query run, returns
        True if there need not be any more hook processing in order
        to get a valid answer to the query.

        :param result: the current result of a metadata query run

        """
        satisfied = False

        if self.query_type == VALUE and not self.key.allow_multiple:
            # We only need one value, so there's no need to continue
            satisfied = True
        elif self.query_type == EXISTS and result is True:
            # No point looking to see if any more metadata exists
            satisfied = True

        return satisfied

    ##################################################################
    # Creating new queries from existing ones

    def replace(self, **kwargs):
        """
        Creates a new query representing the query with the
        initialising parameters in kwargs replacing their
        counterparts in this query.

        :param kwargs: A keyword argument dict of substitutions
            to make.
        """
        init_args = {
            'subject': self.subject,
            'date': self._date,
            'strand': self.strand,
            'key': self.key,
            'query_type': self.query_type
        }
        init_args.update(kwargs)
        return self.__class__(**init_args)

    ##################################################################
    # Other uses of queries

    @property
    def date(self):
        """Returns the target metadata date of this query.

        This will be the time of query creation if no date was specified.
        """
        return self._date if self._date else self.construct_date

    def cache_key(self):
        """
        Returns a representation of the query that can be used as a
        cache key.

        :rtype: basestring

        """
        return '-'.join((repr(x) for x in (
            self.subject.__class__,
            self.subject.id,
            self._date,
            self.strand,
            self.key,
            self.query_type
        ))).replace('_', '__').replace(' ', '_')
