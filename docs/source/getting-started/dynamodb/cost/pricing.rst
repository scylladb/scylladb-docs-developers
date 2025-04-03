.. contents::
   :depth: 4
   :local:

Understanding Pricing Models
----------------------------

We've put together an overview of each pricing model to help you understand the differences and choose the one that's right for you when considering DynamoDB.

Pricing Model Overview
======================

DynamoDB offers three pricing models: On Demand, Provisioned, and Reserved Capacity. Each model has its own pricing structure and is designed to meet different needs. The pricing model you choose will depend on your application's requirements and usage patterns.

On Demand
.........

On Demand pricing is a pay-as-you-go model that charges you based on the number of read and write requests your application makes. This model is suited for applications with unpredictable workloads or for those that are just starting out. However there is a premium for this flexibility, and costs can quickly add up if your application has unpredictable or high-volume traffic.

Provisioned
...........

Provisioned pricing allows you to reserve read and write capacity for your tables. You pay a fixed hourly rate for the capacity you reserve, regardless of how much you use. This model is ideal for applications with predictable workloads, as it can help you save money by reserving capacity in advance. However, if you exceed your reserved capacity, your requests will be throttled, which can impact your application's performance.

Reserved Capacity
..................

Reserved Capacity pricing allows you to reserve read and write capacity for your tables for a one or three year term. You pay an upfront fee for the capacity you reserve, and receive a discount on the hourly rate. This model is ideal for applications with steady workloads, as it can help you save money in the long run. However, you will be charged for the reserved capacity even if you don't use it.

How these Models Compare to Themselves
======================================

When comparing the three pricing models, it's important to consider your application's requirements and usage patterns. If you have relatively low volume workloads, On Demand pricing may still be the best option for you. If you have a relatively static workload, Provisioned pricing may be the best option for you.

Relative cost can vary significantly depending on your application's usage patterns. In general, On Demand pricing is the most expensive option, while Reserved Capacity pricing is the cheapest option. Provisioned pricing falls in between the two.

.. raw:: html

    <p class="mark">What you need to know up front is that the On Demand pricing model is the most expensive option. You will be paying up to a +700% premium for the flexibility of not having to provision capacity.</p>

The Reserved Capacity pricing model is the cheapest option, but it requires you to pay for the reserved capacity even if you don't use it.

Take a look at the tables below for a quick comparison of the three pricing models.

Write Heavy Workloads
.....................

Write-heavy workloads are those that have a high number of write requests compared to read requests. These workloads are typically characterized by a high volume of data being written to the database, such as real time events, logs, or telemetry data.

.. list-table:: Steady State Write Heavy @ 20k reads/sec + 100k writes/sec
    :widths: 33 33 33
    :header-rows: 1

    * - On Demand
      - Provisioned
      - Reserved Capacity
    * - `$170k <https://calculator.scylladb.com/?pricing=demand&storageGB=512&itemSizeB=1024&tableClass=standard&ratio=50&baselineReads=20000&baselineWrites=100000&peakReads=20000&peakWrites=100000&peakDurationReads=0&peakDurationWrites=0&reserved=0&readConst=100>`_ per month

        most expensive
      - `$49k <https://calculator.scylladb.com/?pricing=provisioned&storageGB=512&itemSizeB=1024&tableClass=standard&ratio=50&baselineReads=20000&baselineWrites=100000&peakReads=20000&peakWrites=100000&peakDurationReads=0&peakDurationWrites=0&reserved=0&readConst=100>`_ per month

        3.4x cheaper
      - `$22k <https://calculator.scylladb.com/?pricing=provisioned&storageGB=512&itemSizeB=1024&tableClass=standard&ratio=50&baselineReads=20000&baselineWrites=100000&peakReads=20000&peakWrites=100000&peakDurationReads=0&peakDurationWrites=0&reserved=100&readConst=100>`_ per month

        7.6x cheaper

.. list-table:: Peak Hour Write Heavy @ 20k reads/sec + 100k writes/sec + 500k writes/sec for 3 hours/day
    :widths: 33 33 33
    :header-rows: 1

    * - On Demand
      - Provisioned
      - Reserved Capacity
    * - `$251k <https://calculator.scylladb.com/?pricing=demand&storageGB=512&itemSizeB=1024&tableClass=standard&ratio=50&baselineReads=20000&baselineWrites=100000&peakReads=20000&peakWrites=500000&peakDurationReads=0&peakDurationWrites=3&reserved=0&readConst=100>`_ per month

        most expensive
      - `$72k <https://calculator.scylladb.com/?pricing=provisioned&storageGB=512&itemSizeB=1024&tableClass=standard&ratio=50&baselineReads=20000&baselineWrites=100000&peakReads=20000&peakWrites=500000&peakDurationReads=0&peakDurationWrites=3&reserved=0&readConst=100>`_ per month

        3.4x cheaper
      - `$46k <https://calculator.scylladb.com/?pricing=provisioned&storageGB=512&itemSizeB=1024&tableClass=standard&ratio=50&baselineReads=20000&baselineWrites=100000&peakReads=20000&peakWrites=500000&peakDurationReads=0&peakDurationWrites=3&reserved=100&readConst=100>`_ per month

        5.4x cheaper

