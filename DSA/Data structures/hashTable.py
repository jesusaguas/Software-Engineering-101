from collections import Counter, defaultdict

# ==============================================================================
# HASHMAPS (PYTHON DICT) FOR DSA
# ==============================================================================

"""
PYTHON HASHMAP OPERATIONS - TIME COMPLEXITY TABLE
=================================================

Let:
n = number of key-value pairs in the hashmap

+----------------------------------+----------------------------------+-------------+-----------------------------------------------+
| Operation                        | Example                          | Complexity  | Explanation                                   |
+----------------------------------+----------------------------------+-------------+-----------------------------------------------+
| Insert / Update                  | d[key] = value                   | O(1)*       | Average-case, hash-based                      |
| Access                           | d[key]                           | O(1)*       | Average-case lookup                           |
| Safe access                      | d.get(key, default)              | O(1)*       | Avoids KeyError                               |
| Delete                           | del d[key]                       | O(1)*       | Average-case                                  |
| Pop key                          | d.pop(key, default)              | O(1)*       | Remove + return value                         |
| Membership (key)                 | key in d                         | O(1)*       | Checks keys only                              |
| Iterate keys/values/items        | d.keys()/d.values()/d.items()    | O(n)        | Full traversal                                |
| Length                           | len(d)                           | O(1)        | Stored metadata                               |
| Clear                            | d.clear()                        | O(n)        | Removes references                            |
| Build Counter                    | Counter(arr)                     | O(n)        | Frequency map                                 |
| defaultdict append               | dd[k].append(v)                  | O(1)*       | Auto-init container                           |
+----------------------------------+----------------------------------+-------------+-----------------------------------------------+

*Average-case O(1); worst-case can degrade due to collisions.
In Python interviews, dict + set are core tools.
"""

# 1. HASHMAP BASICS
mp = {}
mp["id"] = 101
mp["name"] = "Alice"
mp["id"] = 202  # update existing key
print(mp)  # {'id': 202, 'name': 'Alice'}

print(mp["name"])          # Alice
print(mp.get("missing"))   # None
print(mp.get("missing", 0))  # 0

if "id" in mp:
    print("id exists")

# delete / pop
val = mp.pop("name", None)
print(val)  # Alice
print(mp)   # {'id': 202}

# Loop over items
for key, value in mp.items():
    print(f"{key}: {value}")

for value in mp.values():
    print(value)


# 2. FREQUENCY COUNTING
arr = [1, 2, 2, 3, 3, 3]
freq = {}
for x in arr:
    freq[x] = freq.get(x, 0) + 1
print(freq)  # {1: 1, 2: 2, 3: 3}

# Counter alternative
print(Counter(arr))  # Counter({3: 3, 2: 2, 1: 1})


# 3. defaultdict PATTERN
groups = defaultdict(list) # Creates empty list for new keys automatically
pairs = [("a", 10), ("b", 20), ("a", 30)]
for k, v in pairs:
    groups[k].append(v)
print(dict(groups))  # {'a': [10, 30], 'b': [20]}

counts = defaultdict(int) # creates 0 for new keys, useful for counting
counts["x"] += 1 # No need to check if "x" exists first
print(dict(counts))  # {'x': 1}


# 4. CLASSIC: TWO SUM (LeetCode 1)
# Description: Given an array of integers and a target, return indices of the two numbers such that they add up to target.
def two_sum(nums, target):
    seen = {}  # value -> index
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i
    return []


print(two_sum([2, 7, 11, 15], 9))  # [0, 1]


# 5. VALID ANAGRAM (LeetCode 242)
# Description: Given two strings, determine if they are anagrams (same char counts).
def is_anagram(s, t):
    return Counter(s) == Counter(t)

print(is_anagram("anagram", "nagaram"))  # True
print(is_anagram("rat", "car"))          # False


# 6. GROUP ANAGRAMS (LeetCode 49)
# Description: Given an array of strings, group anagrams together.
def group_anagrams(strs):
    mp = defaultdict(list)
    for word in strs:
        key = tuple(sorted(word))  # canonical signature
        mp[key].append(word)
    return list(mp.values())

print(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))


# 7. TOP K FREQUENT ELEMENTS (LeetCode 347)
def top_k_frequent(nums, k):
    freq = Counter(nums)
    # Sort by frequency and take top k keys
    return [num for num, count in freq.most_common(k)]

