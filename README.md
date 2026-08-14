# Ayurveda Intelligence — Evidence-Aware Ayurvedic Formulation Discovery

> **Project:** Ayurveda Intelligence — Evidence-Aware Ayurvedic Formulation Discovery
> **Project Type:** Hackathon Prototype / Research Platform
> **Architecture:** Modular Full-Stack Knowledge Intelligence Platform
> **Status:** Active Development / Prototype
> **Primary Goal:** Explainable Ayurvedic formulation discovery through terminology normalization, structured knowledge retrieval, ranking, and evidence traceability

---

## 1. Project Overview

The Ayurveda Intelligence system is a research-oriented software platform
designed to help users discover and explore Ayurvedic formulations through
structured terminology, disease relationships, formulation information,
ingredients, and available evidence.

The platform is designed around a central principle:

> Do not simply return a formulation. Show the path that explains why the
> formulation was surfaced.

The intended experience is:

    USER QUERY
        |
        v
    TERMINOLOGY NORMALIZATION
        |
        v
    CONDITION / DISEASE IDENTIFICATION
        |
        v
    FORMULATION RETRIEVAL
        |
        v
    RESULT RANKING
        |
        v
    EXPLAINABILITY
        |
        v
    FORMULATION DETAILS
        |
        v
    INGREDIENTS
        |
        v
    EVIDENCE / REFERENCES
        |
        v
    KNOWLEDGE GRAPH / RESEARCH EXPLORATION

The system therefore behaves as a knowledge-discovery and research
platform rather than a conventional keyword-search application.

---

## 2. Problem Statement

Ayurvedic knowledge is distributed across classical literature, reference
materials, repositories, structured datasets, and other sources.

The same disease, symptom, or concept may appear under different:

- Names
- Synonyms
- Spellings
- Transliteration formats
- Sanskrit terminology
- Regional terminology
- Alternative terminology
- Context-dependent representations

A traditional keyword search system may therefore fail when the user's
input does not exactly match the stored database value.

For example:

    USER INPUT
    "fever"

        |
        v

    NORMALIZATION

        |
        v

    "Jvara"

        |
        v

    CONDITION

        |
        v

    RELATED FORMULATIONS

The system is intended to bridge this terminology gap.

---

## 3. Core Project Objective

The primary objective is to build a platform that can transform an
unstructured user query into a structured and explainable research path.

The intended pipeline is:

    QUERY
      |
      v
    INTERPRETATION
      |
      v
    NORMALIZED CONCEPT
      |
      v
    CONDITION / DISEASE
      |
      v
    FORMULATION CANDIDATES
      |
      v
    RANKING
      |
      v
    EXPLANATION
      |
      v
    EVIDENCE
      |
      v
    RESEARCH EXPLORATION

The system should allow the user to understand not only what result was
returned, but also why it was returned.

---

## 4. Product Vision

The long-term product vision is:

    SEARCH
      |
      v
    UNDERSTAND
      |
      v
    DISCOVER
      |
      v
    EXPLAIN
      |
      v
    COMPARE
      |
      v
    VERIFY
      |
      v
    EXPLORE

The platform should provide an experience similar to a premium research
and knowledge product.

The interface and backend should work together to make complex Ayurvedic
knowledge easier to search, understand, navigate, and inspect.

---

## 5. Core System Principles

The project is based on the following principles.

### Explainability

Every ranked result should have an understandable retrieval path whenever
the backend has sufficient information to provide one.

### Traceability

Relationships between:

    TERM
      |
      v
    CONDITION
      |
      v
    FORMULATION
      |
      v
    INGREDIENT
      |
      v
    EVIDENCE
      |
      v
    REFERENCE

should remain inspectable.

### Structured Knowledge

Important Ayurvedic concepts should be represented as structured entities
and relationships rather than only as unstructured text.

### Modular Architecture

Frontend, backend, data, ML/NLP, and evidence components should remain
separable so that each can evolve independently.

### Progressive Intelligence

The initial system can use deterministic structured retrieval while future
versions can introduce increasingly sophisticated ML/NLP capabilities.

### Data Integrity

The platform must distinguish between:

    VERIFIED INFORMATION
    INFERRED INFORMATION
    MODEL-GENERATED INFORMATION
    INFORMATION NOT AVAILABLE

The system must never fabricate evidence or references.

---

## 6. High-Level System Architecture

