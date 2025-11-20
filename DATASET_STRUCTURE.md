# Benchmark Dataset Structure

## Task Format

Each benchmark task follows this JSON schema:

```json
{
  "id": "unique_task_identifier",
  "difficulty": "easy|medium|hard|extreme",
  "category": "string_manipulation|algorithms|data_structures|oop|async|...",
  "title": "Short task title",
  "prompt": "The actual task description given to the model",
  "test_cases": [
    {
      "input": "function arguments as dict or list",
      "expected_output": "expected return value",
      "timeout": 1.0,
      "weight": 1.0,
      "description": "what this test case validates"
    }
  ],
  "reference_solution": "optimal python solution",
  "metadata": {
    "python_version": "3.11+",
    "allowed_imports": ["list", "of", "allowed", "modules"],
    "tags": ["list", "comprehension", "edge-cases"],
    "created_at": "2025-01-15",
    "author": "contributor_name"
  }
}
```

## Difficulty Tiers

### Easy (50+ tasks)
**Target Time**: < 5 seconds
**Skills Tested**: Basic syntax, built-in functions, simple logic

**Categories**:
- String manipulation
- List/dict operations
- Basic math
- Simple conditionals
- File I/O basics

**Example Task**:
```json
{
  "id": "easy_001",
  "difficulty": "easy",
  "category": "string_manipulation",
  "title": "Reverse Words in String",
  "prompt": "Write a function that takes a string and returns it with words in reverse order.\n\nExample:\nInput: 'hello world'\nOutput: 'world hello'",
  "test_cases": [
    {
      "input": {"s": "hello world"},
      "expected_output": "world hello",
      "timeout": 0.5,
      "weight": 1.0,
      "description": "basic case"
    },
    {
      "input": {"s": ""},
      "expected_output": "",
      "timeout": 0.5,
      "weight": 1.0,
      "description": "empty string"
    },
    {
      "input": {"s": "python is awesome"},
      "expected_output": "awesome is python",
      "timeout": 0.5,
      "weight": 1.0,
      "description": "multiple words"
    }
  ],
  "reference_solution": "def reverse_words(s: str) -> str:\n    return ' '.join(s.split()[::-1])",
  "metadata": {
    "python_version": "3.8+",
    "allowed_imports": [],
    "tags": ["strings", "basic"]
  }
}
```

### Medium (50+ tasks)
**Target Time**: 5-15 seconds
**Skills Tested**: Algorithms, OOP, error handling, common patterns

**Categories**:
- Sorting/searching algorithms
- Class design
- Exception handling
- Regular expressions
- Data validation
- JSON/CSV processing

**Example Task**:
```json
{
  "id": "medium_001",
  "difficulty": "medium",
  "category": "algorithms",
  "title": "Binary Search Implementation",
  "prompt": "Implement binary search on a sorted list. Return the index of the target if found, otherwise return -1.\n\nSignature: def binary_search(arr: List[int], target: int) -> int",
  "test_cases": [
    {
      "input": {"arr": [1, 3, 5, 7, 9], "target": 5},
      "expected_output": 2,
      "timeout": 1.0,
      "weight": 1.0,
      "description": "target in middle"
    },
    {
      "input": {"arr": [1, 3, 5, 7, 9], "target": 1},
      "expected_output": 0,
      "timeout": 1.0,
      "weight": 1.0,
      "description": "target at start"
    },
    {
      "input": {"arr": [1, 3, 5, 7, 9], "target": 10},
      "expected_output": -1,
      "timeout": 1.0,
      "weight": 1.0,
      "description": "target not found"
    },
    {
      "input": {"arr": [], "target": 5},
      "expected_output": -1,
      "timeout": 1.0,
      "weight": 1.5,
      "description": "empty array edge case"
    }
  ],
  "reference_solution": "def binary_search(arr: List[int], target: int) -> int:\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1",
  "metadata": {
    "python_version": "3.8+",
    "allowed_imports": ["typing"],
    "tags": ["algorithms", "binary_search", "arrays"]
  }
}
```

### Hard (30+ tasks)
**Target Time**: 15-45 seconds
**Skills Tested**: Complex algorithms, design patterns, optimization, async

