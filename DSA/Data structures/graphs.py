from collections import defaultdict, deque
import heapq

# ==============================================================================
# GRAPHS
# ==============================================================================

## Graph: A collection of nodes and edges.
## Directed Graph: Each edge has a direction.
## Directed Acyclic Graph (DAG): Each edge has a direction and no cycles.
## Undirected Graph: Each edge has no direction.
## Weighted Graph: Each edge has a weight/cost.
## Unweighted Graph: Each edge has no weight.


"""
PYTHON GRAPH INTERVIEW GUIDE - SENIOR SOFTWARE ENGINEER EDITION
===============================================================

Core goals for interviews:
1) Quickly identify graph type (directed/undirected, weighted/unweighted, DAG/cyclic)
2) Pick the correct traversal/algorithm with correct complexity
3) Write clean, bug-resistant code under time pressure

Notation:
n = number of vertices
m = number of edges

+--------------------------------------+---------------------------------------+-----------------------------+
| Problem Type                         | Preferred Algorithm                   | Time Complexity             |
+--------------------------------------+---------------------------------------+-----------------------------+
| Traversal                            | BFS / DFS                             | O(n + m)                    |
| Connected Components                 | BFS / DFS / DSU                       | O(n + m) / near O(m alpha)  |
| Shortest path (unweighted)           | BFS                                   | O(n + m)                    |
| Shortest path (weighted, no negative)| Dijkstra (heap)                       | O((n + m) log n)            |
| Shortest path (negative edges)       | Bellman-Ford                          | O(n * m)                    |
| All-pairs shortest path              | Floyd-Warshall                        | O(n^3)                      |
| DAG ordering                         | Topological Sort (Kahn / DFS)         | O(n + m)                    |
| Cycle detection (undirected)         | DFS parent-tracking / DSU             | O(n + m)                    |
| Cycle detection (directed)           | DFS recursion stack / Kahn            | O(n + m)                    |
| Minimum Spanning Tree                | Kruskal / Prim                        | O(m log m) / O(m log n)     |
| Bipartite check                      | BFS/DFS 2-coloring                    | O(n + m)                    |
| 0/1 weights shortest path            | 0-1 BFS (deque)                       | O(n + m)                    |
+--------------------------------------+---------------------------------------+-----------------------------+

Key senior-level expectations:
- Explain tradeoffs, not only the final code.
- Handle disconnected graphs and edge cases deliberately.
- Return reusable outputs (distance + parent) for reconstruction.
- Be explicit about directed vs undirected assumptions.
"""


# ------------------------------------------------------------------------------
# 1) REPRESENTATIONS
# ------------------------------------------------------------------------------
# For integer-labeled graphs (0..n-1), an adjacency list is often simplest and most efficient.
def build_adj_list(n, edges, directed=False, weighted=False):
	"""
	Build adjacency list.

	Unweighted format:
		edges = [(u, v), ...]
		adj[u] -> [v1, v2, ...]

	Weighted format:
		edges = [(u, v, w), ...]
		adj[u] -> [(v1, w1), (v2, w2), ...]
	"""
	adj = [[] for _ in range(n)]
	for edge in edges:
		if weighted:
			u, v, w = edge
			adj[u].append((v, w))
			if not directed:
				adj[v].append((u, w))
		else:
			u, v = edge
			adj[u].append(v)
			if not directed:
				adj[v].append(u)
	return adj


# For string-labeled graphs (Node "A", "B"...), we use a dictionary instead of a list
def build_adj_map(edges, directed=False):
	"""Useful when node labels are strings, not 0..n-1."""
	adj = defaultdict(list)
	for u, v in edges:
		adj[u].append(v)
		if not directed:
			adj[v].append(u)
	return adj


# ------------------------------------------------------------------------------
# 2) BFS / DFS TEMPLATES
# ------------------------------------------------------------------------------
def bfs_traversal(adj, start):
	"""Standard BFS traversal order from one source."""
	visited = set([start])
	order = []
	q = deque([start])

	while q:
		node = q.popleft()
		order.append(node)
		for nei in adj[node]:
			if nei not in visited:
				visited.add(nei)
				q.append(nei)
	return order


def dfs_iterative(adj, start):
	"""Iterative DFS avoids recursion depth limits."""
	visited = set([start])
	order = []
	st = [start]

	while st:
		node = st.pop()
		order.append(node)

		# Reverse if you want behavior closer to recursive DFS for stable ordering.
		for nei in reversed(adj[node]):
			if nei not in visited:
				visited.add(nei)
				st.append(nei)

	return order


