from collections import deque

# ==============================================================================
# TREES
# ==============================================================================

## Binary Tree: Each node has at most 2 children (left and right).
## N-ary Tree: A tree where each node can have 0 or more children (not limited to 2).
## Binary Search Tree (BST): A binary tree where left < node < right for all nodes. 
### BST maintains a perfectly sorted dataset while still allowing you to add, remove, and find items incredibly fast.
### Balanced Tree (AVL / Red-Black Tree): A tree where the height difference between left and right subtrees is at most 1 for every node.
## Trie: A tree where each node can have multiple children, often used for prefix storage (e.g. strings).


"""
PYTHON TREE OPERATIONS - TIME COMPLEXITY TABLE
==============================================

Let:
n = number of nodes in the tree
h = height of the tree (balanced: O(log n), skewed: O(n))

+--------------------------------------+--------------------------------------+-------------+--------------------------------------------------+
| Operation                            | Example                              | Complexity  | Explanation                                      |
+--------------------------------------+--------------------------------------+-------------+--------------------------------------------------+
| DFS Traversal (pre/in/post)          | preorder(root)                       | O(n)        | Visits every node once                           |
| BFS Traversal (level order)          | level_order(root)                    | O(n)        | Queue processes each node once                   |
| Search in BST                        | bst_search(root, x)                  | O(h)        | Compare and move left/right                      |
| Insert in BST                        | bst_insert(root, x)                  | O(h)        | Follow search path, attach node                  |
| Delete in BST                        | bst_delete(root, x)                  | O(h)        | May find successor/predecessor                   |
| Min/Max in BST                       | bst_min(root), bst_max(root)         | O(h)        | Walk extreme left/right                          |
| Validate BST                         | is_valid_bst(root)                   | O(n)        | Inorder property or bound checks                 |
| Build tree from traversals           | build_tree(preorder, inorder)        | O(n)        | Hash map + recursion                             |
| Height / Max depth                   | max_depth(root)                      | O(n)        | Explore all nodes                                |
| Balance check                        | is_balanced(root)                    | O(n)        | Bottom-up height checks                          |
| Diameter of binary tree              | diameter_of_binary_tree(root)        | O(n)        | Single DFS tracks longest path                   |
| LCA (Binary Tree)                    | lca_binary_tree(root, p, q)          | O(n)        | DFS to locate split point                        |
| LCA (BST)                            | lca_bst(root, p, q)                  | O(h)        | Use BST ordering                                 |
| Serialize/Deserialize (BT)           | Codec().serialize(root)              | O(n)        | Process all nodes                                |
| Kth smallest in BST                  | kth_smallest(root, k)                | O(h + k)    | Iterative inorder                                |
+--------------------------------------+--------------------------------------+-------------+--------------------------------------------------+

IMPORTANT NOTES
---------------

1) In interviews, start from traversal pattern recognition: DFS recursion, DFS stack, BFS queue.
2) For BST questions, exploit ordering aggressively before using brute force.
3) Clarify constraints: duplicates allowed? node values range? recursion depth risk?
4) For production-level answers, mention stack overflow risk for skewed trees and iterative fallback.
5) For any O(n) DFS, explicitly state space: O(h) recursion stack.
"""


# 1) FOUNDATIONAL NODE DEFINITIONS
class TreeNode:
	def __init__(self, val=0, left=None, right=None):
		self.val = val
		self.left = left
		self.right = right


class NaryNode:
	def __init__(self, val=0, children=None):
		self.val = val
		self.children = children if children is not None else []


# 2) DFS TRAVERSALS (RECURSIVE)
# Preorder: node -> left -> right
def preorder_recursive(root):
	out = []

	def dfs(node):
		if not node:
			return
		out.append(node.val)
		dfs(node.left)
		dfs(node.right)

	dfs(root)
	return out

# Inorder: left -> node -> right
def inorder_recursive(root):
	out = []

	def dfs(node):
		if not node:
			return
		dfs(node.left)
		out.append(node.val)
		dfs(node.right)

	dfs(root)
	return out

# Postorder: left -> right -> node
def postorder_recursive(root):
	out = []

	def dfs(node):
		if not node:
			return
		dfs(node.left)
		dfs(node.right)
		out.append(node.val)

	dfs(root)
	return out


