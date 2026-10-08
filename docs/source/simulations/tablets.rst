:hide-secondary-sidebar:

.. meta::
   :description: Add, stop, and remove nodes, and see the load balancer move tablet replicas until the cluster is balanced.

Tablets
=======

This simulation shows ScyllaDB **tablets**, the unit of data distribution that
replaces vnodes.

* Add, stop, decommission, and remove nodes.
* See the load balancer move tablet replicas until the load on each node and
  shard is equal again.
* Each balancing round uses the same rules as the ScyllaDB load balancer. The
  simulation shows the rule that stops each round.

.. simulation:: scylladb-tablets-demo

.. note::

   This is an educational simulation. It is simplified, and it does not show
   all of the ScyllaDB internals exactly.

Source code: `tzach/scylladb-tablets-demo on GitHub <https://github.com/tzach/scylladb-tablets-demo>`_
