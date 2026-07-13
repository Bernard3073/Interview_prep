# Week 16 — Concurrency for Robotics (async/await + sensor streams)

> Perception is a pipeline: data arrives, waits, gets processed, moves on. The
> bottleneck is usually *waiting*, not computing. This note covers Python
> async/await, where it belongs (and where it emphatically does not), and the same
> concurrency reasoning applied to multi-sensor robotics systems.

---

## 1. The one idea to anchor everything: two worlds

Robotics has two concurrency regimes, and interviewers test whether you know the
boundary:

| | Real-time on-vehicle loop | Offline / infra layer |
|---|---|---|
| Examples | control, sensor fusion at deadline | data pipelines, batch perception, tooling, ingestion |
| Language | C++, ROS2, lock-free queues | Python, asyncio, threads |
| Deadline | **hard** (worst-case matters) | **soft** (throughput matters) |
| async/await? | ❌ wrong — GC + event loop are non-deterministic | ✅ natural fit for I/O-bound work |

**If you say nothing else about async in a robotics interview, say which layer it
belongs to.** Python's async is right for the data/infra side (Scale AI, AV data
pipelines) and wrong for the on-vehicle real-time control loop.

---

## 2. async/await fundamentals

- `async def` defines a **coroutine**; calling it returns a coroutine object that
  does nothing until awaited.
- `await` **yields control to the event loop** while waiting, letting other
  coroutines run. You can only `await` inside `async def`.
- `asyncio.run(main())` starts the event loop.
- `asyncio.gather(*coros)` runs coroutines **concurrently**, returns results in
  submission order. Total time ≈ **max**, not **sum**.
- `asyncio.create_task(coro)` schedules a coroutine to start *now* and run in the
  background; `await` the task later to collect its result.

### Diagnose the workload FIRST (the #1 scored signal)

- **I/O-bound** (network, disk, DB, downloads) → async wins; overlaps waiting.
- **CPU-bound** (decode point cloud, run inference, image transforms) → async alone
  does **nothing**. It blocks the event loop. Offload with
  `await asyncio.to_thread(fn, ...)` or a `ProcessPoolExecutor`.

> The classic trap: interviewer plants CPU-heavy work in an "async" problem to see
> if you keep it on the event loop. Name the workload out loud early.

### The other classic trap: `time.sleep` vs `asyncio.sleep`

```python
await asyncio.sleep(1)   # ✅ yields — other coroutines run
time.sleep(1)            # ❌ blocks the whole event loop — now sequential
```

async only helps if you actually yield with `await`.

---

## 3. The interview problem (pipeline of steps)

**Prompt seen at Scale AI:** tasks made of named steps with durations, e.g.
`Task 1: [("Download", 1000), ("Fetch", 200)]`. Print the step/task and its time.

The insight: **two levels of scheduling** — steps *sequential within* a task,
tasks *concurrent across* each other.

```python
import asyncio, time

async def run_task(task_id: int, steps: list[tuple[str, int]]):
    start = time.perf_counter()
    for name, duration_ms in steps:          # steps run IN ORDER
        await asyncio.sleep(duration_ms / 1000)
        print(f"Task {task_id} · {name} done "
              f"@ {(time.perf_counter()-start)*1000:.0f}ms")
    print(f"Task {task_id} finished in {(time.perf_counter()-start)*1000:.0f}ms")

async def main():
    tasks = {
        1: [("Download", 1000), ("Fetch", 200)],
        2: [("Download", 500),  ("Fetch", 800)],
    }
    await asyncio.gather(*(run_task(tid, s) for tid, s in tasks.items()))

asyncio.run(main())
```

Two mistakes it catches at once:

- **Over-serializing:** `for t in tasks: await run_task(t)` makes tasks sequential
  (total = 1200 + 1300 = 2500ms). `gather` makes them concurrent → **1300ms** = max.
- **Over-parallelizing:** `gather`-ing the *steps* breaks the pipeline — Fetch
  would start before Download finishes.

