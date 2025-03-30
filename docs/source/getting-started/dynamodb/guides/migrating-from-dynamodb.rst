.. meta::
   :description: Migrating from DynamoDB to ScyllaDB, the NoSQL database for data-intensive applications. Learn how to migrate from DynamoDB to ScyllaDB, whether you're using Alternator or CQL.
   :keywords: migrating from DynamoDB, DynamoDB to ScyllaDB, DynamoDB to Alternator, DynamoDB to CQL

Migrating from DynamoDB
-----------------------

Assuming that all features required by the application are supported by ScyllaDB (irrespective of which API you choose), the level of effort should be minimal. The process typically involves lifting your existing DynamoDB tables’ data and then replaying changes from DynamoDB Streams to ScyllaDB. Once that is complete, you update your application to connect to ScyllaDB.

Migrating from DynamoDB to Alternator
=====================================

As the migration target leverages the same API as the source, no transformation is required on the data.
The overall steps are:

#. Enable dual writes (or DynamoDB Streams)
#. Migrate historical data
#. If relying on DynamoDB Streams, replay streams after historical data migration is done

`ScyllaDB’s Migrator <https://github.com/scylladb/scylla-migrator>`_ is a very powerful tool to help users migrate from DynamoDB into ScyllaDB Alternator, as well as from Cassandra to ScyllaDB using CQL.

Check out ScyllaDB Migrator at the `GitHub repo <https://github.com/scylladb/scylla-migrator>`_ as well as the `ScyllaDB University lesson <https://university.scylladb.com/courses/scylla-operations/lessons/migrating-to-scylla/topic/scylladb-migrator/>`_

Step 1: Enable Dual Writes
..........................

#. Use DynamoDB-compatible API libraries such as Boto3, Java AWS SDK, or Golang SDK. No driver changes are needed.
#. Configure your application to write to both AWS DynamoDB and the Alternator cluster simultaneously.
#. Ensure both databases receive all writes and implement retry mechanisms for consistency.
#. Alternatively, use DynamoDB Streams to replicate live writes:
    #. Enable DynamoDB Streams to capture write events.
    #. Use AWS Lambda or an external function to replay these writes into the Alternator cluster.

Step 2: Migrate Historical Data (Lift and Shift)
................................................

#. Use Spark or similar tools to scan the entire DynamoDB table.
#. Alternatively, export data to Amazon S3 and then import the backup into Alternator.

.. warning:: Be mindful of Read Capacity Units (RCUs) to avoid throttling and high costs.

.. note::
    Libraries that leverage the DynamoDB API also work with Alternator. That includes:

    * Python boto3, Java AWS SDK, golang AWS SDK
    * Kafka Streams Connector
    * NoSQL Workbench
    * Spark connectors

Step 3: (If using DynamoDB Streams) Replay Streams
..................................................

#. Use ScyllaDB Migrator to replay DynamoDB Streams

Step 4: Validation
..................

#. Dual-read from both sources, in parallel or in shadowed mode, to ensure consistency
#. If inconsistencies are found, map and correct them

Step 5: Phase out the previous database
.......................................

#. As soon as you are confident with the migration, phase out the old database to avoid costs

Migrating from DynamoDB to CQL
==============================

When migrating from DynamoDB to CQL, table design must be adjusted to meet CQL’s schema and types.

As you plan the migration, map out all Item attributes in DynamoDB and their types in CQL.

Spark is a great way of performing the ETL necessary for the migration. You can  leverage ScyllaDB’s Spark Connector, which relies on its exclusive shard-aware driver, to ensure maximum performance when communicating with ScyllaDB.

Step 1: Enable Dual Writes
..........................

#. Keep using DynamoDB-compatible APIs for writing to DynamoDB.
#. Use ScyllaDB CQL libraries for writing to ScyllaDB.
#. Configure your application to write to both DynamoDB and Scylla CQL in parallel.
#. Use ScyllaDB’s shard-aware drivers for optimal performance.

Step 2: Migrate Historical Data
...............................

#. Read historical data directly from the DynamoDB table or use S3 exports.
#. Convert DynamoDB’s schema-less data to Scylla’s schema-enforced format.
#. Apply ETL transformations to align data types between DynamoDB and CQL.

**To optimize CQL performance**:

#. Use ScyllaDB’s shard-aware drivers (enabled by default), which are available for C, Python, Go, Java, and other languages.
#. Ensure rack-awareness to minimize cross-AZ traffic to reduce cost and optimize latency.
