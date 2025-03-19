:hide-secondary-sidebar:

.. meta::
   :description: Switching from DynamoDB to ScyllaDB. This guide covers the differences between the two databases and how to migrate your data.
   :keywords: dynamodb, scylladb, migration, switch, guide

Switching from DynamoDB
=======================
.. toctree::
    :hidden:

    labs/index
    fit/index
    considerations/index
    guides/index
    users/index

.. raw:: html

    <div class="grid-x grid-margin-x">
        <div class="cell large-8 small-8">

**Ditch the DynamoDB Tax**

ScyllaDB is a cost-effective and flexible alternative to DynamoDB – at least 50% lower cost and lower latency under most workloads. This exceptional price-performance results from a close-to-the-metal architecture and numerous engineering optimizations for performance, elasticity, and efficiency. Another advantage: with ScyllaDB, you can take your DynamoDB workloads beyond AWS and run on any cloud, bare metal, or hybrid.

To simplify migration, we offer ScyllaDB Alternator, an open-source DynamoDB-compatible API. You redirect your application to ScyllaDB and it “just works” (actually, it listens on a specific port that understands the DynamoDB API). In most cases, minimal code changes are required.

.. raw:: html

        </div>
    <div class="cell large-4 small-4">

.. figure:: images/placeholder.png
   :width: 300px
   :alt: Placeholder Image

.. raw:: html

      </div>
    </div>

=============
Featured Labs
=============

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

======================
Featured Documentation
======================

.. raw:: html

    <div class="card-grid">

.. card-box::
    :link: https://opensource.docs.scylladb.com/stable/using-scylla/alternator/
    :title: ScyllaDB Alternator
    :description: Project Alternator is an open-source project for an Amazon DynamoDB™-compatible API written in C++.

.. card-box::
    :link: https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/Welcome.html
    :title: API Reference
    :description: Amazon DynamoDB provides low-level API documentation.

.. card-box::
    :link: https://opensource.docs.scylladb.com/stable/alternator/compatibility.html
    :title: Differences
    :description: The purpose of this document is to highlight differences between the API and ScyllaDB Alternator.

.. raw:: html

    </div>&nbsp;

`See more documentation <https://opensource.docs.scylladb.com/stable/index.html>`_