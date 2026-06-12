from collections import Counter, deque
from itertools import count

from heapq import (
    heapify,
    heappop,
    heappush,
    heappushpop,
    heapreplace,
    merge,
    nlargest,
    nsmallest,
)
import math

# ==============================================================================
# PYTHON HEAPS (heapq)
# ==============================================================================

"""
PYTHON HEAP OPERATIONS - TIME COMPLEXITY TABLE
==============================================

Let:
n = number of elements in the heap
k = requested number of elements

+-----------------------------------+---------------------------------------------+-------------+--------------------------------------------------------+
| Operation                         | Example                                     | Complexity  | Explanation                                            |
+-----------------------------------+---------------------------------------------+-------------+--------------------------------------------------------+
| Build heap from list              | heapify(arr)                                | O(n)        | In-place linear-time heap construction                 |
| Push                              | heappush(h, x)                              | O(log n)    | Sifts up to maintain heap property                     |
| Pop minimum                       | heappop(h)                                  | O(log n)    | Removes root, sifts down                               |
| Peek minimum                      | h[0]                                        | O(1)        | Root of min-heap                                       |
| Push then pop (faster combo)      | heappushpop(h, x)                           | O(log n)    | One combined adjust                                    |
| Pop then push (replace root)      | heapreplace(h, x)                           | O(log n)    | Always pops first, then pushes                         |
| k smallest / largest              | nsmallest(k, arr), nlargest(k, arr)         | O(n log k)  | Better than full sort when k << n                      |
| Merge sorted iterables            | merge(a, b, c...)                           | O(total n)  | Lazy k-way merge                                       |
| Heap sort via repeated pop        | while h: heappop(h)                         | O(n log n)  | Not in-place sort in Python                            |
+-----------------------------------+---------------------------------------------+-------------+--------------------------------------------------------+

IMPORTANT NOTES
---------------
1. Python's heapq is a MIN-heap.
2. There is no built-in decrease-key operation.
3. For MAX-heap behavior, push negative numbers or use tuple transformations.
4. Heaps are great for:
   - Top K
   - Streaming min/max
   - Priority queue scheduling
   - Dijkstra / A* / best-first search
   - K-way merge
"""

# 1) HEAP BASICS
nums = [5, 1, 9, 3, 7]
heapify(nums)  # O(n), in-place
print(nums)    # heap layout; only nums[0] guaranteed to be smallest
print(nums[0]) # peek min, O(1)

heappush(nums, 2)  # O(log n)
print(heappop(nums))  # 1, O(log n)

## You can store arbitrary data in the heap while ordering by a priority key
heap = []
my_object = {"id": 1, "name": "task"}
priority = 5
heappush(heap, (priority, my_object)) 
priority, obj = heappop(heap)

## You can push tuples for multi-key sorting (e.g. by count, then value):
heap = []
for x in [5, 1, 9, 3]:
    heappush(heap, (x % 3, x))  # sort by x mod 3, then by x
print(heappop(heap))  # (0, 3) - smallest mod 3 is 0, tie-break by value

# 2) MIN-HEAP VS MAX-HEAP
# heapq is min-heap only.
# Max-heap trick: store negatives.
max_heap = []
for x in [5, 1, 9, 3]:
    heappush(max_heap, -x)
print(-heappop(max_heap))  # 9
print(-heappop(max_heap))  # 5

# 3) PUSH/POP COMBINATIONS
h = [2, 4, 7]
heapify(h)

# heappushpop: push first, then pop smallest (good when maintaining top-k largest via min-heap)
print(heappushpop(h, 6))  # returns 2
print(h)

# heapreplace: pop first, then push new item (heap must be non-empty)
print(heapreplace(h, 10))  # pops current min
print(h)

# 4) TOP-K PATTERNS
def kth_largest(nums, k):
    """Return k-th largest element using min-heap of size k. O(n log k)."""
    heap = []
    for x in nums:
        if len(heap) < k:
            heappush(heap, x)
        elif x > heap[0]:
            heapreplace(heap, x)
    return heap[0]


def top_k_largest(nums, k):
    """Return k largest numbers in descending order."""
    return nlargest(k, nums)

def top_k_largestV2(nums, k):
    """Return k largest numbers in descending order."""
    heap = []
    for x in nums:
        if len(heap) < k:
            heappush(heap, x)
        elif x > heap[0]:
            heapreplace(heap, x)
    return sorted(heap, reverse=True) # O(k log k) to sort final k elements

def top_k_smallest(nums, k):
    """Return k smallest numbers in ascending order."""
    return nsmallest(k, nums)

