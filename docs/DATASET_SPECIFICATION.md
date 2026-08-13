# Dataset Specification

## Seed dataset

The hackathon prototype should begin with a small, manually reviewed dataset that is sufficient to demonstrate the complete pipeline.

## Recommended record groups

### Formulations
- formulation ID
- name
- aliases
- description
- source reference

### Ingredients
- ingredient ID
- canonical name
- aliases
- relationships
- source reference

### Indications / concepts
- concept ID
- canonical term
- aliases
- source reference

### Evidence
- evidence ID
- linked entity
- reference
- evidence type
- provenance metadata

## Validation

Run checks for:
- duplicate IDs
- missing required fields
- broken references
- inconsistent terminology
- unsupported claims
- malformed relationships
