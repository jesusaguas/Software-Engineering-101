from collections import deque
from queue import LifoQueue

# ==============================================================================
# STACKS
# ==============================================================================

"""
PYTHON STACK OPERATIONS - TIME COMPLEXITY TABLE
===============================================

Let:
n = number of elements in the stack

+----------------------------------+-----------------------------+-------------+------------------------------------------------------+
| Operation                        | Example                     | Complexity  | Explanation                                          |
+----------------------------------+-----------------------------+-------------+------------------------------------------------------+
| Push (list)                      | stack.append(x)             | O(1)*       | Amortized; occasional resize                         |
| Pop (list)                       | stack.pop()                 | O(1)        | Removes top element                                  |
| Peek/top (list)                  | stack[-1]                   | O(1)        | Last element access                                  |
| Empty check                      | len(stack) == 0             | O(1)        | Length is stored                                     |
| Size                             | len(stack)                  | O(1)        | Direct length read                                   |
| Push (deque)                     | dq.append(x)                | O(1)        | Fast append at right                                 |
| Pop (deque)                      | dq.pop()                    | O(1)        | Fast pop at right                                    |
| Peek/top (deque)                 | dq[-1]                      | O(1)        | Right-most element                                   |
| Push (LifoQueue)                 | q.put(x)                    | O(1)        | Thread-safe overhead                                 |
| Pop (LifoQueue)                  | q.get()                     | O(1)        | Thread-safe overhead                                 |
| Membership test                  | x in stack                  | O(n)        | Linear scan                                          |
| Clear                            | stack.clear()               | O(n)        | Removes references                                   |
+----------------------------------+-----------------------------+-------------+------------------------------------------------------+

IMPORTANT NOTES
---------------

1. In Python interviews, the default stack is usually a list:
    stack = []
    stack.append(x)    # push
    stack.pop()        # pop

2. list is preferred for single-threaded DSA/interview usage.
   Use deque if you also need queue operations.
   Use LifoQueue for thread-safe producer-consumer code.

3. Never use list.pop(0) for stack/queue in large inputs (O(n) shift).

4. Stack is LIFO: Last In, First Out.
"""

# 1. STACK BASICS (LIST-BASED STACK)
stack = []
stack.append(10)  # push
stack.append(20)
stack.append(30)
print(stack)      # [10, 20, 30]

top = stack[-1]   # peek
print(top)        # 30

popped = stack.pop()
print(popped)     # 30
print(stack)      # [10, 20]

print(len(stack) == 0)  # False


# 2. SAFE POP / SAFE PEEK HELPERS
## These guard against popping/peeking from an empty stack, which raises IndexError.
def safe_pop(stack_list):
    if not stack_list:
     return None
    return stack_list.pop()


def safe_peek(stack_list):
    if not stack_list:
     return None
    return stack_list[-1]


print(safe_peek(stack))  # 20
print(safe_pop(stack))   # 20
print(safe_pop([]))      # None


# 3. ALTERNATIVE STACK IMPLEMENTATIONS
# 3.1 deque-based stack
dq_stack = deque()
dq_stack.append(1)
dq_stack.append(2)
print(dq_stack.pop())  # 2

# 3.2 thread-safe stack with LifoQueue
## Thread-safe means it can be safely used across multiple threads without race conditions
q_stack = LifoQueue()
q_stack.put("A")
q_stack.put("B")
print(q_stack.get())   # B


# 4. CLASSIC STACK USE CASE: REVERSE DATA
def reverse_string(s):
    st = list(s)
    out = []
    while st:
     out.append(st.pop())
    return "".join(out)


print(reverse_string("stack"))  # "kcats"


# 5. BALANCED BRACKETS / VALID PARENTHESES (LeetCode 20)
def is_valid_parentheses(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    st = []

    for ch in s:
     if ch in "([{":
         st.append(ch)
     elif ch in pairs:
         if not st or st[-1] != pairs[ch]:
          return False
         st.pop()
    return len(st) == 0


print(is_valid_parentheses("()[]{}"))  # True
print(is_valid_parentheses("(]"))      # False


# 6. MIN STACK (LeetCode 155)
# Description: Design a stack that supports push, pop, top, getMin in O(1)
class MinStack:
    def __init__(self):
     self.stack = []
     self.min_stack = []

    def push(self, val):
     self.stack.append(val)
     if not self.min_stack:
         self.min_stack.append(val)
     else:
         self.min_stack.append(min(val, self.min_stack[-1]))

    def pop(self):
     if not self.stack:
         return None
     self.min_stack.pop()
     return self.stack.pop()

    def top(self):
     if not self.stack:
         return None
     return self.stack[-1]

    def get_min(self):
     if not self.min_stack:
         return None
     return self.min_stack[-1]


ms = MinStack()
ms.push(3)
ms.push(5)
ms.push(2)
ms.push(4)
print(ms.get_min())  # 2
ms.pop()
ms.pop()
print(ms.get_min())  # 3


# 7. MONOTONIC STACK PATTERN (INCREASING / DECREASING)
# Core interview pattern for "next greater/smaller" problems.

# 7.1 Next Greater Element to the RIGHT for each index
# For each nums[i], find first element to the right that is greater; else -1.
def next_greater_right(nums):
    n = len(nums)
    ans = [-1] * n
    st = []  # stack holds indices; values are decreasing in stack

    for i in range(n):
     while st and nums[i] > nums[st[-1]]:
         idx = st.pop()
         ans[idx] = nums[i]
     st.append(i)
    return ans


print(next_greater_right([2, 1, 2, 4, 3]))  # [4, 2, 4, -1, -1]


# 7.2 Next Greater Element to the LEFT for each index
def next_greater_left(nums):
    ans = [-1] * len(nums)
    st = []  # decreasing stack of values

    for i, x in enumerate(nums):
     while st and st[-1] <= x:
         st.pop()
     ans[i] = st[-1] if st else -1
     st.append(x)
    return ans


print(next_greater_left([2, 1, 2, 4, 3]))  # [-1, 2, -1, -1, 4]


# 8. DAILY TEMPERATURES (LeetCode 739)
# Description: Given a list of daily temperatures T, return a list such that, 
# for each day in the input, tells you how many days you would have to wait until a warmer temperature. 
# If there is no future day for which this is possible, put 0 instead.
def daily_temperatures(temperatures):
    n = len(temperatures)
    ans = [0] * n
    st = []  # indices with decreasing temperatures

    for i, t in enumerate(temperatures):
     while st and t > temperatures[st[-1]]:
         idx = st.pop()
         ans[idx] = i - idx
     st.append(i)
    return ans


print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))
# [1, 1, 4, 2, 1, 1, 0, 0]


