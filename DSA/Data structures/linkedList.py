from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable, Tuple


# ==============================================================================
# LINKED LISTS
# ==============================================================================

"""
LINKED LIST OPERATIONS - TIME COMPLEXITY TABLE
==============================================

Let:
n = number of nodes

+---------------------------------------+--------------------------------------+-------------+--------------------------------------------------+
| Operation                             | Example                              | Complexity  | Explanation                                      |
+---------------------------------------+--------------------------------------+-------------+--------------------------------------------------+
| Access i-th node                      | get(i)                               | O(n)        | Must traverse from head                          |
| Search value                          | find(x)                              | O(n)        | Linear scan                                      |
| Insert at head                        | prepend(x)                           | O(1)        | Pointer update only                              |
| Insert at tail (with tail pointer)    | append(x)                            | O(1)        | No traversal needed                              |
| Insert at tail (without tail pointer) | append(x)                            | O(n)        | Must walk to end                                 |
| Delete head                           | head = head.next                     | O(1)        | Pointer move                                     |
| Delete by value/index                 | delete(x) / delete_at(i)             | O(n)        | Need predecessor                                 |
| Reverse list                          | reverse(head)                        | O(n)        | One pass pointer rewiring                        |
| Detect cycle                          | has_cycle(head)                      | O(n)        | Floyd slow/fast pointers                         |
| Find middle                           | middle_node(head)                    | O(n)        | Slow/fast pointers                               |
| Merge two sorted lists                | merge(l1, l2)                        | O(n + m)    | Single linear merge                              |
+---------------------------------------+--------------------------------------+-------------+--------------------------------------------------+

SENIOR INTERVIEW NOTES
----------------------

1. Linked list questions mostly test pointer discipline and edge cases.
2. Always clarify: singly/doubly, sorted/unsorted, mutable/immutable.
3. Use a dummy node to simplify head modifications and avoid branch-heavy code.
4. Write and maintain loop invariants while coding.
5. For in-place operations, reason in terms of local pointer rewiring.
"""


# ------------------------------------------------------------------------------
# 1) NODE DEFINITIONS
# ------------------------------------------------------------------------------


@dataclass
class ListNode:
	value: int
	next: Optional["ListNode"] = None


@dataclass
class DoublyListNode:
	value: int
	prev: Optional["DoublyListNode"] = None
	next: Optional["DoublyListNode"] = None


# ------------------------------------------------------------------------------
# 2) HELPER UTILITIES (BUILD / PRINT)
# ------------------------------------------------------------------------------


def build_singly(values: Iterable[int]) -> Optional[ListNode]:
	dummy = ListNode(0)
	cur = dummy
	for v in values:
		cur.next = ListNode(v)
		cur = cur.next
	return dummy.next


def to_list(head: Optional[ListNode]) -> list[int]:
	out: list[int] = []
	cur = head
	while cur:
		out.append(cur.value)
		cur = cur.next
	return out


def print_list(head: Optional[ListNode]) -> None:
	vals = to_list(head)
	print(" -> ".join(map(str, vals)) if vals else "EMPTY")


# ------------------------------------------------------------------------------
# 3) MINIMAL SINGLY LINKED LIST CLASS
# ------------------------------------------------------------------------------


class SinglyLinkedList:
	def __init__(self) -> None:
		self.head: Optional[ListNode] = None
		self.tail: Optional[ListNode] = None
		self.size = 0

	def prepend(self, value: int) -> None:
		node = ListNode(value, self.head)
		self.head = node
		if self.tail is None:
			self.tail = node
		self.size += 1

	def append(self, value: int) -> None:
		node = ListNode(value)
		if self.tail is None:
			self.head = self.tail = node
		else:
			self.tail.next = node
			self.tail = node
		self.size += 1

	def find(self, target: int) -> Optional[ListNode]:
		cur = self.head
		while cur:
			if cur.value == target:
				return cur
			cur = cur.next
		return None

	## Deletes first occurrence of target value. Returns True if deleted, False if not found.
	def delete_first(self, target: int) -> bool:
		dummy = ListNode(0, self.head)
		prev, cur = dummy, self.head

		while cur:
			if cur.value == target:
				prev.next = cur.next
				if cur == self.tail:
					self.tail = prev if prev != dummy else None
				self.head = dummy.next
				self.size -= 1
				if self.size == 0:
					self.tail = None
				return True
			prev, cur = cur, cur.next

		self.head = dummy.next
		return False

	def reverse(self) -> None:
		prev = None
		cur = self.head
		self.tail = self.head

		while cur:
			nxt = cur.next
			cur.next = prev
			prev = cur
			cur = nxt

		self.head = prev


