:hide-secondary-sidebar:

.. meta::
   :description: How ScyllaDB compaction works, step by step, with a diagram of the SSTables on disk for each step: flush, incremental compaction (ICS), the space amplification goal, leveled compaction (LCS) and time-window compaction (TWCS).
   :keywords: ScyllaDB, compaction, ICS, incremental compaction, space amplification goal, LCS, TWCS, SSTable, LSM tree

Compaction, Step by Step
========================

ScyllaDB writes fast because it never updates data in place. Compaction is the
price of that design. This page shows what compaction does, one step at a time,
with diagrams from a compaction simulator.

.. raw:: html

   <style>
   /* Diagrams: static copies of the compaction simulator's "SSTables on disk"
      panel. The rules are the simulator's disk rules, with its design tokens
      resolved; light by default, overridden under html.dark like the theme. */
   .cv-fig, .cv-legend {
     --cv-bg:#ffffff; --cv-track:oklch(98% 0.007 250); --cv-border:oklch(90% 0.031 256);
     --cv-faint:oklch(69% 0.052 262); --cv-muted:#5f6480;
     --cv-warn:oklch(58% 0.185 68); --cv-ok:oklch(53% 0.191 164); --cv-ok-bg:oklch(97% 0.040 140);
     --cv-t0:oklch(87% 0.118 218); --cv-t1:oklch(84% 0.140 222); --cv-t2:oklch(76% 0.125 226);
     --cv-t3:oklch(64% 0.125 230); --cv-t4:oklch(54% 0.111 234); --cv-t5:oklch(44% 0.091 238);
     --cv-dark:oklch(21% 0.039 277); --cv-light:oklch(98% 0.007 250);
     --cv-i0:var(--cv-dark); --cv-i1:var(--cv-dark); --cv-i2:var(--cv-dark);
     --cv-i3:var(--cv-dark); --cv-i4:var(--cv-light); --cv-i5:var(--cv-light);
     --cv-mono:"Roboto Mono","SFMono-Regular",Consolas,"Liberation Mono",monospace;
   }
   html.dark .cv-fig, html.dark .cv-legend {
     --cv-bg:oklch(25% 0.046 274); --cv-track:oklch(21% 0.039 277); --cv-border:oklch(32% 0.051 271);
     --cv-faint:oklch(46% 0.053 268); --cv-muted:#8b93b8;
     --cv-warn:oklch(74% 0.210 77); --cv-ok:oklch(69% 0.247 156); --cv-ok-bg:oklch(24% 0.064 180);
     --cv-t0:oklch(37% 0.071 242); --cv-t1:oklch(44% 0.091 238); --cv-t2:oklch(54% 0.111 234);
     --cv-t3:oklch(64% 0.125 230); --cv-t4:oklch(76% 0.125 226); --cv-t5:oklch(84% 0.140 222);
     --cv-i0:var(--cv-light); --cv-i1:var(--cv-light); --cv-i2:var(--cv-light);
     --cv-i3:var(--cv-dark); --cv-i4:var(--cv-dark); --cv-i5:var(--cv-dark);
   }
   .cv-fig { margin:8px 0 32px; }
   .cv-fig * { box-sizing:border-box; }
   .cv-snap { background:var(--cv-bg); border:1px solid var(--cv-border); border-radius:4px; padding:16px 18px 18px; }
   .cv-snap-head { font-size:12px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--cv-muted); line-height:1.4; }
   .cv-snap-head span { font-weight:400; letter-spacing:0; text-transform:none; color:var(--cv-faint); }
   .cv-disk { position:relative; margin-top:14px; --lane-x:178px; }
   .cv-disk .lane-layer { position:absolute; inset:0; }
   .cv-disk .sst-layer { position:absolute; left:var(--lane-x); right:0; top:0; bottom:0; }
   .cv-disk .row-label { position:absolute; left:0; width:calc(var(--lane-x) - 12px); font:700 11px/1.25 var(--cv-mono);
     letter-spacing:.04em; text-transform:uppercase; color:var(--cv-faint); text-align:right; }
   .cv-disk .row-label em { display:block; font-style:normal; font-weight:400; text-transform:none; letter-spacing:0; opacity:.8; }
   .cv-disk .row-track { position:absolute; left:var(--lane-x); right:0; height:34px; background:var(--cv-track);
     border:1px solid var(--cv-border); border-radius:5px; }
   .cv-disk .row-track.keyspace { background:repeating-linear-gradient(90deg, transparent 0 24px, var(--cv-border) 24px 25px), var(--cv-track); }
   .cv-disk .sst { position:absolute; height:28px; min-width:7px; border-radius:3px; background:var(--tier-c, var(--cv-t2));
     border:1px solid color-mix(in srgb, var(--cv-i2) 22%, transparent); color:var(--cv-i2); font:700 11px var(--cv-mono);
     display:flex; align-items:center; justify-content:center; overflow:hidden; white-space:nowrap; }
   .cv-disk .sst[data-depth="0"] { --tier-c:var(--cv-t0); color:var(--cv-i0); }
   .cv-disk .sst[data-depth="1"] { --tier-c:var(--cv-t1); color:var(--cv-i1); }
   .cv-disk .sst[data-depth="2"] { --tier-c:var(--cv-t2); color:var(--cv-i2); }
   .cv-disk .sst[data-depth="3"] { --tier-c:var(--cv-t3); color:var(--cv-i3); }
   .cv-disk .sst[data-depth="4"] { --tier-c:var(--cv-t4); color:var(--cv-i4); }
   .cv-disk .sst[data-depth="5"] { --tier-c:var(--cv-t5); color:var(--cv-i5); }
   .cv-disk .sst.compacting { outline:2px solid var(--cv-warn); outline-offset:1px; }
   .cv-disk .sst.output { background:var(--cv-ok-bg); border:1px dashed var(--cv-ok); color:var(--cv-ok); }
   .cv-disk .sst.expired { opacity:.35; }
   .cv-fig figcaption { font-size:14px; line-height:1.6; color:var(--cv-muted); margin-top:10px; }
   .cv-fig figcaption b { color:inherit; font-weight:700; }
   .cv-legend { list-style:none; padding:0; margin:16px 0 24px; display:grid; gap:10px; }
   .cv-legend li { display:flex; gap:12px; align-items:flex-start; margin:0; }
   .content .content-body ul.cv-legend > li:before { content:none; }   /* the theme draws its bullets here */
   .cv-key { flex:0 0 96px; display:flex; gap:2px; align-items:center; min-height:1.6em; }
   .cv-blk { display:inline-block; height:18px; border-radius:3px; font:700 10px/18px var(--cv-mono); text-align:center; color:var(--cv-i2); }
   .cv-blk.t0 { background:var(--cv-t0); } .cv-blk.t1 { background:var(--cv-t1); } .cv-blk.t2 { background:var(--cv-t2); }
   .cv-blk.t3 { background:var(--cv-t3); } .cv-blk.t4 { background:var(--cv-t4); } .cv-blk.t5 { background:var(--cv-t5); }
   .cv-blk.sel { background:var(--cv-t2); outline:2px solid var(--cv-warn); outline-offset:1px; }
   .cv-blk.out { background:var(--cv-ok-bg); color:var(--cv-ok); border:1px dashed var(--cv-ok); }
   @media (max-width:600px) { .cv-disk { --lane-x:112px; } .cv-snap { padding:12px; } }
   </style>

How to read the diagrams
------------------------

