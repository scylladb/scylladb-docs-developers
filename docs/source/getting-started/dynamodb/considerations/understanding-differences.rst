:hide-secondary-sidebar:

Understanding Differences
=========================

ScyllaDB offers a lower-latency, higher-performance alternative to DynamoDB, especially for write-heavy workloads. Its C++ architecture and binary protocol enable better resource utilization and scalability. ScyllaDB’s Alternator API provides seamless DynamoDB compatibility, while its CQL mode offers a robust SQL-like querying model with advanced features.

Four key differences are:

* **Provisioning**: In ScyllaDB you provision nodes, not tables. In other words, a single ScyllaDB deployment is able to host several tables and serve traffic for multiple workloads combined.
* **Load Balancing**: Application clients do not route traffic through a single endpoint as in AWS DynamoDB (``dynamodb.<region_name>.amazonaws.com``). Instead, clients may use one of our load balancing libraries, or implement a server-side load balancer.
* **Limits**: ScyllaDB does not impose a 400KB limit per item, nor any partition access limits.
* **Metrics and Integration**: Since ScyllaDB is not a “native AWS service,” it naturally does not integrate in the same way as other AWS services (such as CloudWatch and others) does with DynamoDB. For metrics specifically, ScyllaDB provides the ScyllaDB Monitoring Stack with specific dashboards for DynamoDB deployments.

Here’s a little more detail on how the two databases compare…

========================
Origins and Architecture
========================

* **DynamoDB**: Originates from Amazon's internal Dynamo system, designed in the early 2000s to handle massive e-commerce traffic during peak events like Prime Day. Dynamo emphasized availability and partition tolerance over strong consistency, introducing concepts like consistent hashing, vector clocks, and hinted handoffs.
* **ScyllaDB**: Inspired by Apache Cassandra, which implemented many Dynamo concepts. ScyllaDB re-engineered Cassandra in C++ to improve performance, reduce latency, and enhance resource utilization.