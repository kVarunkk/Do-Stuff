---
name: react-performance-optimizer
description: Identifies react performance bottlenecks, unnecessary re-renders, and memory leaks in React/Next.js components. Trigger when reviewing React code for performance optimizations.
---

# React & Next.js Performance Optimization Guidelines

When reviewing or refactoring React components for performance, follow these guidelines to eliminate unnecessary re-renders and reduce bundle size:

## 1. Primary Inspection Rules

1. **State Co-location:**
   - Move state as close to where it's used as possible. Avoid pushing state up into parent components if sibling components don't consume it.

2. **Memoization Boundaries:**
   - Wrap expensive computation in `useMemo`.
   - Wrap callback props passed to memoized child components in `useCallback`.
   - Do **not** blindly wrap every primitive function in `useCallback` (adds overhead without benefit).

3. **Context Provider Splitting:**
   - Separate Context into distinct State and Dispatch contexts to prevent consumers from re-rendering on action dispatches.

4. **Dynamic Imports & Code Splitting:**
   - Heavy client components (e.g., charts, rich text editors) must use `next/dynamic` or `React.lazy()` with `Suspense`.

## 2. Deep Reference

For a complete audit checklist on Context splitting and `useCallback` dependencies, refer to the auxiliary reference file located at:
`references/re-render-checklist.md` relative to this skill's root directory.

## 3. Output Format

Provide your feedback in the following format:

- **Root Cause Analysis:** Short explanation of the bottleneck.
- **Optimized Code:** Updated component code.
- **Impact Summary:** Estimated reduction in render cycles or bundle footprint.