The diagrams on this page come from the `compaction simulator <https://tzach.github.io/compaction-viz/>`__. Each
diagram is a copy of one part of the simulator: the **SSTables on disk**. Each
diagram shows the disk at one moment in the simulated time. Put the pointer on a
block to see the details of that SSTable.

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="Example diagram: ICS runs during a compaction">
       <div class="cv-snap-head">SSTables on disk <span>— 6 runs</span></div>
       <div class="cv-disk" style="height:294px"><div class="lane-layer"><div class="row-label" style="top:1px">RUN #34<em>1 fragment · 307 MB</em></div><div class="row-track" style="top:0px"></div><div class="row-label" style="top:42px">RUN #36<em>1 fragment · 313 MB</em></div><div class="row-track" style="top:41px"></div><div class="row-label" style="top:83px">RUN #33<em>1 fragment · 604 MB</em></div><div class="row-track" style="top:82px"></div><div class="row-label" style="top:124px">RUN #35<em>1 fragment · 1000 MB</em></div><div class="row-track" style="top:123px"></div><div class="row-label" style="top:165px">RUN #31<em>3 fragments · 2056 MB</em></div><div class="row-track" style="top:164px"></div><div class="row-label" style="top:206px">RUN #16<em>3 fragments · 2124 MB</em></div><div class="row-track" style="top:205px"></div><div class="row-label" style="top:247px">WRITING<em>ICS output</em></div><div class="row-track" style="top:246px"></div></div><div class="sst-layer"><div class="sst" data-depth="0" title="SSTable #41&#10;307 MB / 307 rows&#10;keys 6–19832&#10;written at t95&#10;run #34, fragment 0" style="--tier-c: var(--cv-t0); top: 3px; left: 0%; width: 14.054%;">307</div><div class="sst" data-depth="0" title="SSTable #44&#10;313 MB / 313 rows&#10;keys 19–19339&#10;written at t100&#10;run #36, fragment 0" style="--tier-c: var(--cv-t0); top: 44px; left: 0%; width: 14.336%;">313</div><div class="sst" data-depth="1" title="SSTable #42&#10;604 MB / 604 rows&#10;keys 3–19991&#10;written at t95&#10;run #33, fragment 0" style="--tier-c: var(--cv-t1); top: 85px; left: 0%; width: 28.037%;">604</div><div class="sst" data-depth="2" title="SSTable #43&#10;1000 MB / 1000 rows&#10;keys 0–1535&#10;written at t99&#10;run #35, fragment 0" style="--tier-c: var(--cv-t2); top: 126px; left: 0%; width: 46.681%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #38&#10;1000 MB / 1000 rows&#10;keys 0–2365&#10;written at t90&#10;run #31, fragment 0" style="--tier-c: var(--cv-t3); top: 167px; left: 0%; width: 46.681%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #39&#10;1000 MB / 1000 rows&#10;keys 2368–17623&#10;written at t92&#10;run #31, fragment 1" style="--tier-c: var(--cv-t3); top: 167px; left: 47.081%; width: 46.681%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #40&#10;56 MB / 56 rows&#10;keys 17673–19976&#10;written at t92&#10;run #31, fragment 2" style="--tier-c: var(--cv-t3); top: 167px; left: 94.162%; width: 2.237%;">56</div><div class="sst compacting" data-depth="3" title="SSTable #19&#10;1000 MB / 1000 rows&#10;keys 4–2330&#10;written at t50&#10;run #16, fragment 0" style="--tier-c: var(--cv-t3); top: 208px; left: 0%; width: 46.681%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #20&#10;1000 MB / 1000 rows&#10;keys 2334–15388&#10;written at t52&#10;run #16, fragment 1" style="--tier-c: var(--cv-t3); top: 208px; left: 47.081%; width: 46.681%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #21&#10;124 MB / 124 rows&#10;keys 15406–19941&#10;written at t52&#10;run #16, fragment 2" style="--tier-c: var(--cv-t3); top: 208px; left: 94.162%; width: 5.438%;">124</div><div class="sst output" data-depth="3" title="Compaction output being written: 684 MB so far" style="--tier-c: var(--cv-t3); top: 249px; left: 0%; width: 31.803%;">684 MB</div></div></div>
     </div>
     <figcaption><b>An example diagram.</b> Incremental compaction at tick 100. The Incremental compaction section explains this diagram. <a href="https://tzach.github.io/compaction-viz/?strategy=ics&amp;workload=hot&amp;tick=100" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

Use these rules to read a diagram:

.. raw:: html

   <ul class="cv-legend">
     <li><span class="cv-key"><span class="cv-blk t2" style="width:96px">RUN / L1</span></span>
       <span><b>One row is one group of SSTables.</b> The group depends on the strategy: a <b>run</b> in ICS, a <b>level</b> in LCS, a <b>time window</b> in TWCS. The label at the left gives the name of the group, the number of SSTables in it, and its size. The heading above the rows gives the number of groups.</span></li>
     <li><span class="cv-key"><span class="cv-blk t2" style="width:30px">160</span><span class="cv-blk t2" style="width:62px">310</span></span>
       <span><b>One block is one SSTable.</b> In ICS, one block is one fragment of a run. The width of a block is proportional to its size on disk. The number in the block is its size in MB.</span></li>
     <li><span class="cv-key"><span class="cv-blk t0" style="width:14px"></span><span class="cv-blk t1" style="width:14px"></span><span class="cv-blk t2" style="width:14px"></span><span class="cv-blk t3" style="width:14px"></span><span class="cv-blk t4" style="width:14px"></span><span class="cv-blk t5" style="width:14px"></span></span>
       <span><b>The shade of blue shows age.</b> The key at the left starts with new, small data and ends with old data that compaction merged many times.</span></li>
     <li><span class="cv-key"><span class="cv-blk sel" style="width:62px">1000</span></span>
       <span><b>An orange outline marks an input of the compaction in progress.</b> The strategy selected these SSTables to merge.</span></li>
     <li><span class="cv-key"><span class="cv-blk out" style="width:62px">684 MB</span></span>
       <span><b>A green, dashed block is the output of the compaction.</b> It is on disk, and it grows while the compaction continues. Its row has the label <b>WRITING</b>.</span></li>
   </ul>

The simulated time is in **ticks**. One tick is one hour. In each tick, the
client writes 64 MB. The memtable flushes to disk when it holds 256 MB. The
caption under each diagram gives the tick and the values that the full simulator
measures at that tick, for example space amplification.

.. note::

   To see more than the disk, click the link under a diagram. It opens the full
   simulator at the same state, paused. Click **Step** to move one tick forward,
   or **Play** to run it. The full simulator also shows the write path, the
   amplification values and a chart. The model is deterministic, so every reader
   sees the same state. The simulator is an educational model. It follows the
   selection rules in the ScyllaDB source, but it is not an exact copy of
   ScyllaDB behavior.

The write path
--------------

ScyllaDB uses a log-structured merge tree (LSM tree). A write goes to two places:

* The **commitlog**, an append-only file on disk. It protects the write if the
  node stops.
* The **memtable**, a sorted table in memory. Reads can see the write
  immediately.

At tick 4, the memtable holds 249 of 256 MB, and the disk is still empty. The
workload is overwrite-heavy: 80% of the writes go to 20% of the keys. A new write
to a key replaces the old value in the memtable, so the memtable already removed
7 MB of duplicates.

When the memtable is full, ScyllaDB **flushes** it to disk as a new file. This
file is an **SSTable** (sorted string table). ScyllaDB then truncates the
commitlog, because the data is now safe in the SSTable.

An SSTable is immutable. ScyllaDB never changes it after the flush. This is the
reason writes are fast: a write is only an append and a memory update.

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="First flush">
       <div class="cv-snap-head">SSTables on disk <span>— 1 run</span></div>
       <div class="cv-disk" style="height:48px"><div class="lane-layer"><div class="row-label" style="top:1px">RUN #1<em>1 fragment · 310 MB</em></div><div class="row-track" style="top:0px"></div></div><div class="sst-layer"><div class="sst" data-depth="0" title="SSTable #1&#10;310 MB / 310 rows&#10;keys 4–19922&#10;written at t5&#10;run #1, fragment 0" style="--tier-c: var(--cv-t0); top: 3px; left: 0%; width: 99.6%;">310</div></div></div>
     </div>
     <figcaption><b>Tick 5.</b> The first flush writes one 310 MB SSTable. The memtable and the commitlog are empty again. <a href="https://tzach.github.io/compaction-viz/?strategy=ics&amp;workload=hot&amp;tick=5" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