def dfs_recursive(adj, start):
	visited = set()
	order = []

	def dfs(node):
		visited.add(node)
		order.append(node)
		for nei in adj[node]:
			if nei not in visited:
				dfs(nei)

	dfs(start)
	return order


# ------------------------------------------------------------------------------
# 3) CONNECTED COMPONENTS (UNDIRECTED)
# ------------------------------------------------------------------------------
def connected_components(adj):
	# Example input: adj = [[1, 2], [0], [0], [4], [3], []]
	"""Return list of components, each component is list of vertices."""
	n = len(adj)
	visited = [False] * n
	components = []

	for src in range(n):
		if visited[src]:
			continue
		comp = []
		q = deque([src])
		visited[src] = True
		while q:
			node = q.popleft()
			comp.append(node)
			for nei in adj[node]:
				if not visited[nei]:
					visited[nei] = True
					q.append(nei)
		components.append(comp)

	return components
# Example output: [[0, 1, 2], [3, 4], [5]]


# ------------------------------------------------------------------------------
# 4) CYCLE DETECTION
# ------------------------------------------------------------------------------
# For undirected graphs, we can use DFS with parent tracking or DSU.
def has_cycle_undirected_dfs(adj):
	n = len(adj)
	visited = [False] * n

	def dfs(node, parent):
		visited[node] = True
		for nei in adj[node]:
			if not visited[nei]:
				if dfs(nei, node):
					return True
			elif nei != parent:
				return True
		return False

	for i in range(n):
		if not visited[i] and dfs(i, -1):
			return True
	return False


# Think of it as a tree. If we see a back edge to a node currently in the recursion stack, we have a cycle.
def has_cycle_directed_dfs(adj):
	"""
	3-color DFS approach:
	0 = unvisited, 1 = visiting (in recursion stack), 2 = done
	Back edge to color 1 means cycle.
	"""
	n = len(adj)
	color = [0] * n

	def dfs(node):
		color[node] = 1
		for nei in adj[node]:
			if color[nei] == 1:
				return True
			if color[nei] == 0 and dfs(nei):
				return True
		color[node] = 2
		return False

	for i in range(n):
		if color[i] == 0 and dfs(i):
			return True
	return False


# ------------------------------------------------------------------------------
# 5) TOPOLOGICAL SORT (DAG)
# Ordering of nodes such that all directed edges go from earlier to later in the order (Dependency resolution).
# ------------------------------------------------------------------------------
# Iterative option [PREFERRED]
def topo_sort_kahn(adj):
	"""Returns topological order; returns [] if a cycle exists."""
	n = len(adj)
	indegree = [0] * n
	for u in range(n):
		for v in adj[u]:
			indegree[v] += 1

	q = deque([i for i in range(n) if indegree[i] == 0]) # Create initial queue of nodes with no dependencies
	order = []

	while q:
		node = q.popleft()
		order.append(node)
		for nei in adj[node]:
			indegree[nei] -= 1
			if indegree[nei] == 0:
				q.append(nei)

	return order if len(order) == n else []


## Recursive option
def topo_sort_dfs(adj):
	"""DFS + postorder stack. Returns [] if a cycle exists."""
	n = len(adj)
	color = [0] * n
	out = []

	def dfs(node):
		color[node] = 1
		for nei in adj[node]:
			if color[nei] == 1:
				return False
			if color[nei] == 0 and not dfs(nei):
				return False
		color[node] = 2
		out.append(node)
		return True

	for i in range(n):
		if color[i] == 0 and not dfs(i):
			return []

	out.reverse()
	return out

""" Leetcode Problem 210. Course Schedule II.
Given the total number of courses and a list of prerequisite pairs, return the ordering of courses you should take to finish all courses. 
If there are multiple valid orderings, return any of them. If it is impossible to finish all courses, return an empty array.
Input: numCourses = 2, prerequisites = [[1,0]]
Output: [0,1]
"""
def find_order(num_courses, prerequisites):
	adj = [[] for _ in range(num_courses)]
	for u, v in prerequisites:
		adj[v].append(u)  # v is a prerequisite of u

	return topo_sort_kahn(adj)


