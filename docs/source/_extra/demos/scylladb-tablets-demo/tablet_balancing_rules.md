# ScyllaDB Tablet Load Balancing — Executable Rule Set

A normative, simulator-ready description of the tablet migration/balancing algorithm as
implemented in `service/tablet_allocator.cc` (class `load_balancer`) and
`locator/load_sketch.hh` on branch `branch-2026.2`.

Every rule has an ID (`LB-x.y`) so a simulator can reference, toggle and test them
individually. Code anchors are given as `file:line` for verification.

---

## 0. What the algorithm is

The balancer is a **stateless incremental planner**. It never executes migrations; it
returns a *plan* — a small batch of migrations — computed from a snapshot of cluster
metadata. The driver (topology coordinator) executes the plan, and calls the planner
again. Balance is reached when the planner returns an empty plan.

- Entry point: `load_balancer::make_plan()` — `service/tablet_allocator.cc:1089`
- Per-DC planner: `make_plan(dc, rack)` — `service/tablet_allocator.cc:4141`
- Driver loop: `service/topology_coordinator.cc:2395`
- Reference simulator harness in-tree: `test/perf/tablet_load_balancing.cc:156`

**LB-0.1** The plan is an increment, not a complete schedule. A simulator must iterate
`plan = make_plan(); apply(plan)` until `plan.empty()`.

**LB-0.2** Sanity iteration cap for a simulator: `1 + 10 * total_tablet_count`
(`test/perf/tablet_load_balancing.cc:166`). Exceeding it is a non-convergence bug.

**LB-0.3** The optimization target is **equal storage utilization** — not equal tablet
count. Tablet count equalization is a special case obtained by declaring all tablets to
be of size `target_tablet_size` (see LB-2.5, capacity-based mode).

---

## 1. State model

### 1.1 Static topology

```
Node {
  id
  dc, rack
  shard_count          # >= 1, may differ per node
  disk_capacity        # bytes; see LB-2.1
  state                # normal | being_decommissioned | being_removed | left
  excluded             # bool ("dead, do not use as target")
  topology_request     # none | leave | remove
}
```

### 1.2 Tables and tablets

```
Table {
  id
  rf_per_dc            # numeric RF, or an explicit rack list (rack-based RF)
  tablet_count         # power of 2 unless arbitrary boundaries are enabled
  tablet_options       # min/max_tablet_count, min_per_shard_tablet_count,
                       # expected_data_size_in_gb, pow2_count
  resize_decision      # none | split(seq) | merge(seq)
}

Tablet {
  table, tablet_id
  replicas: [ (host, shard) ]      # len == sum(RF over DCs)
  transition: none | { kind, next_replicas, pending_replica, stage }
  size_per_replica[host]           # bytes, from load stats
}
```

**LB-1.1 (replica uniqueness)** All replicas of a tablet are on distinct nodes. Invariant
the planner must never break; assert it in the simulator after every applied plan.

**LB-1.2 (in-flight = done)** For every load computation, a tablet under transition is
accounted at `transition.next_replicas`, not `replicas`
(`service/tablet_allocator.cc:981`, `locator/load_sketch.hh:126`). Migrations are
assumed to succeed.

**LB-1.3 (shard validity)** `replica.shard < node.shard_count` for every replica. Violation
is an internal error, not a recoverable state.

---

## 2. The load metric

**LB-2.1 (node capacity)** In priority order (`service/tablet_allocator.cc:1204`):
1. If cluster feature `tablet_load_stats_v2` is off →
   `capacity = target_tablet_size * shard_count` (this makes load ≡ tablet count).
2. Else if per-node tablet stats exist and capacity-based mode is off →
   `capacity = effective_capacity` = *sum of all tablet sizes on the node + free disk
   space* (`locator/tablets.hh:513`). Note this excludes non-tablet disk usage, so a
   node with unrelated data on disk reports lower capacity.
3. Else `capacity = reported gross disk capacity`.
4. Else node has no capacity → see LB-3.6.

**LB-2.2 (shard capacity)** `shard_capacity = node_capacity / shard_count`
(integer division, `service/tablet_allocator.cc:1218`). Shards of a node are equal-capacity
by construction, even if real utilization differs.

**LB-2.3 (tablet size used for load)**
```
size(tablet, host) = max(reported_size(tablet, host), minimal_tablet_size)
```
`minimal_tablet_size` default = `target_tablet_size / 100` = 50 MiB
(`db/config.cc:1679`). This floor prevents empty tablets from being treated as free.

