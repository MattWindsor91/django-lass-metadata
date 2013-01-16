"""
Default hooks for the metadata system, as well as a function for
running metadata hooks on queries.

"""

from django.core.cache import cache

from metadata.query import COUNT, EXISTS, VALUE


######################################################################
# Running queries

class QueryFailureError(Exception):
    """
    Exception raised when a metadata query returns no results, but
    was expected to do so.

    """
    def __init__(self, value):
        """
        Initialises the :class:`QueryFailureError`.

        :param value: The value, typically a string, to display
            when this exception is shown as a string.

        """
        self.value = value

    def __str__(self):
        """
        Produces a string representation of this exception.

        """
        return repr(self.value)


def run_query(query, hooks=None):
    """
    Runs a metadata query, optionally with the given set of hooks.

    If hooks is None, the default set will be used.
    (See :data:`metadata.hooks.DEFAULT_HOOKS`)

    :param query: A metadata query.
    :type query: :class:`metadata.query.MetadataQuery` or similar
        :class:`object`.

    :param hooks: A set of hooks to run the query with.
    :type hooks: iterable, for example list

    """
    if hooks is None:
        hooks = DEFAULT_HOOKS

    result = query.initial_state()
    awaiting_result = True

    for hook in hooks:
        try:
            this_result = hook(query)
        except HookFailureError:
            continue
        else:
            # We've got _some_ sort of result, which means the
            # query hasn't been a complete failure.
            result = (
                this_result
                if awaiting_result
                else query.join(result, this_result)
            )
            awaiting_result = False

            # Can we stop processing hooks now?
            if query.satisfied_by(result):
                break

    if awaiting_result:
        raise QueryFailureError(
            "All hooks {0} exhausted.".format(
                hooks
            )
        )

    cache.set(query.cache_key(), result, query.key.cache_duration)
    return result


class HookFailureError(Exception):
    """
    Exception raised when a metadata hook fails to fulfil a query,
    but not in a way that should halt execution.

    """
    def __init__(self, value):
        """
        Initialises the :class:`HookFailureError`.

        :param value: The value, typically a string, to display
            when this exception is shown as a string.

        """
        self.value = value

    def __str__(self):
        """
        Produces a string representation of this exception.

		:return 
        """
        return repr(self.value)


def metadata_from_cache(query):
    """
    Given a metadata query, attempts to fulfil the request using
    the Django cache.

    :param query: The MetadataQuery this hook is trying to run.
    :type query: :class:`metadata.query.MetadataQuery` or similar
        :class:`object`.

    """
    val = cache.get(query.cache_key())
    if val is None:
        raise HookFailureError('Cache miss.')
    return val


def metadata_from_strand_sets(query):
    """
    Given a metadata query, attempts to use the query element's
    own metadata sets to fulfil the request.

    Will raise :class:`metadata.hooks.HookFailureError` on failure.

    :param query: The MetadataQuery this hook is trying to run.
    :type query: :class:`metadata.query.MetadataQuery` or similar
        :class:`object`.

    """
    strand_set = get_strand_set(query)
    active_metadata = get_active_metadata(
        strand_set,
        query.key,
        query.date
    )
    return handle_set(
        active_metadata,
        query.key.allow_multiple,
        query.query_type
    )


def metadata_from_parent(query):
    """
    Given a metadata query, attempts to use the query element's
    designated parent to fulfil the request.

    Will raise :class:`metadata.hooks.HookFailureError` on failure.

    :param query: The MetadataQuery this hook is trying to run.
    :type query: :class:`metadata.query.MetadataQuery` or similar
        :class:`object`.

    """
    subject = query.subject
    try:
        parent = subject.metadata_parent()
    except AttributeError:
        raise HookFailureError(
            'Element does not support metadata_parent().'
        )

    if parent is None:
        raise HookFailureError(
            'Parent explicitly disabled.'
        )
    return run_query(query.replace(subject=parent))


def metadata_from_package(query):
    """
    Given a metadata query, attempts to use the query element's
    designated metadata packages to fulfil the request.

    Will raise :class:`metadata.hooks.HookFailureError` on failure.

    :param query: The MetadataQuery this hook is trying to run.
    :type query: :class:`metadata.query.MetadataQuery` or similar
        :class:`object`.

    """
    subject = query.subject
    try:
        entries = subject.packages
    except AttributeError:
        raise HookFailureError(
            'Element does not support packages.'
        )

    if entries is None:
        raise HookFailureError(
            'Packages explicitly disabled.'
        )

    found = False
    for entry in entries().at(query.date):
        try:
            result = run_query(query.replace(subject=entry.package))
        except HookFailureError:
            continue
        else:
            found = True
            break
    if not found:
        raise HookFailureError(
            'None of the packages provided metadata.'
        )

    return result


def metadata_from_default(query):
    """
    Given a metadata query, attempts to return the default value
    for the metadata key in the given strand.

    Will raise :class:`metadata.hooks.HookFailureError` on failure.

    :param query: The MetadataQuery this hook is trying to run.
    :type query: :class:`metadata.query.MetadataQuery` or similar
        :class:`object`.

    """
    strand_set = get_strand_set(query)
    active_metadata = get_active_metadata(
        strand_set.model.objects.filter(element__isnull=True),
        query.key,
        query.date
    )
    return handle_set(
        active_metadata,
        query.key.allow_multiple,
        query.query_type
    )


######################################################################
# Default hooks list

DEFAULT_HOOKS = [
    # TODO: metadata_from_cache
    metadata_from_strand_sets,
    metadata_from_parent,
    metadata_from_package,
    metadata_from_default,
]


######################################################################
# Utility functions

def get_strand_set(query):
    """
    Attempts to get a metadata strand related-set from the element
    of the given query, given the query's requested strand.

    """
    st = query.strand
    subject = query.subject

    try:
        strand_sets = subject.metadata_strands()
    except AttributeError:
        raise HookFailureError(
            "Element doesn't support metadata_strands."
        )

    try:
        strand_set = strand_sets[st]
    except KeyError:
        raise HookFailureError(
            "Element doesn't have {0} in its strand sets.".format(
                st
            )
        )
    return strand_set


def handle_set(metadata, allow_multiple, query_type):
    """
    Handles a metadata set as required by the metadata's multiplicity
    and the metadata query type.

    :param metadata: A set of metadata.
    :type metadata: QuerySet

    :param allow_multiple: Whether or not multiple values should be
        returned, in the case of the query type being VALUE.
    :type allow_multiple: :class:`bool`

    :param query_type: The query type, which determines the behaviour
        expected of this function.

    """
    if query_type == VALUE:
        if allow_multiple:
            result = [x.value for x in metadata]
        else:
            try:
                result = metadata.latest().value
            except metadata.model.DoesNotExist:
                raise HookFailureError(
                    "No match."
                )
    elif query_type == COUNT:
        count = metadata.count()
        result = count if allow_multiple else max(1, count)
    elif query_type == EXISTS:
        result = metadata.exists()
    else:
        raise HookFailureError(
            'Unsupported query type {0}'.format(query_type)
        )

    return result


def get_active_metadata(strand_set, key, date):
    """
    From the given queryset, extracts metadata matching the given
    key that was active at the given date.

    """
    return strand_set.at(date).filter(key__pk=key.id)