# ------------------------------------------------------------------------------
# 6) BIPARTITE CHECK (2-COLORING)
# A graph is bipartite if we can color its vertices with 2 colors such that no edge connects same-color vertices.
# ------------------------------------------------------------------------------
# -1 = uncolored
#  0 = first color
#  1 = second color
def is_bipartite(adj):
	n = len(adj)
	color = [-1] * n

	# The outer loop handles disconnected graphs, like 0 --- 1    2 --- 3
	for src in range(n):
		# If a vertex was already colored by a previous BFS, it skips it:
		if color[src] != -1:
			continue
		q = deque([src])
		color[src] = 0

		while q:
			node = q.popleft()
			for nei in adj[node]:
				if color[nei] == -1:
					color[nei] = color[node] ^ 1 # Alternate color
					q.append(nei)
				# This happens when there is an odd-length cycle, like 0 --- 1 --- 2 --- 0, which cannot be colored with 2 colors:
				elif color[nei] == color[node]:
					return False

	return True


# ------------------------------------------------------------------------------
# 7) SHORTEST PATHS
# ------------------------------------------------------------------------------
def shortest_path_unweighted(adj, src):
	"""BFS shortest path in unweighted graph. Returns (dist, parent)."""
	n = len(adj)
	dist = [float("inf")] * n
	parent = [-1] * n # For path reconstruction. parent[v] = u means we reached v from u.
	dist[src] = 0

	q = deque([src])
	while q:
		u = q.popleft()
		for v in adj[u]:
			if dist[v] == float("inf"):
				dist[v] = dist[u] + 1
				parent[v] = u
				q.append(v)

	return dist, parent


def reconstruct_path(parent, src, dst):
	"""Reconstruct path using parent array from BFS/Dijkstra/etc."""
	if src == dst:
		return [src]
	if parent[dst] == -1:
		return []
	path = []
	cur = dst
	while cur != -1:
		path.append(cur)
		cur = parent[cur]
	path.reverse()
	return path if path and path[0] == src else []

# Only start to end O((n + m) log n). For all distances from src, see dijkstra() below.
# Time:  O((V + E) log V)
# Space: O(V)
def dijkstra_shortest_path(graph, start, target):
    """
    Returns the shortest distance from start to target.
    Does not reconstruct the path.

    graph format:
    {
        'A': [('B', 4), ('C', 2)],
        'B': [('D', 5)],
        'C': [('B', 1)],
        'D': []
    }
    """

    pq = [(0, start)]          # (distance_so_far, node)
    dist = {start: 0}          # only store distances we actually discover

    while pq:
        current_dist, node = heapq.heappop(pq)

        # Ignore outdated queue entries
        if current_dist != dist[node]:
            continue

        # As soon as target is popped, we have the shortest distance
        if node == target:
            return current_dist

        for neighbor, weight in graph.get(node, []):
            new_dist = current_dist + weight

            if new_dist < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))

    # target is unreachable
    return float("inf")

# All distances from src
# Time:  O((V + E) log V)
# Space: O(V)
def dijkstra(n, edges, src):
	"""
	edges: list of (u, v, w), directed graph. Example: [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5), (3, 4, 3)]
	For undirected, add both directions before calling or adjust builder.
	"""
	adj = [[] for _ in range(n)]
	for u, v, w in edges:
		adj[u].append((v, w))

	dist = [float("inf")] * n
	parent = [-1] * n
	dist[src] = 0
	pq = [(0, src)]

	while pq:
		d, u = heapq.heappop(pq)
		if d != dist[u]:
			continue

		for v, w in adj[u]:
			nd = d + w
			if nd < dist[v]:
				dist[v] = nd
				parent[v] = u
				heapq.heappush(pq, (nd, v))

	return dist, parent


# Like Dijkstra but handles negative edges and detects reachable negative cycles. O(n * m).
# Time:  O(VE)
# Space: O(V)
def bellman_ford(n, edges, src):
	"""
	Handles negative edges and detects reachable negative cycles.
	Returns (dist, parent, has_negative_cycle).
	"""
	dist = [float("inf")] * n
	parent = [-1] * n
	dist[src] = 0

	for _ in range(n - 1):
		updated = False
		for u, v, w in edges:
			if dist[u] != float("inf") and dist[u] + w < dist[v]:
				dist[v] = dist[u] + w
				parent[v] = u
				updated = True
		if not updated:
			break

	for u, v, w in edges:
		if dist[u] != float("inf") and dist[u] + w < dist[v]:
			return dist, parent, True

	return dist, parent, False

