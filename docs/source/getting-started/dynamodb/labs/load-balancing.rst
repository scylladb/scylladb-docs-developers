:hide-secondary-sidebar:

Load Balancing
--------------

ScyllaDB has a symmetric, peer-to-peer architecture. There are no leaders or followers traditionally found in legacy NoSQL and SQL architectures (primaries with replicas).

However, DynamoDB SDKs expect a single endpoint to connect to. In order to properly distribute DynamoDB-compatible requests across a ScyllaDB Alternator cluster, developers must use load balancing libraries.

Learn how Load Balancing works on ScyllaDB Alternator and see available Load Balancing techniques.

This lab will walk you through a simple application that runs without Load Balancing, explore Load Balancing options and finally test how a properly-setup application balances load across a ScyllaDB cluster.

.. tabs::

  .. group-tab:: Hands On

    .. raw:: html

      <iframe width="1140"
       height="640"
       sandbox="allow-forms allow-modals allow-popups allow-same-origin allow-scripts allow-popups-to-escape-sandbox"
       src="https://play.instruqt.com/embed/scylladb/tracks/alternator-load-balancing?token=em_PHrk40b9EJEjlFoK&show_description=true" style="border: 0;"
       allowfullscreen>
      </iframe>


  .. group-tab:: ASCII Cast

      First, let's prepare the environment by setting up our cluster and Monitoring:

      .. code-block:: shell

        cd ~/load-balancer-lab
        docker compose up -d

      Then wait a couple of seconds and run `nodetool status` via the command below.

      .. code-block:: shell

        docker compose exec node_1 nodetool status

      You should see nodes in UN mode - meaning up and normal, ready!

      This is the code used for the `load-balancer-lab/docker-compose.yaml` file:

      .. code-block:: yaml

        services:
            node_1:
            image: ${SCYLLA_IMAGE:-scylladb/scylla:2025.1.0}
            command: |
                --smp ${SCYLLA_SMP:-2}
                --memory ${SCYLLA_MEM:-750M}
                --seeds node_1
                --overprovisioned 1
                --alternator-port 8000
                --alternator-write-isolation o
            ports:
                - 8000:8000
            networks:
                scylladb:
            healthcheck:
                test: curl --fail http://node_1:8000 || exit 1
                interval: 1s
                timeout: 5s
                retries: 180
            node_2:
            image: ${SCYLLA_IMAGE:-scylladb/scylla:2025.1.0}
            command: |
                --smp ${SCYLLA_SMP:-2}
                --memory ${SCYLLA_MEM:-750M}
                --seeds node_1
                --overprovisioned 1
                --alternator-port 8000
                --alternator-write-isolation o
            networks:
                scylladb:
            healthcheck:
                test: curl --fail http://node_2:8000 || exit 1
                interval: 1s
                timeout: 5s
                retries: 180
            depends_on:
                node_1:
                condition: service_healthy
            node_3:
            image: ${SCYLLA_IMAGE:-scylladb/scylla:2025.1.0}
            command: |
                --smp ${SCYLLA_SMP:-2}
                --memory ${SCYLLA_MEM:-750M}
                --seeds node_1
                --overprovisioned 1
                --alternator-port 8000
                --alternator-write-isolation o
            networks:
                scylladb:
            healthcheck:
                test: curl --fail http://node_3:8000 || exit 1
                interval: 1s
                timeout: 5s
                retries: 180
            depends_on:
                node_2:
                condition: service_healthy
        networks:
            scylladb:
            driver: bridge
            ipam:
                driver: default
                config:
                - subnet: 10.1.0.0/24
                    gateway: 10.1.0.1

      Now that the cluster is up and running, let’s start the Monitoring stack.

      .. code-block:: shell

        cd ~/load-balancer-lab/scylla-monitoring-4.9.4
        ./start-all.sh -d promdata --target-directory prometheus/targets --no-loki --no-alertmanager --no-cas-cdc --no-renderer -l

      Then you can access http://localhost:3000 to view the Monitoring dashboards.

      Up next, we'll run the unmodified application, which should not balance load across the cluster:

      .. code-block:: shell

        python3 load-balancer-lab/simple-endpoint/app.py

      The code used for the app can be reviewed below.

      Source for the script to create and populate the table (`load-balancer-lab/simple-endpoint/create_and_populate.py`):

      .. code-block:: python

        #!/bin/python3
        import boto3
        import concurrent.futures
        import time

        def create_table():
            try:
                table = dynamodb.create_table(
                    BillingMode='PAY_PER_REQUEST',
                    TableName='mutant_data',
                    KeySchema=[
                    {
                        'AttributeName': 'last_name',
                        'KeyType': 'HASH'
                    },
                    ],
                    AttributeDefinitions=[
                    {
                        'AttributeName': 'last_name',
                        'AttributeType': 'S'
                    },
                    ]
                )
                return table
            except Exception as e:
                    if e.__class__.__name__ == 'ResourceInUseException':
                        print(f"Table already exists: {e}")


        def put_item(i):
            last_name = f"Mutant{i}"
            first_name = f"First{i}"
            address = f"{i} Way"
            try:
                table.put_item(
                    Item={
                        "last_name": last_name,
                        "first_name": first_name,
                        "address": address,
                    }
                )
            except Exception as e:
                print(f"Error putting item {i}: {e}")


        def write():
            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                executor.map(put_item, range(1, 1000))  # 1 million items

            end_time = time.time()
            print(
                "Finished writing to table",
                table.table_name,
                "in",
                end_time - start_time,
                "seconds",
            )

        if __name__ == "__main__":
            dynamodb = boto3.resource(
                "dynamodb",
                endpoint_url="http://localhost:8000",
                region_name="None",
                aws_access_key_id="None",
                aws_secret_access_key="None",
            )
            table = create_table()
            table = dynamodb.Table("mutant_data")
            write()

    Code used for the reading application (`load-balancer-lab/simple-endpoint/app.py`):

    .. code-block:: python

        #!/usr/bin/env python3
        import boto3
        import time
        import os
        import threading
        import random


        dynamodb = boto3.client(
            "dynamodb",
            endpoint_url="http://localhost:8000",
            region_name="None",
            aws_access_key_id="None",
            aws_secret_access_key="None",
        )

        TABLE_NAME = "mutant_data"

        def timeout_killer(timeout_seconds):
            print(f"[Timer] App will automatically terminate in {timeout_seconds / 60} minutes.")
            time.sleep(timeout_seconds)
            print("[Timer] Time is up! Shutting down...")
            # Forcefully kill the process
            os._exit(0)

        def get_item(last_name):
            try:
                response = dynamodb.get_item(
                            TableName=TABLE_NAME,
                            Key={
                                "last_name": {"S": last_name}
                            }
                        )
                item = response.get("Item")
                if item:
                    #print(f"Got item: {item['last_name']}")
                    return item
                else:
                    print(f"Item not found: {last_name}")
                    return None
            except Exception as e:
                print(f"Error getting item {last_name}: {e}")
                return None

        def get_last_names(START,END):
            while True:
                yield f"Mutant{random.choice(range(START,END))}"

        def main():
            # Set timeout
            timeout_seconds = 5 * 60  # 5 minutes

            # Start the background killer thread
            killer_thread = threading.Thread(target=timeout_killer, args=(timeout_seconds,), daemon=True)
            killer_thread.start()

            names = get_last_names(1,1000)
            for name in names:
                get_item(name)

        if __name__ == "__main__":
            main()


    The script should run for 5 minutes.
    Meanwhile, go to the Alternator dashboard in Monitoring and check out the distribution of requests per-node and shard.

    Lastly, let's run the application with load-balancing enabled using ScyllaDB provided libraries.

    .. code-block:: bash

        python3 load-balancer-lab/load-balanced-app/app.py

    And here's the code for that script (`load-balancer-lab/load-balanced-app/app.py`):

    .. code-block:: python

        #!/usr/bin/env python3
        import time
        import os
        import threading
        import random
        from alternator_lb import AlternatorLB, Config

        alternator_endpoint = AlternatorLB(Config(nodes=["localhost"], port=8000))
        dynamodb = alternator_endpoint.new_boto3_dynamodb_client()

        TABLE_NAME = "mutant_data"

        def timeout_killer(timeout_seconds):
            print(f"[Timer] App will automatically terminate in {timeout_seconds / 60} minutes.")
            time.sleep(timeout_seconds)
            print("[Timer] Time is up! Shutting down...")
            # Forcefully kill the process
            os._exit(0)

        def get_item(last_name):
            try:
                response = dynamodb.get_item(
                            TableName=TABLE_NAME,
                            Key={
                                "last_name": {"S": last_name}
                            }
                        )
                item = response.get("Item")
                if item:
                    #print(f"Got item: {item['last_name']}")
                    return item
                else:
                    print(f"Item not found: {last_name}")
                    return None
            except Exception as e:
                print(f"Error getting item {last_name}: {e}")
                return None

        def get_last_names(START,END):
            while True:
                yield f"Mutant{random.choice(range(START,END))}"

        def main():
            # Set timeout
            timeout_seconds = 5 * 60  # 5 minutes

            # Start the background killer thread
            killer_thread = threading.Thread(target=timeout_killer, args=(timeout_seconds,), daemon=True)
            killer_thread.start()

            names = get_last_names(1,1000)
            for name in names:
                get_item(name)

        if __name__ == "__main__":
            main()

    We also relied on the Library provided by ScyllaDB, which can be found at the GitHub repo: https://github.com/scylladb/alternator-load-balancing/tree/master/python