Conceptual architecture:

                         USER
                           |
                           v
                  +------------------+
                  |     FRONTEND     |
                  | Research UI      |
                  | Search / Explore |
                  +--------+---------+
                           |
                           | HTTP / API
                           v
                  +------------------+
                  |     BACKEND      |
                  | API / Retrieval  |
                  | Business Logic   |
                  +--------+---------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
        +---------+   +---------+   +---------+
        |  DATA   |   |  ML/NLP |   | EVIDENCE|
        |  LAYER  |   |  LAYER  |   |  LAYER  |
        +---------+   +---------+   +---------+
             |             |             |
             +-------------+-------------+
                           |
                           v
                  KNOWLEDGE RELATIONSHIPS

The architecture is designed so that the frontend focuses on presentation
and interaction while the backend owns retrieval, ranking, processing,
and knowledge logic.

---

## 7. Repository Architecture

The project repository is organized into major functional areas.

    ayurveda/
    |
    +-- architecture/
    |
    +-- backend/
    |
    +-- data/
    |
    +-- docs/
    |
    +-- frontend/
    |
    +-- ml/
    |
    +-- scripts/
    |
    +-- ARCHITECTURE.md
    +-- IDEATION_AND_STRATEGY.md
    +-- HANDOFF.md
    +-- MASTER_BUILD_PROMPT.md
    +-- PRE_TEST_READINESS.md
    +-- README.md

Each directory has a defined responsibility.

---

## 8. Repository Components

### `architecture/`

Contains system-level architecture and flow documentation.

Expected documentation includes:

- System architecture
- Component relationships
- Data flow
- Search flow
- Retrieval flow
- Explainability flow
- Evidence flow
- Future ML/NLP architecture
- Knowledge graph architecture

---

### `backend/`

Contains the backend API and application logic.

The backend is responsible for:

- API endpoints
- Request validation
- Search processing
- Terminology normalization
- Disease retrieval
- Formulation retrieval
- Ingredient retrieval
- Ranking
- Explanation generation
- Evidence relationships
- Error handling
- Future ML/NLP integration

Detailed backend implementation information is maintained in:

    backend/README.md

---

### `data/`

Contains structured Ayurvedic knowledge.

The data layer can contain:

    DISEASE
    FORMULATION
    INGREDIENT
    SYNONYM
    RELATIONSHIP
    EVIDENCE
    REFERENCE

The data directory forms the foundation of the knowledge system.

---

### `docs/`

Contains supporting documentation such as:

- Research notes
- Development notes
- Architecture decisions
- Implementation guides
- Testing information
- Project planning

---

### `frontend/`

Contains the user-facing research and knowledge interface.

The frontend is responsible for:

- Search
- Processing reveal
- Normalization display
- Ranked results
- Match scores
- Explainability
- Formulation details
- Disease details
- Ingredient details
- Comparison
- Evidence presentation
- Knowledge graph visualization
- Research dashboard

Detailed frontend implementation information is maintained in:

    frontend/README.md

---

### `ml/`

Contains current or future machine-learning and NLP components.

Potential capabilities include:

- Semantic terminology matching
- Entity recognition
- Query normalization
- Semantic similarity
- Intelligent ranking
- Knowledge extraction
- Context-aware search

---

### `scripts/`

Contains utility scripts for:

- Data processing
- Data validation
- Dataset preparation
- Development setup
- Import / export
- Automation

---

## 9. Main Application Flow

The primary end-to-end flow is:

    USER
      |
      v
    SEARCH QUERY
      |
      v
    QUERY VALIDATION
      |
      v
    TERMINOLOGY NORMALIZATION
      |
      v
    CONDITION IDENTIFICATION
      |
      v
    FORMULATION RETRIEVAL
      |
      v
    RESULT RANKING
      |
      v
    EXPLAINABILITY
      |
      v
    FORMULATION DETAILS
      |
      v
    INGREDIENTS
      |
      v
    EVIDENCE
      |
      v
    RESEARCH EXPLORATION

---

## 10. Core User Loop

The most important user loop is:

    SEARCH
      |
      v
    UNDERSTAND
      |
      v
    DISCOVER
      |
      v
    EXPLAIN
      |
      v
    VERIFY

The user should finish the loop with:

> A clear and traceable understanding of why a formulation was surfaced
> for their search term.

---

## 11. Search Architecture

The initial search architecture is based on structured retrieval.

    USER QUERY
        |
        v
    QUERY VALIDATION
        |
        v
    TERM LOOKUP
        |
        +---- EXACT MATCH
        |
        +---- SYNONYM MATCH
        |
        +---- ALTERNATIVE TERM
        |
        v
    NORMALIZED TERM
        |
        v
    CONDITION / DISEASE
        |
        v
    RELATED FORMULATIONS
        |
        v
    RANKING
        |
        v
    RESPONSE

The architecture can later be extended with semantic retrieval.

---

## 12. Terminology Normalization

Terminology normalization is a core capability of the platform.

Its purpose is to transform a user-provided term into a structured
knowledge concept.