# Instead of finding the shortest path from one node A to one node B, it finds the shortest distance between every pair of nodes.
# Time:  O(V³)
# Space: O(V²)
def floyd_warshall(n, edges):
	"""All-pairs shortest path. Works with negative edges (no negative cycles)."""
	INF = float("inf")
	dist = [[INF] * n for _ in range(n)]

	for i in range(n):
		dist[i][i] = 0
	for u, v, w in edges:
		dist[u][v] = min(dist[u][v], w)

	for k in range(n):
		for i in range(n):
			if dist[i][k] == INF:
				continue
			for j in range(n):
				if dist[k][j] == INF:
					continue
				if dist[i][k] + dist[k][j] < dist[i][j]:
					dist[i][j] = dist[i][k] + dist[k][j]

	return dist


# ------------------------------------------------------------------------------
# 8) MINIMUM SPANNING TREE
# ------------------------------------------------------------------------------
# How can I connect all nodes together with the minimum total edge cost?
# It is used on a weighted, undirected graph.
# A spanning tree connects all vertices using exactly: V - 1 edges

# Example graph:
#  A --1-- B
#  |       |
#  4       2
#  |       |
#  C --3-- D

# MST:
#  A --1-- B
#          |
#          2
#          |
#  C --3-- D
# ------------------------------------------------------------------------------
# You will need this DSU (Disjoint Set Union) data structure for Kruskal's algorithm, and it's also a common interview topic on its own.
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n  # Number of nodes in the component for which this node is the representative (root)

    def find(self, x):
        while x != self.parent[x]:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra = self.find(a)
        rb = self.find(b)

        if ra == rb:
            return False

        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra

        self.parent[rb] = ra
        self.size[ra] += self.size[rb]

        return True


def kruskal_mst(n, edges):
	"""
	edges = [(u, v, w), ...] for undirected graph.
	Returns (mst_weight, mst_edges). If disconnected, mst_edges has < n-1 edges.
	"""
	dsu = DSU(n)
	mst_weight = 0
	mst_edges = []

	for u, v, w in sorted(edges, key=lambda x: x[2]):
		if dsu.union(u, v):
			mst_weight += w
			mst_edges.append((u, v, w))
			if len(mst_edges) == n - 1:
				break

	return mst_weight, mst_edges


def prim_mst(n, edges):
	"""
	Prim using adjacency list + min-heap.
	Returns MST weight for connected graph, or None if disconnected.
	"""
	adj = [[] for _ in range(n)]
	for u, v, w in edges:
		adj[u].append((v, w))
		adj[v].append((u, w))

	visited = [False] * n
	min_heap = [(0, 0)]  # (weight, node)
	total = 0
	picked = 0

	while min_heap and picked < n:
		w, u = heapq.heappop(min_heap)
		if visited[u]:
			continue
		visited[u] = True
		total += w
		picked += 1

		for v, w2 in adj[u]:
			if not visited[v]:
				heapq.heappush(min_heap, (w2, v))

	return total if picked == n else None


# ------------------------------------------------------------------------------
# 9) HIGH-YIELD ADVANCED PATTERNS
# ------------------------------------------------------------------------------
# This is a common pattern in "nearest X" grid/graph problems, where you have multiple sources and want the distance to the nearest one.
def multi_source_bfs(n, adj, sources):
	"""
	Distance from nearest source.
	Common in "nearest X" grid/graph interview problems.
	"""
	dist = [float("inf")] * n
	q = deque()
	for s in sources:
		dist[s] = 0
		q.append(s)

	while q:
		u = q.popleft()
		for v in adj[u]:
			if dist[v] == float("inf"):
				dist[v] = dist[u] + 1
				q.append(v)

	return dist

# This is a specialized BFS for graphs with edge weights of only 0 or 1. It uses a deque to achieve O(V + E) time, which is faster than Dijkstra's O((V + E) log V) for this specific case.
# The optimization is that when we traverse a 0-weight edge, we add the neighbor to the front of the deque (since it doesn't increase distance), and when we traverse a 1-weight edge, we add it to the back (since it increases distance by 1).
def zero_one_bfs(n, edges, src):
	"""
	edges = [(u, v, w)] where w in {0, 1}.
	Faster than Dijkstra for 0/1 weighted graphs.
	"""
	adj = [[] for _ in range(n)]
	for u, v, w in edges:
		adj[u].append((v, w))

	INF = float("inf")
	dist = [INF] * n
	dist[src] = 0
	dq = deque([src])

	while dq:
		u = dq.popleft()
		for v, w in adj[u]:
			nd = dist[u] + w
			if nd < dist[v]:
				dist[v] = nd
				if w == 0:
					dq.appendleft(v)
				else:
					dq.append(v)

	return dist