**LB-2.4 (load)**
```
load(x) = used_bytes(x) / capacity(x)          # x is a shard or a node
node.avg_load = node.used / node.capacity      # NOT the mean of shard loads
```
(`locator/load_sketch.hh:34`). Both are dimensionless disk-utilization fractions in
`[0, 1+]`.

**LB-2.5 (capacity-based mode)** If `force_capacity_based_balancing = true`, or the
`size_based_load_balancing` cluster feature is off, then: every tablet is assumed to be
exactly `target_tablet_size`, and *gross* capacity is used instead of `effective_capacity`
(`locator/load_sketch.hh:131`, `service/tablet_allocator.cc:1069`). This degenerates to
"equalize tablets per shard, weighted by shard capacity".

**LB-2.6 (missing data)** A node is "incomplete" if its capacity is unknown or any of its
tablet sizes is unknown (`locator/load_sketch.hh:265`). See LB-3.5/LB-3.6.

---

## 3. Scope and node-set selection

**LB-3.1 (per-DC independence)** Plans are made for each DC separately and merged; DC
plans execute in parallel (`service/tablet_allocator.cc:1097`). Tablets never move between
DCs during balancing.

**LB-3.2 (per-rack scope)** Planning is narrowed to a single rack (nodes of one rack only)
when any of: `rf_rack_valid_keyspaces`, `enforce_rack_list`, an ongoing rack-list
colocation, or a pending per-rack RF change (`service/tablet_allocator.cc:1098`).
Otherwise the scope is the whole DC.

**LB-3.3 (drained nodes)** A node is a *drain source* if:
`state ∈ {being_decommissioned, being_removed}`, or `topology_request ∈ {leave, remove}`,
or the node has `left` but still holds replicas (`service/tablet_allocator.cc:4190`,
`:4235`). Drained nodes are never migration targets.

**LB-3.4 (participants)** Otherwise a node participates only if `state == normal` and
`!excluded`. Excluded nodes are dropped entirely — they cannot receive tablets.

**LB-3.5 (skiplist)** Dead nodes (`skiplist`) are removed from the node set **only when
there is nothing to drain** (`service/tablet_allocator.cc:4208`). During a drain, dead
nodes stay in the set, because routing around them could overload the survivors.

**LB-3.6 (bail-outs)** With no nodes to drain, nodes with incomplete stats are dropped
(`:4293`). But if any *remaining, non-drained* node has unknown capacity, or any node
still has incomplete tablet stats (excluded-and-draining nodes excepted), the planner
returns an **empty plan for the whole DC** (`:4305`, `:4316`). Rationale: partial data
produces wrong load and destructive decisions.

**LB-3.7 (finished drain)** A drain source with `tablet_count == 0` is removed from the
node set (`:4263`).

**LB-3.8 (no targets)** If every node in scope is drained, each drain source gets a
`drain_failure` ("consider adding nodes or reducing RF") and no migrations are emitted
(`:4328`).

---

## 4. Candidate set construction

Per `(node, shard)` the planner builds candidate sets, keyed by table
(`service/tablet_allocator.cc:4402`).

**LB-4.1** A tablet replica on `(host, shard)` is a candidate iff the tablet has no active
transition and was not already scheduled in this same planning round (`_scheduled_tablets`).

**LB-4.2 (merge colocation unit)** If the table `needs_merge` and both sibling tablets are
co-located on the same `(host, shard)` and **neither** sibling is migrating, the pair is
inserted as a **single candidate** whose size is the sum of both. The pair then migrates
together, preserving colocation (`:4419`). If either sibling is migrating, neither is a
candidate this round (counted in `_migrating_candidates`).

**LB-4.3 (table-aware vs. flat)** With `use_table_aware_balancing = true` (default),
candidates are bucketed per table and scored per table (§6). With it false, a single
flat set per shard is used and the first element is taken with no scoring.

**LB-4.4 (aggregates)** Per round the planner also computes, for the scope:
`table_size[table]` = total bytes of that table's replicas, `total_capacity_storage` = sum
of capacities of non-drained nodes, `total_capacity_shards`, `total_capacity_nodes`.

---

## 5. Round structure

One `make_plan()` call, in order (`service/tablet_allocator.cc:1089`):

