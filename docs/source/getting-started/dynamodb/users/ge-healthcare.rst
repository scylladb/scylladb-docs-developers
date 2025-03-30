:hide-secondary-sidebar:

.. meta::
   :description: GE Healthcare’s Edison AI platform faced the challenge of deploying their AWS cloud-based Edison AI Workbench on-premises for research customers who required it within their own data centers. Learn how they avoided vendor lock-in with ScyllaDB.
   :keywords: ScyllaDB, DynamoDB, migration, cost-effectiveness, performance, compatibility

GE Healthcare
-------------

.. raw:: html

     <div style="position: relative; width: 100%; padding-bottom: 56.25%; height: 0; overflow: hidden;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
             src="https://www.youtube.com/embed/tt7b81w63Do?si=SwtRiooFW3xbK7e8"
             title="YouTube video player" frameborder="0"
             allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
             referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>
         </iframe>
     </div>

Avoiding Vendor Lock-In with ScyllaDB
=====================================

GE Healthcare’s Edison AI platform faced the challenge of deploying their AWS cloud-based Edison AI Workbench on-premises for research customers who required it within their own data centers. The core issue was the Workbench’s dependency on DynamoDB, leading to the need to either rewrite the application or find a DynamoDB-compatible database.

Why ScyllaDB?
=============

To address this challenge, they chose ScyllaDB’s Project Alternator for its:

#. DynamoDB API compatibility, enabling migration with minimal code changes.
#. Kubernetes support, which facilitated microservice porting and deployment.
#. Ability to run in hybrid topologies with DynamoDB.
#. Developer-level support and effective partnership from the ScyllaDB team.

How Did They Migrate?
=====================

The migration process involved a quick proof-of-concept (POC) to validate ScyllaDB’s DynamoDB API compatibility and on-premises deployment capabilities, which enabled the rapid deployment of the Edison AI Workbench on-premises, met customer requirements for local data center operations, and accelerated the delivery timeline for the Workbench solution.