# ------------------------------------------------------------------------------
# 10) GRID AS GRAPH (VERY COMMON IN INTERVIEWS)
# ------------------------------------------------------------------------------
def shortest_path_grid(grid, start, target):
	"""
	grid values:
	0 = blocked, 1 = walkable
	Returns minimum steps with 4-directional movement, else -1.
	"""
	rows = len(grid)
	cols = len(grid[0]) if rows else 0
	sr, sc = start
	tr, tc = target

	if rows == 0 or cols == 0:
		return -1
	if grid[sr][sc] == 0 or grid[tr][tc] == 0:
		return -1

	q = deque([(sr, sc, 0)])
	visited = [[False] * cols for _ in range(rows)]
	visited[sr][sc] = True
	dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

	while q:
		r, c, d = q.popleft()
		if (r, c) == (tr, tc):
			return d

		for dr, dc in dirs:
			nr, nc = r + dr, c + dc
			if 0 <= nr < rows and 0 <= nc < cols:
				if grid[nr][nc] == 1 and not visited[nr][nc]:
					visited[nr][nc] = True
					q.append((nr, nc, d + 1))

	return -1


# ------------------------------------------------------------------------------
# 11) INTERVIEW CHECKLIST + PITFALLS
# ------------------------------------------------------------------------------
"""
Interview checklist before coding:
1) Is graph directed or undirected?
2) Is it weighted? Any negative weights?
3) Need one path, shortest path, all paths, or ordering?
4) Could graph be disconnected?
5) Node labels integer or arbitrary strings?
6) Need to return path itself or just cost/boolean?

Common pitfalls:
- Forgetting to mark visited at enqueue-time in BFS, causing duplicates.
- Using Dijkstra on negative-weight edges.
- Missing disconnected components (only starting from node 0).
- Mixing up indegree for directed vs undirected graphs.
- For topological sort, forgetting cycle detection.
- In DFS cycle detection (undirected), not tracking parent.
"""


if __name__ == "__main__":
	# Basic undirected graph
	n1 = 6
	edges1 = [(0, 1), (0, 2), (1, 3), (2, 4), (4, 5)]
	adj1 = build_adj_list(n1, edges1, directed=False)

	print("BFS:", bfs_traversal(adj1, 0))
	print("DFS iterative:", dfs_iterative(adj1, 0))
	print("Connected components:", connected_components(adj1))
	print("Bipartite:", is_bipartite(adj1))

	dist, parent = shortest_path_unweighted(adj1, 0)
	print("Unweighted dist:", dist)
	print("Path 0->5:", reconstruct_path(parent, 0, 5))

	# Directed acyclic graph for topo sort
	n2 = 6
	dag_edges = [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)]
	dag_adj = build_adj_list(n2, dag_edges, directed=True)
	print("Topo Kahn:", topo_sort_kahn(dag_adj))
	print("Topo DFS:", topo_sort_dfs(dag_adj))

	# Weighted shortest path
	n3 = 5
	weighted_edges = [
		(0, 1, 4),
		(0, 2, 1),
		(2, 1, 2),
		(1, 3, 1),
		(2, 3, 5),
		(3, 4, 3),
	]
	d_dist, d_parent = dijkstra(n3, weighted_edges, 0)
	print("Dijkstra dist:", d_dist)
	print("Path 0->4:", reconstruct_path(d_parent, 0, 4))

	# Bellman-Ford with a negative edge (no negative cycle)
	bf_edges = [
		(0, 1, 1),
		(1, 2, -1),
		(2, 3, -1),
		(0, 3, 4),
	]
	bf_dist, _, neg = bellman_ford(4, bf_edges, 0)
	print("Bellman-Ford dist:", bf_dist, "negative_cycle:", neg)

	# MST
	n4 = 4
	mst_edges = [(0, 1, 10), (0, 2, 6), (0, 3, 5), (1, 3, 15), (2, 3, 4)]
	print("Kruskal MST:", kruskal_mst(n4, mst_edges))
	print("Prim MST weight:", prim_mst(n4, mst_edges))

	# Grid shortest path
	grid = [
		[1, 1, 0, 1],
		[0, 1, 1, 1],
		[0, 0, 1, 0],
		[1, 1, 1, 1],
	]
	print("Grid shortest path:", shortest_path_grid(grid, (0, 0), (3, 3)))