def top_k_smallest_v2(nums, k):
    """Return k smallest numbers in ascending order."""
    heap = []
    for x in nums:
        if len(heap) < k:
            heappush(heap, -x)  # max-heap via negatives
        elif x < -heap[0]:
            heapreplace(heap, -x)
    return sorted([-x for x in heap])  # O(k log k)


print(kth_largest([3, 2, 1, 5, 6, 4], 2))  # 5
print(top_k_largest([9, 1, 7, 3, 8, 4], 3))  # [9, 8, 7]
print(top_k_smallest([9, 1, 7, 3, 8, 4], 3))  # [1, 3, 4]

# 5) PRIORITY QUEUE WITH TIE-BREAKER
# Common in production/interviews: deterministic order when priorities tie.
class PriorityQueue:
    """
    Min-priority queue:
    smaller priority number == higher priority.
    """
    def __init__(self):
        self.heap = []
        self._seq = count()  # tie-breaker sequence, count() returns 0, 1, 2, ... on each call

    def push(self, priority, item):
        heappush(self.heap, (priority, next(self._seq), item)) # tie-breaker ensures FIFO order for same priority

    def pop(self):
        if not self.heap:
            return None
        _, _, item = heappop(self.heap)
        return item

    def peek(self):
        return self.heap[0][2] if self.heap else None

    def __len__(self):
        return len(self.heap)

pq = PriorityQueue()
pq.push(2, "low")
pq.push(1, "high-A")
pq.push(1, "high-B")
print(pq.pop())  # high-A
print(pq.pop())  # high-B


# 6) K-WAY MERGE OF SORTED LISTS
# Description: Given k sorted lists, merge them into one sorted list. 
# Common in external sorting, merging log files, or combining results from multiple sources.

def merge_k_sorted_lists(lists):
    """Merge sorted lists into one sorted list. O(total_n log k) if using heap manually, O(total_n) lazy merge API."""
    return list(merge(*lists)) # merge is a lazy iterator that efficiently merges multiple sorted inputs O(total_n)

def merge_k_sorted_lists_V2(lists): # O(total_n log k) if implemented with manual heap, since we push/pop from heap for each element across k lists.
    """Merge sorted lists into one sorted list using a min-heap."""
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            heappush(heap, (lst[0], i, 0))  # (value, list_index, element_index)

    merged = []
    while heap:
        value, list_idx, elem_idx = heappop(heap)
        merged.append(value)
        if elem_idx + 1 < len(lists[list_idx]):
            next_value = lists[list_idx][elem_idx + 1]
            heappush(heap, (next_value, list_idx, elem_idx + 1))
    return merged

print(merge_k_sorted_lists([[1, 4, 7], [2, 5], [3, 6, 9]]))  # [1, 2, 3, 4, 5, 6, 7, 9]
print(merge_k_sorted_lists_V2([[1, 4, 7], [2, 5], [3, 6, 9]]))  # [1, 2, 3, 4, 5, 6, 7, 9]

# 7) STREAMING PROBLEM: MAINTAIN KTH LARGEST
# Description: Design a class that maintains the k-th largest element in a stream of numbers.
class KthLargest:
    """LeetCode 703 pattern."""
    def __init__(self, k, nums):
        self.k = k
        self.heap = nums[:]
        heapify(self.heap)
        while len(self.heap) > k:
            heappop(self.heap)

    def add(self, val):
        if len(self.heap) < self.k:
            heappush(self.heap, val)
        elif val > self.heap[0]:
            heapreplace(self.heap, val)
        return self.heap[0]


obj = KthLargest(3, [4, 5, 8, 2])
print(obj.add(3))   # 4
print(obj.add(10))  # 5
print(obj.add(9))   # 8

# 8) FREQUENCY + HEAP: TOP K FREQUENT ELEMENTS
def top_k_frequent(nums, k):
    """
    Return k most frequent values. O(n log k).
    """
    freq = Counter(nums)
    heap = []  # (count, value)
    for value, count_val in freq.items():
        if len(heap) < k:
            heappush(heap, (count_val, value))
        elif count_val > heap[0][0]:
            heapreplace(heap, (count_val, value))
    return [value for _, value in sorted(heap, reverse=True)]

## Note, doing it via sorting all frequencies would be O(n log n), so heap is better when k << n.
def top_k_frequent_suboptimal(nums, k):
    freq = Counter(nums)
    items = list(freq.items())  # [(value, count), ...]
    items.sort(key=lambda x: x[1])  # sort by frequency
    return [value for value, _ in items[-k:]] # take last k items, for each unpack the tuple (value, _), and return just the value

