# Ayurveda Intelligence — Frontend

> **Project:** Ayurveda Intelligence — Evidence-Aware Ayurvedic Formulation Discovery  
> **Component:** Research, Discovery & Explainability Interface  
> **Project Type:** Hackathon Prototype  
> **Frontend Status:** Prototype Architecture / Incremental Development

---

## 1. Overview

The Ayurveda Intelligence frontend is the user-facing research and
discovery layer of the platform.

Its primary purpose is to transform the backend's structured knowledge
and recommendation output into an interface that allows users to:

- Search Ayurvedic terminology
- Understand terminology normalization
- Explore disease / condition mappings
- Discover ranked formulations
- Understand why a formulation was surfaced
- Inspect formulation information
- Trace the evidence path behind a result
- Compare formulations
- Explore the underlying knowledge base

The frontend is designed around one central principle:

> **A result should be understandable, not merely displayed.**

Instead of presenting a formulation as a black-box recommendation, the
interface exposes the reasoning path that produced the result.

---

# 2. Product Philosophy

The interface follows a premium research / knowledge-platform approach.

The visual and interaction design should feel closer to a modern
research intelligence product than a conventional medical website.

### Core principles

- Evidence before decoration
- Explanation before complexity
- Clear information hierarchy
- Minimal visual noise
- Structured data presentation
- Traceable results
- Consistent terminology
- Fast search-to-result interaction
- Explicit distinction between prototype ranking and clinical advice

---

# 3. Primary User Journey

The main experience follows this pipeline:

```text
                    USER
                     │
                     ▼
             Search / Query Input
                     │
                     ▼
          ┌──────────────────────┐
          │ Input Normalization  │
          └──────────┬───────────┘
                     │
                     ▼
          Terminology Resolution
                     │
                     ▼
              Disease / Condition
                     │
                     ▼
          Formulation Candidate Set
                     │
                     ▼
             Ranking / Scoring
                     │
                     ▼
          ┌──────────────────────┐
          │ Explainable Results  │
          └──────────┬───────────┘
                     │
             ┌───────┼────────┐
             ▼       ▼        ▼
          Details  Compare  Evidence