**Categories**:
- Graph algorithms
- Dynamic programming
- Advanced OOP (decorators, metaclasses)
- Async/await patterns
- Memory optimization
- Concurrency

**Example Task**:
```json
{
  "id": "hard_001",
  "difficulty": "hard",
  "category": "graphs",
  "title": "Shortest Path in Weighted Graph",
  "prompt": "Implement Dijkstra's algorithm to find the shortest path in a weighted graph.\n\nInput: graph as adjacency list (dict), start node, end node\nOutput: (shortest_distance, path)\n\nExample:\ngraph = {'A': [('B', 1), ('C', 4)], 'B': [('C', 2), ('D', 5)], 'C': [('D', 1)], 'D': []}\nshortest_path(graph, 'A', 'D') -> (4, ['A', 'B', 'C', 'D'])",
  "test_cases": [
    {
      "input": {
        "graph": {
          "A": [["B", 1], ["C", 4]],
          "B": [["C", 2], ["D", 5]],
          "C": [["D", 1]],
          "D": []
        },
        "start": "A",
        "end": "D"
      },
      "expected_output": [4, ["A", "B", "C", "D"]],
      "timeout": 2.0,
      "weight": 1.0,
      "description": "basic weighted graph"
    },
    {
      "input": {
        "graph": {"A": [["B", 1]], "B": [], "C": []},
        "start": "A",
        "end": "C"
      },
      "expected_output": [null, []],
      "timeout": 2.0,
      "weight": 1.5,
      "description": "no path exists"
    }
  ],
  "reference_solution": "import heapq\nfrom typing import Dict, List, Tuple, Optional\n\ndef shortest_path(graph: Dict[str, List[Tuple[str, int]]], start: str, end: str) -> Tuple[Optional[int], List[str]]:\n    distances = {node: float('inf') for node in graph}\n    distances[start] = 0\n    previous = {}\n    pq = [(0, start)]\n    \n    while pq:\n        current_dist, current = heapq.heappop(pq)\n        if current == end:\n            break\n        if current_dist > distances[current]:\n            continue\n        for neighbor, weight in graph[current]:\n            distance = current_dist + weight\n            if distance < distances[neighbor]:\n                distances[neighbor] = distance\n                previous[neighbor] = current\n                heapq.heappush(pq, (distance, neighbor))\n    \n    if distances[end] == float('inf'):\n        return (None, [])\n    \n    path = []\n    current = end\n    while current in previous:\n        path.append(current)\n        current = previous[current]\n    path.append(start)\n    path.reverse()\n    \n    return (distances[end], path)",
  "metadata": {
    "python_version": "3.8+",
    "allowed_imports": ["heapq", "typing"],
    "tags": ["graphs", "dijkstra", "algorithms", "shortest_path"]
  }
}
```

### Extremely Hard (20+ tasks)
**Target Time**: 45+ seconds
**Skills Tested**: System design, advanced algorithms, optimization, edge cases

**Categories**:
- Advanced algorithms (suffix trees, segment trees)
- Custom metaclasses and descriptors
- Complex async systems
- Memory-efficient data structures
- Compiler/parser design
- Performance optimization

