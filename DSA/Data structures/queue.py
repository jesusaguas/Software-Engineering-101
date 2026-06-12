from collections import deque
from queue import Queue, SimpleQueue


# ==============================================================================
# QUEUES
# ==============================================================================

"""
PYTHON QUEUE OPERATIONS - TIME COMPLEXITY TABLE
===============================================

Let:
n = number of elements in the queue

+----------------------------------+----------------------------------+-------------+--------------------------------------------------+
| Operation                        | Example                          | Complexity  | Explanation                                      |
+----------------------------------+----------------------------------+-------------+--------------------------------------------------+
| Enqueue (deque)                  | q.append(x)                      | O(1)        | Fast append on right                             |
| Dequeue (deque)                  | q.popleft()                      | O(1)        | Fast pop on left                                 |
| Pop right (deque)                | q.pop()                          | O(1)        | Fast pop on right                                |
| Front/peek (deque)               | q[0]                             | O(1)        | Left-most access                                 |
| Back/rear (deque)                | q[-1]                            | O(1)        | Right-most access
| Middle access (deque)            | q[i]                             | O(n)        | Linear scan                                     |
| Empty check                      | len(q) == 0                      | O(1)        | Length stored internally                         |
| Size                             | len(q)                           | O(1)        | Direct length read                               |
| Enqueue (list)                   | q.append(x)                      | O(1)*       | Amortized                                        |
| Dequeue (list)                   | q.pop(0)                         | O(n)        | Shifts all remaining elements                    |
| Enqueue (queue.Queue)            | q.put(x)                         | O(1)        | Thread-safe FIFO queue                           |
| Dequeue (queue.Queue)            | q.get()                          | O(1)        | Thread-safe FIFO queue                           |
| Membership test                  | x in q                           | O(n)        | Linear scan                                      |
| Clear (deque)                    | q.clear()                        | O(n)        | Removes references                               |
+----------------------------------+----------------------------------+-------------+--------------------------------------------------+

IMPORTANT NOTES
---------------

1) For interview DSA code, prefer collections.deque for queues.
2) Avoid list.pop(0) for large inputs: it is O(n).
3) Queue is FIFO: First In, First Out.
4) Use queue.Queue / SimpleQueue for multi-threading scenarios.
"""

# 1) QUEUE BASICS (DEQUE-BASED)
q = deque()
q.append(10)  # enqueue
q.append(20)
q.append(30)
print(q)  # deque([10, 20, 30])

front = q[0]  # peek/front
print(front)  # 10

removed = q.popleft()  # dequeue
print(removed)  # 10
print(q)  # deque([20, 30])

print(len(q) == 0)  # False

## Can create a queue from an array
q2 = deque([1, 2, 3])
print(q2)  # deque([1, 2, 3])


# 2) SAFE HELPERS (avoid IndexError on empty queue)
def safe_dequeue(queue_deque):
    if not queue_deque:
        return None
    return queue_deque.popleft()


def safe_front(queue_deque):
    if not queue_deque:
        return None
    return queue_deque[0]


def safe_rear(queue_deque):
    if not queue_deque:
        return None
    return queue_deque[-1]


print(safe_front(q))      # 20
print(safe_rear(q))       # 30
print(safe_dequeue(q))    # 20
print(safe_dequeue(deque()))  # None


# 3) ALTERNATIVE QUEUE IMPLEMENTATIONS
# 3.1 Thread-safe FIFO queue
thread_q = Queue()
thread_q.put("A")
thread_q.put("B")
print(thread_q.get())  # A

# 3.2 Simpler thread-safe FIFO queue
simple_q = SimpleQueue()
simple_q.put(100)
simple_q.put(200)
print(simple_q.get())  # 100


# 4) CLASSIC USE CASE: SIMULATE PROCESSING ORDER (FIFO)
def process_tasks(tasks):
    dq = deque(tasks)
    order = []
    while dq:
        order.append(dq.popleft())
    return order


print(process_tasks(["task1", "task2", "task3"]))  # ['task1', 'task2', 'task3']


# 5) IMPLEMENT CIRCULAR QUEUE (LeetCode 622 style)
# Description: Fixed-size circular queue with O(1) operations.
class MyCircularQueue:
    def __init__(self, k):
        self.k = k
        self.data = [0] * k
        self.head = 0
        self.count = 0

    def en_queue(self, value):
        if self.is_full():
            return False
        tail = (self.head + self.count) % self.k
        self.data[tail] = value
        self.count += 1
        return True

    def de_queue(self):
        if self.is_empty():
            return False
        self.head = (self.head + 1) % self.k
        self.count -= 1
        return True

    def front(self):
        if self.is_empty():
            return -1
        return self.data[self.head]

    def rear(self):
        if self.is_empty():
            return -1
        tail = (self.head + self.count - 1) % self.k
        return self.data[tail]

    def is_empty(self):
        return self.count == 0

    def is_full(self):
        return self.count == self.k


