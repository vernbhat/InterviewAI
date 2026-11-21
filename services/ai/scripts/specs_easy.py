"""Easy problems. Reference functions must be self-contained (imports inside the body):
the test suite runs each one in isolation via inspect.getsource()."""

from __future__ import annotations

import random
from typing import Any


def P(id, title, difficulty, pattern, statement, constraints, fn, params, returns, examples, edge_cases, generator, reference, time, space, hints):
    return {
        "id": id, "title": title, "difficulty": difficulty, "pattern": pattern, "statement": statement,
        "constraints": constraints, "function": {"name": fn, "params": params, "returns": returns},
        "examples": [{"args": a, "explanation": e} for a, e in examples], "edge_cases": edge_cases,
        "generator": generator, "reference": reference, "complexity": {"time": time, "space": space}, "hints": hints,
    }


# --------------------------------------------------------------------------- references

def contains_duplicate(nums):
    return len(set(nums)) != len(nums)


def is_anagram(s, t):
    return sorted(s) == sorted(t)


def move_zeroes(nums):
    nz = [x for x in nums if x != 0]
    return nz + [0] * (len(nums) - len(nz))


def majority_element(nums):
    cand, count = 0, 0
    for x in nums:
        if count == 0:
            cand = x
        count += 1 if x == cand else -1
    return cand


def is_palindrome(s):
    t = [c.lower() for c in s if c.isascii() and c.isalnum()]
    return t == t[::-1]


def climb_stairs(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def single_number(nums):
    x = 0
    for v in nums:
        x ^= v
    return x


def missing_number(nums):
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)


def plus_one(digits):
    out = list(digits)
    i = len(out) - 1
    while i >= 0 and out[i] == 9:
        out[i] = 0
        i -= 1
    if i < 0:
        return [1] + out
    out[i] += 1
    return out


def merge_sorted(nums1, nums2):
    i = j = 0
    out = []
    while i < len(nums1) and j < len(nums2):
        if nums1[i] <= nums2[j]:
            out.append(nums1[i]); i += 1
        else:
            out.append(nums2[j]); j += 1
    return out + nums1[i:] + nums2[j:]


def first_uniq_char(s):
    counts = {}
    for c in s:
        counts[c] = counts.get(c, 0) + 1
    for i, c in enumerate(s):
        if counts[c] == 1:
            return i
    return -1


def longest_common_prefix(strs):
    if not strs:
        return ""
    prefix = strs[0]
    for s in strs[1:]:
        k = 0
        while k < len(prefix) and k < len(s) and prefix[k] == s[k]:
            k += 1
        prefix = prefix[:k]
    return prefix


def count_bits(n):
    out = [0] * (n + 1)
    for i in range(1, n + 1):
        out[i] = out[i >> 1] + (i & 1)
    return out


def is_subsequence(s, t):
    i = 0
    for c in t:
        if i < len(s) and s[i] == c:
            i += 1
    return i == len(s)


def roman_to_int(s):
    val = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, c in enumerate(s):
        if i + 1 < len(s) and val[c] < val[s[i + 1]]:
            total -= val[c]
        else:
            total += val[c]
    return total


def sorted_squares(nums):
    return sorted(x * x for x in nums)


# --------------------------------------------------------------------------- generators

def _ints(rng, lo, hi, nlo, nhi):
    return [rng.randint(lo, hi) for _ in range(rng.randint(nlo, nhi))]


def gen_contains_dup(rng):
    return [_ints(rng, -20, 20, 1, 15) if rng.random() < 0.5 else rng.sample(range(-100, 100), rng.randint(1, 15))]


def gen_anagram(rng):
    s = "".join(rng.choice("abcde") for _ in range(rng.randint(1, 10)))
    if rng.random() < 0.5:
        t = "".join(rng.sample(s, len(s)))
    else:
        t = "".join(rng.choice("abcde") for _ in range(rng.randint(1, 10)))
    return [s, t]


def gen_move_zeroes(rng):
    return [[0 if rng.random() < 0.4 else rng.randint(-9, 9) for _ in range(rng.randint(1, 15))]]


