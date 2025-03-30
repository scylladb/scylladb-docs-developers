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
