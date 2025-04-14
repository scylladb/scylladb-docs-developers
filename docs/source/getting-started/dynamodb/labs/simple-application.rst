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

      .. code-block:: python

        #!/usr/bin/python3
        import dnslib.server
        import dnslib
        import random
        import _thread
        import urllib.request
        import time

        # The list of live nodes, all of them supposedly answering HTTP requests on
        # alternator_port. One of these nodes will be returned at random from every
        # DNS request. This list starts with one or more known nodes, but then the
        # livenodes_update() thread periodically replaces this list by an up-to-date
        # list retrieved from makeing a "localnodes" requests to one of these nodes.
        livenodes = ['127.0.0.1']
        alternator_port = 8000
        def livenodes_update():
            global alternator_port
            global livenodes
            while True:
                # Contact one of the already known nodes by random, to fetch a new
                # list of known nodes.
                ip = random.choice(livenodes)
                url = 'http://{}:{}/localnodes'.format(ip, alternator_port)
                print('updating livenodes from {}'.format(url))
                try:
                    nodes = urllib.request.urlopen(url, None, 1.0).read().decode('ascii')
                    a = [x.strip('"').rstrip('"') for x in nodes.strip('[').rstrip(']').split(',')]
                    # If we're successful, replace livenodes by the new list
                    livenodes = a
                    print(livenodes)
                except:
                    # TODO: contacting this ip was unsuccessful, maybe we should
                    # remove it from the list of live nodes.
                    pass
                time.sleep(1)
        _thread.start_new_thread(livenodes_update,())

        class Resolver:
            def resolve(self, request, handler):
                qname = request.q.qname
                reply = request.reply()
                # Note responses have TTL 4, as in Amazon's Dynamo DNS
                ip = random.choice(livenodes)
                reply.add_answer(*dnslib.RR.fromZone('{} 4 A {}'.format(qname, ip)))
                return reply
        resolver = Resolver()
        logger = dnslib.server.DNSLogger(prefix=True)
        tcp_server = dnslib.server.DNSServer(Resolver(), port=53, address='localhost', logger=logger, tcp=True)
        tcp_server.start_thread()
        udp_server = dnslib.server.DNSServer(Resolver(), port=53, address='localhost', logger=logger, tcp=False)
        udp_server.start_thread()

        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print('Goodbye!')
        finally:
            tcp_server.stop()
            udp_server.stop()
