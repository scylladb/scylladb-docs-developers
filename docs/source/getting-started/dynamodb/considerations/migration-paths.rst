:hide-secondary-sidebar:

Migration Paths
===============

.. image:: migration-paths-light.png
    :alt: Migration Paths
    :width: 90%
    :class: light-mode

.. image:: migration-paths-dark.png
    :alt: Migration Paths
    :width: 90%
    :class: dark-mode

The process for moving from DynamoDB to ScyllaDB depends on whether you decide to use Alternator or CQL. In general:

#. **Migrating to ScyllaDB Alternator**: Minimal changes required. DynamoDB-compatible applications run natively without modifications. Tables and data types are fully compatible. This allows running DynamoDB-compatible workloads outside AWS, on any cloud or on-premises.

#. **Migrating to ScyllaDB CQL**: Requires application refactoring. You need to rewrite the application to use CQL drivers and modify table schemas to fit CQL’s data model. The tradeoff is access to ScyllaDB’s richer feature set and higher performance.
