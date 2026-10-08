:hide-secondary-sidebar:

.. meta::
   :description: See how incremental repair reads only the SSTables that no earlier repair verified, and skips the rest.

Incremental Repair
==================

This simulation shows ScyllaDB **incremental repair**. A repair round reads only
the SSTables that no earlier repair verified. It skips all other SSTables.

* Three replicas hold one tablet. Writes start when the page opens. You can
  pause them.
* Run a repair, and see it read the unrepaired SSTables, send the rows that
  are different, and mark the SSTables as repaired.
* Run the repair again. The second round skips the SSTables that the first
  round verified.
* Compare the ``incremental``, ``full``, and ``disabled`` repair modes.

.. simulation:: repair-viz

.. note::

   This is an educational simulation. It is simplified, and it does not show
   all of the ScyllaDB internals exactly.

Source code: `tzach/repair-viz on GitHub <https://github.com/tzach/repair-viz>`_