Why compaction is necessary
---------------------------

Each flush adds one more SSTable. Over time, this causes two problems:

* **Wasted space.** If you update or delete a row, the old version stays in an
  older SSTable. Both versions use disk space.
* **Slower reads.** A row can be in many SSTables. A read must look in each one
  and merge the results. Bloom filters help, but more SSTables still mean more
  disk reads.

**Compaction** fixes both problems. It reads a set of SSTables, merges them, and
writes new SSTables that contain only the live data. For each key, the newest
version wins. Then ScyllaDB deletes the input SSTables.

The three costs
^^^^^^^^^^^^^^^

Each compaction strategy balances three costs. The simulator measures all three
from the simulated data:

.. list-table::
   :header-rows: 1
   :widths: 20 35 45

   * - Cost
     - Definition
     - Why it matters
   * - **Space amplification**
     - Bytes on disk ÷ bytes of live data
     - You pay for disk that holds old versions and in-progress compaction output.
   * - **Write amplification**
     - Bytes written to disk ÷ bytes flushed from the memtable
     - Each rewrite uses disk bandwidth and CPU that user queries cannot use.
   * - **Read amplification**
     - Files that one key lookup can touch
     - More files per read means higher read latency.

No strategy makes all three costs low. Each strategy selects which cost to keep
low for a given workload.

Incremental compaction (ICS)
----------------------------

Size tiers
^^^^^^^^^^

Incremental compaction (ICS) puts SSTables of similar size into the same
**bucket**, or tier. When a tier has enough SSTables, ICS merges them into one
larger SSTable. That SSTable goes into the next, larger tier.

The diagram below shows the first compaction. The two SSTables have almost the
same size (308 MB and 310 MB), so they are in the same tier. The orange outline
shows the SSTables that the strategy selected.

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="First compaction starts">
       <div class="cv-snap-head">SSTables on disk <span>— 2 runs</span></div>
       <div class="cv-disk" style="height:89px"><div class="lane-layer"><div class="row-label" style="top:1px">RUN #2<em>1 fragment · 308 MB</em></div><div class="row-track" style="top:0px"></div><div class="row-label" style="top:42px">RUN #1<em>1 fragment · 310 MB</em></div><div class="row-track" style="top:41px"></div></div><div class="sst-layer"><div class="sst compacting" data-depth="0" title="SSTable #2&#10;308 MB / 308 rows&#10;keys 36–19941&#10;written at t10&#10;run #2, fragment 0" style="--tier-c: var(--cv-t0); top: 3px; left: 0%; width: 98.955%;">308</div><div class="sst compacting" data-depth="0" title="SSTable #1&#10;310 MB / 310 rows&#10;keys 4–19922&#10;written at t5&#10;run #1, fragment 0" style="--tier-c: var(--cv-t0); top: 44px; left: 0%; width: 99.6%;">310</div></div></div>
     </div>
     <figcaption><b>Tick 10.</b> Two SSTables of similar size are selected for compaction. Read amplification is 2. <a href="https://tzach.github.io/compaction-viz/?strategy=ics&amp;workload=hot&amp;tick=10" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="First compaction done">
       <div class="cv-snap-head">SSTables on disk <span>— 1 run</span></div>
       <div class="cv-disk" style="height:48px"><div class="lane-layer"><div class="row-label" style="top:1px">RUN #3<em>1 fragment · 594 MB</em></div><div class="row-track" style="top:0px"></div></div><div class="sst-layer"><div class="sst" data-depth="0" title="SSTable #3&#10;594 MB / 594 rows&#10;keys 4–19941&#10;written at t12&#10;run #3, fragment 0" style="--tier-c: var(--cv-t0); top: 3px; left: 0%; width: 99.6%;">594</div></div></div>
     </div>
     <figcaption><b>Tick 12.</b> The merge is complete. One 594 MB SSTable replaces 618 MB of input, because the merge removed old versions of hot keys. Read amplification is 1 again. Write amplification is 1.96: most data is now on disk twice in history, once from the flush and once from the compaction. <a href="https://tzach.github.io/compaction-viz/?strategy=ics&amp;workload=hot&amp;tick=12" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

ICS copies each row approximately once per tier. For this reason, its write
amplification is low.

Runs and fragments
^^^^^^^^^^^^^^^^^^

A merge of a large tier has a problem. If the merge writes one large output file
before it deletes the inputs, the disk holds two copies of the tier for a short
time. A merge of the largest tier can almost double the disk usage.

ICS prevents this. It splits each large SSTable into an **SSTable run**: a set of
small fragments with key ranges that do not overlap. The fragment size is
``sstable_size_in_mb``. The default is 1000 MB.

ICS compacts runs, not files:

#. It selects two or more runs of similar size.
#. It reads the fragments in key order.
#. When an output fragment is full, ICS seals it.
#. When ICS has read all of an input fragment, it deletes that fragment
   immediately.

Thus, the temporary space is only a few fragments, not a full copy of the tier.

