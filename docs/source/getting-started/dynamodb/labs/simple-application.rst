:hide-secondary-sidebar:

Simple Application
------------------

`Alternator is an API <https://github.com/scylladb/scylla/blob/master/docs/alternator/alternator.md>`_ that gives ScyllaDB compatibility with Amazon DynamoDB.

This lab starts with an introduction to the project. Afterward, you’ll create a one-node ScyllaDB cluster with Alternator enabled, and performing some basic operations on it, using Python.

The goal of Alternator is to provide a fully compatible DynamoDB API, so that users can run their existing applications without any changes. It is designed to be compatible with the DynamoDB API, but it is not a drop-in replacement. Alternator is deployable on-premise or on public clouds like Amazon Web Services, Microsoft Azure or Google Cloud Platform. DynamoDB users can keep their same client code unchanged. Alternator is written in C++ and is a part of ScyllaDB.

.. tabs::

  .. group-tab:: Hands On

    .. raw:: html

      <iframe width="1140"
       height="640"
       sandbox="allow-forms allow-modals allow-popups allow-same-origin allow-scripts allow-popups-to-escape-sandbox"
       src="https://play.instruqt.com/embed/scylladb/tracks/alternator-getting-started?token=em_OBJmJZ1tHYu_9K4K&show_description=true" style="border: 0;"
       allowfullscreen>
      </iframe>

  .. group-tab:: Screen Cast

    .. raw:: html

       <div style="position: relative; width: 100%; padding-bottom: 56.25%; height: 0; overflow: hidden;">
           <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
               src="https://www.youtube.com/embed/ONv-yrGOIlg?si=W1cynu3j4m9aqQOa"
               title="YouTube video player" frameborder="0"
               allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
               referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>
           </iframe>
       </div>

  .. group-tab:: ASCII Cast

    Let’s kick things off by launching a ScyllaDB container with Alternator enabled.

    We’re using Docker here to spin up a one-node ScyllaDB instance. This is strictly for learning — don’t use this setup in production.

    **Step 1: Run the Container**

    Paste this into your terminal tab:

    .. code-block:: shell

      docker run --name scylla-node1 \
        -p 8000:8000 \
        -d scylladb/scylla:2025.1.0 \
        --alternator-port=8000 \
        --alternator-write-isolation=only_rmw_uses_lwt \
        --overprovisioned 1 \
        --smp 1 --memory 1G

    This does a few things:

    * Launches the ``scylladb/scylla:2025.1.0`` image
    * Exposes port ``8000`` — that’s where Alternator will listen
    * Configures write isolation to only use LWT for conditional writes
    * Restricts the container to 1 CPU and 1 GB RAM
    * Tells ScyllaDB to behave nicely on resource-constrained environments

    Once the container starts, you’ll see a long hash — that’s the Docker container ID.

    **Step 2: Check Cluster Status**

    Next, let’s confirm that ScyllaDB is actually up and running:

    .. code-block:: shell

      docker exec -it scylla-node1 nodetool status

    You should see something like this:

    .. code-block:: shell
      :class: hide-copy-button

      Status=Up/Down
      |/ State=Normal/Leaving/Joining/Moving
      UN 172.17.0.2 ... rack1

    The key part here is ``UN`` — Up and Normal. That’s the healthy state we want.

    **Step 3: Understanding the Parameters**

    Let’s quickly break down what each part of the docker run command is doing:

    * ``--name scylla-node1``: Gives the container a fixed name. Useful for repeated interactions.
    * ``-p 8000:8000``: Maps port ``8000`` from the container to your host — so we can interact with Alternator from the outside.
    * ``scylladb/scylla:2025.1.0``: Specifies the image to run.
    * ``--alternator-port=8000``: Enables the Alternator API on port 8000.
    * ``--alternator-write-isolation=only_rmw_uses_lwt``: Only use LWT for read-modify-write or conditional updates.
    * ``--overprovisioned 1``: Reduces ScyllaDB’s resource footprint. No core pinning or aggressive polling.
    * ``--smp 1``: Use a single CPU core.
    * ``--memory 1G``: Cap RAM usage at 1 GB — enough for this lab.

    You can read more about these and other ScyllaDB options in the `config reference <https://docs.scylladb.com/manual/stable/reference/configuration-parameters.html>`_.

    Now that we have our ScyllaDB container with Alternator running, let’s see how we can interact with it using the AWS CLI.

    Because Alternator is DynamoDB API-compatible, anything that works with DynamoDB works here — that includes the CLI and SDKs.

    **Step 1: AWS CLI Installation (Optional)**

    In this lab environment, AWS CLI is already installed. But here’s how you’d install it on a Debian-based system like Ubuntu:

    .. code-block:: shell

      sudo apt install -y unzip curl
      curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
      unzip awscliv2.zip
      sudo ./aws/install

    For other OSes, just check the `AWS CLI docs <https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html>`_.

    **Step 2: Set Environment Variables**

    Next, let’s prep the environment so the CLI knows how to connect.

    .. code-block:: shell

      export AWS_DEFAULT_REGION=local
      export AWS_ACCESS_KEY_ID=foo
      export AWS_SECRET_ACCESS_KEY=bar

    Even though Alternator doesn’t do any actual authentication by default, the CLI still expects these to be set.

    **Step 3: Create a Table**

    Let’s create a DynamoDB-style table using the CLI — and point it at our local Alternator instance:

    .. code-block:: shell

      aws dynamodb create-table \
        --table-name MusicCollection \
        --attribute-definitions AttributeName=Artist,AttributeType=S AttributeName=SongTitle,AttributeType=S \
        --key-schema AttributeName=Artist,KeyType=HASH AttributeName=SongTitle,KeyType=RANGE \
        --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
        --endpoint http://localhost:8000

    Even though Alternator ignores provisioned throughput, we still need to include the ``ReadCapacityUnits`` and ``WriteCapacityUnits`` — the CLI requires them.

    Also, note the ``--endpoint`` flag — everything points to ``localhost:8000`` because that’s where Alternator is listening.

    You should see a JSON response with ``"TableStatus": "ACTIVE"`` — that means it worked.

    **Step 4: Put an Item**

    Now let’s insert some data into that table:

    .. code-block:: shell

      aws dynamodb put-item \
        --table-name MusicCollection \
        --item '{
            "Artist": {"S": "No One You Know"},
            "SongTitle": {"S": "Call Me Today"} ,
            "AlbumTitle": {"S": "Somewhat Famous"}
          }' \
        --endpoint http://localhost:8000

    This inserts one item into ``MusicCollection``.

    **Step 5: Query the Table**

    Let’s now query using both the **partition key** and the **sort key**, with a ``KeyConditionExpression``:

    .. code-block:: shell

      aws dynamodb query --table-name MusicCollection \
        --key-condition-expression "Artist = :v1 AND SongTitle = :v2" \
        --expression-attribute-values '{
          ":v1": {"S": "No One You Know"},
          ":v2": {"S": "Call Me Today"}
          }' \
      --endpoint http://localhost:8000

    You should get back the item we just inserted, along with some metadata like ``Count`` and ``ScannedCount``.

    **Step 6: Delete the Table**

    Finally, let’s clean up by deleting the table we just created:

    .. code-block:: shell

      aws dynamodb delete-table --table-name MusicCollection \
        --endpoint http://localhost:8000

    This deletes the table from our local Alternator instance — just like you would with a real DynamoDB endpoint.

    You just created, queried, and deleted a table in ScyllaDB Alternator — using nothing but the AWS CLI.

    Up next, we’ll do the same thing from code, using Python and boto3.

    **Step 1: Install boto3 (Optional)**

    All dependencies are already installed in this lab environment. But here’s how you’d install boto3 on your own machine:

    For Debian-based systems:

    .. code-block:: shell

      sudo apt install python3-boto3

    Or, use pip:

    .. code-block:: shell

      pip install boto3

    Once that’s done, you’re ready to go.

    **Step 2: Review Python App Code**

    Let’s open the app.

    Head over to the **Editor tab** and open create.py.

    Focus on lines 3 and 4:

    .. code-block:: python
      :class: hide-copy-button

      dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url='http://localhost:8000',
        region_name='None',
        aws_access_key_id='None',
        aws_secret_access_key='None'
      )

    This is where the override happens.

    By setting endpoint_url to ``http://localhost:8000``, we’re telling boto3 to skip the real DynamoDB service and talk to our **local Alternator container** instead.

    The other values like region and credentials don’t matter — Alternator doesn’t require authentication by default.

    .. note:: In production, you’ll want to avoid hardcoding a single endpoint — doing so introduces a single point of failure. We’ll cover high-availability setups in a later lab.

    **Step 3: Create the Table**

    .. code-block:: shell

      python3 alternator-getting-started/create.py

    This script will create a table on the Alternator instance using the same schema we used earlier in the CLI section.

    If successful, you’ll see a confirmation message printed to stdout.

    .. code-block:: python

      #!/bin/python3
      import boto3
      dynamodb = boto3.resource('dynamodb',endpoint_url='http://localhost:8000',
                        region_name='None', aws_access_key_id='None', aws_secret_access_key='None')

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

      print("Finished creating table ", table.table_name ,". Status: ", table.table_status)

    **Step 4: Write Data**

    Let’s insert some data now.

    Open write.py in the Editor tab and review what it’s doing — it performs a simple PutItem operation.

    When ready, go to the **Terminal tab** and run it:

    .. code-block:: shell

      python3 alternator-getting-started/write.py

    The script will report that the data was successfully inserted.

    .. code-block:: python

      #!/bin/python3
      import boto3
      dynamodb = boto3.resource('dynamodb',endpoint_url='http://localhost:8000',
                        region_name='None', aws_access_key_id='None', aws_secret_access_key='None')

      dynamodb.batch_write_item(RequestItems={
          'mutant_data': [
              {
                   'PutRequest': {
                       'Item': {
                           "last_name": "Loblaw",
                           "first_name": "Bob",
                           "address": "1313 Mockingbird Lane"
                       }
                    }
              },
              {
                   'PutRequest': {
                       'Item': {
                           "last_name": "Jeffries",
                           "first_name": "Jim",
                           "address": "1211 Hollywood Lane"
                       }
                   }
              }
          ]
      })

      table = dynamodb.Table('mutant_data')
      print("Finished writing to table ", table.table_name)

    **Step 5: Read Data**

    Last step: let’s read what we just wrote.

    Open read.py in the **Editor tab**, then run it from the **Terminal tab**:

    .. code-block:: shell

      python3 alternator-getting-started/read.py

    The output will look something like this:

    .. code-block:: shell
      :class: hide-copy-button

      Responses
      mutant_data : [
        {'last_name': 'Jeffries', 'address': '1211 Hollywood Lane', 'first_name': 'Jim'},
        {'last_name': 'Loblaw', 'address': '1313 Mockingbird Lane', 'first_name': 'Bob'}
      ]
      ...
      HTTPStatusCode : 200

    This confirms that the app queried the table correctly and got the data back from Alternator.

    .. code-block:: python

      #!/bin/python3
      import boto3
      dynamodb = boto3.resource('dynamodb',endpoint_url='http://localhost:8000',
                        region_name='None', aws_access_key_id='None', aws_secret_access_key='None')

      response = dynamodb.batch_get_item(
          RequestItems={
              'mutant_data' : { 'Keys': [{ 'last_name': 'Loblaw' }, {'last_name': 'Jeffries'}] }
          }
      )
      for x in response:
          print (x)
          for y in response[x]:
              print (y,':',response[x][y])

    **Bonus: Read Consistency**

    DynamoDB supports **strong** and **eventual consistency**. ScyllaDB does too — under the hood, it uses ``LOCAL_QUORUM`` for strong reads, and ``LOCAL_ONE`` for eventual.

    If you want a deeper dive on Scylla’s consistency models, check out the `ScyllaDB University courses <https://university.scylladb.com/courses/scylla-essentials-overview/>`_ or the :doc:`Multiple Data Center guide <../guides/migration/multiple-data-centers>`.
