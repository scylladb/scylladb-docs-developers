Request Patterns and Billing Surprises
--------------------------------------

DynamoDB’s pricing is heavily tied to how your application interacts with it. Small changes in request patterns can lead to big cost swings especially if you’re not monitoring usage or optimizing access.

Here’s what you need to watch out for.

Request Spikes = Cost Spikes
============================
DynamoDB charges per read/write unit. In On-Demand mode, every request costs money. If your app suddenly increases request volume—due to a bug, traffic spike, or misconfigured job, you’ll see it directly reflected on your bill.

If you’re using Provisioned mode, overestimating capacity means paying for what you don’t use. Underestimating means throttling, retries, and possibly even more costs depending on how your client handles retries.

Recommended actions:

#. Use Auto Scaling to adjust capacity dynamically, but monitor its responsiveness—it’s not instant.
#. Set CloudWatch alarms to detect unusual usage patterns quickly.

Smart Cost Management Strategies
================================

#. Pick the right mode:
    Use Provisioned if traffic is steady and predictable.
    Use On-Demand if traffic is spiky or hard to forecast.
#. Instrument and monitor:
    Use CloudWatch and set budgets in AWS Billing to catch anomalies early. Monitor not just overall throughput, but also table/index-specific metrics.
#. Data model matters:
    Poor design leads to excessive reads, writes, and index usage. Minimize the number of operations per request by denormalizing data where appropriate.
#. Use caching:
    Use DAX, ElastiCache, or an app-level cache to offload read traffic from DynamoDB.
#. Run cost simulations:
    Our calculator can help you model expected workloads and costs. It’s available at `calculator.scylladb.com <https://calculator.scylladb.com>`_.

.. tip::

    If you’re hitting scale or budget limits, ScyllaDB (with Alternator, our DynamoDB-compatible API) will give you more predictable performance and cost control.

Hidden Costs You Shouldn’t Ignore
=================================

These can silently eat your budget:

#. Network transfer:
    Accessing DynamoDB from outside AWS incurs transfer fees.
#. TTL deletions:
    Even automated TTL removals count as write ops.
#. Frequent DELETEs:
    These cost as much as writes; batch deletions if possible.
#. Scans and large queries:
    Inefficient access patterns result in expensive read units.
#. Consistent reads:
    These double your read capacity usage.
#. Secondary indexes:
    Every index writes and reads in parallel with your table.
#. Provisioned throughput waste:
    Unused provisioned RCU/WCUs = money burned.
#. Throttling + retries:
    Retry logic can make bad situations worse. Use exponential backoff.
#. Global Tables:
    Data replication across regions adds storage, write, and transfer costs.
#. DAX:
    Adds infra cost and inter-service data transfer fees.
#. Backup & restore:
    Charges apply for both storage and restore operations.
#. CloudWatch metrics/logs:
    Detailed metrics, logs, and alarms all incur extra charges.
#. Streams:
    Streams and their consumers add to your overall DynamoDB bill.

.. raw:: html

    <p class="mark">DynamoDB makes it easy to scale, but easy to overspend too. Monitor usage, model costs, and revisit your data access patterns regularly. Small inefficiencies compound fast, especially at scale, which is why so many DynamoDB customers switch to ScyllaDB.</p>