Compare the two diagrams below. They show one compaction, three ticks apart. The
two input runs (outlined) had three fragments each. Three ticks later, each has
only two fragments. The output (green, dashed) grew from 684 MB to 948 MB. Disk
usage went down from 7088 MB to 6352 MB while the compaction continued.

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="Incremental compaction in progress">
       <div class="cv-snap-head">SSTables on disk <span>— 6 runs</span></div>
       <div class="cv-disk" style="height:294px"><div class="lane-layer"><div class="row-label" style="top:1px">RUN #34<em>1 fragment · 307 MB</em></div><div class="row-track" style="top:0px"></div><div class="row-label" style="top:42px">RUN #36<em>1 fragment · 313 MB</em></div><div class="row-track" style="top:41px"></div><div class="row-label" style="top:83px">RUN #33<em>1 fragment · 604 MB</em></div><div class="row-track" style="top:82px"></div><div class="row-label" style="top:124px">RUN #35<em>1 fragment · 1000 MB</em></div><div class="row-track" style="top:123px"></div><div class="row-label" style="top:165px">RUN #31<em>3 fragments · 2056 MB</em></div><div class="row-track" style="top:164px"></div><div class="row-label" style="top:206px">RUN #16<em>3 fragments · 2124 MB</em></div><div class="row-track" style="top:205px"></div><div class="row-label" style="top:247px">WRITING<em>ICS output</em></div><div class="row-track" style="top:246px"></div></div><div class="sst-layer"><div class="sst" data-depth="0" title="SSTable #41&#10;307 MB / 307 rows&#10;keys 6–19832&#10;written at t95&#10;run #34, fragment 0" style="--tier-c: var(--cv-t0); top: 3px; left: 0%; width: 14.054%;">307</div><div class="sst" data-depth="0" title="SSTable #44&#10;313 MB / 313 rows&#10;keys 19–19339&#10;written at t100&#10;run #36, fragment 0" style="--tier-c: var(--cv-t0); top: 44px; left: 0%; width: 14.336%;">313</div><div class="sst" data-depth="1" title="SSTable #42&#10;604 MB / 604 rows&#10;keys 3–19991&#10;written at t95&#10;run #33, fragment 0" style="--tier-c: var(--cv-t1); top: 85px; left: 0%; width: 28.037%;">604</div><div class="sst" data-depth="2" title="SSTable #43&#10;1000 MB / 1000 rows&#10;keys 0–1535&#10;written at t99&#10;run #35, fragment 0" style="--tier-c: var(--cv-t2); top: 126px; left: 0%; width: 46.681%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #38&#10;1000 MB / 1000 rows&#10;keys 0–2365&#10;written at t90&#10;run #31, fragment 0" style="--tier-c: var(--cv-t3); top: 167px; left: 0%; width: 46.681%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #39&#10;1000 MB / 1000 rows&#10;keys 2368–17623&#10;written at t92&#10;run #31, fragment 1" style="--tier-c: var(--cv-t3); top: 167px; left: 47.081%; width: 46.681%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #40&#10;56 MB / 56 rows&#10;keys 17673–19976&#10;written at t92&#10;run #31, fragment 2" style="--tier-c: var(--cv-t3); top: 167px; left: 94.162%; width: 2.237%;">56</div><div class="sst compacting" data-depth="3" title="SSTable #19&#10;1000 MB / 1000 rows&#10;keys 4–2330&#10;written at t50&#10;run #16, fragment 0" style="--tier-c: var(--cv-t3); top: 208px; left: 0%; width: 46.681%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #20&#10;1000 MB / 1000 rows&#10;keys 2334–15388&#10;written at t52&#10;run #16, fragment 1" style="--tier-c: var(--cv-t3); top: 208px; left: 47.081%; width: 46.681%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #21&#10;124 MB / 124 rows&#10;keys 15406–19941&#10;written at t52&#10;run #16, fragment 2" style="--tier-c: var(--cv-t3); top: 208px; left: 94.162%; width: 5.438%;">124</div><div class="sst output" data-depth="3" title="Compaction output being written: 684 MB so far" style="--tier-c: var(--cv-t3); top: 249px; left: 0%; width: 31.803%;">684 MB</div></div></div>
     </div>
     <figcaption><b>Tick 100.</b> ICS merges run #31 and run #16, three fragments each. 684 MB of output is written. 7088 MB on disk. <a href="https://tzach.github.io/compaction-viz/?strategy=ics&amp;workload=hot&amp;tick=100" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="Input fragments released">
       <div class="cv-snap-head">SSTables on disk <span>— 6 runs</span></div>
       <div class="cv-disk" style="height:294px"><div class="lane-layer"><div class="row-label" style="top:1px">RUN #34<em>1 fragment · 307 MB</em></div><div class="row-track" style="top:0px"></div><div class="row-label" style="top:42px">RUN #36<em>1 fragment · 313 MB</em></div><div class="row-track" style="top:41px"></div><div class="row-label" style="top:83px">RUN #33<em>1 fragment · 604 MB</em></div><div class="row-track" style="top:82px"></div><div class="row-label" style="top:124px">RUN #31<em>2 fragments · 1056 MB</em></div><div class="row-track" style="top:123px"></div><div class="row-label" style="top:165px">RUN #16<em>2 fragments · 1124 MB</em></div><div class="row-track" style="top:164px"></div><div class="row-label" style="top:206px">RUN #35<em>2 fragments · 2000 MB</em></div><div class="row-track" style="top:205px"></div><div class="row-label" style="top:247px">WRITING<em>ICS output</em></div><div class="row-track" style="top:246px"></div></div><div class="sst-layer"><div class="sst" data-depth="0" title="SSTable #41&#10;307 MB / 307 rows&#10;keys 6–19832&#10;written at t95&#10;run #34, fragment 0" style="--tier-c: var(--cv-t0); top: 3px; left: 0%; width: 14.95%;">307</div><div class="sst" data-depth="0" title="SSTable #44&#10;313 MB / 313 rows&#10;keys 19–19339&#10;written at t100&#10;run #36, fragment 0" style="--tier-c: var(--cv-t0); top: 44px; left: 0%; width: 15.25%;">313</div><div class="sst" data-depth="1" title="SSTable #42&#10;604 MB / 604 rows&#10;keys 3–19991&#10;written at t95&#10;run #33, fragment 0" style="--tier-c: var(--cv-t1); top: 85px; left: 0%; width: 29.8%;">604</div><div class="sst compacting" data-depth="2" title="SSTable #39&#10;1000 MB / 1000 rows&#10;keys 2368–17623&#10;written at t92&#10;run #31, fragment 1" style="--tier-c: var(--cv-t2); top: 126px; left: 0%; width: 49.6%;">1000</div><div class="sst compacting" data-depth="2" title="SSTable #40&#10;56 MB / 56 rows&#10;keys 17673–19976&#10;written at t92&#10;run #31, fragment 2" style="--tier-c: var(--cv-t2); top: 126px; left: 50%; width: 2.4%;">56</div><div class="sst compacting" data-depth="2" title="SSTable #20&#10;1000 MB / 1000 rows&#10;keys 2334–15388&#10;written at t52&#10;run #16, fragment 1" style="--tier-c: var(--cv-t2); top: 167px; left: 0%; width: 49.6%;">1000</div><div class="sst compacting" data-depth="2" title="SSTable #21&#10;124 MB / 124 rows&#10;keys 15406–19941&#10;written at t52&#10;run #16, fragment 2" style="--tier-c: var(--cv-t2); top: 167px; left: 50%; width: 5.8%;">124</div><div class="sst" data-depth="3" title="SSTable #43&#10;1000 MB / 1000 rows&#10;keys 0–1535&#10;written at t99&#10;run #35, fragment 0" style="--tier-c: var(--cv-t3); top: 208px; left: 0%; width: 49.6%;">1000</div><div class="sst" data-depth="3" title="SSTable #45&#10;1000 MB / 1000 rows&#10;keys 1537–3005&#10;written at t101&#10;run #35, fragment 1" style="--tier-c: var(--cv-t3); top: 208px; left: 50%; width: 49.6%;">1000</div><div class="sst output" data-depth="3" title="Compaction output being written: 948 MB so far" style="--tier-c: var(--cv-t3); top: 249px; left: 0%; width: 47%;">948 MB</div></div></div>
     </div>
     <figcaption><b>Tick 103.</b> The same compaction. ICS deleted one fragment from each input run. 948 MB of output is written. 6352 MB on disk. <a href="https://tzach.github.io/compaction-viz/?strategy=ics&amp;workload=hot&amp;tick=103" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

Thus, ICS has low write amplification and a small temporary space overhead. ICS
is also the only strategy where a major compaction does not need 50% free disk
space.

The space amplification goal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Runs and fragments solve the temporary space problem. They do not solve a second
problem: **duplicate data across tiers**. With an overwrite workload, the same
key can be in many tiers at the same time. Only the newest version is live. The
other versions use space until a compaction merges those tiers. The
``space_amplification_goal`` (SAG) option, added in ICS 2.0, solves this problem.

With SAG on, the largest tier behaves like a level in leveled compaction: it has
no duplicate data. The smaller tiers keep their usual behavior: SSTables collect
in them, so they stay write-optimized. When the space amplification is more than
the goal, ICS starts a **cross-tier compaction**. This compaction merges the two
largest tiers. With a goal of 1.5, the cross-tier compaction starts when the
second-largest tier is half the size of the largest tier.

