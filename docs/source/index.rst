:full-width:
:hide-sidebar:
:hide-secondary-sidebar:
:hide-version-warning:
:hide-pre-content:
:hide-post-content:
:landing:

.. title:: ScyllaDB Developers

.. hero-box::
  :title: Developing Monster Scale
  :image: https://scylladb.github.io/scylladb-docs-developers/stable/_static/img/scylladb-monster-lookup-left-pad.png
  :class: hero-box--primary

  At ScyllaDB, we give developers the database technology required to achieve predictable performance at scale, so you can build robust, high-speed applications.

.. raw:: html

   <script type="text/javascript">
    window.heapReadyCb=window.heapReadyCb||[],window.heap=window.heap||[],heap.load=function(e,t){window.heap.envId=e,window.heap.clientConfig=t=t||{},window.heap.clientConfig.shouldFetchServerConfig=!1;var a=document.createElement("script");a.type="text/javascript",a.async=!0,a.src="https://cdn.us.heap-api.com/config/"+e+"/heap_config.js";var r=document.getElementsByTagName("script")[0];r.parentNode.insertBefore(a,r);var n=["init","startTracking","stopTracking","track","resetIdentity","identify","getSessionId","getUserId","getIdentity","addUserProperties","addEventProperties","removeEventProperty","clearEventProperties","addAccountProperties","addAdapter","addTransformer","addTransformerFn","onReady","addPageviewProperties","removePageviewProperty","clearPageviewProperties","trackPageview"],i=function(e){return function(){var t=Array.prototype.slice.call(arguments,0);window.heapReadyCb.push({name:e,fn:function(){heap[e]&&heap[e].apply(heap,t)}})}};for(var p=0;p<n.length;p++)heap[n[p]]=i(n[p])};
    heap.load("2144880022");
  </script>

.. raw:: html

  <div class="landing__content landing__content">
    <div class="topics-grid grid-container full">
      <div class="grid-x grid-margin-x">

.. topic-box::
  :title: Getting Started
  :link: https://docs.scylladb.com/stable/get-started/
  :link_target: _self
  :icon: scylla-icon scylla-icon--getting-started
  :class: large-6
  :anchor: Learn more

  This guide will help you get started with ScyllaDB, from installation to running your first query.

.. topic-box::
  :title: Cloud
  :link: https://cloud.scylladb.com/
  :link_target: _self
  :icon: scylla-icon scylla-icon--cloud
  :class: large-6
  :anchor: Learn more

  Try ScyllaDB Cloud, our managed NoSQL database as a service running ScyllaDB Enterprise.

.. topic-box::
  :title: Labs
  :link: https://scylladb.instruqt.com/pages/virtual-labs
  :link_target: _self
  :icon: scylla-icon scylla-icon--apps
  :class: large-6
  :anchor: Learn more

  Experiment with ScyllaDB in your browser with these interactive labs.

.. topic-box::
  :title: University
  :link: https://university.scylladb.com/
  :link_target: _self
  :icon: scylla-icon scylla-icon--university
  :class: large-6
  :anchor: Learn more

  Level up your skills at your own pace, with our NoSQL database courses.

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

         docker run --name scylla -d scylladb/scylla

   .. group-tab:: Linux

      For a production ready installation try our simple Linux Installer.

      .. code-block:: shell

         curl -sSf get.scylladb.com/server | sudo bash

For detailed installation instructions, see our `documentation. <https://opensource.docs.scylladb.com/stable/getting-started/install-scylla/index.html>`_

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


For a full list of drivers, refer to our `documentation. <https://opensource.docs.scylladb.com/master/using-scylla/drivers/cql-drivers/index.html>`_