Correct answer = concurrent tasks **and** sequential steps. Printing real elapsed
time *proves* the concurrency (~1300ms wall clock, not 2500ms).

---

## 4. Bounded concurrency & backpressure (senior signal)

"Now run 10,000 of these." Firing them all at once exhausts file handles / memory /
downstream rate limits. Bound it:

```python
async def run_task(tid, steps, sem):
    async with sem:                       # at most N concurrent
        for name, ms in steps:
            await asyncio.sleep(ms / 1000)

async def main():
    sem = asyncio.Semaphore(5)
    await asyncio.gather(*(run_task(t, s, sem) for t, s in tasks.items()))
```

- **Semaphore** — cap concurrent tasks.
- **Bounded `asyncio.Queue`** between producer (ingest) and consumer (process/upload)
  stages so a fast producer can't OOM the box — this *is* backpressure.
- **Failure handling:** `gather(..., return_exceptions=True)` for partial failure;
  `asyncio.wait_for(coro, timeout)`; retries with exponential backoff; cancellation.

This maps directly to real AV/robotics infra: throttling thousands of concurrent
sensor-log downloads without falling over.

---

## 5. async vs threads vs multiprocessing vs a queue

| Tool | Use when | Why |
|---|---|---|
| **asyncio** | many I/O-bound tasks, one process | cheap concurrency, no thread overhead |
| **threads** | blocking I/O in non-async libs | GIL released during I/O; simpler than rewriting async |
| **multiprocessing** | CPU-bound work | sidesteps the GIL with real parallelism |
| **message queue** (Kafka/SQS) | cross-service, durable, decoupled | survives restarts, scales beyond one box |

async is *one* tool. Knowing when **not** to use it is the senior signal.

---

## 6. The robotics-specific version: multi-sensor concurrency

This is likelier to matter than raw asyncio. Same reasoning, applied to sensors.

- **Streams at different rates:** camera 30Hz, LiDAR 10Hz, IMU 200Hz. Consume
  concurrently so one slow stream doesn't block others.
- **Time synchronization** (the real problem): messages arrive out of order / at
  different rates. Align by **sensor timestamp, not wall clock**. In ROS:
  `message_filters` **ExactTime** / **ApproximateTime** to fuse a camera+LiDAR pair.
- **Producer/consumer with bounded buffers:** capture thread → ring buffer →
  processing thread. Drop-oldest policy when the consumer falls behind (real-time
  prefers fresh data over complete data).
- **ROS2 executors** = the domain's event loop: single-threaded executor (callbacks
  serialized) vs multi-threaded executor + **callback groups** (Reentrant vs
  MutuallyExclusive) to control which callbacks may run in parallel. Guard shared
  state — the same data-race concerns as any threaded system.
- **Thread safety in a node:** subscriber callback writes, timer callback reads →
  needs a lock or a lock-free queue. Classic bug source.

> Bridge line for the interview: "async/await is how I'd handle the *offline* data
> pipeline — concurrent downloads with a semaphore and backpressure. On-vehicle,
> the same producer/consumer reasoning applies but I'd use ROS2 executors / C++
> threads with bounded queues, because the control loop needs bounded worst-case
> latency, which a GC'd event loop can't guarantee."

---

## 7. Interviewer's checklist (self-score)

1. Diagnose **I/O- vs CPU-bound** out loud early.
2. `asyncio.sleep`, never `time.sleep`, inside a coroutine.
3. Output comes back in **completion order**; total time = **max, not sum**.
4. Extend to **sequential steps + concurrent tasks** correctly.
5. **Bound concurrency** (semaphore / bounded queue) + backpressure + failure handling.
6. Know **async vs threads vs multiprocessing vs queue** tradeoffs.
7. **Robotics awareness:** the real-time boundary + sensor time-sync + ROS executors.

Hit 1–4 = solid. Add 5–7 = senior. See also
[systems & ROS](09-systems-ros-interview.md) and
[C++ for robotics](10-cpp-for-robotics.md).