The diagram below shows ICS with SAG set to 1.25, after 1500 ticks of the
overwrite-heavy workload. The same workload with SAG off has a space
amplification of 1.90×, a write amplification of 5.00×, and 26,366 MB on disk.

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="ICS with SAG 1.25 after 1500 ticks">
       <div class="cv-snap-head">SSTables on disk <span>— 10 runs</span></div>
       <div class="cv-disk" style="height:458px"><div class="lane-layer"><div class="row-label" style="top:1px">RUN #498<em>1 fragment · 310 MB</em></div><div class="row-track" style="top:0px"></div><div class="row-label" style="top:42px">RUN #500<em>1 fragment · 311 MB</em></div><div class="row-track" style="top:41px"></div><div class="row-label" style="top:83px">RUN #496<em>1 fragment · 312 MB</em></div><div class="row-track" style="top:82px"></div><div class="row-label" style="top:124px">RUN #499<em>1 fragment · 312 MB</em></div><div class="row-track" style="top:123px"></div><div class="row-label" style="top:165px">RUN #501<em>1 fragment · 312 MB</em></div><div class="row-track" style="top:164px"></div><div class="row-label" style="top:206px">RUN #502<em>1 fragment · 314 MB</em></div><div class="row-track" style="top:205px"></div><div class="row-label" style="top:247px">RUN #492<em>1 fragment · 487 MB</em></div><div class="row-track" style="top:246px"></div><div class="row-label" style="top:288px">RUN #495<em>1 fragment · 883 MB</em></div><div class="row-track" style="top:287px"></div><div class="row-label" style="top:329px">RUN #478<em>5 fragments · 4342 MB</em></div><div class="row-track" style="top:328px"></div><div class="row-label" style="top:370px">RUN #497<em>10 fragments · 10000 MB</em></div><div class="row-track" style="top:369px"></div><div class="row-label" style="top:411px">WRITING<em>ICS output</em></div><div class="row-track" style="top:410px"></div></div><div class="sst-layer"><div class="sst" data-depth="0" title="SSTable #835&#10;310 MB / 310 rows&#10;keys 20–19769&#10;written at t1480&#10;run #498, fragment 0" style="--tier-c: var(--cv-t0); top: 3px; left: 0%; width: 2.7%;">310</div><div class="sst" data-depth="0" title="SSTable #841&#10;311 MB / 311 rows&#10;keys 6–19714&#10;written at t1490&#10;run #500, fragment 0" style="--tier-c: var(--cv-t0); top: 44px; left: 0%; width: 2.71%;">311</div><div class="sst" data-depth="0" title="SSTable #833&#10;312 MB / 312 rows&#10;keys 46–19903&#10;written at t1475&#10;run #496, fragment 0" style="--tier-c: var(--cv-t0); top: 85px; left: 0%; width: 2.72%;">312</div><div class="sst" data-depth="0" title="SSTable #838&#10;312 MB / 312 rows&#10;keys 0–19858&#10;written at t1485&#10;run #499, fragment 0" style="--tier-c: var(--cv-t0); top: 126px; left: 0%; width: 2.72%;">312</div><div class="sst" data-depth="0" title="SSTable #844&#10;312 MB / 312 rows&#10;keys 11–19262&#10;written at t1495&#10;run #501, fragment 0" style="--tier-c: var(--cv-t0); top: 167px; left: 0%; width: 2.72%;">312</div><div class="sst" data-depth="0" title="SSTable #847&#10;314 MB / 314 rows&#10;keys 10–19791&#10;written at t1500&#10;run #502, fragment 0" style="--tier-c: var(--cv-t0); top: 208px; left: 0%; width: 2.74%;">314</div><div class="sst compacting" data-depth="1" title="SSTable #831&#10;487 MB / 487 rows&#10;keys 9943–19991&#10;written at t1471&#10;run #492, fragment 3" style="--tier-c: var(--cv-t1); top: 249px; left: 0%; width: 4.47%;">487</div><div class="sst" data-depth="2" title="SSTable #832&#10;883 MB / 883 rows&#10;keys 3–19965&#10;written at t1474&#10;run #495, fragment 0" style="--tier-c: var(--cv-t2); top: 290px; left: 0%; width: 8.43%;">883</div><div class="sst compacting" data-depth="3" title="SSTable #812&#10;1000 MB / 1000 rows&#10;keys 12532–14175&#10;written at t1440&#10;run #478, fragment 9" style="--tier-c: var(--cv-t3); top: 331px; left: 0%; width: 9.6%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #813&#10;1000 MB / 1000 rows&#10;keys 14176–15899&#10;written at t1442&#10;run #478, fragment 10" style="--tier-c: var(--cv-t3); top: 331px; left: 10%; width: 9.6%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #815&#10;1000 MB / 1000 rows&#10;keys 15900–17605&#10;written at t1445&#10;run #478, fragment 11" style="--tier-c: var(--cv-t3); top: 331px; left: 20%; width: 9.6%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #816&#10;1000 MB / 1000 rows&#10;keys 17606–19392&#10;written at t1447&#10;run #478, fragment 12" style="--tier-c: var(--cv-t3); top: 331px; left: 30%; width: 9.6%;">1000</div><div class="sst compacting" data-depth="3" title="SSTable #817&#10;342 MB / 342 rows&#10;keys 19396–19999&#10;written at t1448&#10;run #478, fragment 13" style="--tier-c: var(--cv-t3); top: 331px; left: 40%; width: 3.02%;">342</div><div class="sst" data-depth="4" title="SSTable #834&#10;1000 MB / 1000 rows&#10;keys 0–999&#10;written at t1478&#10;run #497, fragment 0" style="--tier-c: var(--cv-t4); top: 372px; left: 0%; width: 9.6%;">1000</div><div class="sst" data-depth="4" title="SSTable #836&#10;1000 MB / 1000 rows&#10;keys 1000–1999&#10;written at t1480&#10;run #497, fragment 1" style="--tier-c: var(--cv-t4); top: 372px; left: 10%; width: 9.6%;">1000</div><div class="sst" data-depth="4" title="SSTable #837&#10;1000 MB / 1000 rows&#10;keys 2000–2999&#10;written at t1483&#10;run #497, fragment 2" style="--tier-c: var(--cv-t4); top: 372px; left: 20%; width: 9.6%;">1000</div><div class="sst" data-depth="4" title="SSTable #839&#10;1000 MB / 1000 rows&#10;keys 3000–3999&#10;written at t1485&#10;run #497, fragment 3" style="--tier-c: var(--cv-t4); top: 372px; left: 30%; width: 9.6%;">1000</div><div class="sst" data-depth="4" title="SSTable #840&#10;1000 MB / 1000 rows&#10;keys 4000–5619&#10;written at t1488&#10;run #497, fragment 4" style="--tier-c: var(--cv-t4); top: 372px; left: 40%; width: 9.6%;">1000</div><div class="sst" data-depth="4" title="SSTable #842&#10;1000 MB / 1000 rows&#10;keys 5620–7280&#10;written at t1490&#10;run #497, fragment 5" style="--tier-c: var(--cv-t4); top: 372px; left: 50%; width: 9.6%;">1000</div><div class="sst" data-depth="4" title="SSTable #843&#10;1000 MB / 1000 rows&#10;keys 7281–8939&#10;written at t1492&#10;run #497, fragment 6" style="--tier-c: var(--cv-t4); top: 372px; left: 60%; width: 9.6%;">1000</div><div class="sst" data-depth="4" title="SSTable #845&#10;1000 MB / 1000 rows&#10;keys 8940–10567&#10;written at t1495&#10;run #497, fragment 7" style="--tier-c: var(--cv-t4); top: 372px; left: 70%; width: 9.6%;">1000</div><div class="sst" data-depth="4" title="SSTable #846&#10;1000 MB / 1000 rows&#10;keys 10569–12223&#10;written at t1497&#10;run #497, fragment 8" style="--tier-c: var(--cv-t4); top: 372px; left: 80%; width: 9.6%;">1000</div><div class="sst" data-depth="4" title="SSTable #848&#10;1000 MB / 1000 rows&#10;keys 12224–13854&#10;written at t1500&#10;run #497, fragment 9" style="--tier-c: var(--cv-t4); top: 372px; left: 90%; width: 9.6%;">1000</div><div class="sst output" data-depth="3" title="Compaction output being written: 405 MB so far" style="--tier-c: var(--cv-t3); top: 413px; left: 0%; width: 3.65%;">405 MB</div></div></div>
     </div>
     <figcaption><b>SAG 1.25, tick 1500.</b> Space amplification is 1.30×. Write amplification is 5.74×. The disk holds 17,988 MB, not 26,366 MB, for the same live data. <a href="https://tzach.github.io/compaction-viz/?strategy=ics&amp;workload=hot&amp;sag=1.25&amp;tick=1500" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

A lower goal uses less disk but causes more compaction, so write amplification
increases. The `ICS 2.0 announcement
<https://www.scylladb.com/2021/04/28/incremental-compaction-2-0-a-revolutionary-space-and-write-optimized-compaction-strategy/>`__
gives this procedure:

#. Set SAG to 1.75.
#. Decrease it in steps of 0.25, and monitor write amplification after each step.
#. Do not set it below 1.25.

ICS with SAG does not replace leveled compaction in all cases. If your overwrites
have high time locality (you often update data that you wrote recently), the
write amplification of LCS can be acceptable. If LCS causes too much write
amplification for your workload, ICS with SAG is a better choice.

Leveled compaction (LCS)
------------------------

Leveled compaction (LCS) uses a different structure. It uses SSTables of a fixed
size (``sstable_size_in_mb``, default 160 MB), arranged in levels:

