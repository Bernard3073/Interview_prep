# Week 11 — C++ for Robotics

> Most production robotics runs on C++: it gives you predictable performance,
> deterministic resource management, direct hardware access, and the ecosystem
> (ROS, Eigen, PCL, OpenCV). This week is the C++ you're expected to *speak
> fluently* in a perception/robotics interview — not the whole language, but the
> idioms that come up over and over.

---

## 1. Why C++ (and where it bites)

- **Performance & determinism:** no GC pauses, control over allocation, cache,
  and layout — essential for real-time control and high-rate perception.
- **Zero-cost abstractions:** templates/inlining give you high-level code that
  compiles down to tight machine code.
- **Ecosystem:** ROS/ROS2 (`rclcpp`), Eigen (linear algebra), PCL (point clouds),
  OpenCV (vision), drivers and DDS middleware.
- **The cost:** manual lifetime/ownership reasoning, undefined behavior, long
  build times, and footguns (dangling refs, data races). The idioms below exist
  to tame exactly these.

---

## 2. RAII — the central idiom

**Resource Acquisition Is Initialization:** tie a resource (memory, lock, file,
socket) to an object's lifetime. The constructor acquires; the **destructor
releases** — automatically, even when an exception unwinds the stack.

```cpp
{
    std::lock_guard<std::mutex> lk(m);   // acquires the lock
    // ... critical section ...
}                                        // destructor releases it — always
```

RAII is *why* C++ can be both manual and safe: you almost never write `delete`,
`unlock()`, or `close()` by hand. Every owning type (`std::vector`,
`std::unique_ptr`, `std::fstream`, `std::lock_guard`) is an RAII wrapper.

> Interview reflex: "How do you avoid leaks / guarantee cleanup on early return or
> exception?" → **RAII**: wrap the resource in an object whose destructor frees it.

---

## 3. Smart pointers & ownership

![Smart pointers and ownership](images/cpp-ownership.svg)

Express **who owns** a heap object in the type system:

- **`std::unique_ptr<T>`** — *sole* ownership, move-only, **zero runtime
  overhead**. The default choice. Create with `std::make_unique<T>(...)`.
- **`std::shared_ptr<T>`** — shared ownership via an **atomic reference count**;
  the object dies when the last owner does. Costs an atomic increment/decrement and
  a control block. Create with `std::make_shared<T>(...)`.
- **`std::weak_ptr<T>`** — a *non-owning* observer of a `shared_ptr`; doesn't keep
  the object alive. Used to **break reference cycles** (which would otherwise leak)
  and to check if an object still exists (`.lock()`).