1. For each DC (or each `(DC, rack)`):
   a. **Inter-node plan** (§7) — only if there are drain sources, or balancing is
      enabled and the DC is not balanced (LB-8.1).
   b. **Intra-node plan** (§10) — if balancing is enabled.
   c. **RF-change plan** — only in rack scope with pending RF actions.
   d. **Merge-colocation plan** — only if (a)–(c) produced *nothing* and no rack-list
      colocation is ongoing (`:4496`).
2. Rack-list colocation plan (if applicable).
3. **Resize plan** (§11) — split/merge decisions, revocations, finalizations.
4. **Repair plan** — skipped if any resize finalization is pending (`:1122`).

**LB-5.1 (priority)** Inter-node migrations are planned before intra-node ones; both can
be in flight simultaneously, but inter-node work claims streaming capacity first.

**LB-5.2** Balancing (a, b, d) is skipped entirely when `tablets.balancing_enabled()` is
false, *except* draining, which always proceeds.

---

## 6. Candidate scoring: "badness"

Badness is the table-aware term. It answers: *does this move improve the distribution of
this particular table?* — because equalizing total bytes can still pile one table's
tablets onto one shard, which hurts that table's throughput.

**LB-6.1 (ideal share)**
```
ideal_table_load = table_size / total_capacity_storage
```
i.e. the utilization fraction this table would occupy on every shard/node if perfectly
spread (`:2902`).

**LB-6.2 (destination badness)** For moving `tablet_set` (size `S`) of `table` onto `dst`:
```
new_shard_load = (shard.used_bytes_of_table + S) / shard.capacity
dst_shard_badness = (new_shard_load - ideal_table_load) / table_size
new_node_load  = (node.used_bytes_of_table + S) / node.capacity
dst_node_badness  = (new_node_load  - ideal_table_load) / table_size
```
(`:2904`–`:2921`). Positive ⇒ the destination would hold more than its fair share of this
table.

**LB-6.3 (source badness)** Symmetric, sign-flipped (`:2940`):
```
src_shard_badness = (ideal_table_load - new_shard_load) / table_size
src_node_badness  = (ideal_table_load - new_node_load)  / table_size
```
Positive ⇒ the source would drop below its fair share.

**LB-6.4 (normalization)** Both are divided by `table_size`: moving one tablet of a small
table perturbs that table's distribution far more than the same move for a large table,
so small tables are protected.

**LB-6.5 (drain shortcuts)** Source is drained → `src badness = (-1, -1, 0, 0)` (always
good). Destination is drained → `dst badness = (table_size, table_size)` (always bad)
(`:2936`, `:2897`).

**LB-6.6 (intra-node)** If `src.host == dst.host`, both *node* badness components are
zeroed — only shard badness matters (`:2969`).

**LB-6.7 (bad)** `is_bad() ⇔ any of the four components > 0`.

**LB-6.8 (ordering)** With `node_badness = max(src_node, dst_node)` and
`shard_badness = max(src_shard, dst_shard)` (`:210`):
```
a < b  ⇔  if node_badness(a) == node_badness(b):  shard_badness(a) < shard_badness(b)
          elif either node_badness > 0:            node_badness(a) < node_badness(b)
          else:                                    shard_badness(a) < shard_badness(b)
```
Node-level imbalance dominates, because fixing shard imbalance within a node is cheap
(local, no network).

---

## 7. Inter-node balancing loop

`make_internode_plan()` — `service/tablet_allocator.cc:3757`.

### 7.1 Setup

**LB-7.1 (initial target)** The target is the **least-loaded non-drained node** in scope,
by `avg_load` (`:4480`).

**LB-7.2 (source/destination split)** For each node in scope (`:3793`):
```
if host != target and (no_drain_sources or node.drained): -> sources (max-heap by avg_load)
else:                                                     -> destinations (min-heap by avg_load)
```
So in free balancing: one destination (the least-loaded node), everything else a source.
While draining: sources are exactly the drain nodes; every non-drained node is a
destination. The direction of the fan reverses.

**LB-7.3 (batch size)** The loop stops after `plan.size() == target.shard_count`
migrations (`:3811`). Rationale: saturate the target with one stream per shard.

**LB-7.4 (skip budget)** `max_skipped_migrations = 2 * target.shard_count`.

### 7.2 The loop

