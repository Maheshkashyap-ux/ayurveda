# Recommendation and Ranking Engine

## Objective

Convert a retrieved candidate set into an ordered result list that can be explained to the user.

## Ranking stages

1. Candidate generation
2. Feature calculation
3. Score calculation
4. Sorting
5. Explanation generation
6. Safety/evidence filtering or annotation

## Explainability

For each top result, expose relevant signals such as:
- matched concept
- matching ingredient/formulation relationship
- semantic relevance
- supporting reference availability
- safety or limitation notice

## Important distinction

A ranking score indicates relevance within the system. It should not be presented as clinical certainty or medical efficacy.
