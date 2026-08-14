# Ayurveda Intelligence — Backend

> **Project:** Ayurveda Intelligence — Evidence-Aware Ayurvedic Formulation Discovery  
> **Component:** Backend / Recommendation Engine  
> **Purpose:** Hackathon Prototype  
> **Status:** Prototype / Incremental Development

---

## 1. Backend Overview

The backend provides the processing and knowledge-retrieval layer for the
Ayurveda Intelligence prototype.

Its primary responsibility is to transform a user's natural-language
search term into a structured and explainable result.

The current prototype follows this pipeline:

```text
User Input
    |
    v
Input Normalization
    |
    v
Terminology Resolution
    |
    v
Disease / Condition Lookup
    |
    v
Formulation Retrieval
    |
    v
Candidate Ranking
    |
    v
Explainable Result

---

# 23. Quick Start

## 23.1 Create a Virtual Environment

From the project root:

```bash
python -m venv .venv
