# Social Media Listening (TikTok + LLMs)

A social-listening pipeline that collects public TikTok content at scale and turns
it into structured insight using large language models. Data is gathered through the
**Apify** platform and then classified and summarized with LLMs.

## Objective

Move from raw, unstructured social-media text to analyzable, labeled data: collect
TikTok posts and comments for a set of accounts or topics, then use LLMs to classify
them (theme, sentiment, intent) and produce post-level analytics.

## What's inside

- **`api_calls/`** — TikTok collection scripts that pull posts and metadata via the
  Apify API (`01_tiktok.py`, `02_tiktok.py`).
- **`llm_classification/`** — LLM-based analysis:
  - `tiktok_posts.py` — classify and structure scraped posts.
  - `tiktok_comentarios.py` — classify comment threads.
  - `analytics_post.py` — post-level analytics and aggregation.
- **`tiktok_unique_url.txt`** — deduplicated set of collected TikTok URLs.
- **`test.ipynb`** — exploratory notebook.

## Stack

Python · Apify · LLM APIs · Poetry.

## Setup

```bash
poetry install
poetry shell
```