# ------------------------------------------------------------------------------
# 4) CORE INTERVIEW PATTERNS (SINGLY LIST)
# ------------------------------------------------------------------------------

## Leetcode 206 - Reverse Linked List
## Description: Reverses list in-place and returns new head -> Standard iterative approach.
def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
	prev = None
	cur = head
	while cur:
		nxt = cur.next
		cur.next = prev
		prev = cur
		cur = nxt
	return prev

## Leetcode 876 - Middle of the Linked List
## Description: Returns middle node (second of two if even length) -> Slow/fast pointer pattern.
def middle_node(head: Optional[ListNode]) -> Optional[ListNode]:
	slow = fast = head
	while fast and fast.next:
		slow = slow.next
		fast = fast.next.next
	return slow

## Leetcode 141 - Linked List Cycle
## Description: Detects if cycle exists -> Floyd's Tortoise and Hare algorithm.
def has_cycle(head: Optional[ListNode]) -> bool:
	slow = fast = head
	while fast and fast.next:
		slow = slow.next
		fast = fast.next.next
		if slow == fast:
			return True
	return False


## Leetcode 142 - Linked List Cycle II
## Description: If cycle exists, returns start node of cycle -> After detection, reset one pointer to head and move both at 1x until they meet.
def cycle_start(head: Optional[ListNode]) -> Optional[ListNode]:
	slow = fast = head
	while fast and fast.next:
		slow = slow.next
		fast = fast.next.next
		if slow == fast:
			break
	else: ## In Python, the else block on a while loop runs only if the loop finishes without hitting a break.
		return None

    ## At this point, slow and fast have met inside the cycle. 
	# To find the start of the cycle we reset one pointer to the head and move both pointers at the same speed. 
	# They will meet at the start of the cycle.
	p1, p2 = head, slow
	while p1 != p2:
		p1 = p1.next
		p2 = p2.next
	return p1

## Leetcode 21 - Merge Two Sorted Lists
## Description: Merges two sorted lists into one sorted list -> Standard merge pattern, dummy head, tail pointing to last node of merged list.
def merge_two_sorted(
	l1: Optional[ListNode], l2: Optional[ListNode]
) -> Optional[ListNode]:
	dummy = ListNode(0)
	tail = dummy

	while l1 and l2:
		if l1.value <= l2.value:
			tail.next = l1
			l1 = l1.next
		else:
			tail.next = l2
			l2 = l2.next
		tail = tail.next

	tail.next = l1 if l1 else l2
	return dummy.next


## Leetcode 19 - Remove Nth Node From End of List
## Description: Removes the n-th node from the end of list using two-pointer technique.
def remove_nth_from_end(head: Optional[ListNode], n: int) -> Optional[ListNode]:
	dummy = ListNode(0, head)
	slow = fast = dummy

	for _ in range(n):
		if fast.next is None:
			return head
		fast = fast.next

	while fast.next:
		slow = slow.next
		fast = fast.next

	slow.next = slow.next.next
	return dummy.next


## Leetcode 86 - Partition List
## Description: Keep relative order while partitioning around x. Nodes < x come first, then nodes >= x.
def partition_list(head: Optional[ListNode], x: int) -> Optional[ListNode]:
	"""
	Keep relative order while partitioning around x.
	Nodes < x come first, then nodes >= x.
	"""
	less_dummy = ListNode(0)
	greater_dummy = ListNode(0)
	less_tail, greater_tail = less_dummy, greater_dummy
	cur = head

	while cur:
		nxt = cur.next
		cur.next = None
		if cur.value < x:
			less_tail.next = cur
			less_tail = cur
		else:
			greater_tail.next = cur
			greater_tail = cur
		cur = nxt

	less_tail.next = greater_dummy.next
	return less_dummy.next


