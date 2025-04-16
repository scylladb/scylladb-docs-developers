.. meta::
   :description: Is ScyllaDB right for you? Assess based on workload patterns, throughput, latency needs, and schema flexibility to see if your use case falls into its "sweet spot."

Is ScyllaDB Right for My Project?
---------------------------------

.. toctree::
    :maxdepth: 2
    :hidden:

    reducing-costs
    improving-latency
    freedom-from-lock-in

ScyllaDB is a powerful option for organizations dealing with data-intensive applications that require high performance, scalability, and cost-efficiency. Its ability to handle massive workloads with low latency makes it particularly attractive for use cases in real-time analytics, IoT, and financial services.

When deciding if ScyllaDB is a good fit, consider the following:

#. **Workload characteristics**: ScyllaDB is ideal for high-throughput, low-latency workloads.
#. **Data intensity and growth**: It's well-suited for organizations with rapidly growing use cases and data-intensive applications.
#. **Performance requirements**: If your application needs consistent single-digit millisecond latencies, ScyllaDB could be an excellent choice.
#. **Cost considerations**: ScyllaDB's efficiency can lead to significant infrastructure cost savings, especially at scale.
#. **API compatibility**: If you're already using DynamoDB, transitioning to ScyllaDB could be relatively straightforward due to its API compatibility.
#. **Flexibility**: ScyllaDB runs anywhere - from any public cloud to private on-prem datacenters. This alows users to port their DynamoDB applications out of the AWS ecosystem with minimal effort.

Use Cases Where ScyllaDB Might Not Be the Best Option
=====================================================

While ScyllaDB is a powerful database, it may not be the best choice for every project. Here are some scenarios where you might want to consider other options:

#. **Highly relational data**: ScyllaDB is a NoSQL database, so relational-heavy use cases might need to be remodeled and denormalized for ScyllaDB. Use cases with joins, subqueries, or filtering on lots of columns are generally not a great fit.
#. **Large, idle dataset**: If the use case has a very large dataset that is very rarely accessed, it might not require ScyllaDB’s performance.
#. **Frequently evolving patterns**: ScyllaDB requires carefully planned table design, which is dictated by the access patterns of the data. If the access patterns tend to change frequently, that would require the team to frequently re-evaluate the table design to adapt to changes.
#. **Large data items**: ScyllaDB is an amazing product, but it might not deliver optimal performance if used in esoteric ways, such as storing large blobs of data (over the megabytes range) as in a file storage.