**Example Task**:
```json
{
  "id": "extreme_001",
  "difficulty": "extreme",
  "category": "data_structures",
  "title": "LRU Cache with TTL",
  "prompt": "Implement an LRU (Least Recently Used) cache with time-to-live (TTL) for entries.\n\nRequirements:\n- get(key): Return value if exists and not expired, else None\n- put(key, value, ttl): Add/update entry with TTL in seconds\n- Auto-evict expired entries\n- Evict least recently used when capacity is full\n- O(1) time complexity for get and put\n\nClass signature:\nclass LRUCacheWithTTL:\n    def __init__(self, capacity: int): ...\n    def get(self, key: str) -> Optional[Any]: ...\n    def put(self, key: str, value: Any, ttl: int): ...",
  "test_cases": [
    {
      "input": {
        "operations": [
          ["init", 2],
          ["put", "a", 1, 10],
          ["put", "b", 2, 10],
          ["get", "a"],
          ["put", "c", 3, 10],
          ["get", "b"]
        ]
      },
      "expected_output": [null, null, null, 1, null, null],
      "timeout": 3.0,
      "weight": 1.0,
      "description": "LRU eviction"
    },
    {
      "input": {
        "operations": [
          ["init", 2],
          ["put", "a", 1, 1],
          ["sleep", 2],
          ["get", "a"]
        ]
      },
      "expected_output": [null, null, null, null],
      "timeout": 5.0,
      "weight": 1.5,
      "description": "TTL expiration"
    }
  ],
  "reference_solution": "from collections import OrderedDict\nimport time\nfrom typing import Any, Optional\n\nclass LRUCacheWithTTL:\n    def __init__(self, capacity: int):\n        self.capacity = capacity\n        self.cache = OrderedDict()\n        self.expiry = {}\n    \n    def _evict_expired(self):\n        current_time = time.time()\n        expired_keys = [k for k, exp in self.expiry.items() if exp < current_time]\n        for key in expired_keys:\n            del self.cache[key]\n            del self.expiry[key]\n    \n    def get(self, key: str) -> Optional[Any]:\n        self._evict_expired()\n        if key not in self.cache:\n            return None\n        if key in self.expiry and self.expiry[key] < time.time():\n            del self.cache[key]\n            del self.expiry[key]\n            return None\n        self.cache.move_to_end(key)\n        return self.cache[key]\n    \n    def put(self, key: str, value: Any, ttl: int):\n        self._evict_expired()\n        if key in self.cache:\n            self.cache.move_to_end(key)\n        self.cache[key] = value\n        self.expiry[key] = time.time() + ttl\n        if len(self.cache) > self.capacity:\n            oldest = next(iter(self.cache))\n            del self.cache[oldest]\n            del self.expiry[oldest]",
  "metadata": {
    "python_version": "3.8+",
    "allowed_imports": ["collections", "time", "typing"],
    "tags": ["data_structures", "lru_cache", "ttl", "optimization"]
  }
}
```

## Task Categories

### Core Categories
1. **String Manipulation**: parsing, regex, formatting
2. **Data Structures**: lists, dicts, sets, trees, graphs
3. **Algorithms**: sorting, searching, DP, greedy
4. **Object-Oriented**: classes, inheritance, patterns
5. **Functional**: lambdas, map/filter/reduce, decorators
6. **Async**: async/await, concurrency, threading
7. **File I/O**: reading, writing, CSV, JSON, binary
8. **Error Handling**: try/except, custom exceptions
9. **Testing**: writing tests, mocking, fixtures
10. **Optimization**: time/space complexity improvements

### Special Categories
11. **Python-Specific**: context managers, generators, itertools
12. **Standard Library**: collections, functools, itertools
13. **Web**: HTTP requests, APIs, parsing HTML
14. **Data Science**: pandas, numpy operations (if applicable)
15. **System**: subprocess, environment, file system

## Quality Guidelines

### Good Tasks
- Clear, unambiguous prompts
- Comprehensive test cases (happy path + edge cases)
- Realistic scenarios
- Multiple valid solutions possible
- Tests for correctness, not specific implementation

### Avoid
- Trick questions
- Overly verbose prompts
- Tasks requiring specific libraries (unless specified)
- Ambiguous expected outputs
- Tasks that are too similar

## Task Contribution

Community members can contribute tasks via:
1. JSON file in `benchmarks/tasks/{difficulty}/`
2. Pull request with task + test cases
3. Automated validation checks
4. Review by maintainers

## Dataset Size Targets

- **Easy**: 50-100 tasks
- **Medium**: 50-100 tasks
- **Hard**: 30-50 tasks
- **Extreme**: 20-30 tasks

**Total**: 150-280 high-quality tasks

## Versioning

Dataset versions follow semantic versioning:
- **Major**: Breaking changes to task format
- **Minor**: New tasks added
- **Patch**: Fixes to existing tasks

Current: `v1.0.0`

## Testing the Dataset

Before adding tasks:
1. Verify test cases pass with reference solution
2. Ensure prompts are clear
3. Check edge cases are covered
4. Test with multiple models
5. Validate JSON schema
