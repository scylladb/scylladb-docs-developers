:hide-secondary-sidebar:

.. meta::
   :description: How ScyllaDB beats Aerospike for key-value — and brings wide-column flexibility, elasticity, and dramatically lower RAM costs at scale.
   :keywords: ScyllaDB, Aerospike, comparison, key-value, wide-column, NoSQL, benchmark, RAM, performance

ScyllaDB vs Aerospike: A Technical Comparison
=============================================

This page covers the main differences between ScyllaDB and Aerospike. The
motivation was to answer a paid promotional benchmark that Aerospike distributed.

Aerospike is a stellar K/V database/cache. Caching keys in RAM while the values
are saved in fast NVMe storage is a novel approach for a simple K/V model. Using
this model, Aerospike achieves high throughput and low latency.

ScyllaDB is designed as a more sophisticated database. It is part of the
wide-column NoSQL family, a wide superset of K/V only. The model allows a full
set of clustering keys inside each row, millions of entries can be saved in a
single row. Independent cells can be accessed without rewriting the whole row.
HA and DR are deep in the model with configurable replication, local and global
indexes, best in-class elasticity and a battle-tested database as a service model
(with connectivity, bring-your-own-cloud, encryption, bring-your-own-keys,
security, and more features).

This page compares the performance of Aerospike vs ScyllaDB to show that
flexibility doesn't need to come at the expense of performance. ScyllaDB can beat
Aerospike at its own game.

At a glance
-----------

