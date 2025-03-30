:hide-secondary-sidebar:

.. meta::
   :description: Yieldmo faced challenges with DynamoDB due to rising costs and limitations in cross-cloud deployment. They chose ScyllaDB for its cost-effectiveness, performance, and compatibility with DynamoDB.
   :keywords: ScyllaDB, DynamoDB, Yieldmo, migration, cost-effectiveness, performance, compatibility

Yieldmo
-------

.. raw:: html

     <div style="position: relative; width: 100%; padding-bottom: 56.25%; height: 0; overflow: hidden;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
             src="https://www.youtube.com/embed/sk0mIiaOwM8?si=V3nAYK9Er4iBETEh"
             title="YouTube video player" frameborder="0"
             allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
             referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>
         </iframe>
     </div>

Facing Challenges with DynamoDB
===============================

Yieldmo, an advertising platform, faced challenges with DynamoDB due to rising costs and limitations in cross-cloud deployment, particularly when attempting to connect from GCP Amsterdam to AWS DynamoDB in Dublin. To address this, they sought an alternative database solution that offered cost reduction, cross-cloud compatibility, and maintained speed and reliability. They evaluated several options including:

#. Caching Layer with DynamoDB
#. Aerospike

Why ScyllaDB?
=============

Ultimately, Yieldmo chose ScyllaDB for its:

#. Multiple cloud provider support
#. Cost-effectiveness
#. Good performance
#. DynamoDB compatibility, which minimized code changes
#. Support from ScyllaDB's team during the proof of concept (POC), making migration easier

How Did They Migrate?
=====================

The migration process involved a POC, collaborative planning with ScyllaDB, addressing data migration challenges with multi-terabyte tables and continuous updates, and utilizing a Spark cluster and Kafka for data loading and synchronization. The impact of the migration included significant cost savings, enabled GCP integration with reduced latency, and modest speed improvements.
