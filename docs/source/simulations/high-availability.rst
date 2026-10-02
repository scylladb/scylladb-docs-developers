:hide-secondary-sidebar:

.. meta::
   :description: See how the replication factor and consistency level control which requests succeed when nodes or zones fail.

High Availability
=================

This simulation shows how ScyllaDB replicates data across nodes and zones (racks),
and how the replication factor (RF) and the consistency level (CL) control
which requests succeed.

* Send writes and reads from each client. Each request goes through a
  coordinator to the replicas of the key.
* Click a node to stop or start it. Click the border of a zone to stop or
  start all of its nodes.
* Change the number of nodes, zones, clients, the RF, and the CL.
* Turn on **Smart Drivers** to compare token-aware routing with routing
  through a proxy node.

.. simulation:: scylladb-ha-demo

.. note::

   This is an educational simulation. It is simplified, and it does not show
   all of the ScyllaDB internals exactly.

Source code: `tzach/scylladb-ha-demo on GitHub <https://github.com/tzach/scylladb-ha-demo>`_