Example:

    USER TERM

    fever

        |
        v

    NORMALIZATION

        |
        v

    Jvara

The system may eventually support:

- Exact terminology
- Synonyms
- Alternative spellings
- Transliteration
- Sanskrit terminology
- Regional terminology
- Related terminology
- Semantic similarity

The normalized interpretation should be returned explicitly by the
backend so that the frontend can display it.

---

## 13. Normalization Pipeline

Conceptual pipeline:

    INPUT
      |
      v
    CLEANING
      |
      v
    TOKENIZATION / PARSING
      |
      v
    TERM LOOKUP
      |
      +---- EXACT
      |
      +---- SYNONYM
      |
      +---- ALTERNATIVE
      |
      +---- FUTURE SEMANTIC MATCH
      |
      v
    NORMALIZED CONCEPT
      |
      v
    CONDITION MAPPING

The exact implementation depends on the current backend and future
ML/NLP architecture.

---

## 14. Disease / Condition Mapping

After normalization, the system identifies the related disease or
condition.

Conceptual relationship:

    USER TERM
        |
        v
    NORMALIZED TERM
        |
        v
    CONDITION
        |
        v
    FORMULATIONS

Example:

    "fever"
        |
        v
    "Jvara"
        |
        v
    Jvara Condition
        |
        +---- Formulation A
        +---- Formulation B
        +---- Formulation C

---

## 15. Formulation Retrieval

The formulation retrieval layer identifies candidate formulations related
to the interpreted condition.

Conceptually:

    CONDITION
        |
        +---- FORMULATION A
        |
        +---- FORMULATION B
        |
        +---- FORMULATION C
        |
        +---- FORMULATION D

The backend should return structured formulation information rather than
only plain text names.

---

## 16. Ranking Architecture

Candidate formulations can be ranked using available relevance signals.

Conceptual ranking pipeline:

    CANDIDATE FORMULATION
            |
            +---- TERMINOLOGY RELEVANCE
            |
            +---- NORMALIZATION MATCH
            |
            +---- CONDITION RELATIONSHIP
            |
            +---- FORMULATION RELATIONSHIP
            |
            +---- FUTURE SEMANTIC SIMILARITY
            |
            v
       RELEVANCE SCORE
            |
            v
       RANKED RESULTS

The ranking score is a retrieval signal.

It must not be interpreted as:

- Clinical effectiveness
- Patient suitability
- Treatment success
- Medical safety
- Guaranteed outcome

---

## 17. Match Score

The frontend can display the backend ranking score as:

    MATCH SCORE

    92 / 100

The backend owns the score calculation.

The frontend should only visualize the score according to the backend
contract.

If score components are available, they can be exposed through the
explainability interface.

---

## 18. Explainability Architecture

Explainability is a major differentiating feature of the project.

The intended architecture is:

    USER QUERY
        |
        v
    NORMALIZED TERM
        |
        v
    CONDITION MATCH
        |
        v
    FORMULATION MATCH
        |
        v
    RELEVANCE SIGNALS
        |
        v
    FINAL SCORE
        |
        v
    EXPLANATION

The frontend should be able to expose this as:

    WHY THIS RESULT?

---

## 19. Score Breakdown

If the backend exposes scoring components, the frontend can display:

    WHY THIS RESULT?

    Terminology relevance       30 / 30
    Condition relevance         38 / 40
    Formulation association     24 / 30
                                ----------
    TOTAL                       92 / 100

The exact values must always originate from the backend.

The frontend must not create artificial score components.

---

## 20. Explainability Data Contract

A future explanation response may conceptually contain:

    {
        query
        normalized_term
        condition
        formulation
        score
        score_breakdown
        relationship_path
        evidence
        references
    }

The exact schema must follow the actual backend implementation.

The frontend should treat explanation information as structured backend
data rather than hard-coded UI text.

---

## 21. Formulation Data Model

A formulation can conceptually contain:

    FORMULATION
        |
        +---- Name
        |
        +---- Description
        |
        +---- Conditions
        |
        +---- Ingredients
        |
        +---- Relationships
        |
        +---- Evidence
        |
        +---- References

This allows the same formulation to be explored from multiple entry
points.

---

## 22. Disease Data Model

A disease / condition can contain:

    CONDITION
        |
        +---- Name
        |
        +---- Synonyms
        |
        +---- Alternative Terms
        |
        +---- Formulations
        |
        +---- Related Ingredients
        |
        +---- Evidence
        |
        +---- References

---

## 23. Ingredient Data Model

An ingredient can contain:

    INGREDIENT
        |
        +---- Name
        |
        +---- Alternative Names
        |
        +---- Formulations
        |
        +---- Related Conditions
        |
        +---- Evidence
        |
        +---- References