def gen_majority(rng):
    n = rng.randint(1, 15)
    m = rng.randint(-10, 10)
    k = n // 2 + 1
    nums = [m] * k + [rng.choice([x for x in range(-10, 11) if x != m]) for _ in range(n - k)]
    rng.shuffle(nums)
    return [nums]


def gen_palindrome(rng):
    core = "".join(rng.choice("abAB1 ,.") for _ in range(rng.randint(0, 8)))
    if rng.random() < 0.5:
        core = core + core[::-1]
    return [core]


def gen_stairs(rng):
    return [rng.randint(1, 45)]


def gen_single(rng):
    vals = rng.sample(range(-50, 50), rng.randint(1, 8))
    nums = vals[1:] * 2 + [vals[0]]
    rng.shuffle(nums)
    return [nums]


def gen_missing(rng):
    n = rng.randint(1, 20)
    nums = list(range(n + 1))
    nums.remove(rng.randint(0, n))
    rng.shuffle(nums)
    return [nums]


def gen_plus_one(rng):
    n = rng.randint(1, 10)
    if rng.random() < 0.3:
        return [[9] * n]
    return [[rng.randint(1, 9)] + [rng.choice([9, 9, rng.randint(0, 9)]) for _ in range(n - 1)]]


def gen_merge_sorted(rng):
    return [sorted(_ints(rng, -20, 20, 0, 10)), sorted(_ints(rng, -20, 20, 0, 10))]


def gen_first_uniq(rng):
    return ["".join(rng.choice(rng.choice(["ab", "abc", "abcdefgh"])) for _ in range(rng.randint(1, 15)))]


def gen_lcp(rng):
    base = "".join(rng.choice("abc") for _ in range(rng.randint(0, 5)))
    return [[base + "".join(rng.choice("abc") for _ in range(rng.randint(0, 4))) for _ in range(rng.randint(1, 5))]]


def gen_count_bits(rng):
    return [rng.randint(0, 64)]


def gen_subseq(rng):
    t = "".join(rng.choice("abc") for _ in range(rng.randint(0, 12)))
    if rng.random() < 0.5 and t:
        s = "".join(c for c in t if rng.random() < 0.5)
    else:
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 5)))
    return [s, t]


def gen_roman(rng):
    n = rng.randint(1, 3999)
    vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, r in vals:
        while n >= v:
            out += r
            n -= v
    return [out]


def gen_squares(rng):
    return [sorted(_ints(rng, -30, 30, 1, 15))]


# --------------------------------------------------------------------------- specs