* **L0** holds new SSTables from flushes. Their key ranges can overlap.
* **L1** holds a run of about 10 SSTables (1.6 GB). Their key ranges do not
  overlap.
* **L2** holds about 100 SSTables (16 GB). Each level is 10 times larger than the
  level before it.

From L1 down, a key is in at most one SSTable per level. Thus, a read touches the
L0 files plus at most one SSTable per level.

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="LCS: L0 to L1">
       <div class="cv-snap-head">SSTables on disk <span>— 1 level</span></div>
       <div class="cv-disk" style="height:89px"><div class="lane-layer"><div class="row-label" style="top:1px">L0<em>4 overlapping</em></div><div class="row-track" style="top:0px"></div><div class="row-label" style="top:42px">L1<em>0 / 1600 MB</em></div><div class="row-track keyspace" style="top:41px"></div></div><div class="sst-layer"><div class="sst compacting" data-depth="0" title="SSTable #2&#10;256 MB / 256 rows&#10;keys 20–19843&#10;written at t9&#10;level L0" style="--tier-c: var(--cv-t0); top: 3px; left: 0%; width: 20.827%;">256</div><div class="sst compacting" data-depth="0" title="SSTable #3&#10;316 MB / 316 rows&#10;keys 42–19941&#10;written at t14&#10;level L0" style="--tier-c: var(--cv-t0); top: 3px; left: 21.227%; width: 25.802%;">316</div><div class="sst compacting" data-depth="0" title="SSTable #4&#10;317 MB / 317 rows&#10;keys 44–19952&#10;written at t19&#10;level L0" style="--tier-c: var(--cv-t0); top: 3px; left: 47.43%; width: 25.885%;">317</div><div class="sst compacting" data-depth="0" title="SSTable #1&#10;317 MB / 317 rows&#10;keys 103–19943&#10;written at t5&#10;level L0" style="--tier-c: var(--cv-t0); top: 3px; left: 73.715%; width: 25.885%;">317</div></div></div>
     </div>
     <figcaption><b>Tick 19.</b> L0 has 4 overlapping SSTables. LCS selects all of them to merge into L1. L1 is empty, so no L1 SSTables join this merge. <a href="https://tzach.github.io/compaction-viz/?strategy=lcs&amp;workload=uniform&amp;sstable_size=160&amp;tick=19" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="LCS: the L1 run">
       <div class="cv-snap-head">SSTables on disk <span>— 1 level</span></div>
       <div class="cv-disk" style="height:89px"><div class="lane-layer"><div class="row-label" style="top:1px">L0<em>0 overlapping</em></div><div class="row-track" style="top:0px"></div><div class="row-label" style="top:42px">L1<em>1182 / 1600 MB</em></div><div class="row-track keyspace" style="top:41px"></div></div><div class="sst-layer"><div class="sst" data-depth="1" title="SSTable #5&#10;160 MB / 160 rows&#10;keys 20–2752&#10;written at t20&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 0%; width: 13.411%;">160</div><div class="sst" data-depth="1" title="SSTable #6&#10;160 MB / 160 rows&#10;keys 2765–5450&#10;written at t20&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 13.771%; width: 13.175%;">160</div><div class="sst" data-depth="1" title="SSTable #7&#10;160 MB / 160 rows&#10;keys 5492–8018&#10;written at t20&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 27.452%; width: 12.377%;">160</div><div class="sst" data-depth="1" title="SSTable #8&#10;160 MB / 160 rows&#10;keys 8039–10551&#10;written at t21&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 40.23%; width: 12.307%;">160</div><div class="sst" data-depth="1" title="SSTable #9&#10;160 MB / 160 rows&#10;keys 10556–13159&#10;written at t21&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 52.857%; width: 12.764%;">160</div><div class="sst" data-depth="1" title="SSTable #10&#10;160 MB / 160 rows&#10;keys 13178–16064&#10;written at t21&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 66.011%; width: 14.184%;">160</div><div class="sst" data-depth="1" title="SSTable #11&#10;160 MB / 160 rows&#10;keys 16129–18919&#10;written at t22&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 80.816%; width: 13.702%;">160</div><div class="sst" data-depth="1" title="SSTable #12&#10;62 MB / 62 rows&#10;keys 18939–19952&#10;written at t22&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 94.913%; width: 4.787%;">62</div></div></div>
     </div>
     <figcaption><b>Tick 22.</b> L1 is now a run of 160 MB SSTables with key ranges that do not overlap. Read amplification is 1. <a href="https://tzach.github.io/compaction-viz/?strategy=lcs&amp;workload=uniform&amp;sstable_size=160&amp;tick=22" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