This supports bidirectional exploration.

For example:

    INGREDIENT
        |
        v
    FORMULATION
        |
        v
    CONDITION

and:

    CONDITION
        |
        v
    FORMULATION
        |
        v
    INGREDIENT

---

## 24. Synonym Data Model

Synonym relationships connect different representations of the same
concept.

Conceptual structure:

    SYNONYM
       |
       +---- Input Term
       |
       +---- Normalized Term
       |
       +---- Concept ID
       |
       +---- Relationship Type
       |
       +---- Confidence / Match Information

This structure allows terminology normalization to remain explainable.

---

## 25. Evidence Architecture

Evidence is treated as a separate knowledge layer.

The intended path is:

    SEARCH TERM
        |
        v
    NORMALIZED TERM
        |
        v
    CONDITION
        |
        v
    FORMULATION
        |
        v
    EVIDENCE
        |
        v
    REFERENCE

Evidence should be associated with actual knowledge relationships.

The platform must not fabricate supporting evidence.

---

## 26. Evidence Availability

The backend and frontend should distinguish between:

    EVIDENCE AVAILABLE

    EVIDENCE PARTIALLY AVAILABLE

    EVIDENCE NOT AVAILABLE

Example:

    Evidence
    ------------------------------
    No verified source information
    is currently available for this
    relationship.

This is preferable to displaying misleading or empty evidence sections.

---

## 27. Evidence Provenance

Where evidence exists, the system should preserve provenance information.

Potential metadata includes:

- Reference title
- Source
- Source type
- Identifier
- Citation metadata
- Relationship supported
- Evidence status

The exact metadata depends on the source and backend data model.

---

## 28. Knowledge Graph Architecture

The long-term platform can represent relationships as a knowledge graph.

Conceptual graph:

                     CONDITION
                         |
                         |
                     FORMULATION
                    /           \
                   /             \
            INGREDIENT          EVIDENCE
                   |
                   |
            RELATED FORMULATION

The graph can eventually support:

- Disease exploration
- Formulation exploration
- Ingredient exploration
- Evidence exploration
- Related concept discovery
- Graph-based research navigation

---

## 29. Knowledge Graph Entity Types

Potential graph entities include:

    DISEASE
    FORMULATION
    INGREDIENT
    SYNONYM
    EVIDENCE
    REFERENCE

Potential relationships include:

    SYNONYM_OF
    ASSOCIATED_WITH
    CONTAINS
    RELATED_TO
    SUPPORTED_BY
    REFERENCED_BY

The exact graph schema should evolve with the actual data model.

---

## 30. Frontend Architecture

The frontend is the visual research layer.

Conceptual structure:

    +-----------------------------------------------+
    |                  FRONTEND                     |
    +-----------------------------------------------+
                       |
          +------------+-------------+
          |            |             |
          v            v             v
       SEARCH        RESULTS       DETAILS
          |            |             |
          v            v             v
    Processing      Ranking      Formulation
    Normalize       Scores       Ingredients
    Interpretation  Explain      Evidence
          |            |             |
          +------------+-------------+
                       |
                       v
                 API CLIENT
                       |
                       v
                  BACKEND API

Detailed frontend architecture is documented in:

    frontend/README.md

---

## 31. Backend Architecture

The backend acts as the application intelligence layer.

Conceptual structure:

    CLIENT
      |
      v
    API
      |
      v
    REQUEST VALIDATION
      |
      v
    SEARCH / RETRIEVAL
      |
      +---- TERMINOLOGY
      |
      +---- CONDITIONS
      |
      +---- FORMULATIONS
      |
      +---- INGREDIENTS
      |
      +---- EVIDENCE
      |
      v
    RANKING
      |
      v
    EXPLANATION
      |
      v
    RESPONSE

Detailed backend architecture is documented in:

    backend/README.md

---

## 32. Backend / Frontend Responsibility Boundary

The backend owns:

    DATA
    TERMINOLOGY
    RETRIEVAL
    RANKING
    SCORING
    EXPLANATION DATA
    EVIDENCE DATA
    KNOWLEDGE RELATIONSHIPS

The frontend owns:

    PRESENTATION
    NAVIGATION
    INTERACTION
    VISUALIZATION
    UI STATE
    USER EXPERIENCE

This separation prevents important business logic from being duplicated
inside the frontend.

---

## 33. API Communication

The frontend communicates with the backend through an API layer.

Conceptual flow:

    UI COMPONENT
        |
        v
    API CLIENT
        |
        v
    BACKEND ENDPOINT
        |
        v
    JSON RESPONSE
        |
        v
    UI STATE
        |
        v
    USER

The API client should centralize request handling.

---

