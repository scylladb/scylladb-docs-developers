:hide-secondary-sidebar:

The True Cost of DynamoDB
-------------------------

.. toctree::
    :maxdepth: 3
    :hidden:

    pricing
    units
    billing
    global-tables
    dax
    scenarios

If you’re building on DynamoDB, understanding its cost model is critical, especially as workloads scale. But AWS’s pricing complexity often makes that easier said than done. That’s why we built the DynamoDB Cost Calculator: a tool that gives you a clear, fast estimate of what your workloads will really cost.

Whether you’re running production systems or just exploring alternatives like ScyllaDB, this tool helps you break down the key cost drivers and compare options with confidence.

This calculator is available at `calculator.scylladb.com <https://calculator.scylladb.com>`_ if you want to share or you can try it below.

Why We Built It
===============

DynamoDB pricing isn’t straightforward. Costs can balloon based on read/write patterns, data volume, provisioned capacity, and usage spikes, especially if you’re on on-demand mode. While AWS offers a pricing calculator, it’s not exactly developer friendly, and it often misses the nuance of real-world workloads (e.g., bursty traffic or uneven access patterns).

We wanted something better. So we built a calculator that’s:

* Simple to use
* Tuned for real workload patterns

Who It’s For
============

If you’re a developer, architect, or decision-maker trying to evaluate DynamoDB costs or considering a switch to ScyllaDB this tool is for you. You can use it to:

* Estimate current DynamoDB costs
* Explore what a move to ScyllaDB could save you
* Justify architectural decisions with real data

Whether you’re optimizing an existing deployment or planning a migration, this calculator gives you the numbers you need to move forward with confidence.

.. raw:: html

    <div style="position: relative; width: 100%; padding-bottom: 170%; height: 0; overflow: hidden;">
        <iframe
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: transparent;"
            src="https://calculator.scylladb.com"
            title="DynamoDB Cost Calculator"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            referrerpolicy="strict-origin-when-cross-origin"
            allowfullscreen>
        </iframe>
    </div>
