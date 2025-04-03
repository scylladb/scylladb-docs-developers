Understanding Cost Units
------------------------

DynamoDB offers three pricing models: On Demand, Provisioned, and Reserved Capacity. Each model has its own pricing structure and is designed to meet different needs. The pricing model you choose will depend on your application's requirements and usage patterns.

Linked to these pricing models are different cost units that you need to understand to estimate your costs accurately.

Reads Explained
===============

On Demand pricing consumes Read Request Units (RCUs) for reads. Provisioned pricing consumes Read Capacity Units (RCUs) for reads. Both terms refer to the same thing: a unit of read throughput for reads of up to 4 KB.

One read unit represents one strongly consistent read, or two eventually consistent reads, for an item up to 4 KB in size. The prices for read requests depend on your table class.

The math is simple:

.. code-block:: javascript
    :class: hide-copy-button

    function calculateReadUnits(itemSizeKB, consistency = 'strong') {
        let readUnits = Math.ceil(itemSizeKB / 4);
        if (consistency === 'eventually') {
            readUnits *= 0.5;
        }
        return readUnits;
    }


.. note::
    Item size affects the cost of reads in DynamoDB. DynamoDB will always round up the item size to the nearest 4 KB when calculating the cost of reads. If the item size is larger than 4 KB, DynamoDB will need to consume additional units to read the item. For example:

    * If you read an item that is 300B in size, you will need to consume 1 RCU for a strongly consistent read, or 0.5 RCUs for an eventually consistent read.
    * if you read an item that is 5000 B in size, you will need to consume 2 RCUs for a strongly consistent read, or 1 RCUs for an eventually consistent read.

Consistent reads are more expensive than eventually consistent reads because they require more resources to ensure that the data is up-to-date. If you can tolerate some lag in the data, you can use eventually consistent reads to save on costs.

Writes Explained
================

On Demand pricing consumes Write Request Units (WCUs) for writes. Provisioned pricing consumes Write Capacity Units (WCUs) for writes. Both terms refer to the same thing: a unit of write throughput for writes of up to 1 KB.

One write unit represents one write for an item up to 1 KB in size. The prices for write requests depend on your table class.

The math is simple:

.. code-block:: javascript
    :class: hide-copy-button

    function calculateWriteUnits(itemSizeKB) {
        return Math.ceil(itemSizeKB / 1);
    }

.. note::
    Item size affects the cost of writes in DynamoDB. DynamoDB will always round up the item size to the nearest 1 KB when calculating the cost of writes. If the item size is larger than 1 KB, DynamoDB will need to consume additional units to write the item. For example:

    * If you write an item that is 300B in size, you will need to consume 1 WCU.
    * If you write an item that is 5000 B in size, you will need to consume 5 WCUs.

Writes are more expensive than reads because they require more resources to ensure that the data is written to the database. If you can batch your writes, you can save on costs by writing multiple items in a single request.

Storage Explained
=================

Storage costs are based on the amount of data stored in DynamoDB. You are charged based on the amount of data stored in your tables, indexes, and backups.

DynamoDB automatically scales storage for your tables based on the size of your items and the number of items in your tables. You do not need to provision storage in advance, and you only pay for the storage you use.

Item Size Explained
===================

The size of your items in DynamoDB affects the cost of your reads and writes. DynamoDB charges based on the size of the items you read and write, rounded up to the nearest 1 KB. If your items are larger than 1 KB, you will need to consume additional RCUs and WCUs to read and write the items.

Network Transfer Explained
==========================

Network transfer costs are based on the amount of data transferred in and out of DynamoDB. You are charged based on the amount of data transferred between your application and DynamoDB, as well as between DynamoDB and other AWS services generally when they are in different regions.
