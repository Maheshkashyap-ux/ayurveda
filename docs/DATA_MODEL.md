# Data Model

## Core entities

```mermaid
erDiagram
    FORMULATION ||--o{ FORMULATION_INGREDIENT : contains
    INGREDIENT ||--o{ FORMULATION_INGREDIENT : used_in
    FORMULATION ||--o{ FORMULATION_INDICATION : associated_with
    INDICATION ||--o{ FORMULATION_INDICATION : maps_to
    ENTITY ||--o{ ENTITY_RELATION : source
    ENTITY ||--o{ ENTITY_RELATION : target
    REFERENCE ||--o{ EVIDENCE : supports
    FORMULATION ||--o{ EVIDENCE : described_by

    FORMULATION {
        string id
        string name
        string description
        string source
    }

    INGREDIENT {
        string id
        string canonical_name
        string aliases
    }

    INDICATION {
        string id
        string name
        string aliases
    }

    REFERENCE {
        string id
        string title
        string source_type
        string citation
    }
```

## Provenance

Each important knowledge record should retain:
- source
- source identifier
- citation or reference
- extraction/entry date
- data version
- validation status

## Design rule

The data model should make it possible to answer not only "what was returned?" but also "why was it returned and where did the supporting information come from?"