## 34. API Response Philosophy

Backend responses should ideally be structured enough for the frontend
to render:

- Query
- Normalized interpretation
- Condition
- Ranked formulations
- Match scores
- Explanation
- Evidence
- References
- Related knowledge

The exact API contract is determined by the backend implementation.

---

## 35. API Error Handling

The backend should return meaningful error states.

The frontend should distinguish between:

    SUCCESS
        |
        +---- RESULTS

    SUCCESS
        |
        +---- NO MATCH

    CLIENT ERROR
        |
        +---- INVALID QUERY

    SERVER ERROR
        |
        +---- TEMPORARY FAILURE

    NETWORK ERROR
        |
        +---- BACKEND UNAVAILABLE

The frontend should present user-friendly messages.

---

## 36. Search State Model

The frontend search process can be represented as:

    IDLE
      |
      v
    SEARCHING
      |
      v
    PROCESSING
      |
      +---- SUCCESS
      |
      +---- NO MATCH
      |
      +---- ERROR

This prevents inconsistent interface states.

---

## 37. Loading / Processing Experience

Instead of showing only a generic spinner, the frontend can expose the
processing pipeline.

Example:

    ✓ Query received

    ✓ Terminology analyzed

    ✓ Normalized interpretation found

    ✓ Condition identified

    ✓ Formulations retrieved

    ✓ Candidates ranked

    ✓ Explanation prepared

The exact steps displayed should correspond to real backend processing.

The UI should never claim that a processing step occurred if the backend
did not perform it.

---

## 38. No-Result Handling

The system should provide an intentional no-result experience.

Example:

    No matching terminology was found.

    Try:
    - Another spelling
    - A synonym
    - A broader term
    - A known Ayurvedic terminology

Suggestions should only be implemented if the backend or frontend
actually supports them.

---

## 39. Formulation Comparison

The platform supports future side-by-side comparison.

Conceptual structure:

    -------------------------------------------------------
                  FORMULATION COMPARISON
    -------------------------------------------------------

              FORMULATION A       FORMULATION B

    Score         92                   84

    Condition     Jvara                Jvara

    Ingredients   A, B, C              A, C, D

    Evidence      Available            Available

The comparison exists to support research reasoning.

It should not imply clinical superiority based solely on a retrieval
score.

---

## 40. Research Dashboard

A future research dashboard can expose knowledge and usage statistics.

Potential metrics include:

    Total Diseases
    Total Formulations
    Total Ingredients
    Total Synonyms
    Evidence Records
    Search Queries
    Successful Matches
    No-Match Queries

Potential charts include:

- Search activity
- Match distribution
- Knowledge coverage
- Evidence coverage
- Most searched terms
- Most retrieved formulations

The backend should remain the authoritative source for analytics.

---

## 41. Knowledge Discovery Navigation

The platform should support navigation between entities.

Example:

    DISEASE
       |
       v
    FORMULATION
       |
       v
    INGREDIENT
       |
       v
    RELATED FORMULATION
       |
       v
    EVIDENCE

Users should be able to move through the knowledge base without being
restricted to the original search query.

---

## 42. Deep Linking

Future research pages should support direct links.

Conceptual routes:

    /search?q=fever

    /diseases/jvara

    /formulations/example-formulation

    /ingredients/example-ingredient

    /compare/formulation-a/formulation-b

    /evidence/example-reference

This enables specific research findings to be shared.

---

## 43. Data Integrity Rules

The platform should follow strict data-integrity principles.

### Rule 1

Do not invent evidence.

### Rule 2

Do not invent references.

### Rule 3

Do not invent disease-formulation relationships.

### Rule 4

Do not represent unavailable data as verified data.

### Rule 5

Clearly distinguish model-generated information from structured source
information.

### Rule 6

Preserve backend source information when displaying it on the frontend.

---

## 44. Medical / Clinical Boundary

The platform is a research and knowledge-discovery system.

It must not be presented as:

    A diagnostic system
    A patient-specific prescription system
    A replacement for a qualified practitioner
    A guarantee of treatment effectiveness
    A clinical decision-making system

The system is intended to organize and explore information.

Conceptually:

    KNOWLEDGE DISCOVERY
            ≠
    CLINICAL DECISION MAKING

Match scores represent retrieval relevance and should not be presented as
medical efficacy or patient suitability.

---

## 45. ML / NLP Roadmap

The ML/NLP layer is intended to extend the structured knowledge system.

Future pipeline:

    USER QUERY
        |
        v
    NLP PROCESSING
        |
        +---- ENTITY RECOGNITION
        |
        +---- TERMINOLOGY NORMALIZATION
        |
        +---- SEMANTIC SIMILARITY
        |
        +---- CONTEXT UNDERSTANDING
        |
        v
    KNOWLEDGE RETRIEVAL
        |
        v
    RANKING
        |
        v
    EXPLANATION

