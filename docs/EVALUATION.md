# Evaluation

## Evaluation goals

Measure whether the system retrieves relevant information and presents it accurately and consistently.

## Retrieval metrics

Depending on the final implementation:
- Precision@K
- Recall@K
- Mean Reciprocal Rank
- qualitative relevance review

## NLP evaluation

Create a small test set containing:
- canonical terms
- aliases
- spelling variations
- natural-language descriptions
- unknown terms

Measure normalization accuracy and failure behavior.

## Ranking evaluation

For a manually reviewed query set:
1. Generate candidates.
2. Obtain expected relevant items.
3. Compare top-k results.
4. Record errors.
5. Tune weights only after reviewing failures.

## Safety evaluation

Test:
- unsupported requests
- ambiguous requests
- missing evidence
- empty results
- invalid inputs
