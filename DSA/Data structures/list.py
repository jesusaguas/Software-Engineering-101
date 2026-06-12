from collections import defaultdict

# ==============================================================================
# PYTHON ARRAYS (LISTS)
# ==============================================================================

"""
PYTHON LIST OPERATIONS - TIME COMPLEXITY TABLE
==============================================

Let:
n = length of the list
k = length of inserted/removed/sliced part

+-------------------------------+---------------------------+-------------+------------------------------------------------------+
| Operation                     | Example                   | Complexity  | Explanation                                          |
+-------------------------------+---------------------------+-------------+------------------------------------------------------+
| Index access                  | arr[i]                    | O(1)        | Direct index lookup                                  |
| Update by index               | arr[i] = x                | O(1)        | Direct write                                          |
| Length                        | len(arr)                  | O(1)        | Length is stored                                     |
| Append                        | arr.append(x)             | O(1)*       | Amortized, occasional resize                         |
| Pop end                       | arr.pop()                 | O(1)        | Removes last element                                 |
| Insert at index               | arr.insert(i, x)          | O(n)        | Elements shift right                                 |
| Pop at index                  | arr.pop(i)                | O(n)        | Elements shift left                                  |
| Delete slice                  | del arr[i:j]              | O(n)        | Compacts remaining elements                          |
| Membership test               | x in arr                  | O(n)        | Linear scan                                          |
| Index search                  | arr.index(x)              | O(n)        | Linear scan                                          |
| Count                         | arr.count(x)              | O(n)        | Full scan                                            |
| Slice                         | arr[a:b]                  | O(k)        | Creates new list copy                                |
| Copy                          | arr.copy()                | O(n)        | Shallow copy                                         |
| Concatenation                 | arr1 + arr2               | O(n + m)    | Creates new list                                     |
| Extend                        | arr.extend(other)         | O(k)        | Appends all elements of other                        |
| Sort                          | arr.sort()                | O(n log n)  | Timsort                                              |
| Reverse                       | arr.reverse()             | O(n)        | In-place swap                                        |
| Min / Max / Sum               | min/max/sum(arr)          | O(n)        | Full scan                                            |
+-------------------------------+---------------------------+-------------+------------------------------------------------------+

IMPORTANT NOTES
---------------

1. Python "array" for DSA usually means list (dynamic array).
2. list uses dynamic resizing, so append is amortized O(1).
3. Insertion/deletion in the middle is expensive due to shifts.
4. Slicing creates a new list (copy), not a view.
5. list.copy() is shallow (nested lists still share inner objects).
"""

# 1. ARRAY BASICS
# Python list is the default dynamic array in interviews/competitive programming.
arr = [10, 20, 30, 40, 50]
print(arr[0])      # 10, O(1)
print(arr[-1])     # 50, O(1)
arr[2] = 99        # update in O(1)
print(len(arr))    # O(1)

# 2. CREATION PATTERNS
arr_zeros = [0] * 5
arr_range = list(range(5))
arr_squares = [i * i for i in range(6)] # list comprehension for transformation
filtered = [x for x in arr if x % 2 == 0]  # [0, 2, 4]
arr_copy = arr_range.copy()         # shallow copy
arr_from_iter = list(map(int, ["1", "2", "3"]))

# 3. INSERT / DELETE OPERATIONS
nums = [1, 2, 3]
nums.append(4)        # [1, 2, 3, 4], amortized O(1)
nums.extend([5, 6])   # [1, 2, 3, 4, 5, 6], O(k)
nums.insert(1, 99)    # [1, 99, 2, 3, 4, 5, 6], O(n)
nums.pop()            # remove last, O(1)
nums.pop(0)           # remove first, O(n)
del nums[1:3]         # remove slice, O(n)

# 4. SLICING AND COPYING
arr = [0, 1, 2, 3, 4, 5]
print(arr[1:4])   # [1, 2, 3]
print(arr[:3])    # [0, 1, 2]
print(arr[3:])    # [3, 4, 5]
print(arr[:-2])   # [0, 1, 2, 3]
print(arr[-2:])   # [4, 5]
print(arr[::2])   # [0, 2, 4]
print(arr[::-1])  # [5, 4, 3, 2, 1, 0]

# Shallow copy warning with nested lists.
matrix = [[1, 2], [3, 4]]
matrix_copy = matrix.copy()
matrix_copy[0][0] = 99
print(matrix)  # [[99, 2], [3, 4]] because inner lists are shared