# 3) DFS TRAVERSALS (ITERATIVE)
def preorder_iterative(root):
	if not root:
		return []
	stack = [root]
	out = []

	while stack:
		node = stack.pop()
		out.append(node.val)
		if node.right:
			stack.append(node.right)
		if node.left:
			stack.append(node.left)

	return out


def inorder_iterative(root):
	out = []
	stack = []
	cur = root

	while stack or cur:
		while cur:
			stack.append(cur)
			cur = cur.left
		cur = stack.pop()
		out.append(cur.val)
		cur = cur.right

	return out


def postorder_iterative(root):
	if not root:
		return []
	stack = [root]
	out = []

	while stack:
		node = stack.pop()
		out.append(node.val)
		if node.left:
			stack.append(node.left)
		if node.right:
			stack.append(node.right)

	return out[::-1]


# 4) BFS LEVEL ORDER (QUEUE CORE PATTERN)
def level_order(root):
	if not root:
		return []

	ans = []
	q = deque([root])

	while q:
		level_size = len(q)
		level = []
		for _ in range(level_size):
			node = q.popleft()
			level.append(node.val)
			if node.left:
				q.append(node.left)
			if node.right:
				q.append(node.right)
		ans.append(level)

	return ans


def zigzag_level_order(root):
	if not root:
		return []

	ans = []
	q = deque([root])
	left_to_right = True

	while q:
		level_size = len(q)
		level = deque()
		for _ in range(level_size):
			node = q.popleft()
			if left_to_right:
				level.append(node.val)
			else:
				level.appendleft(node.val)
			if node.left:
				q.append(node.left)
			if node.right:
				q.append(node.right)

		ans.append(list(level))
		left_to_right = not left_to_right

	return ans


# 5) CORE TREE METRICS
def max_depth(root):
	if not root:
		return 0
	return 1 + max(max_depth(root.left), max_depth(root.right))


def min_depth(root):
	if not root:
		return 0
	if not root.left:
		return 1 + min_depth(root.right)
	if not root.right:
		return 1 + min_depth(root.left)
	return 1 + min(min_depth(root.left), min_depth(root.right))


def is_balanced(root):
	"""
	Returns True if for every node, |height(left) - height(right)| <= 1.
	"""

	def height(node):
		if not node:
			return 0
		lh = height(node.left)
		if lh == -1:
			return -1
		rh = height(node.right)
		if rh == -1:
			return -1
		if abs(lh - rh) > 1:
			return -1
		return 1 + max(lh, rh)

	return height(root) != -1


def diameter_of_binary_tree(root):
	"""
	Diameter = number of edges in the longest path between any two nodes.
	"""
	best = 0

	def dfs(node):
		nonlocal best
		if not node:
			return 0
		left_h = dfs(node.left)
		right_h = dfs(node.right)
		best = max(best, left_h + right_h)
		return 1 + max(left_h, right_h)

	dfs(root)
	return best


def max_path_sum(root):
	"""
	Maximum path sum where path can start/end at any nodes.
	"""
	best = float("-inf")

	def gain(node):
		nonlocal best
		if not node:
			return 0
		left_gain = max(gain(node.left), 0)
		right_gain = max(gain(node.right), 0)
		best = max(best, node.val + left_gain + right_gain)
		return node.val + max(left_gain, right_gain)

	gain(root)
	return best


# 6) BST (BINARY SEARCH TREE) OPERATIONS
def bst_search(root, target):
	cur = root
	while cur:
		if target == cur.val:
			return cur
		if target < cur.val:
			cur = cur.left
		else:
			cur = cur.right
	return None


def bst_insert(root, val):
	if not root:
		return TreeNode(val)

	cur = root
	while True:
		if val < cur.val:
			if not cur.left:
				cur.left = TreeNode(val)
				break
			cur = cur.left
		else:
			if not cur.right:
				cur.right = TreeNode(val)
				break
			cur = cur.right

	return root


def bst_min(root):
	if not root:
		return None
	cur = root
	while cur.left:
		cur = cur.left
	return cur.val


def bst_max(root):
	if not root:
		return None
	cur = root
	while cur.right:
		cur = cur.right
	return cur.val


