:hide-secondary-sidebar:

.. meta::
   :description: Digital Turbine migrated from DynamoDB to ScyllaDB to improve performance and cost efficiency. Learn how they did it.
   :keywords: ScyllaDB, DynamoDB, Digital Turbine, migration, performance, cost efficiency

Digital Turbine
---------------

.. raw:: html

     <div style="position: relative; width: 100%; padding-bottom: 56.25%; height: 0; overflow: hidden;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
             src="https://www.youtube.com/embed/kkoi66MA9C4?si=znC4RyOp0SP7ancr"
             title="YouTube video player" frameborder="0"
             allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
             referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>
         </iframe>
     </div>

Improving Performance and Cost Efficiency
=========================================

Digital Turbine, a mobile ad tech company, faced challenges with DynamoDB due to:

#. Rising costs as they scaled.
#. Performance issues with a high volume of read operations.
#. A need to standardize on Google Cloud Platform (GCP) following acquisitions.

Why ScyllaDB?
=============

To address these challenges, they sought a database solution that offered cost reduction, improved performance, and seamless migration from DynamoDB without extensive refactoring. They evaluated several options and ultimately chose ScyllaDB for its:

#. DynamoDB API compatibility (ScyllaDB Alternator), which minimized code changes.
#. Better performance compared to DynamoDB, reducing the need for excessive scaling.
#. Cost-effectiveness (an initial 20% cost savings, even with minimal cluster utilization).

How Did They Migrate?
=====================

The migration process involved a thorough proof of concept (POC) to pressure-test ScyllaDB’s performance and reliability in a real-world scenario. The impact of the migration included improved performance, reduced infrastructure needs, and significant cost savings, positioning Digital Turbine for future scalability and competitiveness.