EASY = [
    P("contains-duplicate", "Contains Duplicate", "Easy", "Hash set",
      "Given an integer array `nums`, return `true` if any value appears at least twice, and `false` if every element is distinct.",
      ["1 <= nums.length <= 10^5", "-10^9 <= nums[i] <= 10^9"], "containsDuplicate", [["nums", "int[]"]], "bool",
      [([[1, 2, 3, 1]], "1 appears twice."), ([[1, 2, 3, 4]], "All distinct."), ([[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]], "Many repeats.")],
      [[[5]], [[0, 0]], [[-1, 1]], [[1000000000, -1000000000, 1000000000]]], gen_contains_dup, contains_duplicate, "O(n)", "O(n)",
      ["Comparing every pair is O(n^2). What could remember values you have already seen?",
       "A hash set gives O(1) average membership checks.",
       "Insert each value into a set; if it is already present, return true. Sorting and checking neighbours is the O(1)-extra-space alternative."]),
    P("valid-anagram", "Valid Anagram", "Easy", "Counting",
      "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s` (same letters with the same counts, in any order).",
      ["1 <= s.length, t.length <= 5 * 10^4", "Lowercase English letters"], "isAnagram", [["s", "string"], ["t", "string"]], "bool",
      [(["anagram", "nagaram"], "Same letters, same counts."), (["rat", "car"], "Different letters.")],
      [["a", "a"], ["a", "b"], ["ab", "a"], ["aacc", "ccac"]], gen_anagram, is_anagram, "O(n)", "O(1) (26 counters)",
      ["If the lengths differ, can they be anagrams?", "Count how many times each letter appears in each string.",
       "Use one array of 26 counters: increment for s, decrement for t, and check that every counter ends at zero."]),
    P("move-zeroes", "Move Zeroes", "Easy", "Two pointers",
      "Given an integer array `nums`, move all `0`s to the end while keeping the relative order of the non-zero elements. Return the resulting array (do it in place in an interview).",
      ["1 <= nums.length <= 10^4", "-2^31 <= nums[i] <= 2^31 - 1"], "moveZeroes", [["nums", "int[]"]], "int[]",
      [([[0, 1, 0, 3, 12]], "Non-zeros keep their order."), ([[0]], "A single zero stays put.")],
      [[[1, 2, 3]], [[0, 0, 1]], [[1, 0]], [[-1, 0, 0, -2]]], gen_move_zeroes, move_zeroes, "O(n)", "O(1)",
      ["Can you do it without a second array?", "Keep a write pointer for where the next non-zero element should go.",
       "Copy each non-zero to nums[write++], then fill the rest with zeros (or swap as you go)."]),
    P("majority-element", "Majority Element", "Easy", "Boyer-Moore voting",
      "Given an array `nums` of size `n`, return the element that appears more than `n / 2` times. Such an element always exists.",
      ["1 <= n <= 5 * 10^4", "-10^9 <= nums[i] <= 10^9"], "majorityElement", [["nums", "int[]"]], "int",
      [([[3, 2, 3]], "3 appears twice out of three."), ([[2, 2, 1, 1, 1, 2, 2]], "2 appears four times.")],
      [[[1]], [[5, 5]], [[-1, -1, 2]], [[7, 1, 7, 2, 7]]], gen_majority, majority_element, "O(n)", "O(1)",
      ["A hash map of counts works in O(n) space. Can you use O(1)?",
       "Pair off different elements and cancel them. What survives?",
       "Boyer-Moore: keep a candidate and a count; on count 0 pick the current value, otherwise +1 for a match and -1 for a mismatch."]),
    P("valid-palindrome", "Valid Palindrome", "Easy", "Two pointers",
      "Given a string `s`, return `true` if it reads the same forwards and backwards after lowercasing it and removing every non-alphanumeric character.",
      ["1 <= s.length <= 2 * 10^5", "s consists of printable ASCII characters"], "isPalindrome", [["s", "string"]], "bool",
      [(["A man, a plan, a canal: Panama"], "amanaplanacanalpanama is a palindrome."), (["race a car"], "raceacar is not."), ([" "], "Empty after cleaning, so true.")],
      [[""], ["0P"], ["a."], [".,"], ["Aa"]], gen_palindrome, is_palindrome, "O(n)", "O(1)",
      ["You do not need to build the cleaned string.", "Use one pointer from each end and skip characters that are not letters or digits.",
       "While l < r: skip non-alphanumerics on both sides, compare lowercase chars, then move both pointers inward."]),
    P("climbing-stairs", "Climbing Stairs", "Easy", "1D dynamic programming",
      "You are climbing a staircase with `n` steps. Each move climbs 1 or 2 steps. Return how many distinct ways there are to reach the top.",
      ["1 <= n <= 45"], "climbStairs", [["n", "int"]], "int",
      [([2], "1+1 or 2."), ([3], "1+1+1, 1+2, 2+1.")],
      [[1], [4], [10], [45]], gen_stairs, climb_stairs, "O(n)", "O(1)",
      ["How can you reach step n? From which earlier steps?", "ways(n) = ways(n - 1) + ways(n - 2). Does that look familiar?",
       "Iterate with two variables holding the last two values (Fibonacci), avoiding exponential recursion."]),
    P("single-number", "Single Number", "Easy", "Bit manipulation",
      "Every element of `nums` appears exactly twice except one. Return that single element, using O(1) extra space.",
      ["1 <= nums.length <= 3 * 10^4", "-3 * 10^4 <= nums[i] <= 3 * 10^4"], "singleNumber", [["nums", "int[]"]], "int",
      [([[2, 2, 1]], "1 appears once."), ([[4, 1, 2, 1, 2]], "4 appears once.")],
      [[[1]], [[-1, 5, 5]], [[0, 7, 7]], [[3, -3, 3]]], gen_single, single_number, "O(n)", "O(1)",
      ["A hash set works but uses O(n) space. Which operation cancels equal values?", "x ^ x = 0 and x ^ 0 = x. XOR is also order-independent.",
       "XOR all the numbers together; the pairs cancel and the single number remains."]),
    P("missing-number", "Missing Number", "Easy", "Math / XOR",
      "Given an array `nums` of `n` distinct numbers taken from the range `[0, n]`, return the one number in the range that is missing.",
      ["1 <= n <= 10^4", "All values are distinct"], "missingNumber", [["nums", "int[]"]], "int",
      [([[3, 0, 1]], "n = 3, and 2 is missing."), ([[0, 1]], "n = 2, and 2 is missing."), ([[9, 6, 4, 2, 3, 5, 7, 0, 1]], "8 is missing.")],
      [[[0]], [[1]], [[1, 2]], [[2, 0]]], gen_missing, missing_number, "O(n)", "O(1)",
      ["What would the sum of 0..n be if nothing were missing?", "Expected sum minus actual sum gives the answer. XOR works too.",
       "Return n*(n+1)/2 - sum(nums), or XOR every index and value together."]),
    P("plus-one", "Plus One", "Easy", "Array, carry",
      "A non-negative integer is stored as an array of `digits`, most significant first, with no leading zeros. Return the digits of that integer plus one.",
      ["1 <= digits.length <= 100", "0 <= digits[i] <= 9"], "plusOne", [["digits", "int[]"]], "int[]",
      [([[1, 2, 3]], "123 + 1 = 124."), ([[9, 9]], "99 + 1 = 100.")],
      [[[0]], [[9]], [[1, 9, 9]], [[8, 9, 9, 9]]], gen_plus_one, plus_one, "O(n)", "O(1) (O(n) when every digit is 9)",
      ["The number may be too big for a 64-bit integer. Work on the digits directly.", "Where does a carry stop? What happens to trailing 9s?",
       "Scan from the right: turn 9s into 0s; increment the first non-9. If every digit was 9, prepend a 1."]),
    P("merge-sorted-arrays", "Merge Two Sorted Arrays", "Easy", "Two pointers",
      "Given two integer arrays `nums1` and `nums2`, each sorted in non-decreasing order, return one sorted array containing all their elements.",
      ["0 <= nums1.length, nums2.length <= 200", "-10^9 <= values <= 10^9"], "mergeSorted", [["nums1", "int[]"], ["nums2", "int[]"]], "int[]",
      [([[1, 2, 3], [2, 5, 6]], "[1,2,2,3,5,6]."), ([[1], []], "One side empty.")],
      [[[], []], [[], [1]], [[4, 5], [1, 2]], [[1, 1], [1, 1]]], gen_merge_sorted, merge_sorted, "O(m + n)", "O(m + n)",
      ["Concatenating and sorting is O((m+n) log(m+n)). Both inputs are already sorted, so use that.",
       "Keep one pointer in each array; the smaller current element goes next.",
       "Two pointers; append the smaller head each step, then append whatever remains. (In place in nums1, fill from the back.)"]),
    P("first-unique-character", "First Unique Character in a String", "Easy", "Counting",
      "Given a string `s`, return the index of the first character that appears exactly once, or `-1` if there is none.",
      ["1 <= s.length <= 10^5", "Lowercase English letters"], "firstUniqChar", [["s", "string"]], "int",
      [(["leetcode"], "'l' at index 0."), (["loveleetcode"], "'v' at index 2."), (["aabb"], "No unique character.")],
      [["a"], ["aa"], ["abcabd"], ["zzy"]], gen_first_uniq, first_uniq_char, "O(n)", "O(1) (26 counters)",
      ["You need to know each character's total count before deciding.", "Two passes: count everything first, then scan in order.",
       "Count with an array of 26; on the second pass return the first index whose count is 1."]),
    P("longest-common-prefix", "Longest Common Prefix", "Easy", "Strings",
      "Given an array of strings `strs`, return the longest prefix shared by all of them, or an empty string if there is none.",
      ["1 <= strs.length <= 200", "0 <= strs[i].length <= 200", "Lowercase English letters"], "longestCommonPrefix", [["strs", "string[]"]], "string",
      [([["flower", "flow", "flight"]], "\"fl\"."), ([["dog", "racecar", "car"]], "No shared prefix.")],
      [[[""]], [["a"]], [["ab", "a"]], [["same", "same"]], [["", "b"]]], gen_lcp, longest_common_prefix, "O(total characters)", "O(1)",
      ["The answer can be no longer than the shortest string.", "Start with the first string as the candidate and shrink it against each other string.",
       "Compare column by column (vertical scan) or shrink a prefix; stop at the first mismatch or string end."]),
    P("counting-bits", "Counting Bits", "Easy", "DP on bits",
      "Given an integer `n`, return an array `ans` of length `n + 1` where `ans[i]` is the number of `1` bits in the binary form of `i`.",
      ["0 <= n <= 10^5"], "countBits", [["n", "int"]], "int[]",
      [([2], "[0, 1, 1]."), ([5], "[0, 1, 1, 2, 1, 2].")],
      [[0], [1], [8], [16]], gen_count_bits, count_bits, "O(n)", "O(1) extra",
      ["Counting the bits of each number separately is O(n log n). Can earlier answers help?",
       "How does i relate to i >> 1 in binary?",
       "ans[i] = ans[i >> 1] + (i & 1)."]),
    P("is-subsequence", "Is Subsequence", "Easy", "Two pointers",
      "Given strings `s` and `t`, return `true` if `s` is a subsequence of `t`: it can be formed by deleting some (or no) characters of `t` without reordering the rest.",
      ["0 <= s.length <= 100", "0 <= t.length <= 10^4"], "isSubsequence", [["s", "string"], ["t", "string"]], "bool",
      [(["abc", "ahbgdc"], "a, b, c appear in order."), (["axc", "ahbgdc"], "There is no x.")],
      [["", ""], ["", "abc"], ["a", ""], ["aa", "a"], ["abc", "abc"]], gen_subseq, is_subsequence, "O(|t|)", "O(1)",
      ["Is it always safe to match the earliest possible character in t?", "Greedy matching works: walk through t once.",
       "Keep a pointer into s; advance it whenever t's current char matches. s is a subsequence if the pointer reaches the end."]),
    P("roman-to-integer", "Roman to Integer", "Easy", "Strings",
      "Convert a valid Roman numeral `s` (symbols I, V, X, L, C, D, M, with subtractive pairs such as IV and CM) to an integer.",
      ["1 <= s.length <= 15", "The value is in [1, 3999]"], "romanToInt", [["s", "string"]], "int",
      [(["III"], "3."), (["LVIII"], "50 + 5 + 3 = 58."), (["MCMXCIV"], "1000 + 900 + 90 + 4 = 1994.")],
      [["I"], ["IV"], ["IX"], ["MMMCMXCIX"], ["XL"]], gen_roman, roman_to_int, "O(n)", "O(1)",
      ["Most symbols just add. When does a symbol subtract?", "A symbol subtracts when a larger symbol comes right after it.",
       "Scan left to right: subtract value[i] if value[i] < value[i+1], else add it."]),
    P("squares-of-sorted-array", "Squares of a Sorted Array", "Easy", "Two pointers",
      "Given an integer array `nums` sorted in non-decreasing order, return the squares of each number, also sorted in non-decreasing order.",
      ["1 <= nums.length <= 10^4", "-10^4 <= nums[i] <= 10^4"], "sortedSquares", [["nums", "int[]"]], "int[]",
      [([[-4, -1, 0, 3, 10]], "[0, 1, 9, 16, 100]."), ([[-7, -3, 2, 3, 11]], "[4, 9, 9, 49, 121].")],
      [[[0]], [[-5]], [[-3, -2, -1]], [[1, 2, 3]]], gen_squares, sorted_squares, "O(n)", "O(n) for the output",
      ["Squaring then sorting is O(n log n). Where are the largest squares?", "The largest square is at one of the two ends.",
       "Two pointers from both ends; place the larger square at the back of the output and move that pointer inward."]),
]