The ML layer should complement structured retrieval rather than
immediately replace it.

---

## 46. Future Semantic Search

A future version can extend the current search model.

Current:

    EXACT
      |
      v
    SYNONYM
      |
      v
    STRUCTURED RETRIEVAL

Future:

    EXACT
      |
      v
    SYNONYM
      |
      v
    SEMANTIC MATCH
      |
      v
    CONTEXT
      |
      v
    RANKING

This allows the system to understand more complex natural-language
queries.

---

## 47. Future Intelligent Ranking

Future ranking can combine:

    TERMINOLOGY MATCH
        +
    SYNONYM MATCH
        +
    CONDITION RELATIONSHIP
        +
    FORMULATION RELATIONSHIP
        +
    SEMANTIC SIMILARITY
        +
    EVIDENCE SIGNALS

        |
        v

    FINAL RELEVANCE SCORE

Any future ranking system should remain explainable.

---

## 48. Future Knowledge Graph

The knowledge graph can eventually become a central exploration layer.

Possible architecture:

                         USER
                           |
                           v
                    KNOWLEDGE GRAPH
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
     DISEASE          FORMULATION         INGREDIENT
        |                  |                  |
        +------------------+------------------+
                           |
                           v
                       EVIDENCE
                           |
                           v
                       REFERENCE

This can transform the system from a search tool into a broader knowledge
exploration platform.

---

## 49. Research Intelligence Roadmap

The long-term platform can evolve through:

    STRUCTURED SEARCH
          |
          v
    TERMINOLOGY INTELLIGENCE
          |
          v
    FORMULATION RANKING
          |
          v
    EXPLAINABILITY
          |
          v
    EVIDENCE TRACEABILITY
          |
          v
    KNOWLEDGE GRAPH
          |
          v
    ML / NLP INTELLIGENCE
          |
          v
    RESEARCH ANALYTICS

---

## 50. Development Phases

### Phase 1 — Repository Foundation

    Repository
        |
        +---- Documentation
        +---- Architecture
        +---- Data
        +---- Frontend
        +---- Backend
        +---- ML

---

### Phase 2 — Structured Knowledge

    Disease
       |
       +---- Synonyms
       |
       +---- Formulations
       |
       +---- Ingredients

---

### Phase 3 — Backend Discovery

    Query
      |
      v
    Normalization
      |
      v
    Disease
      |
      v
    Formulations
      |
      v
    Ranking

---

### Phase 4 — Frontend Discovery

    Search
      |
      v
    Processing
      |
      v
    Results
      |
      v
    Details

---

### Phase 5 — Explainability

    Query
      |
      v
    Interpretation
      |
      v
    Relationship
      |
      v
    Score
      |
      v
    Why This Result?

---

### Phase 6 — Evidence

    Formulation
      |
      v
    Evidence
      |
      v
    References

---

### Phase 7 — Research Intelligence

    Comparison
      |
      v
    Knowledge Graph
      |
      v
    Research Dashboard

---

### Phase 8 — ML / NLP

    Structured Retrieval
          +
    ML / NLP
          |
          v
    Semantic Discovery
          |
          v
    Intelligent Ranking
          |
          v
    Explainable Intelligence

---

## 51. Testing Strategy

The platform should eventually support multiple testing levels.

    UNIT TESTS
        |
        v
    COMPONENT TESTS
        |
        v
    API TESTS
        |
        v
    INTEGRATION TESTS
        |
        v
    END-TO-END TESTS

The most important end-to-end workflow is:

    SEARCH
      |
      v
    NORMALIZE
      |
      v
    RETRIEVE
      |
      v
    RANK
      |
      v
    EXPLAIN
      |
      v
    DISPLAY

---

## 52. Important Backend Test Cases

### Valid Search

    Input:
    fever

    Expected:
    Structured search response.

### Normalization

    Input:
    supported terminology

    Expected:
    Normalized interpretation.

### Disease Mapping

    Expected:
    Associated condition returned where available.

### Formulation Retrieval

    Expected:
    Related formulations returned.

### Ranking

    Expected:
    Results contain ranking information when supported.

### Explanation

    Expected:
    Explanation data corresponds to actual retrieval logic.

### No Match

    Expected:
    Clear empty result.

### Invalid Input

    Expected:
    Validation error.

### Backend Failure

    Expected:
    Structured error response.

---

## 53. Important Frontend Test Cases

### Search

    User enters a term.

    Expected:
    Search request is initiated.

### Processing

    Expected:
    Processing state is displayed.

### Normalization

    Expected:
    Normalized interpretation appears.