```
while plan.size() < batch_size:
    if sources empty: STOP (no_candidates)

    src_host = pop_max(sources)                                     # LB-7.5
    drain_skipped = src.shards_by_load empty and src.drained
                    and src.skipped_candidates nonempty             # LB-7.6

    if src.shards_by_load empty and not drain_skipped:               # LB-7.7
        max_off_candidate_load = max(max_off_candidate_load, src.avg_load)
        drop src from sources; continue

    if drain_skipped:
        take src.skipped_candidates.back()
        src = that entry's replica
        destinations := that entry's viable_targets only             # LB-7.8
    else:
        src_shard = pop_max(src.shards_by_load)                      # LB-7.9
        if that shard has no candidates: drop the shard; continue    # LB-7.10

    if destinations empty: STOP (no_candidates)
    target = pop_min(destinations)                                   # LB-7.11

    if convergence_checks_enabled:                                   # LB-7.12
        max_load = max(max_off_candidate_load, src.avg_load)
        if is_balanced(target.avg_load, max_load): STOP (balanced)

    dst_shard = least_loaded_shard(target)                           # LB-7.13
    candidate = pick_candidate(src, dst)                             # §8, may move src/dst
    if convergence_checks_enabled and not check_convergence(src, dst, candidate):
        STOP (load_inversion)                                        # LB-7.14

    if not drain_skipped:
        skip = check_constraints(...)                                # §9
        if skip: record skipped candidate(s); continue                # LB-7.15

    kind = rebuild if src is being_removed/left/remove-requested else migration  # LB-7.16
    if can_accept_load(streaming):                                   # §12
        emit migration
    else:
        skipped_migrations += 1
        if skipped_migrations >= max_skipped: STOP (skip_limit)       # LB-7.17

    erase candidate from all its replicas' candidate lists           # LB-7.18
    update src/dst node+shard load as if the move happened           # LB-7.19
    if src.tablet_count == 0: drop src from sources
```

**LB-7.5** Sources are always visited most-loaded-first; the source node heap is re-pushed
after each iteration so its position reflects the updated load.

**LB-7.7 / off-candidate tracking** `max_off_candidate_load` records the highest load among
sources abandoned for lack of candidates. It is what makes the convergence test (LB-7.12)
sound: sources are drained in load order, so
`max(max_off_candidate_load, current_src.avg_load)` is the max load in the cluster.

**LB-7.13** `least_loaded_shard` comes from the `load_sketch`, ordering by
`(load, shard_id)` so ties break deterministically on the lower shard id
(`locator/load_sketch.hh:60`).

**LB-7.16 (rebuild vs migration)** Removing a node cannot stream from it, so the transition
kind becomes `rebuild` (stream from surviving replicas) rather than `migration`
(stream from source). Rebuild has `stream_weight = 2` for `rebuild_v2`/`repair`
(`locator/tablets.hh:408`).

