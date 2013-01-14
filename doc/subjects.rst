.. _hooks:

=====
Hooks
=====

.. sectionauthor:: Matt Windsor <matt.windsor@ury.org.uk>

The engine for running :ref:`metadata queries <queries>` is quite
flexible and overridable for individual
:ref:`metadata subject models <subjects>`.  It is based on the idea
of running the query against a list of functions, known as *hooks*.

The default hooks set and support scaffolding for running hooks is
found in the module :mod:`metadata.hooks`.

What a hook does
================

A hook is a function that takes a metadata query, processes it, and
either returns the result of that query (if the hook can find metadata
to fulfil it) or raises :class:`metadata.hooks.HookFailureError` if it
cannot fulfil it.

A hook can use *any* means necessary to find the metadata, including
searching external files, caches, the database, or even recursively
running metadata queries for other models.  This makes the metadata
system very general and very powerful.

How hooks lists are used
========================

The hooks system runs lists of hooks in order from first to last with
the query being passed to each.

If :class:`metadata.hooks.HookFailureError` is raised, the hook runner
skips to the next hook.

If the hook succeeds, the hook runner checks with the query to see if
it can terminate with the result it has.  If it can, it does so;
otherwise, it runs either until it can or the runner hits the end of
the hook list, at which point
:class:`metadata.hooks.QueryFailureError` is raised and the query
fails.

The default hooks
=================

When running a metadata query through the high-level :ref:`subject
API <subjects>`, unless the subject has overridden the default
behaviour, the hooks in :py:data:`metadata.hooks.DEFAULT_HOOKS` are
called.

The current set of default hooks and their semantics can be found in the
API documentation for :py:module:`metadata.hooks`.