<h1 align="center">Social Media Listening</h1>

<p align="center">
  <strong>Collect public TikTok content at scale and turn it into structured insight with large language models.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Apify-scraping-00b04f?logo=apify&logoColor=white" alt="Apify">
  <img src="https://img.shields.io/badge/LLM-classification-412991?logo=openai&logoColor=white" alt="LLM">
  <img src="https://img.shields.io/badge/Poetry-deps-60a5fa?logo=poetry&logoColor=white" alt="Poetry">
</p>

---

## Overview

A social-listening pipeline that goes from raw, unstructured social media to analyzable,
labeled data. It collects TikTok **posts and comments** through the **Apify** platform,
then uses LLMs to classify and summarize them (theme, sentiment, intent) and produce
post-level analytics. The goal is to make large-scale social text usable for research and
decision-making, where one search angle or a manual read would never scale.

## Pipeline

| Stage | What happens |
|---|---|
| **Collect** | `api_calls/01_tiktok.py`, `02_tiktok.py` pull posts and metadata via the Apify API |
| **Deduplicate** | `tiktok_unique_url.txt` keeps a clean, deduplicated set of collected URLs |
| **Classify** | `llm_classification/tiktok_posts.py` and `tiktok_comentarios.py` label posts and comment threads with LLMs |
| **Analyze** | `llm_classification/analytics_post.py` aggregates into post-level analytics |

## What's inside

- **`api_calls/`** — TikTok collection scripts (Apify).
- **`llm_classification/`** — LLM classification of posts and comments, plus analytics.
- **`test.ipynb`** — exploratory notebook.

## Tech Stack

Python · Apify · LLM APIs · Poetry.

## Setup

```bash
poetry install
poetry shell
```
