:hide-secondary-sidebar:

.. meta::
   :description: Advanced DynamoDB cost calculator for real-world workloads, with bursty traffic, Global Tables, DAX, and more. Geared for developers who need accurate cost estimates fast.

DynamoDB Cost Calculator
------------------------

.. raw:: html

    <div style="position: relative; width: 100%; padding-bottom: 170%; height: 0; overflow: hidden;">
        <iframe
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: transparent;"
            src="https://calculator.scylladb.com"
            title="DynamoDB Cost Calculator"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            referrerpolicy="strict-origin-when-cross-origin"
            allowfullscreen>
        </iframe>
    </div>

You might be wondering: "AWS already offers a `DynamoDB pricing calculator <https://calculator.aws/#/createCalculator/DynamoDB/>`_. Why create another one?" 

Short answer: Because teams comparing DynamoDB costs with ScyllaDB costs report that the official AWS calculator is:
 
* Overly complex
* Not developer friendly
* Insufficient for estimating the costs of real-world workloads (e.g., with bursty traffic or uneven access patterns)

To enable simpler, more accurate comparisons, we designed something a bit different. 

Long answer: See :doc:`the intro page <index>`.
