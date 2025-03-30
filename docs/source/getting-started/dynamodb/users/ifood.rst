:hide-secondary-sidebar:

.. meta::
   :description: iFood, Latin America's largest food delivery company, faced challenges with their database infrastructure as they experienced rapid growth from 1 million to 20 million orders per month in under two years. Learn how they migrated from DynamoDB to ScyllaDB to address these challenges.
    :keywords: ScyllaDB, DynamoDB, iFood, migration, cost reduction, scalability

iFood
-------

.. raw:: html

     <div style="position: relative; width: 100%; padding-bottom: 56.25%; height: 0; overflow: hidden;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
             src="https://www.youtube.com/embed/iTTWDXLyzcc?si=WafgN5iSpUkMxnCa"
             title="YouTube video player" frameborder="0"
             allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
             referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>
         </iframe>
     </div>

Handling Rapid Growth with ScyllaDB
===================================

iFood, Latin America's largest food delivery company, faced challenges with their database infrastructure as they experienced rapid growth from 1 million to 20 million orders per month in under two years. Initially using PostgreSQL, they encountered failures and transitioned to DynamoDB for their Connection-Polling service. However, DynamoDB's autoscaling proved insufficient for their bursty traffic spikes around meal times, leading to high costs due to maintaining a high minimum throughput.


Why ScyllaDB?
=============

To address these issues, iFood sought a more cost-effective and scalable solution. They evaluated options and ultimately chose ScyllaDB Cloud due to its:

#. Easily meeting throughput requirements.
#. Enabling scaling to support 500,000 connected merchants.
#. Reducing database expenses for the Connection-Polling service from $54,000 to $6,000, resulting in a 9x savings.

How Did They Migrate?
=====================

The migration process involved transitioning their Connection-Polling service to ScyllaDB Cloud, maintaining the same data model from their DynamoDB migration. The impact of the migration included easily meeting throughput requirements, enabling them to scale to support 500,000 connected merchants, and significantly reducing database expenses for the Connection-Polling service from $54,000 to $6,000, resulting in a 9x savings.