### Results

    Expected:
    Ranked formulations are displayed.

### Explanation

    Expected:
    "Why this result?" displays backend-provided explanation.

### Formulation Details

    Expected:
    Structured formulation information is displayed.

### Evidence

    Expected:
    Only available evidence is displayed.

### Comparison

    Expected:
    Two formulations can be compared.

---

## 54. Performance Strategy

The platform should prioritize:

- Fast initial frontend loading
- Efficient API requests
- Minimal unnecessary requests
- Efficient rendering
- Lazy loading for advanced visualizations
- Efficient graph rendering
- Appropriate caching
- Avoiding unnecessary re-computation

The core search experience should remain lightweight even as advanced
research features are added.

---

## 55. Security Principles

The system should:

- Avoid storing secrets in source code
- Protect API credentials
- Validate incoming requests
- Sanitize user-controlled content
- Avoid rendering untrusted HTML
- Use environment variables
- Use HTTPS in production
- Configure CORS appropriately
- Avoid exposing internal implementation details unnecessarily

Security configuration should remain environment-specific.

---

## 56. Environment Configuration

The application may require configuration such as:

    API_BASE_URL
    DATABASE_URL
    ENVIRONMENT
    ML_SERVICE_URL
    EVIDENCE_SERVICE_URL

The exact variables depend on the actual implementation.

Environment-specific configuration should not be hard-coded throughout
the codebase.

---

## 57. Development Workflow

Recommended development workflow:

    1. Clone repository
    2. Open project
    3. Configure environment
    4. Install dependencies
    5. Start backend
    6. Start frontend
    7. Verify API connectivity
    8. Test search
    9. Test normalization
    10. Test formulation retrieval
    11. Test ranking
    12. Test explanation
    13. Test detail pages
    14. Test evidence
    15. Run tests
    16. Commit changes

---

## 58. Git Development Workflow

Changes should be committed in focused units.

Example:

    git status

    git add .

    git commit -m "Improve formulation discovery workflow"

    git push

Recommended commit styles:

    Add terminology normalization API
    Improve formulation ranking
    Add explainability response
    Add formulation detail page
    Improve evidence display
    Add knowledge graph prototype
    Improve search processing UI

Focused commits make project progress easier to understand and review.

---

## 59. Documentation Architecture

The repository documentation is divided into specialized files.

### `README.md`

Main project overview and system-level documentation.

### `ARCHITECTURE.md`

System architecture and component relationships.

### `IDEATION_AND_STRATEGY.md`

Project ideation, product direction, and strategic reasoning.

### `MASTER_BUILD_PROMPT.md`

Central implementation and build guidance.

### `HANDOFF.md`

Project continuation and handoff information.

### `PRE_TEST_READINESS.md`

Prototype readiness and validation information.

### `backend/README.md`

Backend architecture, API behavior, processing logic, and implementation
details.

### `frontend/README.md`

Frontend architecture, UI behavior, user flows, and research interface
details.

---

## 60. Recommended Developer Reading Order

A developer joining the project should read:

    README.md
        |
        v
    ARCHITECTURE.md
        |
        v
    IDEATION_AND_STRATEGY.md
        |
        v
    backend/README.md
        |
        v
    frontend/README.md
        |
        v
    data/
        |
        v
    ml/

This provides a progressive understanding of the platform.

---

## 61. Prototype Boundaries

The current repository represents a prototype foundation.

It should not be interpreted as a complete Ayurvedic knowledge base.

Current limitations may include:

- Limited structured data
- Prototype terminology mappings
- Incomplete evidence coverage
- Evolving backend APIs
- Evolving frontend functionality
- Incomplete ML/NLP functionality
- Future knowledge graph implementation
- Future research analytics

These limitations are expected during incremental development.

---

## 62. Current Project Status

Current stage:

    INITIAL STRUCTURE
           |
           v
       PROTOTYPE
           |
           v
    INCREMENTAL DEVELOPMENT

Current project components include:

- Project architecture
- Repository organization
- Structured data foundation
- Disease records
- Formulation records
- Ingredient structure
- Synonym mappings
- Backend foundation
- Frontend foundation
- Documentation
- Planned ML/NLP layer
- Planned evidence layer
- Planned knowledge graph

The exact implementation status of each component should be reflected in
its corresponding directory documentation.

---

## 63. Current Prototype Data

The current sample data is intended to demonstrate:

- Data relationships
- Search behavior
- Formulation discovery
- Terminology normalization
- Backend / frontend integration
- Prototype UI behavior

The sample dataset should not be interpreted as:

    COMPLETE AYURVEDIC KNOWLEDGE

or as a clinically validated dataset.

---

## 64. Future Feature Set