# 9. NEXT GREATER ELEMENT I (LeetCode 496)
# Description: You are given two distinct 0-indexed integer arrays nums1 and nums2, where nums1 is a subset of nums2.
# For each value in nums1, determine the next greater element of it in nums2
def next_greater_element(nums1, nums2):
    st = []
    ng = {}  # value -> next greater value in nums2

    for x in nums2:
     while st and x > st[-1]:
         ng[st.pop()] = x
     st.append(x)

    while st:
     ng[st.pop()] = -1

    return [ng[x] for x in nums1]

print(next_greater_element([4, 1, 2], [1, 3, 4, 2]))  # [-1, 3, -1]


# 10. LARGEST RECTANGLE IN HISTOGRAM (LeetCode 84)
# Given an array of integers heights representing the histogram's bar height where the width of each bar is 1, 
# return the area of the largest rectangle in the histogram.
def largest_rectangle_area(heights):
    st = []
    max_area = 0
    arr = heights + [0]  # sentinel to flush stack

    for i, h in enumerate(arr):
     while st and arr[st[-1]] > h:
         height = arr[st.pop()]
         left = st[-1] if st else -1
         width = i - left - 1
         max_area = max(max_area, height * width)
     st.append(i)
    return max_area


print(largest_rectangle_area([2, 1, 5, 6, 2, 3]))  # 10


# 11. EVALUATE REVERSE POLISH NOTATION (LeetCode 150)
# Description: Evaluate the value of an arithmetic expression in Reverse Polish Notation.
def eval_rpn(tokens):
    st = []
    for token in tokens:
     if token in {"+", "-", "*", "/"}:
         b = st.pop()
         a = st.pop()
         if token == "+":
          st.append(a + b)
         elif token == "-":
          st.append(a - b)
         elif token == "*":
          st.append(a * b)
         else:
          # Truncate toward zero (LeetCode behavior)
          st.append(int(a / b))
     else:
         st.append(int(token))
    return st[-1]


print(eval_rpn(["2", "1", "+", "3", "*"]))  # 9


# 12. SIMPLIFY PATH (LeetCode 71)
# Description: Given an absolute path for a file (Unix-style), simplify it.
# For example, path = "/a/./b/../../c/" simplifies to "/c".
def simplify_path(path):
    st = []
    for part in path.split("/"):
     if part == "" or part == ".":
         continue
     if part == "..":
         if st:
          st.pop()
     else:
         st.append(part)
    return "/" + "/".join(st)


print(simplify_path("/a/./b/../../c/"))  # "/c"


# 13. ITERATIVE DFS USING STACK
# Common interview requirement: avoid recursion depth issues.
def dfs_iterative(graph, start):
    visited = set()
    order = []
    st = [start]

    while st:
     node = st.pop()
     if node in visited:
         continue
     visited.add(node)
     order.append(node)

     # reverse to mimic recursive DFS order when needed
     for nei in reversed(graph.get(node, [])):
         if nei not in visited:
          st.append(nei)
    return order


graph = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [],
    "E": [],
    "F": []
}
print(dfs_iterative(graph, "A"))


# 14. CUSTOM STACK CLASS (OPTIONAL INTERVIEW STYLE)
class Stack:
    def __init__(self):
     self._data = []

    def push(self, x):
     self._data.append(x)

    def pop(self):
     if not self._data:
         return None
     return self._data.pop()

    def peek(self):
     if not self._data:
         return None
     return self._data[-1]

    def is_empty(self):
     return len(self._data) == 0

    def size(self):
     return len(self._data)


# 15. PERFORMANCE TIPS
# - Prefer list.append()/list.pop() for DSA interview stacks.
# - Avoid insert(0)/pop(0): these are O(n).
# - For heavy string building, stack/list + ''.join(...) is efficient.
# - Monotonic stack problems are usually O(n): each index pushed/popped once.
# - Use sentinel values (e.g., appended 0) to simplify boundary handling.


# 16. COMMON PITFALLS
# 1) Popping from empty stack -> IndexError (guard with if stack).
# 2) Forgetting to pop when matching parentheses.
# 3) In monotonic stack, storing values instead of indices when index is required.
# 4) Not handling final flush step in histogram/next-greater variants.
# 5) Confusing queue (FIFO) with stack (LIFO).