# Deep copy can be done with list comprehension or copy.deepcopy.
matrix_deep_copy = [row[:] for row in matrix]  # Creates a new list with new inner lists
matrix_deep_copy[0][0] = 88
print(matrix)           # [[99, 2], [3, 4]] - original unaffected by deep copy change   
# or using copy module:
import copy
matrix_deep_copy = copy.deepcopy(matrix)
print(matrix)           # [[99, 2], [3, 4]] - original unaffected by deep copy change

# 5. COMMON METHODS
arr = [3, 1, 4, 1, 5, 9]
arr.sort()                    # in-place sort
arr.reverse()                 # in-place reverse
print(min(arr), max(arr), sum(arr))
print(arr.count(1))           # frequency
print(arr.index(5))           # first index of value

# 6. SORTING NOTES
# Timsort is stable, so equal elements preserve original order.
items = [(2, "b"), (1, "x"), (2, "a")]
items.sort(key=lambda x: x[0])
print(items)  # [(1, 'x'), (2, 'b'), (2, 'a')]

# 7. SEARCHING
arr = [2, 4, 6, 8, 10]
print(6 in arr)  # True, O(n)

# Binary search with bisect on sorted array.
from bisect import bisect_left, bisect_right
idx = bisect_left(arr, 6)
print(idx)  # 2
left = bisect_left(arr, 7)
right = bisect_right(arr, 7)
print(left, right)  # insertion range for 7


# 8. PREFIX SUM
def build_prefix_sum(nums):
    prefix = [0]
    for num in nums:
        prefix.append(prefix[-1] + num)
    return prefix


def range_sum(prefix, left_idx, right_idx):
    # Sum of nums[left_idx:right_idx + 1]
    return prefix[right_idx + 1] - prefix[left_idx]


nums = [1, 2, 3, 4, 5]
prefix = build_prefix_sum(nums)
print(prefix)  # [0, 1, 3, 6, 10, 15]
print(range_sum(prefix, 1, 3))  # 2 + 3 + 4 = 9


# 9. TWO POINTERS (SORTED INPUT)
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        cur = nums[left] + nums[right]
        if cur == target:
            return [left, right]
        if cur < target:
            left += 1
        else:
            right -= 1
    return []


# 10. SLIDING WINDOW (FIXED SIZE)
def max_subarray_sum_k(nums, k):
    if k <= 0 or k > len(nums):
        return 0

    window_sum = sum(nums[:k])
    best = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        best = max(best, window_sum)
    return best


# 11. KADANE'S ALGORITHM - MAX SUBARRAY SUM IN O(N)
def max_subarray_sum(nums):
    best = nums[0]
    cur = nums[0]
    for i in range(1, len(nums)):
        cur = max(nums[i], cur + nums[i])
        best = max(best, cur)
    return best


# 12. BINARY SEARCH TEMPLATE
def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


# 13. 2D ARRAYS (MATRICES)
rows, cols = 3, 4
matrix = [[0] * cols for _ in range(rows)]  # safe creation
matrix[0][1] = 7
print(matrix)
# Do not do [[0] * cols] * rows for mutable rows (aliasing bug).


# 14. FREQUENCY COUNTING
def frequency_map(nums):
    freq = defaultdict(int)
    for num in nums:
        freq[num] += 1
    return dict(freq)

# Counter from collections can also be used for frequency counting:
from collections import Counter
nums = [1, 2, 2, 3, 3, 3, 3]
def frequency_map_counter(nums):
    counter = Counter(nums) # creates a frequency map directly
    print(counter) # Counter({1: 1, 2: 2, 3: 4})
    print(counter[1])  # 1
    print(counter[2])  # 2
    print(counter[3])  # 4
    return dict(counter) # convert to regular dict if needed

# 15. Read - write pointers
# Useful for in-place modifications like removing elements or partitioning, moving zeroes, etc. to the end of the array.
def remove_element(nums, val):
    write = 0
    for read in range(len(nums)):
        if nums[read] != val:
            nums[write] = nums[read]
            write += 1
    return write  # new length of array without val



# 16. PRACTICAL INTERVIEW PROBLEMS

# LeetCode 1: Two Sum (unsorted).
## Description: Given an array of integers and a target, 
## return indices of the two numbers such that they add up to target.
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        need = target - num # the complement we need to find
        if need in seen:
            return [seen[need], i]
        seen[num] = i
    return []