Potential future capabilities include:

- Advanced semantic search
- Multilingual terminology support
- Sanskrit terminology processing
- NLP entity recognition
- Semantic similarity
- Intelligent ranking
- Explainable ranking
- Evidence quality indicators
- Reference provenance
- Formulation comparison
- Ingredient exploration
- Disease exploration
- Knowledge graph visualization
- Research analytics
- Advanced filtering
- Search suggestions
- Related concept discovery
- Knowledge coverage analysis

Features should be introduced incrementally without compromising the
core discovery workflow.

---

## 65. Product Success Criteria

The prototype should ultimately demonstrate that a user can:

    1. Enter an Ayurvedic-related query
                |
                v
    2. Receive a normalized interpretation
                |
                v
    3. Identify an associated condition
                |
                v
    4. Discover ranked formulations
                |
                v
    5. Understand why a formulation was surfaced
                |
                v
    6. Inspect formulation information
                |
                v
    7. Explore ingredients
                |
                v
    8. Follow available evidence
                |
                v
    9. Compare formulations
                |
                v
    10. Explore related knowledge

The key success criterion is:

> Can the platform provide a traceable and understandable path from a
> user's search term to a formulation result?

---

## 66. Quality Checklist

Before considering a major prototype milestone complete:

    [ ] Repository structure is organized
    [ ] Main documentation is updated
    [ ] Architecture documentation is updated
    [ ] Backend documentation is updated
    [ ] Frontend documentation is updated
    [ ] Sample data is valid
    [ ] Disease records are structured
    [ ] Formulation records are structured
    [ ] Ingredient records are structured
    [ ] Synonym mappings are structured
    [ ] Backend API is testable
    [ ] Frontend communicates with backend
    [ ] Search workflow works
    [ ] Normalization workflow works
    [ ] Formulation retrieval works
    [ ] Ranking is available where implemented
    [ ] Explanation data is available where implemented
    [ ] Evidence state is clearly represented
    [ ] No unsupported evidence is fabricated
    [ ] Error states are handled
    [ ] No-result states are handled
    [ ] Prototype boundaries are documented
    [ ] No secrets are committed
    [ ] Git repository is synchronized

---

## 67. Long-Term Architecture

The long-term system can evolve into:

                         USER
                           |
                           v
                     FRONTEND
                           |
                           v
                      API LAYER
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     TERMINOLOGY       RETRIEVAL        ML / NLP
          |                |                |
          +----------------+----------------+
                           |
                           v
                    KNOWLEDGE BASE
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      DISEASE        FORMULATION       INGREDIENT
          |                |                |
          +----------------+----------------+
                           |
                           v
                       EVIDENCE
                           |
                           v
                       REFERENCE
                           |
                           v
                    KNOWLEDGE GRAPH
                           |
                           v
                  RESEARCH INTELLIGENCE

---

## 68. Final Product Architecture

The complete product vision can be represented as:

    USER
      |
      v
    SEARCH
      |
      v
    TERMINOLOGY INTELLIGENCE
      |
      v
    KNOWLEDGE RETRIEVAL
      |
      v
    FORMULATION RANKING
      |
      v
    EXPLAINABILITY
      |
      v
    EVIDENCE TRACEABILITY
      |
      v
    KNOWLEDGE GRAPH
      |
      v
    RESEARCH ANALYTICS

This creates a system that combines structured knowledge retrieval with
future intelligent search and explainability.

---

## 69. Final User Experience

The final user experience should transform:

    "Find me a formulation."

into:

    "Help me understand the relationship between
     my search term, the Ayurvedic concept it represents,
     the condition it maps to, the formulations associated
     with that condition, why those formulations were ranked,
     and what evidence supports the relationships."

The platform therefore aims to provide:

    SEARCH
      +
    INTERPRETATION
      +
    DISCOVERY
      +
    EXPLANATION
      +
    COMPARISON
      +
    EVIDENCE
      +
    EXPLORATION

---

## 70. Final Vision

The Ayurveda Intelligence system is intended to become an:

    EVIDENCE-AWARE
    EXPLAINABLE
    TRACEABLE
    RESEARCH-ORIENTED
    AYURVEDIC KNOWLEDGE PLATFORM

Its core philosophy is:

> Search should lead to understanding, not merely a result.

The long-term workflow is:

    SEARCH
      |
      v
    UNDERSTAND
      |
      v
    DISCOVER
      |
      v
    EXPLAIN
      |
      v
    COMPARE
      |
      v
    VERIFY
      |
      v
    EXPLORE

The platform should make Ayurvedic formulation discovery more structured,
transparent, navigable, and research-friendly while maintaining a clear
boundary between information retrieval and clinical decision making.