When L1 becomes larger than its target size, LCS moves one SSTable from L1 into
L2. LCS merges it with each L2 SSTable that has an overlapping key range. This
rewrite is the source of the high write amplification of LCS: the same data is
rewritten each time it moves one level down.

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="LCS: L1 to L2">
       <div class="cv-snap-head">SSTables on disk <span>— 3 levels</span></div>
       <div class="cv-disk" style="height:130px"><div class="lane-layer"><div class="row-label" style="top:1px">L0<em>3 overlapping</em></div><div class="row-track" style="top:0px"></div><div class="row-label" style="top:42px">L1<em>2080 / 1600 MB</em></div><div class="row-track keyspace" style="top:41px"></div><div class="row-label" style="top:83px">L2<em>3356 / 16000 MB</em></div><div class="row-track keyspace" style="top:82px"></div></div><div class="sst-layer"><div class="sst" data-depth="0" title="SSTable #114&#10;318 MB / 318 rows&#10;keys 8–19853&#10;written at t103&#10;level L0" style="--tier-c: var(--cv-t0); top: 3px; left: 0%; width: 33.003%;">318</div><div class="sst" data-depth="0" title="SSTable #118&#10;315 MB / 315 rows&#10;keys 22–19987&#10;written at t108&#10;level L0" style="--tier-c: var(--cv-t0); top: 3px; left: 33.403%; width: 32.688%;">315</div><div class="sst" data-depth="0" title="SSTable #106&#10;319 MB / 319 rows&#10;keys 84–19997&#10;written at t98&#10;level L0" style="--tier-c: var(--cv-t0); top: 3px; left: 66.492%; width: 33.108%;">319</div><div class="sst compacting" data-depth="1" title="SSTable #94&#10;160 MB / 160 rows&#10;keys 8–934&#10;written at t94&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 0.04%; width: 4.335%;">160</div><div class="sst" data-depth="1" title="SSTable #95&#10;160 MB / 160 rows&#10;keys 937–2002&#10;written at t94&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 4.685%; width: 5.03%;">160</div><div class="sst" data-depth="1" title="SSTable #96&#10;160 MB / 160 rows&#10;keys 2006–2941&#10;written at t94&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 10.03%; width: 4.38%;">160</div><div class="sst" data-depth="1" title="SSTable #97&#10;160 MB / 160 rows&#10;keys 2949–3964&#10;written at t95&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 14.745%; width: 4.78%;">160</div><div class="sst" data-depth="1" title="SSTable #98&#10;160 MB / 160 rows&#10;keys 3966–4949&#10;written at t95&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 19.83%; width: 4.62%;">160</div><div class="sst" data-depth="1" title="SSTable #99&#10;160 MB / 160 rows&#10;keys 4951–5923&#10;written at t95&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 24.755%; width: 4.565%;">160</div><div class="sst" data-depth="1" title="SSTable #100&#10;160 MB / 160 rows&#10;keys 5934–7252&#10;written at t96&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 29.67%; width: 6.295%;">160</div><div class="sst" data-depth="1" title="SSTable #101&#10;160 MB / 160 rows&#10;keys 7254–8633&#10;written at t96&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 36.27%; width: 6.6%;">160</div><div class="sst" data-depth="1" title="SSTable #102&#10;160 MB / 160 rows&#10;keys 8636–10096&#10;written at t96&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 43.18%; width: 7.005%;">160</div><div class="sst" data-depth="1" title="SSTable #103&#10;160 MB / 160 rows&#10;keys 10101–11557&#10;written at t97&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 50.505%; width: 6.985%;">160</div><div class="sst" data-depth="1" title="SSTable #104&#10;160 MB / 160 rows&#10;keys 11561–12153&#10;written at t97&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 57.805%; width: 2.665%;">160</div><div class="sst" data-depth="1" title="SSTable #105&#10;160 MB / 160 rows&#10;keys 12154–14433&#10;written at t97&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 60.77%; width: 11.1%;">160</div><div class="sst" data-depth="1" title="SSTable #107&#10;160 MB / 160 rows&#10;keys 14437–16943&#10;written at t98&#10;level L1" style="--tier-c: var(--cv-t1); top: 44px; left: 72.185%; width: 12.235%;">160</div><div class="sst compacting" data-depth="2" title="SSTable #32&#10;160 MB / 160 rows&#10;keys 0–1405&#10;written at t44&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 0%; width: 6.73%;">160</div><div class="sst" data-depth="2" title="SSTable #34&#10;160 MB / 160 rows&#10;keys 1415–2877&#10;written at t46&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 7.075%; width: 7.015%;">160</div><div class="sst" data-depth="2" title="SSTable #35&#10;160 MB / 160 rows&#10;keys 2879–4342&#10;written at t48&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 14.395%; width: 7.02%;">160</div><div class="sst" data-depth="2" title="SSTable #37&#10;160 MB / 160 rows&#10;keys 4347–5702&#10;written at t50&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 21.735%; width: 6.48%;">160</div><div class="sst" data-depth="2" title="SSTable #57&#10;160 MB / 160 rows&#10;keys 5782–6747&#10;written at t63&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 28.91%; width: 4.53%;">160</div><div class="sst" data-depth="2" title="SSTable #59&#10;160 MB / 160 rows&#10;keys 6750–7765&#10;written at t65&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 33.75%; width: 4.78%;">160</div><div class="sst" data-depth="2" title="SSTable #60&#10;160 MB / 160 rows&#10;keys 7782–8745&#10;written at t67&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 38.91%; width: 4.52%;">160</div><div class="sst" data-depth="2" title="SSTable #62&#10;160 MB / 160 rows&#10;keys 8750–9725&#10;written at t69&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 43.75%; width: 4.58%;">160</div><div class="sst" data-depth="2" title="SSTable #63&#10;160 MB / 160 rows&#10;keys 9726–10740&#10;written at t71&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 48.63%; width: 4.775%;">160</div><div class="sst" data-depth="2" title="SSTable #64&#10;160 MB / 160 rows&#10;keys 10744–11625&#10;written at t73&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 53.72%; width: 4.11%;">160</div><div class="sst" data-depth="2" title="SSTable #85&#10;160 MB / 160 rows&#10;keys 12309–13056&#10;written at t82&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 61.545%; width: 3.44%;">160</div><div class="sst" data-depth="2" title="SSTable #87&#10;160 MB / 160 rows&#10;keys 13059–13798&#10;written at t84&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 65.295%; width: 3.4%;">160</div><div class="sst" data-depth="2" title="SSTable #88&#10;160 MB / 160 rows&#10;keys 13801–14582&#10;written at t86&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 69.005%; width: 3.61%;">160</div><div class="sst" data-depth="2" title="SSTable #89&#10;160 MB / 160 rows&#10;keys 14596–15313&#10;written at t88&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 72.98%; width: 3.29%;">160</div><div class="sst" data-depth="2" title="SSTable #91&#10;160 MB / 160 rows&#10;keys 15316–16013&#10;written at t90&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 76.58%; width: 3.19%;">160</div><div class="sst" data-depth="2" title="SSTable #92&#10;160 MB / 160 rows&#10;keys 16015–16849&#10;written at t92&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 80.075%; width: 3.875%;">160</div><div class="sst" data-depth="2" title="SSTable #113&#10;160 MB / 160 rows&#10;keys 16946–17534&#10;written at t101&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 84.73%; width: 2.645%;">160</div><div class="sst" data-depth="2" title="SSTable #115&#10;160 MB / 160 rows&#10;keys 17535–18147&#10;written at t103&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 87.675%; width: 2.765%;">160</div><div class="sst" data-depth="2" title="SSTable #116&#10;160 MB / 160 rows&#10;keys 18150–18750&#10;written at t105&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 90.75%; width: 2.705%;">160</div><div class="sst" data-depth="2" title="SSTable #117&#10;160 MB / 160 rows&#10;keys 18757–19404&#10;written at t107&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 93.785%; width: 2.94%;">160</div><div class="sst" data-depth="2" title="SSTable #119&#10;156 MB / 156 rows&#10;keys 19405–19999&#10;written at t109&#10;level L2" style="--tier-c: var(--cv-t2); top: 85px; left: 97.025%; width: 2.675%;">156</div></div></div>
     </div>
     <figcaption><b>Tick 110.</b> L1 holds 2080 MB, more than its 1600 MB target. LCS moves one L1 SSTable and the one L2 SSTable that overlaps it (outlined) into L2. <a href="https://tzach.github.io/compaction-viz/?strategy=lcs&amp;workload=uniform&amp;sstable_size=160&amp;tick=110" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

If L0 collects 32 or more SSTables, LCS cannot keep up. It then merges L0
SSTables of similar size, to decrease the number of files quickly.

LCS has low space amplification and low read amplification. It has the highest
write amplification. Use it for read-heavy workloads, or for overwrite workloads
with high time locality.

Time-window compaction (TWCS)
-----------------------------

Time-window compaction (TWCS) is for time-series data. It puts SSTables into
**time windows**, by the time of the newest write in each SSTable. You set the
window with ``compaction_window_size`` and ``compaction_window_unit``. The default
is 1 day. In the simulator, one tick is one hour, so one window is 24 ticks.

* In the current window, TWCS merges SSTables of similar size.
* When a window closes, TWCS compacts all its SSTables into one.
* TWCS never merges SSTables from different windows.

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="TWCS seals a window">
       <div class="cv-snap-head">SSTables on disk <span>— 2 windows</span></div>
       <div class="cv-disk" style="height:89px"><div class="lane-layer"><div class="row-label" style="top:1px">WINDOW 1 · NOW<em>t24–47 · 256 MB</em></div><div class="row-track" style="top:0px"></div><div class="row-label" style="top:42px">WINDOW 0<em>t0–23 · 1280 MB</em></div><div class="row-track" style="top:41px"></div></div><div class="sst-layer"><div class="sst" data-depth="0" title="SSTable #9&#10;256 MB / 256 rows&#10;keys 1280–1535&#10;written at t24&#10;window 1" style="--tier-c: var(--cv-t0); top: 3px; left: 0%; width: 19.6%;">256</div><div class="sst compacting" data-depth="1" title="SSTable #7&#10;256 MB / 256 rows&#10;keys 1024–1279&#10;written at t20&#10;window 0" style="--tier-c: var(--cv-t1); top: 44px; left: 0%; width: 19.6%;">256</div><div class="sst compacting" data-depth="1" title="SSTable #8&#10;1024 MB / 1024 rows&#10;keys 0–1023&#10;written at t20&#10;window 0" style="--tier-c: var(--cv-t1); top: 44px; left: 20%; width: 79.6%;">1024</div></div></div>
     </div>
     <figcaption><b>Tick 24.</b> Window 0 (hours 0–23) is closed. TWCS merges its two SSTables into one. Window 1 starts to collect new flushes. <a href="https://tzach.github.io/compaction-viz/?strategy=twcs&amp;tick=24" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