# LeetCode 26: Remove Duplicates from Sorted Array
# Description: Given a sorted array, remove duplicates in-place and return the new length.
def remove_duplicates(nums):
    if not nums:
        return 0
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[read - 1]:
            nums[write] = nums[read]
            write += 1
    return write


# LeetCode 283: Move Zeroes
# Description: Given an array, move all zeroes to the end while maintaining the relative order of non-zero elements.
def move_zeroes(nums):
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1

# LeetCode 75: Sort an Array ff 0s 1s and 2s
# Description: Given an array of integers where each element is 0, 1, or 2, sort the array in-place.
def sort_colors(nums):
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else: # nums[mid] == 2
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1


# LeetCode 189: Rotate Array
# Description: Rotate the array to the right by k steps, where k is non-negative.
# O(n) time, O(n) space solution using reversal.
def rotate_array(nums, k):
    n = len(nums)
    if n == 0:
        return
    k %= n
    nums[:] = nums[-k:] + nums[:-k]

# O(n) time, O(1) space solution using reversal.
def rotate_array_inplace(nums, k):
    n = len(nums)
    if n == 0:
        return
    k %= n

    # Helper function to reverse a portion of the array in-place.
    def reverse(start, end):
        while start < end:
            nums[start], nums[end] = nums[end], nums[start]
            start += 1
            end -= 1

    # Step 1: Reverse the entire array.
    reverse(0, n - 1)
    # Step 2: Reverse the first k elements.
    reverse(0, k - 1)
    # Step 3: Reverse the remaining n-k elements.
    reverse(k, n - 1)




# LeetCode 238: Product of Array Except Self (WITHOUT DIVISION)
# Description: Given an array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i], 
# for example, given [1, 2, 3, 4], return [24, 12, 8, 6].
def product_except_self(nums):
    n = len(nums)
    ans = [1] * n

    prefix = 1
    for i in range(n):
        ans[i] = prefix
        prefix *= nums[i]

    suffix = 1
    for i in range(n - 1, -1, -1):
        ans[i] *= suffix
        suffix *= nums[i]

    return ans

# LeetCode 48: Rotate Image (2D matrix)
# Description: You are given an n x n 2D matrix representing an image, rotate the image by 90 degrees (clockwise) in-place.
def rotate_image(matrix):
    n = len(matrix)
    # Transpose the matrix
    for i in range(n):
        for j in range(i, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    # Reverse each row
    for i in range(n):
        matrix[i].reverse()


# LeetCode 73: Set Matrix Zeroes
# Description: Given an m x n matrix, if an element is 0, set its entire row and column to 0 in-place.
def set_matrix_zeroes(matrix):
    m, n = len(matrix), len(matrix[0])
    rows = set()
    cols = set()

    # First pass to find all rows and columns that need to be zeroed
    for i in range(m):
        for j in range(n):
            if matrix[i][j] == 0:
                rows.add(i)
                cols.add(j)

    # Second pass to set the identified rows and columns to zero
    for i in range(m):
        for j in range(n):
            if i in rows or j in cols:
                matrix[i][j] = 0

# LeetCode 54: Spiral Matrix
# Description: Given an m x n matrix, return all elements of the matrix in spiral order.
def spiral_order(matrix):    
    if not matrix:
        return []
    
    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    
    while top <= bottom and left <= right:
        # Traverse from left to right
        for j in range(left, right + 1):
            result.append(matrix[top][j])
        top += 1
        
        # Traverse from top to bottom
        for i in range(top, bottom + 1):
            result.append(matrix[i][right])
        right -= 1
        
        if top <= bottom:
            # Traverse from right to left
            for j in range(right, left - 1, -1):
                result.append(matrix[bottom][j])
            bottom -= 1
        
        if left <= right:
            # Traverse from bottom to top
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][left])
            left += 1
            
    return result



# 16. PERFORMANCE TIPS
# - Prefer append/pop at end; avoid insert/pop at index 0 in large lists.
# - Use list comprehensions for fast, readable transformations.
# - Prefer local variables in tight loops for speed-critical code.
# - Use bisect for binary search and insertion points on sorted arrays.
# - Use prefix sums when multiple range-sum queries are needed.
# - Use nums[:] = ... when you must modify list in place.


# 17. COMMON PITFALLS
# 1) Aliasing in 2D arrays:
#    bad = [[0] * 3] * 3
# 2) Forgetting sorted requirement for binary search/two pointers.
# 3) Using arr = arr + [x] in loop (creates new list each iteration).
# 4) Confusing shallow vs deep copy for nested lists.