def bst_delete(root, key):
	if not root:
		return None

	if key < root.val:
		root.left = bst_delete(root.left, key)
	elif key > root.val:
		root.right = bst_delete(root.right, key)
	else:
		if not root.left:
			return root.right
		if not root.right:
			return root.left

		# Replace with inorder successor (min of right subtree).
		successor = root.right
		while successor.left:
			successor = successor.left
		root.val = successor.val
		root.right = bst_delete(root.right, successor.val)

	return root


def is_valid_bst(root):
	def dfs(node, low, high):
		if not node:
			return True
		if not (low < node.val < high):
			return False
		return dfs(node.left, low, node.val) and dfs(node.right, node.val, high)

	return dfs(root, float("-inf"), float("inf"))


def kth_smallest(root, k):
	stack = []
	cur = root

	while stack or cur:
		while cur:
			stack.append(cur)
			cur = cur.left

		cur = stack.pop()
		k -= 1
		if k == 0:
			return cur.val
		cur = cur.right

	return None


# 7) LOWEST COMMON ANCESTOR (LCA)
def lca_binary_tree(root, p, q):
	if not root or root == p or root == q:
		return root

	left = lca_binary_tree(root.left, p, q)
	right = lca_binary_tree(root.right, p, q)

	if left and right:
		return root
	return left if left else right


def lca_bst(root, p, q):
	low, high = min(p.val, q.val), max(p.val, q.val)
	cur = root

	while cur:
		if cur.val < low:
			cur = cur.right
		elif cur.val > high:
			cur = cur.left
		else:
			return cur

	return None


# 8) TREE CONSTRUCTION PATTERNS
## LeetCode 105 - Build tree from preorder + inorder
## Description: Given preorder and inorder traversal of a tree, construct the binary tree.
def build_tree_pre_in(preorder, inorder):
	"""
	Build binary tree from preorder + inorder traversals.
	"""
	if not preorder or not inorder or len(preorder) != len(inorder):
		return None

	index_map = {val: i for i, val in enumerate(inorder)}
	pre_idx = 0

	def helper(left, right):
		nonlocal pre_idx
		if left > right:
			return None

		root_val = preorder[pre_idx]
		pre_idx += 1
		root = TreeNode(root_val)

		mid = index_map[root_val]
		root.left = helper(left, mid - 1)
		root.right = helper(mid + 1, right)
		return root

	return helper(0, len(inorder) - 1)

## LeetCode 108 - Build tree from sorted array
## Description: Given a sorted array, construct a height-balanced binary search tree.
def sorted_array_to_bst(nums):
	"""
	Builds height-balanced BST from sorted array.
	"""

	def helper(left, right):
		if left > right:
			return None
		mid = (left + right) // 2
		root = TreeNode(nums[mid])
		root.left = helper(left, mid - 1)
		root.right = helper(mid + 1, right)
		return root

	return helper(0, len(nums) - 1)


# 9) SERIALIZATION / DESERIALIZATION (BINARY TREE)
## LeetCode 297 - Serialize and Deserialize Binary Tree
## Description: Design an algorithm to serialize and deserialize a binary tree. The encoded string should be as compact as possible.
class Codec:
	"""
	BFS serialization with '#' for nulls.
	"""

	# Serialize a binary tree to a string.
	def serialize(self, root):
		if not root:
			return ""

		q = deque([root])
		out = []
		while q:
			node = q.popleft()
			if node is None:
				out.append("#")
				continue

			out.append(str(node.val))
			q.append(node.left)
			q.append(node.right)

		# Trim trailing null markers for compactness.
		while out and out[-1] == "#":
			out.pop()

		return ",".join(out)

	# Deserialize a string to a binary tree.
	def deserialize(self, data):
		if not data:
			return None

		vals = data.split(",")
		root = TreeNode(int(vals[0]))
		q = deque([root])
		i = 1

		while q and i < len(vals):
			node = q.popleft()

			if i < len(vals) and vals[i] != "#":
				node.left = TreeNode(int(vals[i]))
				q.append(node.left)
			i += 1

			if i < len(vals) and vals[i] != "#":
				node.right = TreeNode(int(vals[i]))
				q.append(node.right)
			i += 1

		return root


