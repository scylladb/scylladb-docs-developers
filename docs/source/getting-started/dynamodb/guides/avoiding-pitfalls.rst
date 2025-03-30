Avoiding Pitfalls
-----------------

To ensure a smooth migration, control the data flow to prevent throttling, validate JSON compatibility when reading from S3, and account for schema differences between DynamoDB and ScyllaDB. Test the process with a small dataset first to catch potential issues early.

Avoid Application Throttling
============================

Many customers simply point their migration tool directly at their table and start inserting data. This often leads to exhausted read/write units, which increases latency, triggers auto-scaling, and raises costs. Eventually, the application slows down or even halts, as the entire system is affected.  To prevent this, monitor capacity units and use controlled batch processing rather than pushing large volumes of data at once.

Reading from S3
===============

If you’re reading from S3 (AWS native feature), using **single x-part export** works smoothly. However, if you use external libraries, custom backup processes, or queuing mechanisms, be aware of JSON compatibility. Alternator, DynamoDB, and CQL have different data type standards, which could require additional ETL (Extract, Transform, Load) operations to clean or reformat JSON files during migration.

Handling Schema Differences
===========================

DynamoDB uses a schema-less design, while ScyllaDB enforces a schema, especially with CQL. During migration, this difference could cause issues. If your application has been running for a while, its schema may have changed through multiple iterations – and that could lead to mismatched data types or unexpected errors. Review and normalize your schema definitions before starting the migration to avoid complications.
