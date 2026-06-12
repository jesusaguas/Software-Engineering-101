from collections import Counter

# ==============================================================================
# STRINGS
# ==============================================================================

"""
PYTHON STRING OPERATIONS — TIME COMPLEXITY TABLE
===============================================

Let:
n = length of the string
k = length of substring / slice
m = length of another string
t = number of substrings produced

+--------------------------+-------------------------+-------------+------------------------------------------------------+
| Operation                | Example                 | Complexity  | Explanation                                          |
+--------------------------+-------------------------+-------------+------------------------------------------------------+
| Index access             | s[i]                    | O(1)        | Direct memory access using index offset              |
| Length                   | len(s)                  | O(1)        | Length stored internally                             |
| Iteration                | for c in s              | O(n)        | Visits every character                               |
| Slice                    | s[a:b]                  | O(k)        | Copies substring into a new string                   |
| Slice with step          | s[a:b:c]                | O(k)        | Builds new string with selected characters           |
| Reverse                  | s[::-1]                 | O(n)        | Creates reversed copy                                |
| Concatenation            | s1 + s2                 | O(n + m)    | Creates new string containing both                   |
| Append character         | s += 'a'                | O(n)        | Creates new string each time                         |
| Join strings             | ''.join(list_of_str)    | O(n)        | Efficient single allocation                          |
| Membership test          | 'a' in s                | O(n)        | Linear scan                                          |
| Find substring           | s.find(sub)             | O(n)        | Substring search                                     |
| Index substring          | s.index(sub)            | O(n)        | Same as find but raises error                        |
| Count substring          | s.count(sub)            | O(n)        | Full scan                                            |
| Replace substring        | s.replace(a, b)         | O(n)        | Creates new string                                   |
| Split string             | s.split(delim)          | O(n)        | Scans entire string                                  |
| Strip whitespace         | s.strip()               | O(n)        | Scans from both ends                                 |
| Startswith / Endswith    | s.startswith(x)         | O(k)        | Checks prefix/suffix length                          |
| Lower / Upper case       | s.lower()               | O(n)        | Converts each character                              |
| Encode / Decode          | s.encode()              | O(n)        | Processes each character                             |
| Format string            | f"{x}"                  | O(n)        | Builds new formatted string                          |
+--------------------------+-------------------------+-------------+------------------------------------------------------+

IMPORTANT NOTES
---------------

1. Python strings are IMMUTABLE
   Every modification creates a new string object.

2. Repeated concatenation is expensive

   BAD (O(n^2)):
       s = ""
       for c in chars:
           s += c

   GOOD (O(n)):
       parts = []
       for c in chars:
           parts.append(c)
       s = "".join(parts)

3. Slicing always creates a new string (copy).

4. Many string methods return new strings rather than modifying the original.

"""

# 1. STRING BASICS & THEORY
# - Strings in Python are IMMUTABLE (cannot be modified in place)
# - When you concatenate, a NEW string is created: O(n)
# - Indexing and slicing are O(n) because they create new strings
# - Use lists and ''.join() for efficient concatenation: O(n) instead of O(n²)

s = "hello"
print(s[0])  # Access: O(1)
print(s[1:4])  # Slice: O(k) where k is slice length

# BAD: O(n²) due to repeated concatenation
result = ""
for char in s:
    result += char  # Creates new string each time

# GOOD: O(n) using list + join
result = ''.join([char for char in s])

# 2. STRING CREATION & CONVERSION
s1 = "hello"
s2 = str(123)  # Convert int to string
s3 = ''.join(['h', 'e', 'l', 'l', 'o']) # "hello"
s4 = "a" * 5  # "aaaaa"
s5 = "\n".join(["a", "b", "c"])  # "a\nb\nc"
# sorted returns a list, not a string
s6 = sorted("hello")  # ['e', 'h', 'l', 'l', 'o']

# 3. COMMON STRING METHODS
s = "Hello World"
print(s.lower())  # "hello world"
print(s.upper())  # "HELLO WORLD"
print(s.strip())  # Remove leading/trailing whitespace -> "Hello World"
print(s.split())  # ['Hello', 'World']
print(s.split('o'))  # ['Hell', ' W', 'rld']
print(s.replace('World', 'Python'))  # "Hello Python"
print(s.find('o'))  # 4 (first index)
print(s.count('l'))  # 3
print(s.startswith('Hello'))  # True
print(s.endswith('World'))  # True
print(s.isalpha())  # False (has space)
print(s.isdigit())  # False
print(s.isalnum())  # False (has space)