## Leetcode 143 - Reorder List
## Description: Reorder as: L0 -> Ln -> L1 -> Ln-1 -> ...
def reorder_list(head: Optional[ListNode]) -> Optional[ListNode]:
	"""
	Reorder as: L0 -> Ln -> L1 -> Ln-1 -> ...
	"""
	if head is None or head.next is None:
		return head

	# 1) Find middle
	slow = fast = head
	while fast and fast.next:
		slow = slow.next
		fast = fast.next.next

	# 2) Reverse second half
	second = reverse_list(slow.next)
	slow.next = None

	# 3) Merge alternating
	first = head
	while second:
		t1, t2 = first.next, second.next
		first.next = second
		second.next = t1
		first, second = t1, t2

	return head


## Leetcode 234 - Palindrome Linked List
## Description: Check if list is a palindrome by reversing second half and comparing.
def is_palindrome_list(head: Optional[ListNode]) -> bool:
	if head is None or head.next is None:
		return True

	slow = fast = head
	while fast and fast.next:
		slow = slow.next
		fast = fast.next.next

	second_half = reverse_list(slow)
	copy_second = second_half

	p1, p2 = head, second_half
	is_pal = True
	while p2:
		if p1.value != p2.value:
			is_pal = False
			break
		p1 = p1.next
		p2 = p2.next

	reverse_list(copy_second)
	return is_pal


## Leetcode 160 - Intersection of Two Linked Lists
## Description: Two-pointer switching trick: pointer A goes A->B, pointer B goes B->A. If intersection exists, they meet there; else both end at None.
def intersection_node(
	head_a: Optional[ListNode], head_b: Optional[ListNode]
) -> Optional[ListNode]:
	"""
	Two-pointer switching trick:
	pointer A goes A->B, pointer B goes B->A.
	If intersection exists, they meet there; else both end at None.
	"""
	a, b = head_a, head_b
	while a != b:
		a = a.next if a else head_b
		b = b.next if b else head_a
	return a


# ------------------------------------------------------------------------------
# 5) DOUBLY LINKED LIST (INTERVIEW-USEFUL SKELETON)
# ------------------------------------------------------------------------------


class DoublyLinkedList:
	"""
	Useful for LRU cache style problems where delete/move must be O(1)
	when node reference is known.
	"""

	def __init__(self) -> None:
		self.head = DoublyListNode(0)
		self.tail = DoublyListNode(0)
		self.head.next = self.tail
		self.tail.prev = self.head

	def _insert_after(self, prev_node: DoublyListNode, node: DoublyListNode) -> None:
		nxt = prev_node.next
		prev_node.next = node
		node.prev = prev_node
		node.next = nxt
		nxt.prev = node

	def _remove(self, node: DoublyListNode) -> None:
		prev_node, next_node = node.prev, node.next
		prev_node.next = next_node
		next_node.prev = prev_node
		node.prev = node.next = None

	def append_left(self, value: int) -> DoublyListNode:
		node = DoublyListNode(value)
		self._insert_after(self.head, node)
		return node

	def pop_right(self) -> Optional[DoublyListNode]:
		if self.tail.prev == self.head:
			return None
		node = self.tail.prev
		self._remove(node)
		return node


# ------------------------------------------------------------------------------
# 6) SENIOR INTERVIEW CHECKLIST
# ------------------------------------------------------------------------------

"""
When solving a linked list question under pressure:

1) Ask clarifying questions:
   - Empty list?
   - Single node?
   - Can values repeat?
   - Should list be restored after check (e.g., palindrome)?

2) Pick a pattern:
   - Dummy node for deletions around head
   - Slow/fast for middle or cycle
   - In-place reverse for reorder/palindrome
   - Two pointers with offset for k-th from end

3) State complexity explicitly:
   - Time O(n), Space O(1) if in-place

4) Validate with edge cases:
   - []
   - [x]
   - [x, y]
   - odd/even length
   - deleting head/tail
"""