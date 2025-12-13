// src/utils/api.js

export function analyzeCode(code) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        issues: [
          {
            type: "Unused Variable",
            severity: "warning",
            line: 12,
            message: "Variable 'x' is declared but never used",
          },
          {
            type: "Missing Docstring",
            severity: "info",
            line: 1,
            message: "Add a docstring to improve readability",
          },
        ],
        complexity: {
          bigO: "O(n^2)",
          score: 68,
          explanation: "Nested loops detected",
        },
        qualityScore: 72,
      });
    }, 600);
  });
}

export function refactorCode(code) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        refactoredCode: `def find_max(nums):\n    return max(nums)`,
        explanation:
          "Simplified the loop using Python built-in max(), improved readability.",
      });
    }, 700);
  });
}

export function analyzeAndRefactor(code) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        issues: [
          {
            type: "Deep Nesting",
            severity: "warning",
            line: 8,
            message: "Reduce nesting to improve readability",
          },
        ],
        complexity: {
          bigO: "O(n)",
          score: 85,
          explanation: "Single loop after refactor",
        },
        qualityScore: 88,
        refactoredCode: `def process(items):\n    return [i*2 for i in items]`,
        explanation: "Removed nested loops and used list comprehension.",
      });
    }, 900);
  });
}

export function getVersionHistory(sessionId) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        {
          id: "v1",
          label: "Initial Upload",
          timestamp: "2 mins ago",
        },
        {
          id: "v2",
          label: "AI Refactor",
          timestamp: "Just now",
        },
      ]);
    }, 400);
  });
}

export function getVersion(versionId) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        code: "def add(a,b): return a+b",
        issues: [],
        complexity: {
          bigO: "O(1)",
          score: 95,
        },
        qualityScore: 92,
        diff: "+ Simplified function",
      });
    }, 400);
  });
}