# 4. CHARACTER CHECKS
char = 'a'
print(char.isalpha())  # True
print(char.isdigit())  # False
print(char.isalnum())  # True
print(char.isupper())  # False
print(char.islower())  # True
print(char.isspace())  # False

# 5. ASCII & UNICODE
print(ord('a'))  # 97 (ASCII value)
print(ord('A'))  # 65
print(chr(97))  # 'a'
print(ord('0'))  # 48

# 6. TWO POINTERS PATTERN
# Example: Check if a string is a palindrome (a word that reads the same backward as forward, 
#           for example, "madam" is a palindrome).
def is_palindrome(s):
    # Remove non-alphanumeric, convert to lowercase
    clean = ''.join(c.lower() for c in s if c.isalnum())
    left, right = 0, len(clean) - 1
    while left < right:
        if clean[left] != clean[right]:
            return False
        left += 1
        right -= 1
    return True

# 7. SLIDING WINDOW PATTERN
# Example: Find the length of the longest substring without repeating characters, 
#           for example, "abcabcbb" has "abc" as the longest substring without repeating characters, which has a length of 3.
def longest_substring_without_repeating(s):
    char_map = {}
    max_len = 0
    left = 0
    for right in range(len(s)):
        if s[right] in char_map:
            left = max(left, char_map[s[right]] + 1)
        char_map[s[right]] = right
        max_len = max(max_len, right - left + 1)
    return max_len

# 8. HASH MAP PATTERN
# Example: Check if two strings are anagrams (contain the same characters in a different order, 
#           for example, "listen" and "silent" are anagrams).
def is_anagram(s, t):
    if len(s) != len(t):
        return False
    char_count = {}
    for char in s:
        char_count[char] = char_count.get(char, 0) + 1
    for char in t:
        if char not in char_count:
            return False
        char_count[char] -= 1
        if char_count[char] < 0:
            return False
    return True

# OR use Counter
def is_anagram_v2(s, t):
    return Counter(s) == Counter(t)

# 9. REVERSE PATTERN
# Example: Reverse a string, for example, "hello" becomes "olleh".
def reverse_string(s):
    return s[::-1]

def reverse_string_v2(s):
    return ''.join(reversed(s)) ## reversed() returns an iterator, so we join it back into a string

def reverse_string_v3(s):
    chars = list(s)
    left, right = 0, len(chars) - 1
    while left < right:
        chars[left], chars[right] = chars[right], chars[left]
        left += 1
        right -= 1
    return ''.join(chars)

def reverse_words(s):
    return ' '.join(s.split()[::-1])

# 10. PRACTICAL LEETCODE PATTERNS

# LeetCode 125: Valid Palindrome
# A palindrome is a string that reads the same backward as forward, for example, "madam".
def is_palindrome_lc(s):
    clean = ''.join(c.lower() for c in s if c.isalnum())
    return clean == clean[::-1]

# LeetCode 242: Valid Anagram
def is_anagram_lc(s, t):
    return sorted(s) == sorted(t)

# LeetCode 1: Two Sum (Hash Map)
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# LeetCode 3: Longest Substring Without Repeating Characters
def length_of_longest_substring(s):
    char_map = {}
    max_len = 0
    left = 0
    for right in range(len(s)):
        if s[right] in char_map and char_map[s[right]] >= left:
            left = char_map[s[right]] + 1
        char_map[s[right]] = right
        max_len = max(max_len, right - left + 1)
    return max_len

# LeetCode 20: Valid Parentheses
def is_valid_parentheses(s):
    stack = []
    pairs = {'(': ')', '{': '}', '[': ']'}
    for char in s:
        if char in pairs:
            stack.append(char)
        else:
            if not stack or pairs[stack.pop()] != char:
                return False
    return len(stack) == 0

# LeetCode 14: Longest Common Prefix
def longest_common_prefix(strs):
    if not strs:
        return ""
    for i in range(len(strs[0])):
        for j in range(1, len(strs)):
            if i >= len(strs[j]) or strs[j][i] != strs[0][i]:
                return strs[0][:i]
    return strs[0]

# LeetCode 49: Group Anagrams
def group_anagrams(strs):
    anagram_map = {}
    for s in strs:
        key = ''.join(sorted(s))
        if key not in anagram_map:
            anagram_map[key] = []
        anagram_map[key].append(s)
    return list(anagram_map.values())

# 11. PERFORMANCE TIPS
# - Use ''.join() for concatenation instead of + : O(n) vs O(n²)
# - Use Counter/dict for frequency: O(n) space, O(n) time
# - String slicing creates new string: O(k) where k is slice length
# - sorted() returns list: O(n log n)
# - Use startswith/endswith instead of slicing for prefix/suffix