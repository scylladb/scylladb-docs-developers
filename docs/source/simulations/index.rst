:hide-secondary-sidebar:

.. meta::
   :description: Interactive simulations of ScyllaDB internals: high availability, tablets, compaction, repair, and materialized views.

Simulations
===========

Use these interactive simulations to see how ScyllaDB works. Each simulation
runs in your browser. You do not need to install ScyllaDB.

.. toctree::
   :hidden:

   high-availability
   tablets
   compaction
   incremental-repair
   materialized-views

.. raw:: html

   <div class="simulation-grid">

.. simulation-card::
   :title: High Availability
   :doc: high-availability
   :image: /_static/img/simulations/scylladb-ha-demo.png
   :description: See how the replication factor and consistency level control which requests succeed when nodes or zones fail.

.. simulation-card::
   :title: Tablets
   :doc: tablets
   :image: /_static/img/simulations/scylladb-tablets-demo.png
   :description: Add, stop, and remove nodes, and see the load balancer move tablet replicas until the cluster is balanced.

.. simulation-card::
   :title: Compaction Strategies
   :doc: compaction
   :image: /_static/img/simulations/compaction-viz.png
   :description: See SSTables flush and merge, and compare the space, write, and read amplification of each compaction strategy.

.. simulation-card::
   :title: Incremental Repair
   :doc: incremental-repair
   :image: /_static/img/simulations/repair-viz.png
   :description: See how incremental repair reads only the SSTables that no earlier repair verified, and skips the rest.

.. simulation-card::
   :title: Materialized Views and Secondary Indexes
   :doc: materialized-views
   :image: /_static/img/simulations/scylladb-mv-viz.png
   :description: Compare materialized views, global indexes, local indexes, and ALLOW FILTERING for the same query.

.. raw:: html

   </div>
