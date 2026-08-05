---
name: product-review-analyzer
description: Use this skill whenever a user provides or requests the analysis of a JSON file containing product reviews. This skill filters for low-rated reviews (< 3 stars), groups them by category, calculates average sentiment, and extracts top negative keywords.
---

# Product Review Analyzer

A workflow for systematic analysis of customer reviews to identify product quality issues and sentiment trends.

## Core Rules & Constraints

- **Filtering:** Always filter the input data to include only reviews with a rating strictly less than 3 stars.
- **Data Integrity:** Group items exactly by the `category` field present in the JSON source.
- **Keyword Extraction:** Perform basic keyword tokenization (words length > 3) to identify the most frequent terms associated with negative feedback.
- **Input Format:** Expects a JSON array of objects, where each object contains: `product_name`, `category`, `rating`, `review`, and `sentiment_score`.

## Workflow Steps

1. **Preparation:** Ensure the review data is available as a JSON file in the workspace.
2. **Analysis:** Run the `skills/product-review-analyzer/scripts/analyze.py` script using the `run_code` tool, providing the path to the user's review file as an argument.
3. **Reporting:** Present the findings in a structured markdown table: `Category | Average Sentiment | Top 3 Negative Keywords`.

*Note: If keyword extraction returns no results (due to insufficient text data), explicitly state that in your response rather than omitting the column.*

## Output Specification

The analysis results should be structured as:

| Category | Average Sentiment | Top 3 Negative Keywords |
| :--- | :--- | :--- |
| Electronics | 0.17 | connection, battery, keeps |

## Reference Script

The logic for this analysis is encapsulated in `skills/product-review-analyzer/scripts/analyze.py`.
