# Retrieval Engine

## Goal

Return a useful candidate set while reducing the limitations of exact keyword matching.

## Hybrid strategy

### Structured retrieval
Uses known fields, relationships, filters, and exact/canonical matches.

### Semantic retrieval
Uses vector or embedding-based similarity when supported by the implementation.

### Candidate fusion

Results from both paths are merged and deduplicated before ranking.

## Conceptual scoring

```text
candidate_score =
    w1 * lexical_relevance
  + w2 * semantic_relevance
  + w3 * relationship_match
  + w4 * evidence_signal
```

The actual weights should be stored in configuration and documented when finalized.

## Failure cases

- no candidates
- ambiguous query
- unavailable vector index
- incomplete metadata
- duplicate records

The system should fail gracefully and explain when a result set is limited.
