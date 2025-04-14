:hide-secondary-sidebar:

Simple Application
------------------

Alternator is an open-source `project <https://github.com/scylladb/scylla/blob/master/docs/alternator/alternator.md>`_ that gives ScyllaDB compatibility with Amazon DynamoDB.

This lab starts with an introduction to the project. Afterward, you’ll create a one-node ScyllaDB cluster with Alternator enabled, and performing some basic operations on it, using Python.

The goal of Alternator is to provide a fully compatible DynamoDB API, so that users can run their existing applications without any changes. It is designed to be compatible with the DynamoDB API, but it is not a drop-in replacement. Alternator is deployable wherever a user would want: on-premises, on other public clouds like AWS, Microsoft Azure or Google Cloud Platform. DynamoDB users can keep their same client code unchanged. Alternator is written in C++ and is a part of ScyllaDB.

.. tabs::

  .. group-tab:: Try It

    .. raw:: html

      <iframe width="1140"
       height="640"
       sandbox="allow-forms allow-modals allow-popups allow-same-origin allow-scripts allow-popups-to-escape-sandbox"
       src="https://play.instruqt.com/embed/scylladb/tracks/alternator-getting-started?token=em_OBJmJZ1tHYu_9K4K" style="border: 0;"
       allowfullscreen>
      </iframe>

  .. group-tab:: Walk Through

    .. raw:: html

       <div style="position: relative; width: 100%; padding-bottom: 56.25%; height: 0; overflow: hidden;">
           <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
               src="https://www.youtube.com/embed/RZ4R_aT1nTI?si=ktfYAI3a0p8IANQL"
               title="YouTube video player" frameborder="0"
               allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
               referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>
           </iframe>
       </div>

  .. group-tab:: Code Examples Used

    Run a single node container with ScyllaDB and Alternator enabled.

    .. code-block:: shell

      docker run --name scylla-node1 \
        -p 8000:8000 \
        -d scylladb/scylla:2025.1.0 \
        --alternator-port=8000 \
        --alternator-write-isolation=only_rmw_uses_lwt \
        --overprovisioned 1 \
        --smp 1 --memory 1G

    Check the status of the node.

    .. code-block:: shell

      docker exec -it scylla-node1 nodetool status

    Create a table.

    .. code-block:: shell

      aws dynamodb create-table \
        --table-name MusicCollection \
        --attribute-definitions AttributeName=Artist,AttributeType=S AttributeName=SongTitle,AttributeType=S \
        --key-schema AttributeName=Artist,KeyType=HASH AttributeName=SongTitle,KeyType=RANGE \
        --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
        --endpoint http://localhost:8000

    Insert an item.

    .. code-block:: shell

      aws dynamodb put-item \
        --table-name MusicCollection \
        --item '{
            "Artist": {"S": "No One You Know"},
            "SongTitle": {"S": "Call Me Today"} ,
            "AlbumTitle": {"S": "Somewhat Famous"}
          }' \
        --endpoint http://localhost:8000

    Query the table.

    .. code-block:: shell

      aws dynamodb query --table-name MusicCollection \
        --key-condition-expression "Artist = :v1 AND SongTitle = :v2" \
        --expression-attribute-values '{
          ":v1": {"S": "No One You Know"},
          ":v2": {"S": "Call Me Today"}
          }' \
      --endpoint http://localhost:8000

    Delete the table.

    .. code-block:: shell

      aws dynamodb delete-table --table-name MusicCollection \
        --endpoint http://localhost:8000

    Create a table using Python.

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

    Write an item using Python.

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

    Read an item using Python.

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
