Alternator or CQL
=================

.. image:: alternator-or-cql-light.png
    :alt: Alternator or CQL
    :width: 90%
    :class: light-mode

.. image:: alternator-or-cql-dark.png
    :alt: Alternator or CQL
    :width: 90%
    :class: dark-mode

ScyllaDB uses CQL (Cassandra Query Language), which serves three purposes:

#. **Query language**: Defines the syntax and structure for building queries.
#. **Protocol**: Uses a binary protocol to transfer data between clients and servers.
#. **Data model**: Provides types and structures for creating keyspaces, column families, indexes, and more.

**Alternator** is ScyllaDB’s DynamoDB-compatible API. It is not a translation layer. Instead, DynamoDB API queries are interpreted directly by ScyllaDB’s native mechanisms. This avoids performance loss caused by translation and ensures efficient execution. Alternator also uses standard data transport protocols.

===================
What is Alternator?
===================

ScyllaDB launched in 2015 with support for Cassandra's CQL API. In 2019, ScyllaDB added the DynamoDB-compatible API called "Alternator." Alternator is not a separate product from ScyllaDB. It's an integrated feature within the same database system that allows ScyllaDB to process DynamoDB API requests alongside traditional CQL requests. It provides the following benefits:

#. Processes HTTP requests with JSON payloads.
#. Uses the same installation as standard ScyllaDB
#. Requires minimal configuration changes:
    #. Uses a port specification for Alternator traffic
    #. Offers read-modify-write operation isolation settings

A single ScyllaDB cluster can simultaneously support both CQL and DynamoDB API requests.

=============
Compatibility
=============

ScyllaDB’s Alternator project aims to achieve full compatibility with the DynamoDB API, allowing users to run unmodified applications originally designed for Amazon's service. While most DynamoDB features are supported, some limitations exist. For example:

#. Single-item transactions are supported
#. Multi-item transactions are not currently implemented

A complete list of supported and unsupported features is maintained in the `documentation <https://docs.scylladb.com/manual/stable/alternator/compatibility.html>`_.

=========================
Architectural Differences
=========================

DynamoDB and Alternator/ScyllaDB operate on fundamentally different architectural models:

#. **DynamoDB**:
    #. Multi-tenant Software as a Service
    #. Users typically unaware of underlying infrastructure
    #. Single endpoint abstracts cluster details
#. **Alternator/ScyllaDB**:
    #. Dedicated installation for each customer
    #. Cluster-aware architecture
    #. Node selection becomes important for request routing

The `ScyllaDB Alternator for DynamoDB users docs page <https://docs.scylladb.com/manual/stable/alternator/compatibility.html>`_ contains a detailed breakdown of different and not yet implemented features. Keep in mind that even if some features are not yet implemented, you might be able to achieve the same functionality in ScyllaDB in other ways.

==============
Load Balancing
==============

In traditional DynamoDB applications, a single endpoint URL (like a US-East-1 regional endpoint) is configured. Applications have no awareness of individual nodes behind that endpoint, which means they cannot:

#. Send requests to the optimal node that holds the data
#. Intelligently distribute load across available nodes in the cluster

This creates a challenge for efficiently routing requests in ScyllaDB Alternator.

==========================
Server-Side Load Balancing
==========================

There are two primary approaches to server-side load balancing:

#. **HTTP/TCP Load Balancer**
    #. Client sends requests to a load balancer
    #. Load balancer forwards to a random live node
    #. ScyllaDB then routes to the node that holds the requested data

    This approach works but requires dedicated load balancer infrastructure and adds network hops, increasing latency.

#. **ScyllaDB Coordinator-Only Node**
    #. Specific ScyllaDB nodes act solely as coordinators
    #. These nodes don't store data but route requests to the appropriate data-holding nodes

Both approaches function correctly but come with infrastructure and performance costs.

==========================
Client-Side Load Balancing
==========================

Client-side load balancing offers a more efficient solution. Implementation follows these steps:

#. Create a wrapper around the standard Amazon SDK
#. Configure the SDK with one initial Scylla node instead of a single endpoint URL
#. The wrapper discovers the cluster topology and learns about all available nodes
#. Applications continue using unmodified API calls (get_item, put_item, etc.)

Behind the scenes, this wrapper:

#. Maintains a list of live nodes (automatically removing failed nodes)
#. Selects nodes based on geographic proximity (regions, availability zones)
#. Routes requests directly to nodes that hold the requested data when possible

The benefits include:

#. Lower infrastructure costs (no dedicated load balancer nodes)
#. Reduced networking costs (avoiding cross-availability zone traffic)
#. Improved request latency (fewer network hops)

=================
CQL or Alternator
=================
ScyllaDB implements CQL (Cassandra Query Language), which serves as a comprehensive ecosystem. CQL functions simultaneously as:

#. A query language for data retrieval
#. A protocol for client-server communication
#. A data model for structural organization

The CQL implementation in ScyllaDB encompasses everything from table design to the binary protocol used for client-server interaction.

**CQL Schema Structure**

CQL enforces a defined schema consisting of:

#. Partition keys (potentially composite)
#. Zero to many clustering keys
#. SQL-inspired native types
#. User-defined types (UDTs)
#. Materialized views
#. Secondary indexes and global secondary indexes
#. Change Data Capture (CDC) capabilities

**DynamoDB Schema Structure**

DynamoDB takes a different approach, enforcing keys rather than a complete schema:

#. Primary key
#. Sharding key
#. DynamoDB native types
#  Local secondary indexes
#. Global secondary indexes
#. DynamoDB streams (implemented as Alternator streams in ScyllaDB)

**When to use each**

You should generally use Alternator if either of the following is true:

#. You do not want to refactor your code to a new API, or
#. You want to start using or evaluating ScyllaDB prior to major code refactoring.

For example, you would want to use the DynamoDB API for a project where hundreds of independent Lambda services communicating with DynamoDB may require quite an effort to refactor. Or, you might use it when you rely on a connector that doesn’t provide compatibility with the CQL protocol. For all other cases, CQL is likely to be a better option. See the protocol comparison for more details.
