# ScyllaDB Incremental Repair Visualizer

An interactive, single-file visualizer of ScyllaDB's **incremental repair** — built to make one
idea concrete: a repair round reads only the SSTables that no earlier repair has verified, and
skips the rest outright.

Three replicas hold one tablet. Writes run on their own from the moment the page opens — pause
them whenever you like — so the unrepaired lane keeps filling the way it does in production. Run a
repair and watch it read the unrepaired SSTables, transfer the rows that differ, stamp everything
it read as repaired, and bump `sstables_repaired_at`. Run it again and the second round skips what
the first one verified — the side panel puts the avoided I/O in numbers.

**Disclaimer:** An independent, educational visualizer — not an official ScyllaDB product and not
100% behaviorally accurate to real ScyllaDB internals. Not affiliated with or endorsed by
ScyllaDB, Inc.

## What it shows

- **Three SSTable classifications, kept apart.** Every replica's SSTables sit in one of three
  lanes — unrepaired, repairing, repaired — matching the three logical compaction groups
  ScyllaDB keeps (`replica::repair_sstable_classification`).
- **The skip decision.** An SSTable counts as repaired only when
  `repaired_at != 0 && repaired_at <= sstables_repaired_at` (`repair::is_repaired`). Cards that
  fail the test are read; cards that pass are marked SKIPPED and never opened.
- **The five phases of a round.** Select SSTables → exchange row hashes → transfer only the rows
  that differ → write them into new SSTables → stamp them and advance the tablet's counter.
- **The three incremental modes**, as passed to `nodetool cluster repair --incremental-mode`:
  - `incremental` — read only unrepaired data, then update the markers.
  - `full` — read every SSTable, still update the markers.
  - `disabled` — classic repair: read everything, read and write no markers at all.
- **Writes keep flowing during a repair.** Bursts keep landing mid-round, and the SSTables they
  flush are not part of the running session — they stay unrepaired and wait for the next round.
- **Separate compaction.** Compact merges within the repaired group and within the unrepaired
  group, never across them — the space-amplification tradeoff that makes short repair intervals
  worth it.
- **The payoff, in bytes.** Each round reports what it read, what it skipped, and what a full
  repair would have read instead.

## Controls

| Control | What it does |
| --- | --- |
| Incremental mode | `incremental`, `full` or `disabled` |
| Rows per write | How many rows each write burst produces (some are updates to existing rows) |
| Write every | How often the auto-writer fires, 1–10 s |
| Replica divergence | Chance a row misses a replica — a dropped mutation, a node that was down, an expired hint. This is the divergence repair has to fix. |
| Speed | Animation speed |
| ⏸ / ▶ | Tape-recorder transport for the writer — it starts running, so the button starts as pause |
| ⏺ | Record one burst by hand, on every replica that received rows |
| Run repair | Run one repair round |
| Compact | Compact each compaction group separately |
| Reset | Empty tablet, `sstables_repaired_at = 0` |

The transport — ⏸ / ▶ and ⏺ alike — stays live while a repair runs; `Run repair`, `Compact` and
`Reset` do not, since a tablet takes one repair session at a time.

The repair log is hidden by default so the page presents cleanly — **Show log** brings it back.
The tablet's `sstables_repaired_at` is on the stage header, above the lanes.

A first-visit guided tour walks through the core interactions; **Show tour** replays it.

## Running it

A static, dependency-free page. Open `index.html` in a browser — no build step, no server.

```bash
open index.html   # or just double-click it / drag into a browser
```

`scylladb-ds.css` is the ScyllaDB design system bundle, vendored so the page works offline and
follows your OS light/dark setting.

## Further reading

- [Incremental Repair](https://docs.scylladb.com/manual/stable/features/incremental-repair.html) — ScyllaDB docs
- Incremental repair needs tablets; it is not available for legacy vnode-based tables.
