Multiple Data Centers
---------------------

ScyllaDB Alternator supports tables in multi-regions by default. On a multi-datacenter cluster, tables are always created using Replication Factor = 3 and covering all regions. That means that all tables are Global Tables by default.
Tables can be customized to cover existing regions as needed. You can have one table that is local to a single DC, while other tables are global covering all existing DCs, or any combination thereof.

Write Consistency
=================

Writes through the Alternator API are always done in LOCAL_QUORUM consistency, meaning it has to achieve quorum on the local datacenter before being considered complete.

In a Multi-DC scenario, writes are replicated according to the Replication Factor of the keyspace. The shard acting as a request’s coordinator sends remote DCs a replica of the data – which is acknowledged by the remote-DC coordinator. In turn, the remote-DC coordinator then sends data locally to other replicas. This avoids cross-Region traffic as data is replicated once per DC and locally to other replicas.

Read Consistency
================

Reads through the Alternator API follow the same concepts as in DynamoDB: they are eventually consistent by default (LOCAL_ONE consistency in ScyllaDB terms) and can be switched to Consistent mode in the API call (LOCAL_QUORUM consistency).

Reads never leave the DC boundary in Alternator – both API-compatible read consistency options are always local.
