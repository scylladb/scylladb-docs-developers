:hide-secondary-sidebar:

Load Balancing
--------------

`Alternator is an API <https://github.com/scylladb/scylla/blob/master/docs/alternator/alternator.md>`_ that gives ScyllaDB compatibility with Amazon DynamoDB.

This lab starts with an introduction to the project. Afterward, you’ll create a one-node ScyllaDB cluster with Alternator enabled, and performing some basic operations on it, using Python.

The goal of Alternator is to provide a fully compatible DynamoDB API, so that users can run their existing applications without any changes. It is designed to be compatible with the DynamoDB API, but it is not a drop-in replacement. Alternator is deployable on-premise or on public clouds like Amazon Web Services, Microsoft Azure or Google Cloud Platform. DynamoDB users can keep their same client code unchanged. Alternator is written in C++ and is a part of ScyllaDB.

.. tabs::

  .. group-tab:: Hands On

    .. raw:: html

      <iframe width="1140"
       height="640"
       sandbox="allow-forms allow-modals allow-popups allow-same-origin allow-scripts allow-popups-to-escape-sandbox"
       src="https://play.instruqt.com/embed/scylladb/tracks/alternator-load-balancing?token=em_PHrk40b9EJEjlFoK&show_description=true" style="border: 0;"
       allowfullscreen>
      </iframe>
