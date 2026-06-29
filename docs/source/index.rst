:full-width:
:hide-sidebar:
:hide-secondary-sidebar:
:hide-version-warning:
:hide-pre-content:
:hide-post-content:
:landing:

.. title:: ScyllaDB Developers

.. toctree::
   :maxdepth: 2
   :hidden:

   getting-started/index
   getting-started/dynamodb/index
   Switching from Aerospike <compare/index>

.. hero-box::
  :title: Developing Monster Scale
  :image: https://scylladb.github.io/scylladb-docs-developers/stable/_static/img/scylladb-monster-lookup-left-pad.png
  :class: hero-box--primary

  At ScyllaDB, we give developers the database technology required to achieve predictable performance at scale, so you can build robust, high-speed applications.

.. raw:: html

  <div class="landing__content landing__content">
    <div class="topics-grid grid-container full">
      <div class="grid-x grid-margin-x">

.. topic-box::
  :title: ScyllaDB Cloud
  :link: https://cloud.scylladb.com/
  :link_target: _self
  :icon: icon-docs-cloud
  :class: large-6
  :anchor: Learn more

  Try ScyllaDB Cloud, our managed NoSQL database as a service running ScyllaDB Enterprise.

.. topic-box::
  :title: Getting Started
  :link: getting-started/index
  :link_target: _self
  :icon: icon-docs-getting-started
  :class: large-6
  :anchor: Learn more

  These guides will help you get started with ScyllaDB, from installation to running your first query.

.. topic-box::
  :title: Labs
  :link: https://scylladb.instruqt.com/pages/virtual-labs
  :link_target: _self
  :icon: icon-docs-commands
  :class: large-6
  :anchor: Learn more

  Experiment with ScyllaDB in your browser with these interactive labs.

.. topic-box::
  :title: University
  :link: https://university.scylladb.com/
  :link_target: _self
  :icon: icon-university
  :class: large-6
  :anchor: Learn more

  Level up your skills at your own pace, with our NoSQL database courses.

.. topic-box::
  :title: ScyllaDB vs Aerospike
  :link: compare/index
  :link_target: _self
  :icon: icon-docs-commands
  :class: large-6
  :anchor: Read the comparison

  How ScyllaDB beats Aerospike at key-value — and brings wide-column flexibility, elasticity, and dramatically lower RAM costs at scale.

.. raw:: html

      <div class="cell large-12 small-12">
        <div class="topic-box">
          <div class="card">
            <div class="title-box">
              <h2 class="title-box__title">Installation</h1>
            </div>

.. tabs::

   .. group-tab:: Docker

      Running ScyllaDB in Docker is the simplest way to experiment with ScyllaDB when you're getting started.

      .. code-block:: shell

         docker run --name scylladb -d  scylladb/scylla

   .. group-tab:: Linux

      For a production ready installation try our simple Linux Installer.

      .. code-block:: shell

         curl -sSf get.scylladb.com/server | sudo bash

For more detailed information, see our `installation instructions. <https://docs.scylladb.com/manual/stable/getting-started/install-scylla/index.html>`_

**Connect via drivers**

.. tabs::

  .. group-tab:: Rust

    .. code::

        cargo add scylla

  .. group-tab:: Python

    .. code::

        pip install scylla-driver

  .. group-tab:: Java

    .. code:: xml

        <dependency>
          <groupId>com.scylladb</groupId>
          <artifactId>java-driver-core</artifactId>
          <version>${driver.version}</version>
        </dependency>

        <dependency>
          <groupId>com.scylladb</groupId>
          <artifactId>java-driver-query-builder</artifactId>
          <version>${driver.version}</version>
        </dependency>

        <dependency>
          <groupId>com.scylladb</groupId>
          <artifactId>java-driver-mapper-runtime</artifactId>
          <version>${driver.version}</version>
        </dependency>

  .. group-tab:: Go

    Add the following line to your project go.mod file:

        .. code::

            github.com/scylladb/gocql latest

  .. group-tab:: JavaScript

    .. code::

      yarn install cassandra-driver


For more detailed information, see our `full list of drivers. <https://docs.scylladb.com/manual/stable/using-scylla/drivers/cql-drivers/>`_

.. raw:: html

          </div>
        </div>
      </div>
    </div>
  </div>

