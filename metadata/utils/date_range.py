"""This module contains general functions for working with objects
that implement the DateRangeMixin interface.

"""

from datetime import datetime
from django.utils.timezone import utc


def exclude_tuples(queryset,
                   *args):
    """Like queryset.exclude(), but accepts a list of key-value
    tuples instead of keyword arguments.

    """
    return queryset.exclude(**(dict(args)))


def in_range(cls,
             start,
             end,
             queryset=None,
             exclude_before_start=False,
             exclude_after_end=False,
             exclude_subsuming=False):
    """Filters a set of objects such that the remaining objects lie
    within a range defined by two datetime objects.

        Keyword arguments:
        cls -- the class, which should be derived from DateRangeMixin
        queryset -- the query set of objects from that class to
            filter (default: cls.objects.all())
        start -- the start of the range, as a datetime or UNIX time
        end -- the end of the range, as a datetime or UNIX time
        exclude_before_start -- if True, the list will exclude all
            items that start before the range, but end within it
            (default: False)
        exclude_after_end -- if True, the list will exclude all items
            that start within the range, but end after it
            (default: False)
        exclude_subsuming -- if True, the list will exclude all items
            that start before, but end after, the range (that is,
            they "subsume" the range)
            (default: False)
    """
    objects = queryset if queryset else cls.objects.all()

    # Coerce UNIX timestamp input into datetimes
    if isinstance(start, int):
        start = datetime.utcfromtimestamp(start).replace(tzinfo=utc)
    if isinstance(end, int):
        end = datetime.utcfromtimestamp(end).replace(tzinfo=utc)

    # The following comments use pictorial diagrams of the ranges
    # they work on, which look like:
    #     ( before range | during range | after range )

    # Drop items that start and end BEFORE the range (##|  |  )
    objects = exclude_tuples(
        objects,
        cls.range_start_filter_arg('lt', start),
        cls.range_end_filter_arg('lte', start))
    # and also AFTER the range (  |  |##)
    objects = exclude_tuples(
        objects,
        cls.range_start_filter_arg('gte', end),
        cls.range_end_filter_arg('gt', end))
    # This leaves:
    #   1) Shows that start and end inside the range
    #      - these will always be returned
    #        (diagrammatically,   |##|  )
    #   2) Shows that start before but end inside the range
    #      - these will be returned if exclude_before_start=False
    #        (diagrammatically, ##|##|  )
    #   3) Shows that start inside but end after the range
    #      - these will be returned if exclude_after_end=False
    #        (diagrammatically,   |##|##)
    #   4) Shows that completely subsume the range
    #      - these will be returned if exclude_subsuming=False
    #        (diagrammatically, ##|##|##)
    if exclude_before_start:  # 1)
        objects = exclude_tuples(
            objects,
            cls.range_start_filter_arg('lt', start),
            cls.range_end_filter_arg('lte', end))
    if exclude_after_end:  # 2)
        objects = exclude_tuples(
            objects,
            cls.range_start_filter_arg('gte', start),
            cls.range_end_filter_arg('gt', end))
    if exclude_subsuming:  # 3)
        objects = exclude_tuples(
            objects,
            cls.range_start_filter_arg('lt', start),
            cls.range_end_filter_arg('gt', end))
    return objects