- **Key-Key-Value, not just Key-Value.** Clustering keys give every row millions
  of independently addressable cells. ScyllaDB updates each cell directly (vs.
  Aerospike's read-modify-write).
- **Indexes don't live in RAM.** Aerospike always pins 64 bytes per key in
  memory. ScyllaDB serves comparable latency straight from NVMe. RAM is cache
  rather than a constraint.
- **Dense instances, fully used.** Limited disk:RAM ratios lock Aerospike out of
  i8ge / i7ie / i3en-class hardware. ScyllaDB runs them at 90% utilization.

One write, or read-modify-write?
--------------------------------

In a K/V model, the row is the unit of allocation. Updating a single element
inside a large value bin means reading the whole object, merging the change, and
writing it all back (so two I/O actions instead of one). ScyllaDB updates a single
cell directly; the LSM tree merges cells in the background using idle-time I/O
schedulers and compaction controllers, without any user involvement or performance
impact.

.. raw:: html

   <style>
   .aero-rmw, .aero-calc {
     /* brand accents (constant in both themes) */
     --scylla:#3cc5f0; --scylla-deep:#1f9fd8; --aero:#ff5a4e; --aero-dim:#c4453c;
     --good:#44d7a8; --radius:14px;
     --mono:"SFMono-Regular","JetBrains Mono",Consolas,"Liberation Mono",monospace;
     /* semantic surfaces — light defaults, overridden under html.dark */
     --surface:#ffffff; --surface-2:#f4f6fc; --text:#1a1f36; --text-muted:#5b6388;
     --border:rgba(13,17,48,.12); --track:rgba(13,17,48,.14); --verdict-bg:#f1f3fa;
     /* op-log is a "terminal" — dark in both themes */
     --oplog-bg:#0d1130; --oplog-fg:#cfe9ff; --keycell-bg:#0d1130;
   }
   html.dark .aero-rmw, html.dark .aero-calc {
     --surface:#141a42; --surface-2:#0d1130; --text:#ffffff; --text-muted:#8b93b8;
     --border:rgba(255,255,255,.10); --track:rgba(255,255,255,.15); --verdict-bg:rgba(255,255,255,.04);
     --keycell-bg:#070a1f;
   }
   .aero-rmw *, .aero-calc * { box-sizing:border-box; }
   .aero-rmw .eyebrow, .aero-calc .eyebrow {
     font-family:var(--mono); font-size:12px; letter-spacing:.18em; text-transform:uppercase;
     color:var(--scylla-deep); display:block; margin-bottom:14px;
   }
   /* ---- RMW playground ---- */
   .aero-rmw { margin:28px 0; }
   .aero-rmw .model-grid { display:grid; grid-template-columns:1fr 1fr; gap:22px; }
   .aero-rmw .model-panel {
     border-radius:var(--radius); padding:24px; border:1px solid var(--border);
     background:var(--surface); color:var(--text);
   }
   .aero-rmw .model-panel.aero { border-top:4px solid var(--aero); }
   .aero-rmw .model-panel.scylla { border-top:4px solid var(--scylla-deep); }
   .aero-rmw .model-panel h3 { font-size:19px; margin:0 0 4px; color:var(--text); }
   .aero-rmw .sub { font-family:var(--mono); font-size:12px; color:var(--text-muted); margin-bottom:18px; }
   .aero-rmw .row-visual { display:flex; align-items:center; gap:6px; flex-wrap:wrap; margin:16px 0; min-height:48px; }
   .aero-rmw .keycell, .aero-rmw .bin, .aero-rmw .cell {
     font-family:var(--mono); font-size:12px; padding:9px 12px; border-radius:8px;
     border:1.5px solid transparent; transition:all .3s ease; white-space:nowrap;
   }
   .aero-rmw .keycell { background:var(--keycell-bg); color:#fff; font-weight:700; }
   .aero-rmw .bin { background:#ffe9e7; border-color:#ffc7c2; color:#8c2f28; }
   .aero-rmw .cell { background:#e3f6fd; border-color:#b5e6f7; color:#0f5e7d; }
   .aero-rmw .bin.rmw-read { box-shadow:0 0 0 3px rgba(255,90,78,.45); transform:scale(1.04); }
   .aero-rmw .bin.flash { box-shadow:0 0 0 3px rgba(255,90,78,.55); transform:scale(1.08); background:#ffd6d3; }
   .aero-rmw .cell.flash { box-shadow:0 0 0 3px rgba(60,197,240,.55); transform:scale(1.08); background:#c4edfb; }
   .aero-rmw .op-log {
     font-family:var(--mono); font-size:12.5px; background:var(--oplog-bg); color:var(--oplog-fg);
     border:1px solid var(--border); border-radius:10px; padding:16px; min-height:140px; line-height:1.8;
   }
   .aero-rmw .op-line { display:block; opacity:0; transform:translateY(4px); transition:opacity .3s, transform .3s; }
   .aero-rmw .op-line.show { opacity:1; transform:none; }
   .aero-rmw .op-log .cost { color:var(--aero); }
   .aero-rmw .op-log .win { color:var(--good); }
   .aero-rmw .play-row { display:flex; align-items:center; gap:16px; margin-top:16px; flex-wrap:wrap; }
   .aero-rmw .demo-btn {
     font:inherit; font-weight:650; font-size:15px; padding:11px 20px; border-radius:10px;
     border:none; cursor:pointer; color:#fff; transition:transform .12s, box-shadow .12s;
   }
   .aero-rmw .demo-btn:hover { transform:translateY(-1px); }
   .aero-rmw .demo-btn.aero-btn { background:var(--aero); box-shadow:0 4px 18px rgba(255,90,78,.3); }
   .aero-rmw .demo-btn.scy-btn { background:var(--scylla); color:#0d1130; box-shadow:0 4px 18px rgba(60,197,240,.35); }
   .aero-rmw .io-meter { font-family:var(--mono); font-size:13px; color:var(--text-muted); }
   .aero-rmw .io-meter b { font-size:18px; }
   .aero-rmw .io-meter.bad b { color:var(--aero-dim); }
   .aero-rmw .io-meter.good b { color:#0d8f6c; }
   html.dark .aero-rmw .io-meter.good b { color:var(--good); }
   /* ---- RAM calculator ---- */
   .aero-calc { margin:28px 0; }
   .aero-calc .calc {
     background:var(--surface); border:1px solid var(--border); border-radius:18px;
     padding:34px; color:var(--text);
   }
   .aero-calc .calc-controls { display:grid; grid-template-columns:1.4fr 1fr 1fr; gap:34px; margin-bottom:36px; }
   .aero-calc .ctrl label {
     font-family:var(--mono); font-size:12px; letter-spacing:.12em; text-transform:uppercase;
     color:var(--text-muted); display:block; margin-bottom:12px;
   }
   .aero-calc .ctrl .val { font-size:26px; font-weight:750; color:var(--text); margin-bottom:10px; font-variant-numeric:tabular-nums; }
   .aero-calc input[type=range] {
     width:100%; appearance:none; -webkit-appearance:none; height:6px; border-radius:4px;
     background:linear-gradient(90deg, var(--scylla) var(--fill,50%), var(--track) var(--fill,50%));
     outline:none; cursor:pointer;
   }
   .aero-calc input[type=range]::-webkit-slider-thumb {
     -webkit-appearance:none; width:22px; height:22px; border-radius:50%;
     background:#fff; border:3px solid var(--scylla); box-shadow:0 2px 10px rgba(0,0,0,.4);
   }
   .aero-calc input[type=range]::-moz-range-thumb {
     width:22px; height:22px; border-radius:50%; background:#fff;
     border:3px solid var(--scylla); box-shadow:0 2px 10px rgba(0,0,0,.4);
   }
   .aero-calc .scale { display:flex; justify-content:space-between; font-family:var(--mono); font-size:11px; color:var(--text-muted); margin-top:8px; }
   .aero-calc .seg { display:flex; gap:8px; flex-wrap:wrap; }
   .aero-calc .seg button {
     font-family:var(--mono); font-size:13px; padding:9px 14px; border-radius:8px;
     background:transparent; color:var(--text-muted); border:1px solid var(--border); cursor:pointer; transition:all .15s;
   }
   .aero-calc .seg button.active { background:var(--scylla); color:#0d1130; border-color:var(--scylla); font-weight:700; }
   .aero-calc .calc-results { display:grid; grid-template-columns:1fr 1fr; gap:22px; }
   .aero-calc .res-card { border-radius:14px; padding:24px; border:1px solid var(--border); }
   .aero-calc .res-card.s { background:rgba(60,197,240,.08); border-color:rgba(60,197,240,.35); }
   .aero-calc .res-card.a { background:rgba(255,90,78,.07); border-color:rgba(255,90,78,.3); }
   .aero-calc .res-card h4 { font-size:16px; margin:0 0 2px; color:var(--text); }
   .aero-calc .res-card .tag { font-family:var(--mono); font-size:11.5px; color:var(--text-muted); margin-bottom:18px; display:block; }
   .aero-calc .stat { display:flex; justify-content:space-between; align-items:baseline; padding:10px 0; border-bottom:1px dashed var(--border); font-size:14px; color:var(--text-muted); }
   .aero-calc .stat:last-child { border-bottom:none; }
   .aero-calc .stat b { font-size:20px; color:var(--text); font-variant-numeric:tabular-nums; }
   .aero-calc .res-card.a .stat b.hot { color:var(--aero); }
   .aero-calc .res-card.s .stat b.cool { color:var(--scylla-deep); }
   html.dark .aero-calc .res-card.s .stat b.cool { color:var(--scylla); }
   .aero-calc .verdict { margin-top:26px; text-align:center; font-size:17px; color:var(--text-muted); background:var(--verdict-bg); border:1px solid var(--border); border-radius:12px; padding:20px; }
   .aero-calc .verdict b { color:var(--aero); font-size:30px; font-variant-numeric:tabular-nums; }
   .aero-calc .calc-foot { margin:18px 0 0; font-size:12.5px; color:var(--text-muted); text-align:center; }
   @media (max-width:820px) {
     .aero-rmw .model-grid, .aero-calc .calc-results { grid-template-columns:1fr; }
     .aero-calc .calc-controls { grid-template-columns:1fr; }
   }
   @media (prefers-reduced-motion:reduce) {
     .aero-rmw *, .aero-rmw *::before, .aero-rmw *::after { transition:none !important; }
   }
   </style>

.. raw:: html

   <div class="aero-rmw">
     <div class="model-grid">
       <div class="model-panel aero">
         <h3>Aerospike &mdash; Key/Value</h3>
         <div class="sub">namespace &rsaquo; set &rsaquo; record &rsaquo; bins (one allocation unit)</div>
         <div class="row-visual" id="aeroRow">
           <span class="keycell">user:9137</span>
           <span class="bin">name</span>
           <span class="bin">email</span>
           <span class="bin">prefs[&hellip;]</span>
           <span class="bin" id="aeroTarget">last_seen</span>
           <span class="bin">cart[&hellip;]</span>
         </div>
         <div class="op-log" id="aeroLog" aria-live="polite">
           <span class="op-line show">&rarr; UPDATE last_seen on record user:9137</span>
           <span class="op-line show"><span class="cost">1. READ entire record from disk (all bins)&hellip;</span></span>
           <span class="op-line show">2. Merge new value into the object in memory</span>
           <span class="op-line show"><span class="cost">3. WRITE entire record back to disk</span></span>
           <span class="op-line show"><span class="cost">&#10007; 2 I/O actions + write amplification &rarr; defrag pressure</span></span>
         </div>
         <div class="play-row">
           <button class="demo-btn aero-btn" type="button" id="aeroBtn">&#9654; Update one element</button>
           <span class="io-meter bad">I/O ops: <b id="aeroIO">2</b></span>
         </div>
       </div>
       <div class="model-panel scylla">
         <h3>ScyllaDB &mdash; Key-Key-Value</h3>
         <div class="sub">keyspace &rsaquo; table &rsaquo; partition key &rsaquo; clustering key &rsaquo; cell</div>
         <div class="row-visual" id="scyRow">
           <span class="keycell">user:9137</span>
           <span class="cell">ck: name</span>
           <span class="cell">ck: email</span>
           <span class="cell">ck: prefs</span>
           <span class="cell" id="scyTarget">ck: last_seen</span>
           <span class="cell">ck: cart</span>
         </div>
         <div class="op-log" id="scyLog" aria-live="polite">
           <span class="op-line show">&rarr; UPDATE last_seen WHERE pk = user:9137</span>
           <span class="op-line show"><span class="win">1. WRITE single cell &mdash; done.</span></span>
           <span class="op-line show">Background: LSM compaction merges cells on idle I/O</span>
           <span class="op-line show"><span class="win">&#10003; 1 I/O action. No read. No user impact.</span></span>
         </div>
         <div class="play-row">
           <button class="demo-btn scy-btn" type="button" id="scyBtn">&#9654; Update one cell</button>
           <span class="io-meter good">I/O ops: <b id="scyIO">1</b></span>
         </div>
       </div>
     </div>
   </div>

The same clustering keys make ScyllaDB a natural **time-series database**:
partition by ``sensor_id``, cluster by ``timestamp``, and range queries become
sequential reads straight off disk. This is well-suited for event logs, messaging,
IoT, AI feature stores. K/V can only fake this with secondary indexes or by
overloading bins with ever-growing lists.

Access patterns
~~~~~~~~~~~~~~~~

Clustering keys aren't a one trick pony. Each pattern below is a different way to
slice a partition.

**01 · Time-series** — Partition by entity, cluster by time

.. code-block:: sql

   PRIMARY KEY ((sensor_id), reading_ts)
   WITH CLUSTERING ORDER BY (reading_ts DESC)

Pairs with **TTL**, time-window compaction, and tiered storage. Range slice:
``WHERE sensor_id=? AND reading_ts >= ? AND < ?``

**02 · Time-bucketing** — Bound the partition size

.. code-block:: sql

   PRIMARY KEY ((sensor_id, day), reading_ts)
   -- day = '2026-06-14'

*Trade-off:* cross-bucket queries fan out to multiple partitions. Pick a
granularity (hour/day/month) to match your read window.

**03 · Messaging / fan-out** — The Discord shape

.. code-block:: sql

   PRIMARY KEY ((channel_id, bucket), message_id)
   WITH CLUSTERING ORDER BY (message_id DESC)
   -- message_id = Snowflake / TimeUUID

Newest-first reads with zero sort at query time. A pure K/V store can't express
this pattern natively.

**04 · Hierarchical** — Compound clustering keys

.. code-block:: sql

   PRIMARY KEY ((user_id), year, month, day, event_id)

Valid: filter ``year``, then ``year+month``… Invalid: filter ``day`` without
``year`` and ``month``.

**05 · Leaderboard** — Cluster by score

.. code-block:: sql

   PRIMARY KEY ((game_id, season), score, player_id)
   WITH CLUSTERING ORDER BY (score DESC, player_id ASC)

``LIMIT 100`` returns the top 100 with no sort at query time.

**06 · Key-Key-Value** — Generic attribute store

.. code-block:: sql

   PRIMARY KEY ((entity_id), attr_name)
   -- rows of (attr_name, value)

Update one attribute without reading or rewriting the others. This is the core
KKV-beats-RMW argument, in schema form.

**07 · Inverted index** — Query-table-per-access-pattern

.. code-block:: sql

   -- base:   PRIMARY KEY ((user_id))
   -- lookup: PRIMARY KEY ((email), user_id)

Direct partition read on ``email`` — no cluster-wide scan, unlike Aerospike's
scatter-gather secondary indexes.

**08 · Graph edges** — Adjacency list

.. code-block:: sql

   PRIMARY KEY ((vertex_id), edge_type, target_id)

Slice by edge type within a vertex; range-scan neighbors in order.

**09 · Event log** — Append-only / event sourcing

.. code-block:: sql

   PRIMARY KEY ((aggregate_id), event_seq)
   WITH CLUSTERING ORDER BY (event_seq ASC)

Sequential write, sequential replay — LSM-friendly and contention-free.

**10 · Hash-prefix** — Split hot/wide partitions

.. code-block:: sql

   PRIMARY KEY ((celebrity_id, shard), post_ts)
   -- shard in 0..N

*Trade-off:* reads query all N shards and merge — a wider single partition becomes
more partitions touched.

**11 · Status + time** — Slice by category, then time

.. code-block:: sql

   PRIMARY KEY ((tenant_id), status, updated_ts)
   WITH CLUSTERING ORDER BY (status ASC, updated_ts DESC)

One partition serves several status-scoped, time-ordered views — no extra index
to maintain.

KKV is harder to build, but it pays off
---------------------------------------

Aerospike's model is elegant precisely because it's simple. Values are bounded
atomic blobs, so they're easy to cache and easy to locate. Just a single NVMe read
(tens of microseconds) brings data to RAM. A wide-column store can't take that
shortcut, and we won't pretend otherwise.

A single key can point to a giant partition. We have customers running a **1 TB
partition** (it's not recommended, but the flexibility is there). Because partition
size is unknown upfront, the engine has to do far more than fetch-a-blob:

- **MVCC** — Multi-version concurrency control so parallel readers and writers see
  consistent results across a partition that may be mid-write.
- **Row-level cache** — Caching has to work at row granularity, not
  whole-partition. You can't evict or populate a terabyte as one unit.
- **Range tombstones** — Deletes aren't a single marker; whole ranges of
  clustering keys can be tombstoned and must be reconciled on read.
- **Multi-allocation parsing** — Unknown partition sizes mean multiple memory
  allocations during parsing instead of one fixed-size slot.
- **Multi-I/O range reads** — Fetching a slice of a partition may require several
  disk accesses, scheduled so they never stall user traffic.
- **Range scans** — Users can scan arbitrary subsets of a partition — a query
  surface a pure K/V store simply doesn't expose.

Altogether, this is a fundamentally harder problem. And ScyllaDB still matches
Aerospike's best benchmarks. The performance advantage of KV comes with a cost —
read on for where each model wins.

64 bytes per key — in RAM, always
----------------------------------

Aerospike keeps its primary index in RAM: a fixed 64 bytes per key, regardless of
record size, scaling linearly with key count. Small partitions are where it hurts
most — at 200 B records the key-to-data ratio approaches 1:3.5. ScyllaDB scales
independently of memory: roughly 100 GB of data per 1 GB of RAM, with no hard
ceiling on keys per node. The table below shows when RAM starts driving your
infrastructure bill.

.. raw:: html

   <div class="aero-calc">
     <span class="eyebrow">Memory footprint at scale &middot; Interactive</span>
     <div class="calc">
       <div class="calc-controls">
         <div class="ctrl">
           <label for="recSlider">Number of records</label>
           <div class="val" id="recVal">1B</div>
           <input type="range" id="recSlider" min="0" max="4" step="0.01" value="2" aria-label="Number of records">
           <div class="scale"><span>10M</span><span>100M</span><span>1B</span><span>10B</span><span>100B</span></div>
         </div>
         <div class="ctrl">
           <label>Record size</label>
           <div class="seg" id="sizeSeg">
             <button type="button" data-size="200">200 B</button>
             <button type="button" data-size="512">512 B</button>
             <button type="button" class="active" data-size="1024">1 KiB</button>
             <button type="button" data-size="2048">2 KiB</button>
           </div>
         </div>
         <div class="ctrl">
           <label>Replication factor</label>
           <div class="seg" id="rfSeg">
             <button type="button" data-rf="1">RF 1</button>
             <button type="button" class="active" data-rf="2">RF 2 <span style="opacity:.6">(Aero default)</span></button>
             <button type="button" data-rf="3">RF 3</button>
           </div>
         </div>
       </div>
       <div class="calc-results">
         <div class="res-card s">
           <h4>ScyllaDB</h4>
           <span class="tag">~100 GB of data per 1 GB of RAM &middot; indexes live on NVMe</span>
           <div class="stat"><span>RAM required (cache)</span><b class="cool" id="sRam">&mdash;</b></div>
           <div class="stat"><span>Total storage (with replication)</span><b id="sStore">&mdash;</b></div>
           <div class="stat"><span>Hard ceiling on keys per node</span><b style="color:var(--good)">None</b></div>
         </div>
         <div class="res-card a">
           <h4>Aerospike</h4>
           <span class="tag">64 B per key per replica &mdash; pinned in RAM</span>
           <div class="stat"><span>RAM required (primary index)</span><b class="hot" id="aRam">&mdash;</b></div>
           <div class="stat"><span>Total storage (with replication)</span><b id="aStore">&mdash;</b></div>
           <div class="stat"><span>Key : data RAM ratio</span><b id="aRatio">&mdash;</b></div>
         </div>
       </div>
       <div class="verdict">At this scale, Aerospike's index needs <b id="xFactor">&mdash;</b> more RAM than ScyllaDB &mdash; <span id="verdictTail">before a single row is cached.</span></div>
       <p class="calc-foot">Base-10 units (1 GB = 10&#8313; B). Theoretical lower bounds &mdash; production adds overhead, secondary indexes, write amplification and headroom. Past a point this forces Aerospike operators to reshape the data model or fall back to all-flash mode, giving away the latency the architecture was built for.</p>
     </div>
   </div>

.. raw:: html

   <script>
   (function () {
     /* ---- RMW animation ---- */
     var aeroBusy = false, scyBusy = false;
     function logLines(el, lines) {
       if (!el) return;
       el.innerHTML = "";
       var i = 0;
       (function next() {
         if (i >= lines.length) return;
         var s = document.createElement("span");
         s.className = "op-line"; s.innerHTML = lines[i];
         el.appendChild(s);
         requestAnimationFrame(function () { s.classList.add("show"); });
         i++; setTimeout(next, 620);
       })();
     }
     function playRMW() {
       if (aeroBusy) return; aeroBusy = true;
       var bins = document.querySelectorAll("#aeroRow .bin");
       var io = document.getElementById("aeroIO");
       io.textContent = "0";
       bins.forEach(function (b) { b.classList.remove("rmw-read", "flash"); });
       logLines(document.getElementById("aeroLog"), [
         "&rarr; UPDATE last_seen on record user:9137",
         "<span class='cost'>1. READ entire record from disk (all bins)&hellip;</span>",
         "2. Merge new value into the object in memory",
         "<span class='cost'>3. WRITE entire record back to disk</span>",
         "<span class='cost'>&#10007; 2 I/O actions + write amplification &rarr; defrag pressure</span>"
       ]);
       setTimeout(function () { bins.forEach(function (b) { b.classList.add("rmw-read"); }); io.textContent = "1"; }, 700);
       setTimeout(function () { bins.forEach(function (b) { b.classList.remove("rmw-read"); }); }, 1900);
       setTimeout(function () { bins.forEach(function (b) { b.classList.add("flash"); }); io.textContent = "2"; }, 2000);
       setTimeout(function () { bins.forEach(function (b) { b.classList.remove("flash"); }); aeroBusy = false; }, 3200);
     }
     function playCell() {
       if (scyBusy) return; scyBusy = true;
       var target = document.getElementById("scyTarget");
       var io = document.getElementById("scyIO");
       io.textContent = "0";
       logLines(document.getElementById("scyLog"), [
         "&rarr; UPDATE last_seen WHERE pk = user:9137",
         "<span class='win'>1. WRITE single cell &mdash; done.</span>",
         "Background: LSM compaction merges cells on idle I/O",
         "<span class='win'>&#10003; 1 I/O action. No read. No user impact.</span>"
       ]);
       setTimeout(function () { target.classList.add("flash"); io.textContent = "1"; }, 700);
       setTimeout(function () { target.classList.remove("flash"); scyBusy = false; }, 2200);
     }
     var aeroBtn = document.getElementById("aeroBtn");
     var scyBtn = document.getElementById("scyBtn");
     if (aeroBtn) aeroBtn.addEventListener("click", playRMW);
     if (scyBtn) scyBtn.addEventListener("click", playCell);

     /* ---- RAM calculator ---- */
     var recSlider = document.getElementById("recSlider");
     if (!recSlider) return;
     var recordSize = 1024, rf = 2;
     function fmtBytes(b) {
       if (b >= 1e15) return (b / 1e15).toPrecision(3).replace(/\.?0+$/, "") + " PB";
       if (b >= 1e12) return (b / 1e12).toPrecision(3).replace(/\.?0+$/, "") + " TB";
       if (b >= 1e9)  return (b / 1e9 ).toPrecision(3).replace(/\.?0+$/, "") + " GB";
       return Math.round(b / 1e6) + " MB";
     }
     function fmtRecs(n) {
       if (n >= 1e9) { var v = n / 1e9; return (v >= 10 ? Math.round(v) : v.toFixed(1).replace(/\.0$/, "")) + "B"; }
       var m = n / 1e6; return (m >= 10 ? Math.round(m) : m.toFixed(1).replace(/\.0$/, "")) + "M";
     }
     function byId(id) { return document.getElementById(id); }
     function calc() {
       var records = Math.pow(10, 7 + parseFloat(recSlider.value));
       byId("recVal").textContent = fmtRecs(records);
       recSlider.style.setProperty("--fill", (parseFloat(recSlider.value) / 4 * 100) + "%");
       var dataBytes = records * recordSize * rf;
       var aeroRam = records * 64 * rf;
       var scyRam = dataBytes / 100;
       byId("aRam").textContent = fmtBytes(aeroRam);
       byId("sRam").textContent = fmtBytes(scyRam);
       byId("aStore").textContent = fmtBytes(dataBytes);
       byId("sStore").textContent = fmtBytes(dataBytes);
       byId("aRatio").textContent = "1 : " + (recordSize / 64).toFixed(1).replace(/\.0$/, "");
       var x = aeroRam / scyRam;
       byId("xFactor").textContent = "×" + (x >= 100 ? Math.round(x) : x.toPrecision(3).replace(/\.?0+$/, ""));
       byId("verdictTail").textContent = recordSize <= 200
         ? "and at 200 B records, the key-to-data RAM ratio is brutal — this is where the bill explodes."
         : "before a single row is cached.";
     }
     recSlider.addEventListener("input", calc);
     byId("sizeSeg").addEventListener("click", function (e) {
       var btn = e.target.closest("button");
       if (!btn || !btn.dataset.size) return;
       byId("sizeSeg").querySelectorAll("button").forEach(function (b) { b.classList.remove("active"); });
       btn.classList.add("active");
       recordSize = +btn.dataset.size; calc();
     });
     byId("rfSeg").addEventListener("click", function (e) {
       var btn = e.target.closest("button");
       if (!btn || !btn.dataset.rf) return;
       byId("rfSeg").querySelectorAll("button").forEach(function (b) { b.classList.remove("active"); });
       btn.classList.add("active");
       rf = +btn.dataset.rf; calc();
     });
     calc();
   })();
   </script>

Dense instances are wasted on Aerospike
----------------------------------------

Because the key cache must live in RAM, Aerospike has a limited disk:RAM ratio and
can't take advantage of storage-dense families like AWS **i8ge, i7ie, i3en**. Look
at the hardware Aerospike chose for its own 2026 benchmark: 6 TB of raw data on
**8× i4g.4xlarge**, with 15 TB of storage per zone. That's roughly **40%
utilization** — so you're paying for disk that sits empty, on a deliberately
less-dense instance family.

.. list-table::
   :widths: 30 35 35
   :header-rows: 1

   * -
     - Aerospike — as benchmarked
     - ScyllaDB — same 6 TB
   * - Configuration
     - 8 × i4g.4xlarge · ~15 TB per zone for 6 TB of data
     - 2 × i8ge.3xlarge — one per zone · 12 vCPU + 7.5 TB NVMe each
   * - Nodes
     - 8
     - 2 (one per zone)
   * - Sized by
     - RAM ceiling, by design
     - Actual data, not RAM
   * - Storage utilization
     - ~40%
     - Up to 90%

This matters more over time. Most deployments become **data-bound** — the dataset
grows until storage, not compute, dominates sizing. That's exactly where
Aerospike's RAM-for-index architecture forces you onto more (and emptier) nodes.

Two more costs of keeping the index in RAM:

- **Slow boot — up to 30 min.** The model assumes every key is cached in RAM, so a
  node rebuilds its entire index on boot. This takes as long as 30 minutes.
  Elasticity suffers (new nodes must build their index), and rolling restarts get
  heavier. Flushing the key cache to disk before reboot helps, but it's still
  slower and more complex than a KKV model that has no such limitation.
- **Small partitions wreck RAM efficiency.** Each key needs 64 bytes of RAM. With
  128–256 B values, the key-to-data ratio gets ugly and you provision enormous
  amounts of RAM for a mediocre result. See the table above to compare RAM required
  and overhead for ScyllaDB KKV vs Aerospike KV at different record sizes.

Flexibility, without giving up the win
--------------------------------------

Despite managing all the complexity outlined above, ScyllaDB still beats
Aerospike's best published numbers in a head-to-head comparison. We keep up with
their chosen workload, and we also do it while offering a data model their
architecture can't express.

**7M+ ops/sec — 2021 benchmark, we repeated theirs at petabyte scale.** Aerospike
claimed 5M TPS read-only and 3.7M TPS 80/20 on 20 i3en.24xlarge. ScyllaDB hit 7M
ops/sec and 7.5M inserts at 4ms P99 — 40% higher throughput on the same hardware
class. See the `petabyte benchmark blog
<https://www.scylladb.com/2022/07/14/benchmarking-petabyte-scale-nosql-workloads-with-scylladb/>`_
and the `presentation
<https://www.scylladb.com/presentations/operating-at-monstrous-new-scales-benchmarking-petabyte-workloads-on-scylladb/>`_.

**On par — 2026 McKnight Group benchmark, corrected config.** The paid benchmark
used incorrect configs: RF3 vs RF2, an old YCSB client. When ScyllaDB reran it with
a corrected configuration, our wide-column KKV model matched throughput and the P99
was only 1–2ms higher at multi-terabyte scale. See the `Aerospike whitepaper
<https://aerospike.com/lp/running-operational-workloads/>`_ or `prove it on your
workload <https://lp.scylladb.com/book-strategy-session-offer>`_.

.. note::

   **About that benchmark.** Aerospike's recent paid whitepaper conveniently showed
   only one narrow scenario suited to its architecture: Key/Value only (the only
   schema it supports), large values (which masks the all-index-in-RAM problem), no
   node failures (masking slow recovery), and no scaling events (masking ScyllaDB's
   elasticity). On that exact workload, ScyllaDB is on par. Change any one of those
   variables and the results shift in ScyllaDB's favor. Let us run it on *your* data
   rather than ours.

Meet Logstor — our native K/V mode
----------------------------------

With demand for pure K/V and the chance to solve the easier problem optimally, we
built our own K/V-only format. It keeps the advantages of ScyllaDB — tablets,
DBaaS, advanced consistency options — and adds a simple value type to push
performance even further. We call it **Logstor**, after the LSA (log-structured
allocator) that already manages ScyllaDB's in-RAM memory. Logstor applies the same
algorithm to managing space on disk.

- **Use KKV when you need the data model.** Time-series, messaging, hierarchies,
  leaderboards, range scans, secondary indexes, multi-cell updates without RMW. The
  wide-column flexibility is the point.
- **Use Logstor KV when it's genuinely key/value.** Simple lookups by key with a
  bounded value — Aerospike's home turf. Logstor delivers better performance than
  Aerospike on that workload, with ScyllaDB's elasticity and DBaaS underneath.

One platform, two storage engines, your choice per workload. For some use cases KKV
is the right tool; for others the new KV format is. Either way, you stay on the same
elastic, fully-managed, multi-region database — and either way you beat the
alternative on its own terms.

And there's more coming beyond raw performance — including fresh benchmark results
on the current i8g generation, not just the older hardware.

Feature by feature
------------------

How do Aerospike and ScyllaDB compare on flexibility, efficiency, scaling,
resiliency, and DBaaS capabilities? Explore each category below.

Flexibility
~~~~~~~~~~~

.. list-table::
   :widths: 18 41 41
   :header-rows: 1

   * - Capability
     - Aerospike
     - ScyllaDB
   * - Data model
     - **Key-Value only.** Namespaces › Sets › Records › Bins. Single-record
       lookups; complex data must be aggregated into one record, document-style.
     - **Wide-column (KKV).** Partition key routes data; clustering keys sort
       millions of independent cells per row. Strict superset of K/V — plus vector
       embeddings for AI retrieval.
   * - Range queries
     - Not a design goal. Try secondary indexes (memory + performance overhead) or
       abuse Collection Data Types — bloated records, bottlenecks.
     - Clustering keys sort data on disk natively. "All readings for sensor A
       between Tuesday and Friday" is one efficient sequential read. Built for
       time-series, messaging, IoT.
   * - Secondary access patterns
     - Local in-memory secondary indexes only. Queries scatter-gather across
       *every* node; strict-SLA users end up dual-writing two tables in the
       application.
     - Local *and* global secondary indexes, plus Materialized Views. Query by
       ``email_address`` with a direct partition read — no cluster-wide scan.
   * - Schema & types
     - Schemaless beyond the primary key. Same bin can be a string in one record,
       an integer in the next — validation burden shifts to app code for years.
     - Schema enforced under CQL with online ``ALTER TABLE``; collections plus
       reusable User-Defined Types. DynamoDB-style free attributes under Alternator.
   * - Query APIs
     - Proprietary API and clients. The data layer is permanently attached to
       Aerospike.
     - CQL (Cassandra protocol) + DynamoDB-compatible API. Migrate from Cassandra,
       DataStax, Keyspaces, Cosmos DB or DynamoDB with little to no change — and
       inherit their Spark / Kafka / Trino ecosystems.

Efficiency
~~~~~~~~~~

.. list-table::
   :widths: 18 41 41
   :header-rows: 1

   * - Capability
     - Aerospike
     - ScyllaDB
   * - Memory
     - Primary index in RAM by default: 64 B per entry. At 90% memory utilization,
       a node enters ``stop-writes`` — writes halt until fixed. All-flash mode
       exists, at the cost of latency.
     - Memory is unified cache (indexes + rows, LRU). Nothing is force-pinned;
       billion-row workloads are dramatically cheaper. Comparable latency served
       straight from NVMe.
   * - CPU
     - OS-native thread pools per task type; the OS owns scheduling, so context
       switching grows with scale. Vertical scaling means hand-tuning pools.
     - Shard-per-core, shared-nothing (Seastar). No locks, no contention; designed
       to run at 90%+ CPU with Workload Prioritization keeping user ops first —
       OLAP beside OLTP safely.
   * - Storage
     - Proprietary, opaque raw-device format — backups and tooling must go through
       Aerospike products. Disk often tuned well below the 90% default for
       write-heavy loads.
     - Industry-standard XFS, open SSTable files. Incremental compaction lets you
       fill disks to 90% (ScyllaDB X Cloud) without risking availability.
   * - Write-heavy workloads
     - Copy-on-write storage triggers aggressive defragmentation under heavy
       updates — write amplification, CPU overhead, latency spikes; admins throttle
       defrag by hand.
     - LSM-tree writes to immutable SSTables; compaction runs in background under
       I/O schedulers that guarantee user workloads aren't impacted. Cell-level
       updates skip RMW entirely.

Scaling
~~~~~~~

.. list-table::
   :widths: 18 41 41
   :header-rows: 1

   * - Capability
     - Aerospike
     - ScyllaDB
   * - Elasticity
     - Fixed 4096 partitions; scaling triggers Migrations whose disk/network I/O
       causes latency spikes — so admins throttle them and scaling stretches out.
     - Tablets move fine-grained data chunks between nodes. Scale from 500K to 2M
       OPS in ~10 minutes. No overprovisioning needed.
   * - Vertical scale
     - RAM-for-indexes architecture caps useful node density; thread pools need
       retuning as cores grow.
     - Lockless shard-per-core design scales linearly to 256+ vCPU meganodes;
       streaming to a 60 TB node is as fast as to a small one.
   * - Global scale
     - XDR for cross-DC; Multi-Site Clustering is a paid add-on, and active-active
       commits every region before a write succeeds — latency climbs.
     - Native multi-DC, eventually-consistent active-active replication. Reads and
       writes are served locally; replication never sits in the write path. No
       bolted-on CDC between DCs.

Resiliency
~~~~~~~~~~

.. list-table::
   :widths: 18 41 41
   :header-rows: 1

   * - Capability
     - Aerospike
     - ScyllaDB
   * - Node failure & maintenance
     - A reboot wipes the in-memory index — it's rebuilt over the network (ASMT
       helps, with extra steps). Rack/AZ loss forces migrations that hit cluster
       performance. Rack awareness: Enterprise add-on.
     - Leaderless, flash-persisted design: nodes leave and rejoin gracefully, no
       availability or performance impact. Region and rack awareness are default —
       for replication and for AZ-local client routing.
   * - Replication economics
     - RF=2 is common — it offsets the RAM cost. One node failure leaves a single
       copy of your data during the most dangerous window.
     - RF=3 is affordable because the architecture is hardware-efficient: quorum
       consistency, seamless rolling upgrades, true fault tolerance.
   * - Consistency
     - Strong Consistency mode is a paid add-on, with higher write latency
       cluster-wide.
     - Per-query Consistency Level: ``LOCAL_QUORUM`` for AZ-spanning safety with
       local reads, global quorum where you need it, tunable along the request path.

DBaaS
~~~~~

.. list-table::
   :widths: 18 41 41
   :header-rows: 1

   * - Capability
     - Aerospike
     - ScyllaDB
   * - Managed service
     - Newer offering — early-adopter territory.
     - ScyllaDB Cloud has run data-intensive production workloads since 2019:
       Tripadvisor, Freshworks, Supercell. Bring-your-own-cloud, BYO keys,
       encryption at rest, advanced networking.
   * - Feature gating
     - Community edition lacks compression, encryption-at-rest, multi-region
       replication, rack awareness — gated behind Enterprise, some priced
       separately.
     - Free tier includes everything: advanced compression, enterprise
       encryption-at-rest, Workload Prioritization, cross-region replication, LDAP.
       Develop locally on your own workstation against the real thing.
   * - Support
     - Standard commercial support tiers.
     - World-class 24×7 support with a 15-minute SLA. Consistently the top-rated
       NoSQL provider on G2.
   * - Multi-DC
     - Cross-Datacenter Replication (XDR); true active-active multi-site clustering
       is a paid add-on with cross-region write latency.
     - Native multi-DC, eventually-consistent active-active — reads and writes
       served locally, replication off the write path. No bolted-on CDC between
       datacenters.
   * - Elasticity & scale
     - Migrations throttled to protect traffic; scaling stretches out.
     - Tablets + X Cloud: scale up *and* out, 500K → 2M OPS in ~10 minutes, no
       overprovisioning.
   * - What's next
     - —
     - Logstor, our new KV storage mode, beats Aerospike on its home turf — and
       there's more coming beyond raw performance. Watch for i8g-generation
       benchmark results.

You don't have to compromise
----------------------------

Teams can enjoy the best DBaaS, elasticity and HA while having a feature-rich
wide-column DB or even a K/V store with the best results in the industry. Reach out
to our engineering team.

- `Book a strategy session <https://lp.scylladb.com/book-strategy-session-offer>`_
- `Get started free <https://cloud.scylladb.com/>`_

.. note::

   RAM model based on `keys-vs-ram <https://fee-mendes.github.io/keys-vs-ram/>`_.
