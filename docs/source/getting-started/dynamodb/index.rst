:hide-secondary-sidebar:

.. meta::
   :description: Switching from DynamoDB to ScyllaDB. This guide covers the differences between the two databases and how to migrate your data.
   :keywords: DynamoDB, ScyllaDB, migration, switch, guide

=======================
Switching from DynamoDB
=======================
.. toctree::
    :hidden:

    labs/index
    fit/index
    cost/index
    considerations/index
    guides/index
    users/index

.. raw:: html

    <div class="grid-x grid-margin-x">
        <div class="cell large-8 small-8">


Ditch the DynamoDB Tax
----------------------

ScyllaDB is a cost-effective and flexible alternative to DynamoDB – at least 50% lower cost and lower latency under most workloads. This exceptional price-performance results from a close-to-the-metal architecture and numerous engineering optimizations for performance, elasticity, and efficiency. Another advantage: with ScyllaDB, you can take your DynamoDB workloads beyond AWS and run on any cloud, bare metal, or hybrid.

To simplify migration, we offer ScyllaDB Alternator, an open-source DynamoDB-compatible API. You redirect your application to ScyllaDB and it “just works” (actually, it listens on a specific port that understands the DynamoDB API). In most cases, minimal code changes are required.

.. raw:: html

        </div>
    <div class="cell large-4 small-4">

.. figure:: images/ditch-the-tax.png
   :width: 300px
   :alt: Ditch the DynamoDB Tax

.. raw:: html

      </div>
    </div>

Featured Labs
-------------

Follow a code-complete, hands-on tutorial to learn about switching to ScyllaDB from DynamoDB.

.. raw:: html

    <div class="card-grid">

.. card-box::
    :link: #
    :image: ../../_static/icons/alternator.svg" style="width:24px
    :title: ScyllaDB Alternator

.. card-box::
    :link: #
    :image: ../../_static/icons/table_chart.svg
    :title: Single table design

.. card-box::
    :link: #
    :image: ../../_static/icons/table_rows.svg
    :title: Multi-table design

.. raw:: html

    </div>&nbsp;

`See more labs <#>`_

Important Considerations
------------------------

.. raw:: html

    <div class="card-grid">

.. card-box::
    :link: considerations/understanding-differences
    :title: Understanding Differences
    :description: How the databases compare: data model, query language, and more.

.. card-box::
    :link: considerations/alternator-or-cql
    :title: Alternator or CQL
    :description: How Alternator and CQL differ – and tips on which to choose.

.. card-box::
    :link: considerations/migration-paths
    :title: Migration Paths
    :description: What’s required to migrate to ScyllaDB with Alternator and CQL.

.. raw:: html

    </div>&nbsp;

:doc:`See more considerations <considerations/index>`

Practical Guides
----------------

.. raw:: html

    <div class="card-grid">

.. card-box::
    :link: guides/multiple-data-centers
    :title: Multiple Data Centers
    :description: Tips for setting up tables in multiple regions.

.. card-box::
    :link: guides/migrating-from-dynamodb
    :title: Migrating from DynamoDB
    :description: A step-by-step look at what a migration involves.

.. card-box::
    :link: guides/avoiding-pitfalls
    :title: Avoiding Migration Pitfalls
    :description: What mistakes commonly arise and how to avoid them.

.. raw:: html

    </div>&nbsp;

:doc:`View more guides <guides/index>`

Popular Use Cases
-----------------

.. raw:: html

    <div class="card-grid">

.. card-box::
    :link: users/yieldmo
    :title: Yieldmo
    :description: Yieldmo moved from DynamoDB for lower costs, improved latencies, and the freedom to run on GCP as well as AWS.

.. card-box::
    :link: users/digital-turbine
    :title: Digital Turbine
    :description: As part of an organization-wide AWS to GCP migration, Digital Turbine moved their DynamoDB workloads to GCP in just one sprint.

.. card-box::
    :link: users/ifood
    :title: iFood
    :description: iFood migrated from DynamoDB to ScyllaDB for lower costs, better performance, and the ability to run on any cloud.

.. raw:: html

    </div>&nbsp;

:doc:`View more guides <guides/index>`

Featured Documentation
----------------------

.. raw:: html

    <div class="card-grid">

.. card-box::
    :link: https://enterprise.docs.scylladb.com/stable/using-scylla/alternator/
    :title: Alternator DynamoDB API
    :description: Project Alternator is an Amazon DynamoDB compatible API written in C++.

.. card-box::
    :link: https://enterprise.docs.scylladb.com/stable/alternator/compatibility.html
    :title: Alternator API differences
    :description: The Alternator API is designed to be compatible with the DynamoDB API, but there are some differences.

.. card-box::
    :link: https://enterprise.docs.scylladb.com/stable/alternator/new-apis.html
    :title: Alternator specific APIs
    :description: The Alternator API has several additional features and APIs that are not available in DynamoDB.

.. raw:: html

    </div>&nbsp;

`See more documentation <https://opensource.docs.scylladb.com/stable/index.html>`_