The largest advantage of TWCS is expiry. In this workload, each row has a TTL of
96 hours. All the rows in an old window expire at approximately the same time.
When all the data in an SSTable has expired, TWCS deletes the full file. It does
not read or rewrite the data.

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="TWCS before expiry">
       <div class="cv-snap-head">SSTables on disk <span>— 5 windows</span></div>
       <div class="cv-disk" style="height:212px"><div class="lane-layer"><div class="row-label" style="top:1px">WINDOW 4 · NOW<em>t96–119 · 1280 MB</em></div><div class="row-track" style="top:0px"></div><div class="row-label" style="top:42px">WINDOW 3<em>t72–95 · 1536 MB</em></div><div class="row-track" style="top:41px"></div><div class="row-label" style="top:83px">WINDOW 2<em>t48–71 · 1536 MB</em></div><div class="row-track" style="top:82px"></div><div class="row-label" style="top:124px">WINDOW 1<em>t24–47 · 1536 MB</em></div><div class="row-track" style="top:123px"></div><div class="row-label" style="top:165px">WINDOW 0<em>t0–23 · 1280 MB</em></div><div class="row-track" style="top:164px"></div></div><div class="sst-layer"><div class="sst" data-depth="0" title="SSTable #49&#10;256 MB / 256 rows&#10;keys 6912–7167&#10;written at t112&#10;window 4" style="--tier-c: var(--cv-t0); top: 3px; left: 0%; width: 16.267%;">256</div><div class="sst" data-depth="0" title="SSTable #50&#10;1024 MB / 1024 rows&#10;keys 5888–6911&#10;written at t112&#10;window 4" style="--tier-c: var(--cv-t0); top: 3px; left: 16.667%; width: 66.267%;">1024</div><div class="sst" data-depth="1" title="SSTable #43&#10;1536 MB / 1536 rows&#10;keys 4352–5887&#10;written at t99&#10;window 3" style="--tier-c: var(--cv-t1); top: 44px; left: 0%; width: 99.6%;">1536</div><div class="sst" data-depth="2" title="SSTable #32&#10;1536 MB / 1536 rows&#10;keys 2816–4351&#10;written at t75&#10;window 2" style="--tier-c: var(--cv-t2); top: 85px; left: 0%; width: 99.6%;">1536</div><div class="sst" data-depth="3" title="SSTable #21&#10;1536 MB / 1536 rows&#10;keys 1280–2815&#10;written at t51&#10;window 1" style="--tier-c: var(--cv-t3); top: 126px; left: 0%; width: 99.6%;">1536</div><div class="sst" data-depth="4" title="SSTable #10&#10;1280 MB / 1280 rows&#10;keys 0–1279&#10;written at t27&#10;window 0" style="--tier-c: var(--cv-t4); top: 167px; left: 0%; width: 82.933%;">1280</div></div></div>
     </div>
     <figcaption><b>Tick 115.</b> Five windows. Window 0 is still on disk, but most of its data has expired. Space amplification is 1.20×. <a href="https://tzach.github.io/compaction-viz/?strategy=twcs&amp;tick=115" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

.. raw:: html

   <figure class="cv-fig">
     <div class="cv-snap" role="img" aria-label="TWCS drops an expired window">
       <div class="cv-snap-head">SSTables on disk <span>— 4 windows</span></div>
       <div class="cv-disk" style="height:171px"><div class="lane-layer"><div class="row-label" style="top:1px">WINDOW 4 · NOW<em>t96–119 · 1536 MB</em></div><div class="row-track" style="top:0px"></div><div class="row-label" style="top:42px">WINDOW 3<em>t72–95 · 1536 MB</em></div><div class="row-track" style="top:41px"></div><div class="row-label" style="top:83px">WINDOW 2<em>t48–71 · 1536 MB</em></div><div class="row-track" style="top:82px"></div><div class="row-label" style="top:124px">WINDOW 1<em>t24–47 · 1536 MB</em></div><div class="row-track" style="top:123px"></div></div><div class="sst-layer"><div class="sst compacting" data-depth="0" title="SSTable #49&#10;256 MB / 256 rows&#10;keys 6912–7167&#10;written at t112&#10;window 4" style="--tier-c: var(--cv-t0); top: 3px; left: 0%; width: 16.267%;">256</div><div class="sst" data-depth="0" title="SSTable #50&#10;1024 MB / 1024 rows&#10;keys 5888–6911&#10;written at t112&#10;window 4" style="--tier-c: var(--cv-t0); top: 3px; left: 16.667%; width: 66.267%;">1024</div><div class="sst compacting" data-depth="0" title="SSTable #51&#10;256 MB / 256 rows&#10;keys 7168–7423&#10;written at t116&#10;window 4" style="--tier-c: var(--cv-t0); top: 3px; left: 83.333%; width: 16.267%;">256</div><div class="sst" data-depth="1" title="SSTable #43&#10;1536 MB / 1536 rows&#10;keys 4352–5887&#10;written at t99&#10;window 3" style="--tier-c: var(--cv-t1); top: 44px; left: 0%; width: 99.6%;">1536</div><div class="sst" data-depth="2" title="SSTable #32&#10;1536 MB / 1536 rows&#10;keys 2816–4351&#10;written at t75&#10;window 2" style="--tier-c: var(--cv-t2); top: 85px; left: 0%; width: 99.6%;">1536</div><div class="sst" data-depth="3" title="SSTable #21&#10;1536 MB / 1536 rows&#10;keys 1280–2815&#10;written at t51&#10;window 1" style="--tier-c: var(--cv-t3); top: 126px; left: 0%; width: 99.6%;">1536</div></div></div>
     </div>
     <figcaption><b>Tick 116.</b> All data in window 0 has expired. TWCS deletes the file, with no rewrite. Space amplification goes back to 1.00×. <a href="https://tzach.github.io/compaction-viz/?strategy=twcs&amp;tick=116" target="_blank" rel="noopener">Open in the simulator</a></figcaption>
   </figure>

TWCS works well only when you obey these rules:

* Use one TTL for all the data in the table. An SSTable stays on disk until all
  of its data has expired.
* Do not write data with explicit old timestamps.
* Do not mix old and new data in the same SSTable. Read repair and late repairs
  can cause this. Run repairs frequently.
* Do not use TWCS for data that you overwrite. New windows continue to open, and
  the old versions stay in old windows.

Which strategy to use
---------------------

.. list-table::
   :header-rows: 1
   :widths: 12 22 12 16 38

   * - Strategy
     - Space amp.
     - Write amp.
     - Read amp.
     - Use it for
   * - **ICS**
     - Low temporary overhead
     - Low
     - Moderate
     - Write-heavy and mixed workloads. Add SAG for overwrite workloads.
   * - **LCS**
     - Low
     - High
     - Low
     - Read-heavy workloads, overwrites with high time locality
   * - **TWCS**
     - Low if data expires in order
     - Very low
     - Low for recent data
     - Time-series data with one TTL

.. caution::

   A change of strategy, or of strategy options, can start a large amount of
   compaction. For example, if you increase ``sstable_size_in_mb`` for LCS, the
   lower levels can hold all the data, and the higher levels do not get
   compacted. Plan the change and monitor it.

To monitor compaction, use ``nodetool compactionstats``,
``nodetool compactionhistory``, and the compaction panels in the ScyllaDB
Monitoring Stack.

Try it yourself
---------------

Open the `simulator <https://tzach.github.io/compaction-viz/>`__ and change one setting at a time. Some tests to
try:

* Select ICS with the overwrite-heavy workload. Set SAG to 1.25, 1.5 and 2.
  Watch the space and write amplification lines in the chart.
* Select LCS with the uniform workload. Watch how each level fills up and pushes
  data into the next level.
* Select TWCS, then change the workload back to overwrite-heavy. Watch the space
  amplification increase.

To share a state, click **Share**. The link opens the simulator paused at the
same tick with the same settings.

More information
----------------

* `Compaction <https://docs.scylladb.com/manual/stable/kb/compaction.html>`__ in
  the ScyllaDB documentation
* `Incremental Compaction 2.0: A Revolutionary Space and Write Optimized
  Compaction Strategy
  <https://www.scylladb.com/2021/04/28/incremental-compaction-2-0-a-revolutionary-space-and-write-optimized-compaction-strategy/>`__
* `Compaction simulator source <https://github.com/tzach/compaction-viz>`__
