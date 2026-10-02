:hide-secondary-sidebar:

.. meta::
   :description: Compare materialized views, global indexes, local indexes, and ALLOW FILTERING for the same query.

Materialized Views and Secondary Indexes
========================================

This simulation shows four ways that ScyllaDB can find rows by a column that is
not the partition key:

* Materialized view
* Global secondary index
* Local secondary index
* ``ALLOW FILTERING``

For each mode, the simulation shows the CQL statements, the base table and the
table that ScyllaDB derives from it, and the write and read paths through the
cluster. Use the **Driver** control to compare a smart (token-aware) driver
with a driver that is not token-aware.

.. simulation:: scylladb-mv-viz

.. note::

   This is an educational simulation. It is simplified, and it does not show
   all of the ScyllaDB internals exactly.

Source code: `tzach/scylladb-mv-viz on GitHub <https://github.com/tzach/scylladb-mv-viz>`_