cq = MyCircularQueue(3)
print(cq.en_queue(1))  # True
print(cq.en_queue(2))  # True
print(cq.en_queue(3))  # True
print(cq.en_queue(4))  # False
print(cq.rear())       # 3
print(cq.is_full())    # True
print(cq.de_queue())   # True
print(cq.en_queue(4))  # True
print(cq.rear())       # 4


# 6) IMPLEMENT QUEUE USING TWO STACKS (LeetCode 232)
# Description: Use two stacks to achieve FIFO order. Amortized O(1) per operation.
class MyQueue:
    def __init__(self):
        self.in_stack = []
        self.out_stack = []

    def _shift(self):
        if not self.out_stack:
            while self.in_stack:
                self.out_stack.append(self.in_stack.pop())

    def push(self, x):
        self.in_stack.append(x)

    def pop(self):
        self._shift()
        if not self.out_stack:
            return None
        return self.out_stack.pop()

    def peek(self):
        self._shift()
        if not self.out_stack:
            return None
        return self.out_stack[-1]

    def empty(self):
        return not self.in_stack and not self.out_stack


mq = MyQueue()
mq.push(1)
mq.push(2)
print(mq.peek())   # 1
print(mq.pop())    # 1
print(mq.empty())  # False


# 7) BFS TRAVERSAL OF GRAPH (QUEUE CORE PATTERN)
def bfs(graph, start):
    visited = set([start])
    order = []
    dq = deque([start])

    while dq:
        node = dq.popleft()
        order.append(node)
        for nei in graph.get(node, []):
            if nei not in visited:
                visited.add(nei)
                dq.append(nei)
    return order


graph = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [],
    "E": [],
    "F": []
}
print(bfs(graph, "A"))  # ['A', 'B', 'C', 'D', 'E', 'F']


# 8) BINARY TREE LEVEL ORDER TRAVERSAL (LeetCode 102)
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def level_order(root):
    if not root:
        return []

    ans = []
    dq = deque([root])

    while dq:
        level_size = len(dq)
        level = []
        for _ in range(level_size):
            node = dq.popleft()
            level.append(node.val)
            if node.left:
                dq.append(node.left)
            if node.right:
                dq.append(node.right)
        ans.append(level)

    return ans


root = TreeNode(1, TreeNode(2), TreeNode(3, TreeNode(4), TreeNode(5)))
print(level_order(root))  # [[1], [2, 3], [4, 5]]


# 9) MULTI-SOURCE BFS ON GRID (Shortest distance to nearest 0)
# Description: Enqueue all 0s as sources, then BFS to fill distances for 1s.
def nearest_zero_distance(mat):
    """
    Returns distance of each cell to nearest 0.
    O(m*n), each cell enters queue at most once.
    """
    if not mat or not mat[0]:
        return []

    rows, cols = len(mat), len(mat[0])
    dist = [[-1] * cols for _ in range(rows)]
    dq = deque()

    for r in range(rows):
        for c in range(cols):
            if mat[r][c] == 0:
                dist[r][c] = 0
                dq.append((r, c))

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while dq:
        r, c = dq.popleft()
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                dq.append((nr, nc))
    return dist


print(nearest_zero_distance([[0, 0, 0], [0, 1, 0], [1, 1, 1]]))
# [[0, 0, 0], [0, 1, 0], [1, 2, 1]]


# 10) TOPOLOGICAL SORT (KAHN'S ALGORITHM, DAG) - queue of indegree-0 nodes
# A topological sort of a directed acyclic graph (DAG) is a linear ordering of its vertices such that 
# for every directed edge uv from vertex u to vertex v, u comes before v in the ordering. 
# Kahn's algorithm uses a queue to repeatedly remove nodes with zero indegree and update the indegrees of their neighbors.
# Example: For graph with edges [(0, 1), (0, 2), (1, 3), (2, 3)], valid topological sorts include [0, 1, 2, 3] and [0, 2, 1, 3].
def topological_sort_kahn(n, edges):
    graph = [[] for _ in range(n)]
    indegree = [0] * n

    for u, v in edges:
        graph[u].append(v)
        indegree[v] += 1

    dq = deque(i for i in range(n) if indegree[i] == 0)
    order = []

    while dq:
        u = dq.popleft()
        order.append(u)
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                dq.append(v)

    return order if len(order) == n else []  # empty => cycle detected