- **Raw pointers / references** — fine for **non-owning** access ("I observe but
  don't manage lifetime"). A raw `T*` should never own.

```cpp
// A pipeline node solely owns its detector; the map is shared between nodes.
auto detector = std::make_unique<Detector>(config);   // sole owner
auto map      = std::make_shared<OccupancyMap>();      // shared owner

planner.setMap(map);                  // planner holds a shared_ptr -> use_count == 2
std::weak_ptr<OccupancyMap> watch = map;               // observes, does NOT own

if (auto m = watch.lock()) {          // promote to shared_ptr iff still alive
    m->update(scan);
}                                     // `detector` is freed automatically here
```

> Default to `unique_ptr`; reach for `shared_ptr` only when ownership is genuinely
> shared. Overusing `shared_ptr` hides lifetimes and adds atomic overhead.

---

## 4. Move semantics & the Rule of 0/3/5

Copying a 10k-point cloud or a big matrix is expensive; **moving** transfers its
guts (pointer + size) and leaves the source empty — cheap.

- An **lvalue** has a name/address; an **rvalue** is a temporary. `T&&` binds to
  rvalues.
- **`std::move(x)`** does **not** move anything — it's just a cast to `T&&` that
  makes `x` eligible to be moved from. The move constructor/assignment does the work.
- Use it to hand off ownership: `vec.push_back(std::move(big));`.

**Rule of 0/3/5:**
- **Rule of 0:** prefer classes that need *no* custom destructor/copy/move — let
  members (`vector`, `unique_ptr`) manage themselves. This is the goal.
- **Rule of 3:** if you define one of destructor / copy ctor / copy assignment, you
  probably need all three.
- **Rule of 5:** with move semantics, that grows to include the move ctor and move
  assignment.

```cpp
struct PointCloud {
    std::vector<float> pts;          // owns the data
    // Rule of 0: std::vector already gives a correct copy AND move — write neither.
};

PointCloud makeCloud();              // returns by value

PointCloud a = makeCloud();          // move / copy-elision — no deep copy
PointCloud b = std::move(a);         // steals a.pts; `a` is now empty-but-valid
queue.push_back(std::move(b));       // hand ownership to the queue (no copy)
```

---

## 5. const correctness & references vs pointers

- **`const` correctness** documents and enforces intent. A `const` **member
  function** promises not to modify the object's observable state; pass read-only
  parameters as `const T&` to avoid copies without allowing mutation.
- **Reference vs pointer:** a reference is an alias — can't be null, can't rebind,
  must be initialized. A pointer can be null and reseated. Prefer references when
  "always present"; use pointers (or `optional`) when absence is meaningful.
- **Parameter passing:** by value for cheap/owned copies; **`const T&`** for large
  read-only inputs; **`T&&`** when you'll take ownership; `T&` for in/out params.

```cpp
class Pose {
public:
    double yaw() const { return yaw_; }                 // const: won't modify *this
    double distanceTo(const Pose& other) const;         // const& param: no copy
    void   integrate(double v, double w, double dt);    // non-const: mutates state
private:
    double x_{}, y_{}, yaw_{};
};

void log(const Pose& p);     // read-only, no copy made, cannot mutate p
```

---

## 6. STL containers & their complexity

| Container | Backing | Access / find | Notes |
|---|---|---|---|
| `vector` | contiguous array | `O(1)` index, `O(n)` find | cache-friendly default; `reserve()` to avoid reallocs |
| `array` | fixed C array | `O(1)` | size known at compile time, no heap |
| `deque` | chunked | `O(1)` ends | fast push front/back |
| `list` | doubly linked | `O(n)` find | stable iterators, rarely worth it |
| `map` / `set` | red-black tree | `O(log n)` | ordered keys |
| `unordered_map` / `set` | hash table | `O(1)` avg, `O(n)` worst | no ordering; needs a good hash |

- **`vector` is the default** — contiguous memory wins on modern CPUs (cache).
- **`unordered_map` for lookups**, `map` only when you need ordering.
- **Iterator invalidation:** `vector` reallocation invalidates all iterators/
  pointers; erasing invalidates from the erase point. Know the rules per container.

```cpp
std::vector<int> v;
v.reserve(1000);                       // one allocation up front — no reallocs below
for (int i = 0; i < 1000; ++i) v.push_back(i);

std::unordered_map<int, Track> tracks; // O(1) average lookup by id
if (auto it = tracks.find(id); it != tracks.end())
    it->second.update(z);

// Erase-while-iterating: erase() returns the next valid iterator.
for (auto it = v.begin(); it != v.end(); )
    it = (*it % 2 == 0) ? v.erase(it) : std::next(it);
```

---

## 7. Memory, performance & real-time

- **Stack vs heap:** stack allocation is essentially free and cache-local; heap
  (`new`/`malloc`) is slow and non-deterministic. In a **real-time / hot loop,
  avoid heap allocation** — preallocate, `reserve()`, reuse buffers, use object
  pools or ring buffers.
- **Cache locality:** prefer contiguous data; consider **SoA vs AoS** layouts for
  hot data. Random pointer chasing (linked lists, `shared_ptr` graphs) is slow.
- **Alignment:** SIMD types need alignment. **Eigen gotcha:** fixed-size Eigen
  members (e.g. `Eigen::Matrix4d`) require aligned storage — add
  `EIGEN_MAKE_ALIGNED_OPERATOR_NEW` to heap-allocated classes that hold them (less
  of an issue with C++17 aligned `new`, but still asked about).
- **Avoid `virtual` in the hot path:** virtual calls cost a vtable indirection and
  block inlining; fine for setup, avoid per-sample in tight loops.
- **Real-time = worst case, not average.** No unbounded loops, no blocking I/O, no
  surprise allocations.

```cpp
// Real-time loop: allocate ONCE, reuse every cycle — no heap in the hot path.
std::vector<float> buffer(MAX_POINTS);            // preallocated outside the loop
while (running) {
    size_t n = sensor.read(buffer.data(), buffer.size());   // fills, no allocation
    process(buffer.data(), n);
}

// Eigen alignment gotcha: a heap-allocated class with a fixed-size Eigen member.
struct KalmanState {
    Eigen::Matrix4d P;                 // fixed-size -> needs over-aligned storage
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW    // makes `new KalmanState` safe (pre-C++17)
};
```

---

## 8. Concurrency

- **`std::thread`** for parallelism; join or detach. Higher-level: `std::async`,
  thread pools.
- **`std::mutex`** + RAII locks (`std::lock_guard`, `std::unique_lock`) protect
  shared state. **`std::condition_variable`** for producer/consumer signalling.
- **`std::atomic<T>`** for lock-free flags/counters; understand that "atomic" ≠
  "ordered" without the right memory order (`memory_order_*`).
- **Hazards:** **data races** (UB — two threads, one writes, no sync), **deadlock**
  (lock ordering!), and **priority inversion** in real-time systems.
- Typical pattern: a **bounded (ring) buffer** between a sensor-capture thread and
  a processing thread, guarded by a mutex + condition variable.

```cpp
std::mutex m;
std::condition_variable cv;
std::queue<Scan> q;
std::atomic<bool> running{true};

void producer(Sensor& s) {
    while (running) {
        Scan scan = s.capture();
        { std::lock_guard<std::mutex> lk(m); q.push(std::move(scan)); }  // lock only to push
        cv.notify_one();
    }
}

void consumer() {
    while (running) {
        std::unique_lock<std::mutex> lk(m);
        cv.wait(lk, [&]{ return !q.empty() || !running; });   // sleep until work arrives
        if (q.empty()) continue;
        Scan s = std::move(q.front()); q.pop();
        lk.unlock();                                          // process OUTSIDE the lock
        process(s);
    }
}
```

---

## 9. Ring buffers — the real-time workhorse

A **ring buffer** (a.k.a. **circular queue**) is a **fixed-capacity** queue stored in a
**pre-allocated** array whose indices *wrap around* (`% cap`, or a bitmask when the
capacity is a power of two). It's the most common data structure in robotics
middleware — sensor drivers, message queues, log buffers, lock-free hand-offs —
because:

- **O(1) push and pop**, contiguous and cache-friendly.
- **Bounded memory** and **zero allocation after construction** → safe in a real-time
  callback (no `malloc` in the hot path).
- A natural **producer/consumer buffer** between a fast sensor callback and slower
  processing.

> "Fixed-capacity, pre-allocated ring buffer" is three words describing one array:
> *circular* = wrap-around indexing, *fixed-capacity* = it never grows, *pre-allocated*
> = the storage is allocated once up front.

### Mechanics
Track a write index plus either a read index or a count. The next element goes at
`head % cap`; wrap-around reuses old slots. **Full** when `count == cap` (or
`head − tail == cap`); **empty** when `count == 0` (or `head == tail`).

### Overflow policy — the real design decision
When a `push` arrives and the buffer is full you must choose:
- **Reject newest** — drop the incoming item (classic bounded queue).
- **Block / backpressure** — make the producer wait (never lose data, but stalls a
  hardware callback — usually unacceptable in flight).
- **Drop oldest (keep-latest)** — overwrite the oldest so the freshest data survives;
  best for perception, where stale frames are useless and latency must stay bounded.

### A simple fixed-capacity ring buffer

```cpp
template <class T>
class RingBuffer {
    std::vector<T> buf_;        // pre-allocated once (fixed capacity)
    size_t head_ = 0;          // index of the oldest element
    size_t count_ = 0;         // how many elements are currently stored
public:
    explicit RingBuffer(size_t capacity) : buf_(capacity) {}

    bool   empty() const { return count_ == 0; }
    bool   full()  const { return count_ == buf_.size(); }
    size_t size()  const { return count_; }

    // keep-latest: when full, drop the oldest so the newest always fits
    void push(const T& x) {
        if (full()) { head_ = (head_ + 1) % buf_.size(); --count_; }  // drop oldest
        buf_[(head_ + count_) % buf_.size()] = x;                     // write newest
        ++count_;
    }
    bool pop(T& out) {                          // take the oldest
        if (empty()) return false;
        out = buf_[head_];
        head_ = (head_ + 1) % buf_.size();
        --count_;
        return true;
    }
    const T& newest() const { return buf_[(head_ + count_ - 1) % buf_.size()]; }
};
```

### Making it thread-safe — lock-free SPSC
When a sensor thread (producer) feeds a processing thread (consumer), wrap the
indices in **atomics** so no mutex is needed. The rule that keeps it lock-free *and*
race-free: **one writer per index** — the producer owns `head_`, the consumer owns
`tail_` — paired with **release/acquire** so a slot's data publishes before its index.

```cpp
template <class T, size_t N>                 // single-producer / single-consumer; N = capacity
class SpscRing {
    std::array<T, N> buf_{};                 // pre-allocated, no heap in flight
    std::atomic<size_t> head_{0}, tail_{0};  // producer writes head_, consumer writes tail_
public:
    bool push(const T& x) {                  // producer only
        size_t h = head_.load(std::memory_order_relaxed);
        if (h - tail_.load(std::memory_order_acquire) == N) return false;  // full
        buf_[h % N] = x;
        head_.store(h + 1, std::memory_order_release);                     // publish
        return true;
    }
    bool pop(T& out) {                        // consumer only
        size_t t = tail_.load(std::memory_order_relaxed);
        if (t == head_.load(std::memory_order_acquire)) return false;      // empty
        out = buf_[t % N];
        tail_.store(t + 1, std::memory_order_release);
        return true;
    }
};
```

> This SPSC version *rejects* when full (returns `false`). To keep-latest **without a
> lock**, keep the producer the sole writer of `head_` and have the consumer *skip*
> any frames the producer overwrote — exactly the
> [Real-Time Frame Ingest Buffer](practice.html?p=rob-frame-ingest) practice problem.

---

## 10. The robotics C++ ecosystem

- **Eigen** — header-only linear algebra. Know fixed-size (`Matrix3d`, stack, fast)
  vs dynamic (`MatrixXd`, heap); lazy evaluation/expression templates; use
  `.noalias()` to avoid temporaries; watch the aliasing trap (`A = A * B`).
- **PCL** for point clouds, **OpenCV** (`cv::Mat`) for images, **ROS2/`rclcpp`**
  for nodes/pub-sub/TF.
- **Build model:** headers are textually included; each `.cpp` is a **translation
  unit**; the **linker** joins them. The **One Definition Rule (ODR)**, header
  guards / `#pragma once`, and `inline`/templates-in-headers all follow from this.
- **CMake** is the de-facto build system: `add_library`, `target_link_libraries`,
  `target_include_directories`, with transitive `PUBLIC`/`PRIVATE` usage.

```cpp
#include <Eigen/Dense>

Eigen::Matrix3d R = Eigen::AngleAxisd(yaw, Eigen::Vector3d::UnitZ()).toRotationMatrix();
Eigen::Vector3d t(1.0, 2.0, 0.0);

Eigen::Vector3d p_world = R * p_body + t;          // transform a point
Eigen::Matrix3d cov_w   = R * cov * R.transpose(); // propagate a covariance

// Solve a (possibly overdetermined) linear system robustly:
Eigen::MatrixXd A = Eigen::MatrixXd::Random(6, 4);
Eigen::VectorXd x = A.colPivHouseholderQr().solve(b);
```

A minimal `CMakeLists.txt` for the above:

```cmake
cmake_minimum_required(VERSION 3.16)
project(perception)
find_package(Eigen3 REQUIRED)
add_executable(node src/node.cpp)
target_link_libraries(node PRIVATE Eigen3::Eigen)
target_compile_features(node PRIVATE cxx_std_17)
```

---

## 11. Modern C++ worth knowing (C++11 → 20)

`auto`, range-based `for`, **lambdas** (and captures), **structured bindings**
(`auto [a, b] = pair`), `std::optional`, `std::array`, `std::string_view`,
`std::span`, `constexpr`, `std::chrono` for timing, `std::variant`, and (C++20)
concepts, ranges, `std::jthread`. You don't need them all — but `auto`, lambdas,
range-for, and structured bindings should be second nature.

```cpp
auto poses = loadPoses();                       // auto: deduce the type

for (const auto& p : poses) { /* range-based for */ }

auto [theta, tx, ty] = solveAlignment(a, b);    // structured bindings on a tuple/struct

std::optional<Match> findMatch(int id);         // "maybe a value"
if (auto m = findMatch(id)) use(*m);

auto cost = [&](const Pose& p){ return error(p, target); };   // lambda capturing by ref

auto t0 = std::chrono::steady_clock::now();     // timing
// ... work ...
double ms = std::chrono::duration<double, std::milli>(
                std::chrono::steady_clock::now() - t0).count();
```

---

## 12. Common pitfalls & undefined behavior

- **Dangling reference / use-after-free** — returning a reference to a local,
  storing a pointer to a `vector` element then growing the vector.
- **Iterator invalidation** during modification.
- **Data races** — concurrent unsynchronized access.
- **Uninitialized variables**, **out-of-bounds** access, **signed integer
  overflow**, **null dereference** — all UB, meaning the compiler may do *anything*.
- A surprising number of "weird robot behavior" bugs are UB or a lifetime bug, not
  an algorithm bug. Tools: `-Wall -Wextra`, AddressSanitizer/UBSan, `valgrind`.

```cpp
// BUG: returns a reference to a destroyed local -> dangling, use-after-free (UB).
const Pose& latest() {
    Pose p = readPose();
    return p;                 // `p` dies at return; caller gets a dangling reference
}

// BUG: caching a pointer into a vector that then reallocates.
int* first = &v[0];
v.push_back(x);               // may reallocate the buffer...
*first = 5;                   // ...so `first` now dangles -> UB

// FIX: return by value; index by position instead of caching raw pointers/iterators.
```

---

## Interview-style questions
*Click a question to reveal a model answer.*

??? What is RAII and why does it matter in robotics?
RAII (Resource Acquisition Is Initialization) ties a resource's lifetime to an object: the **constructor acquires** it and the **destructor releases** it automatically, including during exception unwinding. It matters because robotics code manages many resources (locks, memory, file/socket/device handles) and must **never leak or deadlock** even on early returns or errors — RAII makes cleanup automatic and exception-safe instead of relying on hand-written `delete`/`unlock`. Every owning STL type (`vector`, `unique_ptr`, `lock_guard`) is an RAII wrapper.

??? unique_ptr vs shared_ptr vs weak_ptr — when do you use each, and what do they cost?
**`unique_ptr`**: sole ownership, move-only, **zero overhead** — the default. **`shared_ptr`**: shared ownership via an **atomic reference count** + control block; use only when ownership is genuinely shared, since the atomics and indirection cost performance and can hide lifetimes. **`weak_ptr`**: a non-owning observer of a `shared_ptr` that doesn't keep the object alive — used to **break reference cycles** (two `shared_ptr`s pointing at each other leak) and to safely check existence via `.lock()`. Rule of thumb: default to `unique_ptr`, escalate to `shared_ptr` only when needed.

??? What does std::move actually do?
**Nothing at runtime** — `std::move(x)` is just a `static_cast` to an rvalue reference (`T&&`). It marks `x` as *eligible to be moved from*, so an overload set picks the **move constructor / move assignment**, which is what actually transfers the internals (e.g. swaps the pointer and size of a vector) and leaves the source in a valid-but-empty state. After moving from `x`, you should only assign to it or destroy it.

??? Explain the Rule of 0 / 3 / 5.
**Rule of 3:** if you define any of destructor, copy constructor, or copy assignment, you almost certainly need all three (they manage the same resource). **Rule of 5:** with move semantics, that set also includes the move constructor and move assignment. **Rule of 0** (the goal): design classes so you need *none* of them — let RAII members (`vector`, `unique_ptr`) handle resources, and the compiler-generated special members just work.

??? map vs unordered_map — how do they differ and when do you pick each?
`std::map` is a balanced **red-black tree**: keys are **ordered**, operations are **`O(log n)`**, iteration is sorted. `std::unordered_map` is a **hash table**: **`O(1)` average** lookup/insert (`O(n)` worst case with bad hashing/collisions), **no ordering**, and needs a good hash function for the key. Pick `unordered_map` for pure fast lookups (the common case), and `map` when you need ordering, range queries, or stable iteration order.

??? Why avoid heap allocation in a real-time control loop, and how?
Heap allocation (`new`/`malloc`) is **non-deterministic** — it can take variable time, may lock, and can fragment — which breaks the worst-case timing guarantees a real-time loop needs. Avoid it by **preallocating** outside the loop: `reserve()` vectors, reuse fixed buffers, use **object pools** or a **ring buffer**, prefer stack/fixed-size (`std::array`, fixed-size Eigen) data, and keep allocations in setup, not the hot path. Real-time cares about worst case, not average.

??? How do you choose between pass-by-value, const reference, and rvalue reference?
**`const T&`** for large read-only inputs (no copy, no mutation) — the default for non-trivial types. **By value** for small/cheap-to-copy types, or when the function needs its own copy anyway (then `std::move` it into place). **`T&&`** (rvalue ref) when the function will **take ownership** of the argument and you want to enable a move. `T&` (non-const) only for genuine in/out parameters. Modern guidance: "take by value and move" is a clean idiom for sink parameters.

??? What is a data race, and how do you prevent one?
A **data race** is when two or more threads access the same memory location concurrently, at least one writes, and there's no synchronization — it is **undefined behavior** in C++. Prevent it by protecting shared state with a **`std::mutex`** (via RAII `lock_guard`/`unique_lock`), using **`std::atomic`** for simple shared flags/counters, or by avoiding sharing altogether (message passing, per-thread data). Also watch for **deadlock** — always acquire multiple locks in a consistent order.

??? What is undefined behavior? Give robotics-relevant examples.
UB is a program construct the standard places **no constraints** on — the compiler may produce any result, including "works on my machine" then crashes in the field. Examples that bite robotics: **dangling references / use-after-free** (returning a reference to a local, or keeping a pointer into a `vector` that then reallocates), **out-of-bounds** array access, **data races**, **uninitialized reads**, **signed overflow**, and **null dereference**. Many "mysterious robot misbehaviors" are UB or lifetime bugs, not algorithm bugs — catch them with `-Wall -Wextra`, ASan/UBSan, and valgrind.

??? Reference vs pointer — what's the difference and when do you use each?
A **reference** is an alias to an existing object: it must be initialized, can't be null, and can't be rebound to another object. A **pointer** can be null, can be reseated, and supports pointer arithmetic. Use a **reference** when the thing is always present and you won't rebind it (cleaner, safer — the common choice for parameters). Use a **pointer** (or `std::optional` / `std::unique_ptr`) when **absence is meaningful**, when you need to reseat it, or to express (non-owning) optional access.

??? What's the Eigen fixed-size alignment gotcha?
Fixed-size, vectorizable Eigen types (e.g. `Eigen::Matrix4d`, `Vector4f`) require **over-aligned storage** for SIMD. If such a type is a member of a class you allocate on the heap with `new`, the default `operator new` may not honor that alignment → crashes or UB. The classic fix is to add the **`EIGEN_MAKE_ALIGNED_OPERATOR_NEW`** macro to the class (and use Eigen's aligned allocator for STL containers of fixed-size Eigen types). C++17's aligned `new` largely fixes this, but interviewers still ask about it.

??? Why can virtual functions hurt performance, and when should you avoid them?
A `virtual` call goes through a **vtable indirection** (load the vtable pointer, load the function pointer, call), which adds a small cost and — more importantly — usually **prevents inlining** and can cause an instruction-cache/branch-predictor miss. That's negligible for setup or low-rate code, but in a **tight per-sample hot loop** (e.g. processing every point in a cloud) it can matter; there you prefer static dispatch (templates/CRTP) or a non-virtual design. Don't prematurely optimize — profile first — but know the mechanism.

## Resources
- *Effective Modern C++* (Scott Meyers) — the canonical interview-prep book.
- *A Tour of C++* (Bjarne Stroustrup) — concise modern overview.
- cppreference.com — the reference you'll actually use day to day.
- C++ Core Guidelines (isocpp.github.io/CppCoreGuidelines).
- Compiler Explorer (godbolt.org) to *see* the generated assembly.

➡ **Practice (solve in-site):** [Real-Time Frame Ingest Buffer](practice.html?p=rob-frame-ingest) — implement the camera → perception ring buffer from Section 8. Then drill the other design/systems problems with the **C++** tab.