**LB-7.17 (skip, don't stop)** A migration blocked purely by streaming limits is *dropped
from the plan but the loop continues as if it had been emitted*. This deliberately keeps
producing work for other shards instead of head-of-line blocking; the next round notices
it was never executed.

**LB-7.20 (unbalanceable)** An empty plan with `_migrating_candidates == 0` is logged as
"Not possible to achieve balance". Heterogeneous shard counts make perfect balance
unreachable — e.g. shards `{1, 1, 7}`, 7 tablets, RF=3: every node must hold every tablet,
so per-shard loads are `{7, 7, 1}` and no move helps (`:4046`).

---

## 8. Choosing the tablet and the destination

`pick_candidate()` — `service/tablet_allocator.cc:3533`.

**LB-8.1 (first guess)** Score one arbitrary candidate per table on the chosen source shard
against the chosen destination shard; keep the minimum by LB-6.8 (`peek_candidate`, `:2982`).
With table-aware balancing off, take any candidate, badness zero.

**LB-8.2 (escalation)** If the best first guess `is_bad()` **and** table-aware balancing is
on, search wider. Otherwise accept it immediately. Cheap path first: most moves are fine.

**LB-8.3 (wider search, non-drain)** For each table present on the source node:
1. Best source shard: over all shards in `shards_by_load`, over all candidate tablet sets
   of that table (only the *first* set per shard when in capacity-based mode, since all
   tablets are then equal), pick min `src_badness`.
2. Best destination node: over all destination-heap nodes passing `check_convergence`,
   pick min `dst_node_badness`; collect all ties.
3. Best destination shard: over all shards of the tied best nodes, pick min badness by
   LB-6.8; collect ties; break ties **uniformly at random** (`:3613`).
4. Stop scanning tables as soon as a non-bad candidate is found.

**LB-8.4 (wider search, drain)** With `drain_skipped`, the tablet set is fixed (the skipped
entry); only steps 2–3 run.

**LB-8.5 (side effects)** The chosen candidate is removed from the source's candidate list
(or popped off `skipped_candidates`), and the source-shard / destination-node heaps are
repaired so that the chosen entries sit at `back()`.

**LB-8.6 (randomness)** Two sources of nondeterminism a simulator must model or seed:
tie-breaking in LB-8.3.3, and `pick_table()` — which selects a table with probability
proportional to its candidate count (`:2860`) — used only when table-aware balancing is off
or in `peek_candidate`'s flat path.

---

## 9. Replication constraints

`check_constraints()` — `service/tablet_allocator.cc:3340`.

**LB-9.1 (no co-located replicas)** A move is rejected if the destination node already holds
a replica of that tablet (`:3423`).

**LB-9.2 (rack-based RF)** If the table's RF for this DC is an explicit rack list, tablets
may only move **within their rack** — any cross-rack destination is rejected (`:3418`).

**LB-9.3 (rack load ceiling)** Otherwise, for a cross-rack move: let `rack_load[r]` = number
of replicas of this tablet in rack `r` of this DC, and `max_rack_load = max(rack_load)`.
The move is rejected if `rack_load[dst.rack] + 1 > max_rack_load` (`:3396`). Effect: replica
distribution over racks may never become *more* skewed than it already is. It does not
require rack-uniformity, it only forbids regressions.

**LB-9.4 (viable targets)** When a move is rejected, the set of viable target hosts is
computed: same DC (same rack if LB-9.2), not drained, not already holding a replica, and
not violating LB-9.3. In rack scope or with rack-based RF, the rack filter is skipped as
vacuously satisfied.

**LB-9.5 (skipped candidates)** Rejected candidates are appended to
`src.skipped_candidates` with their viable-target set, and retried later via the
`drain_skipped` path (LB-7.6/7.8). In free (non-drain) balancing the skip list is only
consulted for drain sources, so a non-drain skip simply loses this round.

**LB-9.6 (drain failure)** If a drain source has a candidate with an **empty** viable-target
set, the plan records a `drain_failure` for that node and the loop stops. Decommission
cannot proceed; the operator must add nodes or lower RF (`:3967`).

**LB-9.7 (colocated pair constraints)** For a sibling pair (LB-4.2), constraints are checked
per sibling. If both siblings share at least one viable target, one skip entry is recorded
for the pair (colocation preserved). If they share none, a *separate* entry per sibling is
recorded — breaking colocation, because completing a decommission outranks preserving a
merge (`:3461`–`:3490`).

**LB-9.8 (excluded source, leave request)** If the source node has a `leave` request and is
also excluded, the drain is failed outright ("Node was marked as excluded") — a decommission
must not silently degrade into a lossy removal.

---

## 10. Convergence and stop conditions

**LB-10.1 (`is_balanced`)** (`:2831`)
```
if capacity_based_mode:  balanced ⇔ min_load == max_load        # exact
if max_load == 0:        balanced
else:                    balanced ⇔ (max_load - min_load) / max_load < threshold
```
`threshold = size_based_balance_threshold_percentage / 100`, default **1%**.

**LB-10.2 (DC gate)** The inter-node phase runs only if there are drain sources, or
`shuffle`, or `not is_balanced(min_node_load, max_node_load)` over non-drained nodes
(`:4480`).

**LB-10.3 (`check_convergence`, inter-node)** (`:3070`)
```
src.drained -> allow;  dst.drained -> reject
reject if src.avg_load <= dst.avg_load                    # already inverted
reject if src.avg_load <= load(dst after adding tablet)   # would invert
allow otherwise
```
This is the anti-oscillation rule: without the post-move test, two nodes trade the same
tablet back and forth across rounds forever.

**LB-10.4 (`check_intranode_convergence`)** `load(src_shard) > load(dst_shard + tablet)`
(`:3102`).

**LB-10.5 (drain overrides convergence)** When `nodes_to_drain` is non-empty, all
convergence checks in the inter-node loop are disabled — the stop condition is "source
drained", and temporary imbalance is accepted (`:3904`).

**LB-10.6 (stop reasons)** A simulator should record which fired, matching the metrics:
`no_candidates`, `balanced` (`stop_balance`), `load_inversion`, `skip_limit`,
`batch_size`, plus `drain_failure`.

---

## 11. Streaming concurrency

**LB-11.1 (per-shard counters)** Each shard has `streaming_read_load` and
`streaming_write_load`, incremented by `stream_weight` for every migration in flight or
newly planned (`:2774`).

**LB-11.2 (limits)** `tablet_streaming_read_concurrency_per_shard` = **2**,
`tablet_streaming_write_concurrency_per_shard` = **2** (`db/config.cc:1620`). Reads are
allowed as much as writes here by default; writes are the more IO-expensive side.

**LB-11.3 (admission test)** (`:2793`)
```
for r in read_from:  reject if load(r) > 0 and load(r) + weight > read_limit
for w in written_to: reject if load(w) > 0 and load(w) + weight > write_limit
```
Note `load > 0` guard: a shard with zero streaming always admits one migration, even if
its weight alone exceeds the limit. Otherwise heavy units (colocated pairs, repairs) could
never be scheduled.

**LB-11.4 (endpoints)** For `migration`/`intranode_migration`:
`read_from = old_replicas \ new_replicas`, `written_to = new_replicas \ old_replicas`
(`locator/tablets.cc:154`). For `rebuild`: write to the pending replica, read from all
other non-excluded next replicas. For `rebuild_v2`/`repair`: read and write across all
non-excluded replicas with `stream_weight = 2`.

**LB-11.5 (weight)** For a migration unit of `n` tablets (n = 2 for a colocated sibling
pair) the weight is `n` (`:2819`).

**LB-11.6 (pre-existing load)** Before planning, all in-flight transitions that are
*actively streaming* contribute to the counters. Streaming stages are:
`allow_write_both_read_old`, `write_both_read_old`, `streaming`, `rebuild_repair`,
`repair`. All later stages (`write_both_read_new`, `use_new`, `cleanup*`, `revert_*`,
`end_*`) do not (`:995`).

---

## 12. Intra-node balancing

`make_node_plan()` — `service/tablet_allocator.cc:3196`. Runs per node, for every node
**except** drain sources (`:3318`).

```
if node.shard_count <= 1: done
src_shards = max-heap of all shards by load
loop:
    if src_shards empty: stop (ran out of candidates)
    src = pop_max(src_shards)
    dst = least_loaded_shard(node)
    if src == dst or is_balanced(load(dst), load(src)): stop (balanced)   # LB-12.1
    if src has no candidates: drop src; continue                          # LB-12.2
    candidate = peek_candidate(src -> dst)                                # LB-6.6 applies
    if not check_intranode_convergence(node, src, dst, candidate): stop   # LB-12.3
    if not can_accept_load(streaming): stop (load limit)                  # LB-12.4
    emit intranode_migration; update loads; continue
```

**LB-12.1** No batch cap: a node is balanced internally in one plan, as far as candidates
and streaming limits allow. Intra-node moves are local (no network), so they are cheap.

**LB-12.4** Unlike LB-7.17, a streaming-limited intra-node move **stops** that node's loop
rather than skipping ahead.

**LB-12.5 (missing capacity)** If either shard's load is unknown, the node is declared
balanced and skipped.

---

## 13. Drain mode summary

Distinct enough to be worth stating as a mode:

| Aspect | Free balancing | Drain |
|---|---|---|
| Sources | all nodes but the target | only drain nodes (LB-7.2) |
| Destinations | one (least loaded) | all non-drained, least-loaded first |
| Convergence checks | on | **off** (LB-10.5) |
| Stop condition | balanced / batch / inversion | source empty, or drain failure |
| Skipped candidates | dropped | retried against viable targets (LB-7.8) |
| Failure mode | none | `drain_failure` → operator action (LB-9.6) |

---

## 14. Resize: split and merge

`make_sizing_plan()` (`:2348`) and `make_resize_plan()` (`:2644`). The balancer does not
split/merge tablets itself; it emits a per-table *resize decision* that replicas act on.
A simulator that models tablet-count changes needs these rules.

**LB-14.1 (target tablet size)** `target_tablet_size = target_tablet_size_in_bytes /
table_group_size`, default `target_tablet_size_in_bytes` = **5 GiB** (`db/config.cc:1616`).
Dividing by group size (co-located tables, e.g. materialized views) keeps the *migration
unit* bounded, since a group migrates together.

**LB-14.2 (thresholds with hysteresis)** With `avg_tablet_size = total_size /
(tablet_count * group_size)`:
```
split  if avg > 2 * target                      or (already splitting and avg >= target)
merge  if avg < target / 2                      or (already merging  and avg <= target)
```
(`:2436`). Split doubles the count; merge halves it (`div_ceil`). The midpoint hysteresis
is what stops split→merge→split churn: after a split, the average lands near `target`,
which is exactly the cancel boundary for the *opposite* decision.

**LB-14.3 (target count = max of all demands)** (`:2387`) Take the maximum over:
- `initial_tablets` (deprecated `initial` option),
- `min_tablet_count`,
- `(expected_data_size_in_gb << 30) / target_tablet_size`,
- the per-shard coverage demand (LB-14.3a),
- the size-derived count from LB-14.2.

Then apply `max_tablet_count` as a hard cap — forced, i.e. it overrides the maximum.

**LB-14.3a (per-shard coverage)** (`:2231`) `min_per_shard_tablet_count` defaults to
`tablets_initial_scale_factor` = **10**, but only if neither `initial_tablets` nor
`min_tablet_count` is set (those imply an explicit count). The demand is the maximum over
DCs and racks of:
```
numeric RF in dc:   ceil(min_per_shard * shards_in_dc / rf)
rack-list RF:       ceil(min_per_shard * shards_in_rack)   # per listed rack
```
i.e. "enough tablets that every shard that replicates this table gets at least
`min_per_shard` of them on average".

**LB-14.4 (no size data)** Without size stats, the target may only *rise* to the current
count, never fall — an unknown-size table is never merged.

**LB-14.5 (per-shard goal)** `tablets_per_shard_goal` = **100** (`db/config.cc:1614`). For
each rack, compute the projected average tablet replicas per shard summed over all tables;
if it exceeds the goal, derive `scale = goal / projected` and apply the **smallest** scale
across racks to every table with replicas in that rack (`:2533`). Numeric RF contributes
`count * rf / shards / racks_in_dc`; a rack-list RF contributes `count / shards` only in
its listed racks.

**LB-14.6 (power-of-2 alignment)** Unless `pow2_count` is false (requires the
`arbitrary_tablet_boundaries` feature), the target is rounded **up** to a power of two.
Scaling (LB-14.5) is applied before alignment, so the goal may be overshot by up to 2×;
it is a soft limit.

**LB-14.7 (decision)** `aligned > current` → split. `aligned < current` → merge, but only
if merges are allowed for the table **and** `div_ceil(current, 2) >= aligned` (prevents
oscillation, since one merge step only halves). Equal → none.

**LB-14.8 (concurrency)** At most **10** new resize requests per round, and a table is only
admitted if its cluster-wide shard presence fits in
`total_shards - shards_currently_resizing` (the first request is always admitted). Tables
are ordered by urgency = largest `avg_tablet_size` first (`:2708`).

**LB-14.9 (revocation)** An in-progress resize is cancelled only if the *opposite* decision
is now indicated — i.e. the average crossed all the way past the far threshold (`:2734`).

**LB-14.10 (finalization)** Split finalizes when every replica of every table in the group
reports `split_ready_seq_number == decision.sequence_number`. Merge finalizes when all
sibling tablets are co-located in all DCs (`:2757`, `:2766`).

**LB-14.11 (ordering)** Resize plans are computed before repair plans, and repair is
suppressed while any finalization is pending.

---

## 15. Merge colocation

**LB-15.1** Runs only when the DC's plan is otherwise empty (`:4496`) — it is the
lowest-priority work. Its job is to bring sibling tablets onto the same `(host, shard)` so
that a merge decision can be finalized (LB-14.10).

**LB-15.2** Once co-located and stable, the pair becomes a single migration unit for all
subsequent balancing (LB-4.2), and ordinary balancing will not separate them.

---

## 16. Tunables (defaults, `db/config.cc`)

| Parameter | Default | Role |
|---|---|---|
| `target_tablet_size_in_bytes` | 5 GiB | split/merge target; unit size in capacity mode |
| `minimal_tablet_size_for_balancing` | 50 MiB | floor on tablet size for load (LB-2.3) |
| `size_based_balance_threshold_percentage` | 1.0 | balanced-enough band (LB-10.1) |
| `force_capacity_based_balancing` | false | count-based instead of size-based (LB-2.5) |
| `tablet_streaming_read_concurrency_per_shard` | 2 | LB-11.2 |
| `tablet_streaming_write_concurrency_per_shard` | 2 | LB-11.2 |
| `tablets_per_shard_goal` | 100 | soft cap on tablets/shard (LB-14.5) |
| `tablets_initial_scale_factor` | 10 | default tablets per shard for a new table |
| batch size | `target.shard_count` | migrations per plan (LB-7.3) |
| max skipped | `2 * target.shard_count` | LB-7.4 |
| max new resize requests | 10 | LB-14.8 |

---

## 17. Simulator driver

```
loop:
    plan = make_plan(snapshot)
    if plan.empty(): converged
    apply(plan)            # mark transitions; or complete them instantly
    if iterations > 1 + 10*tablet_count: FAIL non-convergence
```

**LB-17.1 (two fidelity levels)**
- *Instant*: apply each migration atomically (replica moves, loads update). Streaming
  counters stay zero, so LB-11 never fires. This tests the balancing math and convergence.
- *Staged*: mark transitions with `next_replicas` and a stage, advance stages over
  simulated time, and let the planner see in-flight streams. This is the only way to
  exercise LB-11, LB-7.17 and the "in-flight counted as done" behavior (LB-1.2).

**LB-17.2 (invariants to assert after every applied plan)**
1. Every tablet has exactly `sum(RF)` replicas, all on distinct nodes (LB-1.1).
2. Per DC, per tablet, replica count per DC equals that DC's RF.
3. Rack skew never increases for any tablet (LB-9.3).
4. With rack-based RF, no replica changed rack (LB-9.2).
5. No shard exceeds the streaming limits, unless it started at zero (LB-11.3).
6. No node in the plan is `excluded` or `drained` as a destination.
7. `plan.size() <= target.shard_count` per DC per round (LB-7.3).

**LB-17.3 (quality metrics to report)** — mirroring
`test/perf/tablet_load_balancing.cc:483`:
- `node_overcommit` = max node load / mean node load, per table and overall.
- `shard_overcommit` = max shard load / mean shard load, per table, and the theoretical
  best achievable given tablet granularity.
- total migrations, total bytes streamed, rounds to convergence.
- count of `bad_migrations` (LB-6.7) and `bad_first_candidates` (LB-8.2 escalations).

**LB-17.4 (shuffle mode)** A test-only injection (`tablet_allocator_shuffle`) that picks
random sources/destinations and disables convergence checks, used to force churn. Worth
implementing as a simulator mode for anti-oscillation and safety testing (`:2827`,
`:3231`).

---

## 18. Design rationale, in one paragraph each

**Why nodes before shards.** Node-level balance is achieved by network streaming; shard
balance inside a node is achieved locally. Equalizing nodes first, then rebalancing each
node internally, reaches global shard balance with far fewer cross-node moves than
optimizing shards globally (`:586`). This is also why badness orders node imbalance ahead
of shard imbalance (LB-6.8).

**Why one destination at a time.** Concentrating on the single least-loaded node makes each
plan a coherent batch that saturates one node's shards. Because plans are increments,
successive rounds pick different targets, so multiple under-loaded nodes still fill in
parallel (`:616`).

**Why "in-flight counts as done".** The planner is stateless and gets called repeatedly
while migrations are still streaming. Treating pending migrations as complete lets each
round plan the *delta* rather than re-deriving and duplicating decisions; overload from
tablets that still exist on both ends is bounded separately by the streaming limits
(`:634`).

**Why table-aware badness.** Byte-level balance can still concentrate one table's tablets,
which concentrates that table's request load. Badness adds a per-table fairness term,
normalized by table size so that small tables — whose distribution is most fragile — get
the most protection (LB-6.4).

**Why the post-move convergence test.** Comparing only current loads permits a move that
overshoots and makes the destination the new maximum, which the next round undoes.
Requiring `src_load > dst_load_after_move` makes every move strictly reduce the spread,
guaranteeing termination (LB-10.3).