print(topological_sort_kahn(4, [(0, 1), (0, 2), (1, 3), (2, 3)]))  # [0,1,2,3] or [0,2,1,3]


# 11) MONOTONIC QUEUE PATTERN: SLIDING WINDOW MAXIMUM (LeetCode 239)
# Description: Given an array of integers nums, and a sliding window of size k which is moving from the very left of the array to the very right. 
# You can only see the k numbers in the window. Each time the sliding window moves right by one position.
# Return an array of the maximum values in each sliding window position.

def max_sliding_window(nums, k):
    """
    Deque stores indices; values are kept in decreasing order.
    Front index is current window max.
    """
    if not nums or k <= 0:
        return []

    dq = deque()  # indices
    ans = []

    for i, x in enumerate(nums):
        # remove indices out of current window
        while dq and dq[0] <= i - k:
            dq.popleft()

        # maintain decreasing values
        while dq and nums[dq[-1]] <= x:
            dq.pop()

        dq.append(i)

        if i >= k - 1:
            ans.append(nums[dq[0]])

    return ans


print(max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3))  # [3,3,5,5,6,7]


# 12) RECENT COUNTER (LeetCode 933)
# Description: Count number of pings in last 3000 ms. Enqueue timestamps, dequeue old ones.
class RecentCounter:
    def __init__(self):
        self.q = deque()

    def ping(self, t):
        self.q.append(t)
        while self.q and self.q[0] < t - 3000:
            self.q.popleft()
        return len(self.q)


rc = RecentCounter()
print(rc.ping(1))     # 1
print(rc.ping(100))   # 2
print(rc.ping(3001))  # 3
print(rc.ping(3002))  # 3


# 13) MOVING AVERAGE FROM DATA STREAM (queue + running sum)
# Description: Maintain a queue of last 'size' values and a running total for O(1) average calculation.
class MovingAverage:
    def __init__(self, size):
        self.size = size
        self.q = deque()
        self.total = 0

    def next(self, val):
        self.q.append(val)
        self.total += val
        if len(self.q) > self.size:
            self.total -= self.q.popleft()
        return self.total / len(self.q)


ma = MovingAverage(3)
print(ma.next(1))   # 1.0
print(ma.next(10))  # 5.5
print(ma.next(3))   # 4.666...
print(ma.next(5))   # 6.0


# 14) ROUND-ROBIN SCHEDULING (queue rotation pattern)
# Description: Simulate round-robin CPU scheduling. Each task gets a time slice (quantum). If it doesn't finish, re-enqueue with remaining time.
def round_robin(tasks, quantum):
    """
    tasks: list of (name, time)
    Returns execution order chunks.
    """
    dq = deque(tasks)
    timeline = []

    while dq:
        name, remaining = dq.popleft()
        used = min(quantum, remaining)
        timeline.append((name, used))
        remaining -= used
        if remaining > 0:
            dq.append((name, remaining))

    return timeline


print(round_robin([("P1", 5), ("P2", 3), ("P3", 7)], 2))
# [('P1', 2), ('P2', 2), ('P3', 2), ('P1', 2), ('P2', 1), ('P3', 2), ('P1', 1), ('P3', 1)]


# 15) CUSTOM QUEUE CLASS (interview style)
class QueueDS:
    def __init__(self):
        self._dq = deque()

    def enqueue(self, x):
        self._dq.append(x)

    def dequeue(self):
        if not self._dq:
            return None
        return self._dq.popleft()

    def front(self):
        if not self._dq:
            return None
        return self._dq[0]

    def rear(self):
        if not self._dq:
            return None
        return self._dq[-1]

    def is_empty(self):
        return len(self._dq) == 0

    def size(self):
        return len(self._dq)


# 16) PERFORMANCE TIPS + COMMON PITFALLS
# PERFORMANCE TIPS
# - Prefer collections.deque for O(1) enqueue/dequeue at ends.
# - Avoid list.pop(0) in DSA problems (O(n)).
# - For BFS, mark visited when ENQUEUING (not when dequeuing) to prevent duplicates.
# - In sliding window problems, store indices (not values) to track expiration.
# - In topological sort, enqueue nodes exactly when indegree becomes 0.

# COMMON PITFALLS
# 1) Forgetting empty checks before popleft() -> IndexError.
# 2) Using stack order accidentally (append/pop) when FIFO is required.
# 3) Not removing out-of-window indices in monotonic queue problems.
# 4) In BFS level traversal, not capturing current level size.
# 5) In circular queue, incorrect modulo arithmetic for head/tail.