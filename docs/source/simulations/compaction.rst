:hide-secondary-sidebar:

.. meta::
   :description: See SSTables flush and merge, and compare the space, write, and read amplification of each compaction strategy.

Compaction Strategies
=====================

This simulation shows the ScyllaDB write path: **write → commitlog → memtable →
flush → compaction**.

* Select a compaction strategy: Incremental (ICS), Leveled (LCS), or
  Time-Window (TWCS).
* Select a workload, and see SSTables accumulate and merge.
* The simulation measures space, write, and read amplification from the
  simulated data.
* The sub-properties have the same names as the
  `CQL compaction options <https://docs.scylladb.com/manual/stable/cql/compaction.html>`_.

.. simulation:: compaction-viz

.. note::

   This is an educational simulation. It is simplified, and it does not show
   all of the ScyllaDB internals exactly.

Source code: `tzach/compaction-viz on GitHub <https://github.com/tzach/compaction-viz>`_