# 10) ADVANCED PATTERN: ITERATIVE TREE DP (POSTORDER STYLE)
def rob_house_iii(root):
	"""
	LeetCode 337 - House Robber III
	Returns max money with no parent-child (two directly-linked nodes) both robbed.
	"""

	def dfs(node):
		# (rob_this, skip_this)
		if not node:
			return 0, 0

		left_rob, left_skip = dfs(node.left)
		right_rob, right_skip = dfs(node.right)

		rob_this = node.val + left_skip + right_skip
		skip_this = max(left_rob, left_skip) + max(right_rob, right_skip)
		return rob_this, skip_this

	rob_val, skip_val = dfs(root)
	return max(rob_val, skip_val)


# 11) N-ARY TREE TRAVERSAL
## LeetCode 429 - N-ary Tree Level Order Traversal
## Description: Given an n-ary tree, return the level order traversal of its nodes' values.
def nary_level_order(root):
	if not root:
		return []

	ans = []
	q = deque([root])
	while q:
		level_size = len(q)
		level = []
		for _ in range(level_size):
			node = q.popleft()
			level.append(node.val)
			for child in node.children:
				q.append(child)
		ans.append(level)

	return ans


# 12) INTERVIEW CHECKLIST (SENIOR-LEVEL EXECUTION)
"""
SENIOR TREE INTERVIEW CHECKLIST
===============================

1) Clarify model quickly:
   - binary tree vs BST vs N-ary
   - unique values or duplicates
   - return node, value, or path

2) Choose a pattern explicitly:
   - traversal only -> DFS/BFS
   - shortest layers -> BFS
   - subtree aggregate -> postorder DFS
   - ancestor queries -> LCA pattern
   - ordered queries in BST -> inorder / BST walk

3) State complexity with precision:
   - time O(n)
   - space O(h) recursion or O(w) BFS queue (w = max width)

4) Senior communication:
   - mention tradeoffs (recursive clarity vs iterative safety)
   - discuss edge cases before coding
   - narrate invariants and failure conditions

5) Testing strategy in interview:
   - empty tree
   - single node
   - skewed tree (depth stress)
   - balanced tree
   - duplicate-like corner behavior when relevant
"""


# 13) COMMON PITFALLS
# 1) Forgetting null checks before accessing node.left/node.right.
# 2) In BFS by level, not freezing level_size each outer loop.
# 3) For BST validation, checking only parent-child instead of full bounds.
# 4) In recursive helpers, leaking mutable state between test runs.
# 5) Off-by-one mistakes in build-tree index boundaries.


# 14) QUICK DEMO
if __name__ == "__main__":
	# Build sample binary tree:
	#         5
	#       /   \
	#      3     8
	#     / \   / \
	#    2   4 7   9
	root = TreeNode(
		5,
		TreeNode(3, TreeNode(2), TreeNode(4)),
		TreeNode(8, TreeNode(7), TreeNode(9)),
	)

	print("Preorder (rec):", preorder_recursive(root))
	print("Inorder (iter):", inorder_iterative(root))
	print("Level order:", level_order(root))
	print("Zigzag:", zigzag_level_order(root))
	print("Depth:", max_depth(root))
	print("Balanced:", is_balanced(root))
	print("Diameter:", diameter_of_binary_tree(root))
	print("Max path sum:", max_path_sum(root))
	print("Valid BST:", is_valid_bst(root))
	print("BST min/max:", bst_min(root), bst_max(root))
	print("Kth smallest (k=3):", kth_smallest(root, 3))

	node_2 = root.left.left
	node_4 = root.left.right
	lca_node = lca_binary_tree(root, node_2, node_4)
	print("LCA(2,4):", lca_node.val if lca_node else None)

	codec = Codec()
	ser = codec.serialize(root)
	restored = codec.deserialize(ser)
	print("Serialized:", ser)
	print("Deserialize -> inorder:", inorder_recursive(restored))

	# Build from traversals demo
	rebuilt = build_tree_pre_in([5, 3, 2, 4, 8, 7, 9], [2, 3, 4, 5, 7, 8, 9])
	print("Rebuilt level order:", level_order(rebuilt))

	# N-ary demo
	nroot = NaryNode(1, [NaryNode(2), NaryNode(3, [NaryNode(5)]), NaryNode(4)])
	print("N-ary level order:", nary_level_order(nroot))