def top_k_frequentV2(nums, k): ## Alternative using heap
    import heappush, heappop, heapify
    freq = Counter(nums)
    heap = [(-count, num) for num, count in freq.items()]  # max-heap by negating count
    heapify(heap)
    return [heappop(heap)[1] for _ in range(k)]

print(top_k_frequent([1, 1, 1, 2, 2, 3], 2))  # [1, 2]
print(top_k_frequentV2([1, 1, 1, 2, 2, 3], 2))  # [1, 2]


# 8. FIRST UNIQUE CHARACTER (LeetCode 387)
# Description: Given a string, find the index of the first non-repeating character.
def first_uniq_char(s):
    count = Counter(s)
    for i, ch in enumerate(s):
        if count[ch] == 1:
            return i
    return -1

print(first_uniq_char("leetcode"))  # 0
print(first_uniq_char("aabb"))      # -1


# 9. SUBARRAY SUM EQUALS K (LeetCode 560)
# Description: Given an array of integers and an integer k, find the total number of continuous subarrays whose sum equals to k.
# Prefix sum + hashmap frequency
def subarray_sum(nums, k):
    pref = 0
    ans = 0
    seen = {0: 1}  # prefix_sum -> count

    for x in nums:
        pref += x
        ans += seen.get(pref - k, 0)
        seen[pref] = seen.get(pref, 0) + 1
    return ans

print(subarray_sum([1, 1, 1], 2))  # 2


# 10. LONGEST SUBSTRING WITHOUT REPEATING CHARS (LeetCode 3)
# Description: Given a string, find the length of the longest substring without repeating characters.
def length_of_longest_substring(s):
    last = {}  # char -> latest index
    left = 0
    best = 0

    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best


print(length_of_longest_substring("abcabcbb"))  # 3


# 11. ISOMORPHIC STRINGS (LeetCode 205)
# Description: Given two strings s and t, determine if they are isomorphic (there is a one-to-one mapping between characters).
def is_isomorphic(s, t):
    s_to_t = {}
    t_to_s = {}

    for a, b in zip(s, t):
        if a in s_to_t and s_to_t[a] != b:
            return False
        if b in t_to_s and t_to_s[b] != a:
            return False
        s_to_t[a] = b
        t_to_s[b] = a
    return True


print(is_isomorphic("egg", "add"))  # True
print(is_isomorphic("foo", "bar"))  # False


# 12. CUSTOM HASHMAP WRAPPER (OPTIONAL INTERVIEW STYLE)
class HashMap:
    def __init__(self):
        self._d = {}

    def put(self, key, value):
        self._d[key] = value

    def get(self, key, default=None):
        return self._d.get(key, default)

    def remove(self, key):
        return self._d.pop(key, None)

    def contains(self, key):
        return key in self._d

    def size(self):
        return len(self._d)

    def items(self):
        return self._d.items()


hm = HashMap()
hm.put("x", 42)
print(hm.get("x"))        # 42
print(hm.contains("x"))   # True
print(hm.remove("x"))     # 42
print(hm.size())          # 0


# 13. PERFORMANCE TIPS
# - Use dict.get(key, 0) for counting.
# - Use defaultdict(list/set/int) to reduce boilerplate.
# - Use Counter for quick frequency tasks.
# - Prefer immutable keys (int, str, tuple); list cannot be a dict key.
# - For ordered behavior: Python 3.7+ dict preserves insertion order.


# 14. COMMON PITFALLS
# 1) Accessing missing key with d[key] raises KeyError; prefer d.get.
# 2) Using mutable keys (like list/set) is invalid.
# 3) Forgetting to initialize prefix hash with {0: 1} in subarray sum patterns.
# 4) Overwriting needed old index in sliding-window map without boundary checks.
# 5) Assuming dict iteration order is sorted (it is insertion order, not sorted).


# 15. INTERVIEW CHECKLIST (HASHMAP PATTERN RECOGNITION)
# - Need fast lookup by value? -> value->index map.
# - Need counts/frequencies? -> Counter or dict frequency map.
# - Need grouping by signature? -> dict[key].append(...).
# - Need running-sum matches? -> prefix_sum hashmap.
# - Need bidirectional constraints? -> two hashmaps (A->B and B->A).