Read Heavy Workloads
....................

Read-heavy workloads are those that have a high number of read requests compared to write requests. These workloads are typically characterized by a high volume of data being read from the database, such as near real time events, caching, or reporting data.

.. list-table:: Steady State Read Heavy @ 100k reads/sec + 20k writes/sec
    :widths: 33 33 33
    :header-rows: 1

    * - On Demand
      - Provisioned
      - Reserved Capacity
    * - `$65k <https://calculator.scylladb.com/?pricing=demand&storageGB=512&itemSizeB=1024&tableClass=standard&ratio=50&baselineReads=100000&baselineWrites=20000&peakReads=100000&peakWrites=20000&peakDurationReads=0&peakDurationWrites=0&reserved=0&readConst=100>`_ per month

        most expensive
      - `$19k <https://calculator.scylladb.com/?pricing=provisioned&storageGB=512&itemSizeB=1024&tableClass=standard&ratio=50&baselineReads=100000&baselineWrites=20000&peakReads=100000&peakWrites=20000&peakDurationReads=0&peakDurationWrites=0&reserved=0&readConst=100>`_ per month

        3.4x cheaper
      - `$8.8k <https://calculator.scylladb.com/?pricing=provisioned&storageGB=512&itemSizeB=1024&tableClass=standard&ratio=50&baselineReads=100000&baselineWrites=20000&peakReads=100000&peakWrites=20000&peakDurationReads=0&peakDurationWrites=0&reserved=100&readConst=100>`_ per month

        7.3x cheaper

.. list-table:: Peak Hour Read Heavy @ 100k reads/sec + 20k writes/sec + 500k reads/sec for 3 hours/day
    :widths: 33 33 33
    :header-rows: 1

    * - On Demand
      - Provisioned
      - Reserved Capacity
    * - `$82k <https://calculator.scylladb.com/?pricing=demand&storageGB=512&itemSizeB=1024&tableClass=standard&ratio=50&baselineReads=100000&baselineWrites=20000&peakReads=500000&peakWrites=20000&peakDurationReads=3&peakDurationWrites=0&reserved=0&readConst=100>`_ per month

        most expensive
      - `$23k <https://calculator.scylladb.com/?pricing=provisioned&storageGB=512&itemSizeB=1024&tableClass=standard&ratio=50&baselineReads=100000&baselineWrites=20000&peakReads=500000&peakWrites=20000&peakDurationReads=3&peakDurationWrites=0&reserved=0&readConst=100>`_ per month

        3.5x cheaper
      - `$13k <https://calculator.scylladb.com/?pricing=provisioned&storageGB=512&itemSizeB=1024&tableClass=standard&ratio=50&baselineReads=100000&baselineWrites=20000&peakReads=500000&peakWrites=20000&peakDurationReads=3&peakDurationWrites=0&reserved=100&readConst=100>`_ per month

        6.3x cheaper

.. note::
    The above scenarios are based on the following assumptions:

    * 512 GB of data stored in DynamoDB
    * 1 KB item size
    * Standard table class
    * 3 hours of peak traffic per day (for the peak hour scenarios)
    * 100% read consistency
    * Upfront payment for reserved capacity included in monthly estimates

How this Compares to ScyllaDB
=============================

ScyllaDB offers a different pricing model than DynamoDB. ScyllaDB charges based on the number of cores/storage you use, rather than the number of read and write requests. This can make it more cost-effective for applications with high-volume traffic, as you don't have to worry about exceeding your provisioned capacity and being throttled.

For example, all of the above scenarios would cost $7k  per month for ScyllaDB. This is a significant savings compared all of the DynamoDB pricing models for ScyllaDB's On Demand pricing. Longer term savings can be achieved with annual commitments.

.. raw:: html

    <p class="mark">In fact, we're so confident in our pricing model that guarantee 50% off your existing DynamoDB workload costs.</p>

When comparing DynamoDB and ScyllaDB, it's important to consider your application's requirements and usage patterns. If you have relatively low volume workloads, DynamoDB's On Demand pricing may still  be the best option for you. If you have a relatively static workload, DynamoDB's Reserved Capacity pricing may be the best option for you.

However, if you have real-life unpredictable workloads, or high-volume traffic and want to avoid throttling, ScyllaDB's pricing model is likely be more cost-effective. Many of ScyllaDB's customers have reported significant cost savings after switching from DynamoDB for these reasons:

* No need to worry about exceeding provisioned capacity and being throttled
* No need to pay for unused capacity
* No need to worry about unpredictable traffic spikes
* No need to worry about the cost of read and write requests

.. note::
    The 7k per month cost for ScyllaDB is based on the following assumptions:

    * Max dataset size 1.961 TB
    * Peak throughput 540,000 ops/sec
    * Sustained throughput 351,000 ops/sec
    * 9 x i4i.xlarge (4 vCPUs, 32 GB RAM, 937 GB storage)
    * Disk storage 8.24 TB
    * Total vCPU 36