print(top_k_frequent([1, 1, 1, 2, 2, 3], 2))  # [1, 2]
print(top_k_frequent_suboptimal([1, 1, 1, 2, 2, 3], 2))  # [1, 2]

# 9) GREEDY + HEAP: CONNECT ROPES WITH MIN COST
def min_cost_to_connect_ropes(ropes):
    """
    Each step connects two smallest ropes.
    Total: O(n log n).
    """
    if not ropes:
        return 0
    heap = ropes[:]
    heapify(heap)
    total = 0
    while len(heap) > 1:
        a = heappop(heap)
        b = heappop(heap)
        s = a + b
        total += s
        heappush(heap, s)
    return total


print(min_cost_to_connect_ropes([4, 3, 2, 6]))  # 29

# 10) DIJKSTRA (SHORTEST PATH, NON-NEGATIVE WEIGHTS)
def dijkstra(n, graph, src):
    """
    graph[u] = list[(v, weight)]
    Returns shortest distance from src to every node.
    Time: O((V + E) log V)
    """
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0

    heap = [(0, src)]  # (distance, node)
    while heap:
        cur_dist, u = heappop(heap)
        if cur_dist != dist[u]:  # stale entry (lazy deletion pattern)
            continue
        for v, w in graph[u]:
            nd = cur_dist + w
            if nd < dist[v]:
                dist[v] = nd
                heappush(heap, (nd, v))
    return dist


graph = [
    [(1, 4), (2, 1)],  # 0
    [(3, 1)],          # 1
    [(1, 2), (3, 5)],  # 2
    []                 # 3
]
print(dijkstra(4, graph, 0))  # [0, 3, 1, 4]

# 11) TWO-HEAP PATTERN: MEDIAN OF DATA STREAM
## Description: Design a class that maintains the median of a stream of numbers. Use two heaps to keep track of the lower and upper halves of the data.
class MedianFinder:
    """
    low  (max-heap via negatives): smaller half
    high (min-heap): larger half
    """
    def __init__(self):
        self.low = []   # max-heap simulated with negatives
        self.high = []  # min-heap

    def add_num(self, num):
        if not self.low or num <= -self.low[0]:
            heappush(self.low, -num)
        else:
            heappush(self.high, num)

        # rebalance sizes: len(low) >= len(high), diff <= 1
        if len(self.low) > len(self.high) + 1:
            heappush(self.high, -heappop(self.low))
        elif len(self.high) > len(self.low):
            heappush(self.low, -heappop(self.high))

    def find_median(self):
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0


mf = MedianFinder()
for x in [1, 2, 3, 4]:
    mf.add_num(x)
    print(mf.find_median())

# 12) INTERVIEW TEMPLATES

def heap_sort_ascending(nums):
    """
    Heap sort (using extra heap in Python): O(n log n), O(n) extra.
    """
    h = nums[:]
    heapify(h)
    out = []
    while h:
        out.append(heappop(h))
    return out


## Example: K closest points to origin (LeetCode 973).
## Description: Given a list of points in the 2D plane, find the k closest points to the origin (0, 0).
def k_closest_points(points, k):
    """
    LeetCode 973.
    Keep max-heap of size k via negative distance.
    """
    heap = []
    for (x, y) in points:
        d = - math.sqrt(x**2+y**2)

        if len(heap) == k:
            heapq.heappushpop(heap, (d, (x,y)))
        else:
            heapq.heappush(heap, (d, (x,y)))

    return [(x, y) for (d, (x,y)) in heap]


print(heap_sort_ascending([5, 3, 8, 1]))
print(k_closest_points([[1, 3], [-2, 2], [2, -2]], 2))

# 13) COMMON PITFALLS
# 1. Assuming heap is fully sorted (it is not).
# 2. Forgetting heapify(list) before pop/push operations on arbitrary lists.
# 3. Using max-heap logic without negating values.
# 4. For custom objects, pushing non-comparable payloads without tie-breakers can raise TypeError.
# 5. No decrease-key in heapq -> push new pair and skip stale entries when popped.
# 6. Using heap when you need fast membership/deletion by value (consider set/dict/balanced tree emulation).

# 14) PERFORMANCE TIPS
# - For repeated top-k on large streams, keep heap size exactly k.
# - Prefer heappushpop over separate push+pop when both are needed.
# - Prefer heapreplace when heap is non-empty and replacement is guaranteed.
# - For already sorted lists merge, use heapq.merge (lazy, memory-efficient).
# - Keep tuples small and avoid heavy objects in tight loops.