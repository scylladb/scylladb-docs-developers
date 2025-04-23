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
    guides/index
    users/index

.. raw:: html

    <div class="grid-x grid-margin-x">
        <div class="cell large-8 small-8">


Ditch the DynamoDB Tax
----------------------

ScyllaDB is a cost-effective and flexible alternative to DynamoDB – at least 50% lower cost and lower latency under most workloads. This exceptional price-performance results from a close-to-the-metal architecture and numerous engineering optimizations for performance, elasticity, and efficiency. Another advantage: with ScyllaDB, you can take your DynamoDB workloads beyond AWS and run on any cloud, bare metal, or hybrid.

To simplify migration, we offer ScyllaDB Alternator, a DynamoDB-compatible API. You redirect your application to ScyllaDB and it “just works” (actually, it listens on a specific port that understands the DynamoDB API). In most cases, minimal code changes are required.

.. raw:: html

        </div>
    <div class="cell large-4 small-4">

.. figure:: images/ditch-the-tax.png
   :width: 300px
   :alt: Ditch the DynamoDB Tax

.. raw:: html

      </div>
    </div>

Featured Lab
------------

Follow a code-complete, hands-on tutorial to learn about switching to ScyllaDB from DynamoDB.

.. raw:: html

    <div class="card-grid">

.. card-box::
    :link: labs/simple-application
    :image: ../../_static/icons/alternator.svg" style="width:24px
    :title: ScyllaDB Alternator

.. raw:: html

    </div>&nbsp;

`See more labs <#>`_

Practical Guides
----------------

.. raw:: html

    <div class="card-grid">

.. card-box::
    :link: guides/cost/caclulator
    :title: DynamoDB Cost Calculator
    :description: Estimate costs for DynamoDB with our handy calculator.

.. card-box::
    :link: guides/cost/scenarios
    :title: Real World Costs
    :description: Understand the true cost of DynamoDB and how ScyllaDB compares.

.. card-box::
    :link: guides/migration/index
    :title: Migrating from DynamoDB
    :description: A step-by-step look at what a migration involves and how to avoid pitfalls.

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

:doc:`View more user stories <users/index>`

Featured Documentation
----------------------

.. raw:: html

    <div class="card-grid">

.. card-box::
    :link: https://docs.scylladb.com/manual/stable/alternator/alternator.html
    :title: Alternator DynamoDB API
    :description: Project Alternator is an Amazon DynamoDB compatible API written in C++.

.. card-box::
    :link: https://docs.scylladb.com/manual/stable/alternator/compatibility.html
    :title: Alternator API differences
    :description: The Alternator API is designed to be compatible with the DynamoDB API, but there are some differences.

.. card-box::
    :link: https://docs.scylladb.com/manual/stable/alternator/new-apis.html
    :title: Alternator specific APIs
    :description: The Alternator API has several additional features and APIs that are not available in DynamoDB.

.. raw:: html

    </div>&nbsp;

`See more documentation <https://docs.scylladb.com/stable/index.html>`_