.. raw:: html

            <div class="topic-box__head">
              <h1 class="topic-box__title">Sign up for our product updates</h1>
            </div>
            <div class="topic-box__body">
              <p>Stay ahead with the latest tutorials, guides, news and events from ScyllaDB.</p>
              <div class="docutils container">
                <form accept-charset="UTF-8" method="post" action="https://lp.scylladb.com/l/934963/2023-05-11/923sq" class="form" id="pardot-form">
                  <p class="form-field email pd-text required">
                    <input type="text" name="934963_128676pi_934963_128676" id="934963_128676pi_934963_128676" value="correkthorse@gmail.com" class="text" size="30" maxlength="255" placeholder="Company Email *">
                  </p>
                  <p class="form-field utm_source pd-hidden hidden">
                    <input type="hidden" name="934963_128679pi_934963_128679" id="934963_128679pi_934963_128679" value="">
                  </p>
                  <p class="form-field utm_medium pd-hidden hidden">
                    <input type="hidden" name="934963_128682pi_934963_128682" id="934963_128682pi_934963_128682" value="">
                  </p>
                  <p class="form-field utm_campaign pd-hidden hidden">
                    <input type="hidden" name="934963_128685pi_934963_128685" id="934963_128685pi_934963_128685" value="">
                  </p>
                  <p class="form-field utm_adgroup pd-hidden hidden">
                    <input type="hidden" name="934963_128688pi_934963_128688" id="934963_128688pi_934963_128688" value="">
                  </p>
                  <p class="form-field utm_term pd-hidden hidden">
                    <input type="hidden" name="934963_128691pi_934963_128691" id="934963_128691pi_934963_128691" value="">
                  </p>
                  <p class="form-field websitePlacement pd-hidden hidden">
                    <input type="hidden" name="934963_128694pi_934963_128694" id="934963_128694pi_934963_128694" value="">
                  </p>
                  <p style="position:absolute; width:190px; left:-9999px; top: -9999px;visibility:hidden;">
                    <label for="pi_extra_field">Comments</label>
                    <input type="text" name="pi_extra_field" id="pi_extra_field">
                  </p>
                  <input name="_utf8" type="hidden" value="☃">
                  <p class="submit">
                    <input type="submit" accesskey="s" value="Subscribe">
                  </p>
                  <div class="onboard-form__field onboard-form__field--checkbox">
                    <input type="hidden" value="No" name="opt_in_consent" id="onboard-opt-in-consent--hidden">
                    <input name="opt_in_consent" id="onboard-opt-in-consent" type="checkbox" class="form-input" value="Yes">
                    <label for="opt_in_consent">Yes, I wish to receive future informational and marketing communications from ScyllaDB, and I understand and agree to the <a href="https://www.scylladb.com/privacy/"><b>privacy policy</b></a>.</label>
                  </div>
                </form>
                <script type="text/javascript">
                  function insertBefore(el, referenceNode) {
                    referenceNode.parentNode.insertBefore(el, referenceNode);
                  }
                  var newEl = document.createElement('div');
                  newEl.innerHTML = '<p><em>* Your information will be handled as detailed in our&nbsp;<a data-mce-href="https://www.scylladb.com/privacy/" href="https://www.scylladb.com/privacy/" target="_blank">privacy policy</a>.</em></p>';
                  var ref = document.querySelector('.add-text-before');
                  insertBefore(newEl, ref);
                </script>
                <script>
                  function getParameterByName(name) {
                    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
                    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
                    results = regex.exec(location.search);
                    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
                  }
                  var source = getParameterByName('utm_source');
                  var medium = getParameterByName('utm_medium');
                  var campaign = getParameterByName('utm_campaign');
                  document.querySelector("p.utm_source input").value = source;
                  document.querySelector("p.utm_medium input").value = medium;
                  document.querySelector("p.utm_campaign input").value = campaign;
                </script>
                <script>
                  (function() {
                    window._zi = {formId: '9c7e343e-3ae3-4097-a2ae-e4ff5059a09c', formLoadTimeout:4000};
                    var zi = document.createElement('script');
                    zi.type = 'text/javascript';
                    zi.async = true;
                    zi.src = 'https://ws-assets.zoominfo.com/formcomplete.js';
                    var s = document.getElementsByTagName('script')[0];
                    s.parentNode.insertBefore(zi, s);
                  })();
                </script>
                <script type="text/javascript">
                  var anchors = document.getElementsByTagName("a");
                  for (var i=0; i<anchors.length; i++) {
                    var anchor = anchors[i];
                    if(anchor.getAttribute("href")&&!anchor.getAttribute("target")) {
                      anchor.target = "_top";
                    }
                  }
                </script>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

.. raw:: html

  <div class="full">
    <div class="container">
      <h2 class="text-center">Featured Resources</h2>
    <!-- Uberflip Embedded Hub Widget -->

    <div id="UfEmbeddedHub1724201969735"></div>

    <script nonce="<?= $nonce ?>">
    window._ufHubConfig = window._ufHubConfig || [];
    window._ufHubConfig.push({
      'containers':{'app':'#UfEmbeddedHub1724201969735'},
      'collection': '11886924',
      'openLink':function(url){
        window.top.location.href=url;
      },
      'lazyloader':{
        'itemDisplayLimit':6,
        'maxTilesPerRow':4,
        'maxItemsTotal': 0
      },
      'tileSize': 'large',
      'enablePageTracking':false,
      'baseUrl': 'https://resources.scylladb.com/',
      'filesUrl': 'https://resources.scylladb.com/',
      'generatedAtUTC': '2024-08-21 00:58:53',
    });
    </script>

    <script nonce="<?= $nonce ?>">(function(d,t,u) {
      function load(){
        var s=d.createElement(t);s.src=u;d.body.appendChild(s);
      }
      if (window.addEventListener) {
        window.addEventListener('load',load,false);
      }
      else if (window.attachEvent) {
        window.attachEvent('onload',load);
      }
      else{
        window.onload=load;
      }
    }(document,'script','https://resources.scylladb.com/hubsFront/embed_collection'));
    </script>
    <!-- /End Uberflip Embedded Hub Widget -->
  </div>

.. raw:: html

    </div>
  </div>
