# Ayurveda Intelligence — Backend

> **Project:** Ayurveda Intelligence — Evidence-Aware Ayurvedic Formulation Discovery  
> **Component:** Backend Intelligence & API Layer  
> **Project Type:** Hackathon Prototype / Research Platform  
> **Status:** Active Development

---

## 1. Backend Overview

The Ayurveda Intelligence backend is the core intelligence and data-processing layer of the platform.

Its primary responsibility is to transform a user's natural-language query into a structured, ranked, explainable, and traceable formulation discovery result.

The backend is designed around the following core pipeline:

    User Query
         |
         v
    Input Normalization
         |
         v
    Terminology Resolution
         |
         v
    Disease / Condition Identification
         |
         v
    Formulation Retrieval
         |
         v
    Candidate Generation
         |
         v
    Candidate Scoring
         |
         v
    Ranking
         |
         v
    Explainability
         |
         v
    Evidence / Provenance
         |
         v
    Structured API Response

The central design principle is:

> Every surfaced formulation should have an understandable reason for why it was returned.

---

## 2. Backend Objectives

The backend is responsible for:

- Processing user search queries
- Normalizing terminology
- Resolving common terms to canonical Ayurvedic terminology
- Identifying related diseases or conditions
- Retrieving relevant formulations
- Ranking formulation candidates
- Generating match scores
- Providing explainable reasoning
- Maintaining structured knowledge
- Preparing evidence and provenance information
- Serving structured information to the frontend
- Providing a foundation for semantic search
- Providing a foundation for knowledge-graph exploration
- Supporting future research-oriented analytics

---

## 3. High-Level Architecture

    +-----------------------+
    |        USER           |
    +-----------+-----------+
                |
                v
    +-----------------------+
    |      FRONTEND         |
    | Search / Results / UI |
    +-----------+-----------+
                |
                | HTTP / JSON
                v
    +-----------------------+
    |       FASTAPI         |
    |      API LAYER        |
    +-----------+-----------+
                |
                v
    +-----------------------+
    |   QUERY PROCESSING    |
    +-----------+-----------+
                |
        +-------+-------+
        |       |       |
        v       v       v
    Terminology  Disease  Formulation
    Resolution   Lookup   Retrieval
        |       |       |
        +-------+-------+
                |
                v
    +-----------------------+
    | CANDIDATE GENERATION  |
    +-----------+-----------+
                |
                v
    +-----------------------+
    |   SCORING ENGINE      |
    +-----------+-----------+
                |
                v
    +-----------------------+
    |   RANKING ENGINE      |
    +-----------+-----------+
                |
                v
    +-----------------------+
    | EXPLAINABILITY ENGINE |
    +-----------+-----------+
                |
                v
    +-----------------------+
    | EVIDENCE / PROVENANCE |
    +-----------+-----------+
                |
                v
    +-----------------------+
    |   STRUCTURED JSON     |
    +-----------+-----------+
                |
                v
    +-----------------------+
    |       FRONTEND        |
    +-----------------------+

---

## 4. Core Architecture Philosophy

The backend is intentionally separated into independent logical stages.

The architecture follows:

    INPUT
      |
      v
    UNDERSTAND
      |
      v
    NORMALIZE
      |
      v
    RETRIEVE
      |
      v
    SCORE
      |
      v
    RANK
      |
      v
    EXPLAIN
      |
      v
    TRACE
      |
      v
    RESPOND

This separation allows individual components to evolve without requiring
the entire backend to be rewritten.

For example, the initial implementation can use deterministic lookup
while future versions can introduce semantic embeddings, vector search,
machine-learning ranking, or knowledge graphs.

---

## 5. End-to-End Query Flow

A typical request follows this sequence:

    1. User enters a query
            |
            v
    2. API receives the request
            |
            v
    3. Input is validated
            |
            v
    4. Query is normalized
            |
            v
    5. Terminology is resolved
            |
            v
    6. Related condition is identified
            |
            v
    7. Candidate formulations are retrieved
            |
            v
    8. Candidates are scored
            |
            v
    9. Candidates are ranked
            |
            v
    10. Explanation is generated
            |
            v
    11. Evidence/provenance is attached
            |
            v
    12. Structured response is returned

---

## 6. Query Normalization

The first stage converts raw user input into a predictable internal
representation.

Example:

    Raw Query
        |
        v
    "   FEVER   "
        |
        v
    Normalization
        |
        v
    "fever"

Normalization may include:

- Removing leading and trailing whitespace
- Standardizing capitalization
- Cleaning basic input variations
- Handling simple formatting differences
- Preparing the query for terminology matching

The purpose is to make equivalent user inputs behave consistently.

For example:

    fever
    FEVER
    Fever
    "  fever  "

can be normalized to the same internal representation.

---

## 7. Terminology Resolution

Terminology resolution converts a user-facing term into a canonical
Ayurvedic representation.

Example:

    User Query
        |
        v
      fever
        |
        v
    Terminology Mapping
        |
        v
      Jvara

Conceptual response:

    {
        "matched": true,
        "input_term": "fever",
        "normalized_term": "Jvara"
    }

This layer is important because users may search using:

- English terms
- Common terminology
- Synonyms
- Alternate spellings
- Transliteration
- Different representations of the same concept

Future versions can extend this component with NLP and embedding-based
semantic matching.

---

## 8. Disease / Condition Resolution

After terminology resolution, the backend identifies the related
condition.

    Canonical Term
         |
         v
    Condition Dataset
         |
         v
    Condition Record

Example:

    Jvara
      |
      v
    Jvara Condition

The backend should distinguish between:

    Known Term + Known Condition

    Known Term + No Condition

    Unknown Term

This enables the frontend to provide meaningful states instead of
treating every unmatched query as a server error.

---

## 9. Formulation Retrieval

Once the relevant condition has been identified, the backend retrieves
associated formulations.

    Condition
       |
       +---- Formulation A
       |
       +---- Formulation B
       |
       +---- Formulation C
       |
       +---- Formulation D

The retrieval stage generates the candidate set.

Retrieval and ranking are intentionally separated.

Retrieval answers:

    "Which formulations could be relevant?"

Ranking answers:

    "Which of these formulations are the most relevant?"

This separation allows the ranking system to become more sophisticated
without rewriting the retrieval system.

---

## 10. Candidate Generation

Candidate generation gathers potentially relevant formulations from the
knowledge layer.

    Condition
        |
        v
    Knowledge Base
        |
        v
    Candidate Generation
        |
        +---- Candidate 1
        +---- Candidate 2
        +---- Candidate 3
        +---- Candidate 4
        +---- Candidate 5

Candidate generation should be designed to avoid prematurely discarding
potentially useful results.

The ranking stage can then determine their final order.

---

## 11. Candidate Scoring

Each retrieved candidate can receive a relevance score.

Conceptual scoring model:

    Terminology Match
          +
    Condition Match
          +
    Formulation Association
          +
    Additional Retrieval Signals
          |
          v
    Candidate Score

A conceptual score breakdown may look like:

    Terminology Relevance       30
    Condition Relevance         40
    Formulation Association     30
                                ---
                                100

The exact scoring formula implemented by the backend is the authoritative
definition.

The match score is a retrieval/ranking signal.

It must not be interpreted as:

- Clinical effectiveness
- Medical suitability
- Treatment success probability
- Patient-specific recommendation

---

## 12. Ranking Engine

After candidates are scored, they are ordered according to relevance.

Example:

    Rank    Formulation       Score
    --------------------------------
      1     Formulation A       92
      2     Formulation B       86
      3     Formulation C       79
      4     Formulation D       68

The ranking layer should preserve enough information for the
explainability layer to describe why a candidate appeared.

---

## 13. Explainability Engine

Explainability is a core architectural principle.

The backend should be able to answer:

    WHAT?
    What formulation was returned?

    WHY?
    Why was it considered relevant?

    HOW?
    Which matching signals contributed to the result?

    WHERE?
    Where did the supporting knowledge or evidence originate?

Conceptual flow:

    User Query
        |
        v
    Normalized Term
        |
        v
    Condition
        |
        v
    Formulation
        |
        v
    Match Score
        |
        v
    Explanation
        |
        v
    Evidence / Reference

---

## 14. "Why This Result?" Architecture

The frontend can expose a dedicated explanation panel using backend
information.

Example explanation:

    Query:
        fever

    Normalized interpretation:
        Jvara

    Condition:
        Jvara

    Match:
        Formulation associated with the identified condition

    Score:
        82

    Reasons:
        - Input matched a known terminology mapping
        - A corresponding condition was identified
        - The formulation is associated with the identified condition

This allows the platform to move beyond a simple search-result model.

Instead of:

    "Here is a formulation."

The platform can communicate:

    "Here is the formulation, and here is why it was surfaced."

---

## 15. Structured Explanation Response

A recommendation can expose machine-readable reasoning.

Conceptual response:

    {
        "formulation": "Example Formulation",
        "match_score": 82,
        "explanation": {
            "query": "fever",
            "normalized_term": "Jvara",
            "condition_match": true,
            "formulation_match": true,
            "reasons": [
                "Input matched a known terminology mapping.",
                "A corresponding condition was identified.",
                "The formulation is associated with the identified condition."
            ]
        }
    }

This structure allows the frontend to render:

- Score breakdown
- Matching signals
- Processing trace
- Explanation cards
- Evidence links
- Research context

---

## 16. Evidence and Provenance

Evidence is treated as a first-class concept in the architecture.

The intended relationship is:

    User Query
        |
        v
    Normalized Term
        |
        v
    Disease / Condition
        |
        v
    Formulation
        |
        v
    Ingredient
        |
        v
    Evidence
        |
        v
    Source / Reference

This enables future capabilities such as:

- Source references
- Publication information
- Traditional textual references
- Research references
- Evidence trails
- Provenance tracking
- Reference identifiers
- Source metadata

The backend must never fabricate evidence or references.

If evidence is unavailable, the response should clearly represent that
state.

---

## 17. Knowledge Layer

The knowledge layer contains the structured information required by the
recommendation pipeline.

Conceptually:

                         KNOWLEDGE BASE
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
          Terminology       Diseases       Formulations
              |                |                |
              +----------------+----------------+
                               |
                               v
                         Data Loader
                               |
                               v
                    Recommendation Engine

The knowledge layer should remain separate from API logic.

This allows datasets to evolve without tightly coupling them to the
HTTP layer.

---

## 18. Data Layer

The data layer is responsible for loading and exposing structured
knowledge to the application.

Conceptual flow:

    Knowledge Files
          |
          v
      Data Loader
          |
          v
    Validated Records
          |
          v
    Structured Representation
          |
          v
    Recommendation Engine

This design makes future migration possible.

Current prototype:

    Structured Files
          |
          v
      Data Loader
          |
          v
    Application Logic

Future architecture:

    Database
          |
          v
    Repository Layer
          |
          v
    Recommendation Engine

The recommendation engine should not need to know whether the underlying
data comes from CSV files, JSON files, SQL, or another storage system.

---

## 19. Data Validation

Knowledge data should be validated before being consumed by the
recommendation system.

Validation should consider:

- Required fields
- Empty values
- Invalid records
- Duplicate mappings
- Unexpected data types
- Missing relationships
- Dataset availability
- Inconsistent terminology
- Broken references

Conceptual flow:

    Raw Dataset
         |
         v
      Validation
         |
         +-------- INVALID --------> Error
         |
         v
    Validated Dataset
         |
         v
      Application

This prevents malformed knowledge from silently producing incorrect
results.

---

## 20. API Layer

FastAPI acts as the communication boundary between the frontend and the
backend intelligence layer.

Responsibilities include:

- Receiving requests
- Validating inputs
- Calling backend services
- Handling errors
- Returning structured JSON
- Exposing interactive API documentation
- Providing health/readiness information

Conceptual flow:

    Frontend
        |
        | HTTP / JSON
        v
    FastAPI
        |
        v
    Backend Logic
        |
        v
    JSON Response
        |
        v
    Frontend

---

## 21. API Contract

The backend communicates with the frontend through structured JSON.

Conceptual recommendation response:

    {
        "query": "fever",
        "normalized_term": "Jvara",
        "condition": {
            "name": "Jvara"
        },
        "recommendations": [
            {
                "name": "Example Formulation",
                "match_score": 82,
                "explanation": {}
            }
        ],
        "status": "success"
    }

The actual API implementation remains the source of truth for the exact
schema.

The README describes the architectural contract; it should not be used
to claim endpoints that are not actually implemented.

---

## 22. API Endpoint Architecture

The backend can be organized conceptually around:

    FastAPI
       |
       +---- Search
       |
       +---- Recommendations
       |
       +---- Diseases
       |
       +---- Formulations
       |
       +---- Evidence
       |
       +---- Health

Potential endpoint patterns include:

    GET /health
    GET /search
    GET /recommend
    GET /diseases
    GET /formulations

Only endpoints implemented in the current backend should be treated as
production-ready.

---

## 23. Search API

Conceptual request:

    GET /search?q=fever

Processing:

    Query
      |
      v
    Validation
      |
      v
    Normalization
      |
      v
    Terminology Resolution
      |
      v
    Structured Search Result

The search layer is intended to support the frontend's terminology
normalization and search experience.

---

## 24. Recommendation API

Conceptual request:

    GET /recommend?q=fever

Processing:

    Query
      |
      v
    Normalization
      |
      v
    Terminology
      |
      v
    Condition
      |
      v
    Formulations
      |
      v
    Candidate Scoring
      |
      v
    Ranking
      |
      v
    Explanation
      |
      v
    Evidence
      |
      v
    JSON Response

This represents the core intelligence path of the platform.

---

## 25. No-Match Handling

Not every query will produce a knowledge match.

Example:

    User Query
        |
        v
    "unknown-term"
        |
        v
    Terminology Resolution
        |
        v
    No Match
        |
        v
    Controlled Response

Conceptual response:

    {
        "status": "no_match",
        "query": "unknown-term",
        "recommendations": []
    }

No-match is a normal application state.

It should not automatically be treated as an internal server error.

---

## 26. Input Validation

Invalid requests should be detected at the API boundary.

Examples include:

- Missing query
- Empty query
- Invalid parameter type
- Excessively malformed input
- Unsupported request structure

Conceptual flow:

    Request
       |
       v
    Validation
       |
       +------ Invalid ------> 4xx Response
       |
       v
    Processing

Input validation should occur before expensive backend processing.

---

## 27. Error Handling

The backend should distinguish different failure categories.

    Client Input Error
          |
          v
    Validation Failure


    Knowledge No-Match
          |
          v
    Valid Request / No Result


    Internal Error
          |
          v
    Unexpected Processing Failure


    Data Error
          |
          v
    Knowledge Base Problem

Clear error classification makes debugging easier and allows the
frontend to display appropriate messages.

---

## 28. Frontend / Backend Boundary

The frontend is responsible for presentation.

The backend is responsible for intelligence and structured information.

    +---------------------------+------------------------------+
    | FRONTEND                  | BACKEND                      |
    +---------------------------+------------------------------+
    | Search Interface          | Query Normalization          |
    | Result Cards              | Terminology Resolution       |
    | Score Visualization       | Candidate Generation         |
    | Explanation UI            | Candidate Scoring            |
    | Detail Pages              | Ranking                      |
    | Comparison UI             | Knowledge Retrieval          |
    | Evidence UI               | Provenance                   |
    | Graph Visualization       | Relationship Data            |
    +---------------------------+------------------------------+

The frontend should not duplicate recommendation or ranking logic.

---

## 29. Frontend / Backend Request Flow

    User
      |
      v
    Frontend Search
      |
      | HTTP Request
      v
    FastAPI
      |
      v
    Recommendation Engine
      |
      +---- Terminology
      |
      +---- Condition
      |
      +---- Formulations
      |
      +---- Scoring
      |
      +---- Ranking
      |
      +---- Explanation
      |
      +---- Evidence
      |
      v
    JSON Response
      |
      v
    Frontend
      |
      +---- Ranked Results
      +---- Match Score
      +---- Why This Result?
      +---- Evidence
      +---- Details
      +---- Comparison

---

## 30. Processing Trace

The backend can expose a processing trace that allows the frontend to
reveal how a query was interpreted.

Example:

    STEP 1
    Input received
          |
          v
    "fever"

    STEP 2
    Query normalized
          |
          v
    "fever"

    STEP 3
    Terminology resolved
          |
          v
    "Jvara"

    STEP 4
    Condition identified
          |
          v
    "Jvara"

    STEP 5
    Formulations retrieved
          |
          v
    Candidate Set

    STEP 6
    Candidates scored
          |
          v
    Ranked Candidates

    STEP 7
    Explanation generated
          |
          v
    Final Response

This supports the project's goal of making the recommendation process
understandable rather than opaque.

---

## 31. Comparison Support

The backend architecture can support comparison of two formulations.

Conceptual request:

    Formulation A
          |
          +----------------+
                           |
                           v
                       Comparison
                           ^
                           |
          +----------------+
          |
    Formulation B

Comparison data may eventually include:

- Formulation name
- Ingredients
- Associated conditions
- Match score
- Evidence
- Sources
- Relationships
- Metadata

The frontend is responsible for visualizing the comparison.

---

## 32. Knowledge Graph Support

The architecture is designed to support a future knowledge graph.

Conceptual relationship model:

    User Term
        |
        | synonym_of
        v
    Ayurvedic Term
        |
        | represents
        v
    Condition
        |
        | associated_with
        v
    Formulation
        |
        | contains
        v
    Ingredient
        |
        | supported_by
        v
    Evidence
        |
        | referenced_by
        v
    Source

This enables relationship-based exploration beyond traditional search.

---

## 33. Future Knowledge Graph API

A future implementation could expose relationships such as:

    GET /graph/term/{term}
    GET /graph/disease/{disease}
    GET /graph/formulation/{formulation}

The exact endpoints should only be introduced when implemented.

The conceptual graph response could contain:

    {
        "node": {},
        "relationships": [],
        "connected_entities": []
    }

This would allow the frontend to build an interactive knowledge graph
explorer.

---

## 34. Evidence Architecture

Evidence can eventually become a dedicated backend entity.

    Query
      |
      v
    Normalized Term
      |
      v
    Condition
      |
      v
    Formulation
      |
      v
    Evidence Record
      |
      +---- Source
      +---- Reference
      +---- Publication
      +---- Identifier
      +---- Provenance

This creates a traceable research path:

    TERM
      |
      v
    DISEASE
      |
      v
    FORMULATION
      |
      v
    SOURCE

The system should clearly distinguish between:

- Structured knowledge
- Traditional references
- Research evidence
- External sources
- Internal metadata

---

## 35. Semantic Search Roadmap

The deterministic retrieval layer can later evolve into semantic search.

Future architecture:

    User Query
        |
        v
    NLP / Embedding Model
        |
        v
    Semantic Representation
        |
        v
    Vector Search
        |
        v
    Candidate Retrieval
        |
        v
    Ranking
        |
        v
    Explainability
        |
        v
    Evidence

The deterministic search layer can remain available as a fallback and
validation mechanism.

---

## 36. Machine Learning Ranking Roadmap

Future ML ranking can operate after candidate generation.

    Candidate Formulations
             |
             v
       Feature Extraction
             |
      +------+------+------+
      |      |      |      |
      v      v      v      v
    Term   Disease  Form   Evidence
    Match  Match    Match  Signals
      |      |      |      |
      +------+------+------+
             |
             v
        ML Ranker
             |
             v
       Ranked Results
             |
             v
       Explainability

Potential future features include:

- Terminology similarity
- Condition similarity
- Formulation relationship strength
- Ingredient relationships
- Evidence metadata
- Semantic similarity

ML scores must remain clearly distinguished from clinical effectiveness
or medical suitability.

---

## 37. Caching Roadmap

Frequently requested queries may eventually be cached.

    Request
       |
       v
    Cache Lookup
       |
       +------ HIT ------> Cached Result
       |
       +------ MISS -----> Recommendation Engine
                                |
                                v
                              Cache
                                |
                                v
                             Response

Caching should not compromise correctness.

When knowledge or evidence changes, cache invalidation must be considered.

---

## 38. Performance Strategy

The prototype is designed to remain lightweight and modular.

Performance principles include:

- Avoid unnecessary repeated dataset parsing
- Load reusable data efficiently
- Keep lookup operations simple
- Separate loading from request processing
- Keep response payloads structured
- Avoid unnecessary computation
- Preserve explainability information

Future optimization options include:

- Query caching
- Database indexing
- Search indexes
- Vector search
- Async processing
- Background processing
- Request tracing

---

## 39. Health and Readiness

The backend should expose operational health information.

Conceptual checks:

    Backend API
       |
       +---- API Available
       |
       +---- Knowledge Base Available
       |
       +---- Required Data Loaded
       |
       +---- Recommendation Engine Available

Possible states:

    READY
    DEGRADED
    ERROR

This allows the frontend and deployment environment to determine whether
the backend is operational.

---

## 40. Logging

Backend logging should make the processing lifecycle visible.

Conceptual logs:

    INFO  Request received
    INFO  Query normalized
    INFO  Terminology resolved
    INFO  Condition identified
    INFO  Candidates retrieved
    INFO  Candidates ranked
    INFO  Explanation generated
    INFO  Response returned

Future structured logs may include:

    request_id
    timestamp
    endpoint
    processing_time
    result_count
    status
    error_type

Logs should not expose sensitive information unnecessarily.

---

## 41. Observability Roadmap

Future monitoring should track:

    Request Count
    Request Latency
    Error Rate
    No-Match Rate
    Recommendation Count
    Dataset Load Status
    API Availability
    Search Success Rate
    Average Candidates Returned

A future processing trace could measure:

    Request
      |
      +---- normalization time
      |
      +---- terminology lookup time
      |
      +---- condition lookup time
      |
      +---- retrieval time
      |
      +---- ranking time
      |
      +---- explanation time
      |
      +---- response time

This helps identify performance bottlenecks.

---

## 42. Testing Architecture

Testing should cover individual components as well as the complete
pipeline.

    TEST SUITE
        |
        +---- Unit Tests
        |
        +---- API Tests
        |
        +---- Integration Tests
        |
        +---- Data Validation Tests
        |
        +---- Ranking Tests
        |
        +---- Explanation Tests

Example:

    Query
      |
      v
    Full Pipeline
      |
      v
    Expected Structured Result

---

## 43. Important Test Cases

### Valid Search

    Input:
    fever

    Expected:
    Known normalized term

### Uppercase Search

    Input:
    FEVER

    Expected:
    Equivalent normalized result

### Whitespace Search

    Input:
    "   fever   "

    Expected:
    Same normalized result

### Unknown Term

    Input:
    unknown-term

    Expected:
    Controlled no-match response

### Empty Input

    Input:
    ""

    Expected:
    Validation failure

### Ranking

Multiple candidates should be ranked consistently according to the
implemented scoring logic.

### Explainability

A returned recommendation should retain the information required to
explain its relevance.

---

## 44. Local Development

Create a Python virtual environment:

    python -m venv .venv

Windows:

    .venv\Scripts\activate

Linux / macOS:

    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

---

## 45. Running the Backend

Start the FastAPI development server using the project's configured
application entry point.

Typical development command:

    uvicorn api:app --reload

The interactive API documentation is normally available at:

    /docs

The OpenAPI schema is normally available at:

    /openapi.json

The exact startup command should follow the current repository structure.

---

## 46. API Development Workflow

Recommended development workflow:

    Modify Backend
          |
          v
    Run Tests
          |
          v
    Validate Dataset
          |
          v
    Start FastAPI
          |
          v
    Open API Documentation
          |
          v
    Test Endpoint
          |
          v
    Inspect JSON
          |
          v
    Connect Frontend
          |
          v
    Verify End-to-End Flow

---

## 47. Git Workflow

Recommended workflow for backend changes:

    1. Create or modify a backend component
    2. Test locally
    3. Review API behaviour
    4. Update documentation
    5. Commit changes
    6. Push to GitHub
    7. Review the repository
    8. Merge after verification

Example:

    git status

    git add backend/

    git commit -m "Improve backend intelligence pipeline"

    git push

Commit messages should describe the actual change.

---

## 48. Security Considerations

The prototype is intended primarily for controlled development and
hackathon environments.

A production deployment should consider:

    Authentication
    Authorization
    Rate Limiting
    Input Validation
    CORS Policy
    HTTPS
    Secret Management
    Security Headers
    Dependency Scanning
    Audit Logging

Secrets must never be committed to GitHub.

Sensitive configuration should be supplied through environment variables
or a secure secret-management system.

---

## 49. Configuration Management

Configuration should remain separate from application logic.

Future configuration may include:

    API_HOST
    API_PORT
    DATABASE_URL
    DATA_PATH
    CACHE_SETTINGS
    LOG_LEVEL
    ENVIRONMENT

Development configuration should not be hard-coded into production
logic.

---

## 50. Deployment Architecture

A future deployment could use:

                         INTERNET
                            |
                            v
                      REVERSE PROXY
                            |
                            v
                       FASTAPI API
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
       DATABASE         VECTOR STORE        CACHE
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                     KNOWLEDGE LAYER

Containerized deployment may eventually separate:

    Frontend
    Backend
    Database
    Vector Search
    Cache

This allows each component to scale independently.

---

## 51. CI/CD Roadmap

Future continuous integration can follow:

    Git Push
       |
       v
    Lint
       |
       v
    Unit Tests
       |
       v
    Integration Tests
       |
       v
    Build
       |
       v
    Security Checks
       |
       v
    Deployment

The goal is to prevent backend changes from silently breaking existing
functionality.

---

## 52. API Versioning

As the platform evolves, API versioning can prevent breaking frontend
integrations.

Example:

    /v1/search
    /v1/recommend
    /v1/diseases
    /v1/formulations

Future API versions can introduce improved schemas while preserving
compatibility with existing clients.

---

## 53. Scalability Roadmap

### Phase 1 — Prototype

    FastAPI
       +
    Structured Knowledge
       +
    Deterministic Retrieval
       +
    Ranking
       +
    Explainability

### Phase 2 — Structured Storage

    FastAPI
       +
    Database
       +
    Indexed Queries
       +
    Ranking
       +
    Explainability

### Phase 3 — Semantic Intelligence

    FastAPI
       +
    Database
       +
    Vector Search
       +
    Semantic Retrieval
       +
    Ranking
       +
    Explainability

### Phase 4 — Knowledge Intelligence

    API
       +
    Database
       +
    Vector Search
       +
    Knowledge Graph
       +
    ML Ranking
       +
    Evidence Layer
       +
    Explainability

---

## 54. Future Research Dashboard Support

The backend can eventually expose aggregated research information to
a dashboard.

Potential metrics include:

    Total Terms
    Total Conditions
    Total Formulations
    Total Ingredients
    Evidence Sources
    Search Queries
    Successful Matches
    No-Match Queries
    Average Candidate Count

Conceptual flow:

    Knowledge Base
          |
          v
    Analytics Layer
          |
          v
    Research Dashboard

This enables the platform to become more than a search interface.

---

## 55. Future Research Analytics

The backend can eventually support analytics such as:

- Most searched terms
- Most frequently matched conditions
- Most surfaced formulations
- No-match terminology
- Knowledge coverage
- Evidence coverage
- Search success rate
- Ranking distributions

These analytics can help identify gaps in the knowledge base.

---

## 56. Prototype Safety Boundary

Ayurveda Intelligence is an educational and research-oriented prototype.

The backend is designed for:

- Knowledge discovery
- Information retrieval
- Formulation exploration
- Terminology exploration
- Evidence-aware research
- Structured knowledge exploration

It is not designed to:

- Diagnose patients
- Prescribe treatment
- Determine patient-specific suitability
- Guarantee therapeutic outcomes
- Replace qualified healthcare professionals

Backend relevance scores represent information retrieval signals and
must not be interpreted as clinical scores.

---

## 57. Development Status

The backend roadmap follows:

    FOUNDATION
        |
        v
    API
        |
        v
    KNOWLEDGE
        |
        v
    RETRIEVAL
        |
        v
    RANKING
        |
        v
    EXPLAINABILITY
        |
        v
    EVIDENCE
        |
        v
    SEMANTIC INTELLIGENCE
        |
        v
    KNOWLEDGE GRAPH
        |
        v
    RESEARCH INTELLIGENCE

The architecture is intentionally incremental.

Each layer can be improved without requiring a complete rewrite of the
platform.

---

## 58. Backend Quality Checklist

Before merging a backend change:

    [ ] Input validation is preserved
    [ ] Existing API behaviour is not unintentionally broken
    [ ] Recommendation logic remains deterministic where expected
    [ ] Dataset assumptions are documented
    [ ] Tests are updated
    [ ] Error handling is implemented
    [ ] API responses remain structured
    [ ] Explainability information is preserved
    [ ] Evidence information is not fabricated
    [ ] No secrets are committed
    [ ] Documentation reflects implementation
    [ ] Frontend integration remains compatible
    [ ] New dependencies are documented
    [ ] Performance regressions are considered

---

## 59. Design Principles

The backend follows these principles:

### Explainability First

A result should be understandable rather than simply displayed.

### Data / Logic Separation

Knowledge should remain separate from application logic.

### Retrieval / Ranking Separation

Finding candidates and ordering candidates are different responsibilities.

### Evidence Awareness

Knowledge should be traceable to an identifiable source wherever
evidence is available.

### Modular Architecture

Each intelligence stage should be replaceable or upgradeable.

### API-First Integration

The frontend should consume structured backend responses rather than
duplicating business logic.

### Incremental Intelligence

The system should support progression from deterministic lookup to
semantic search and knowledge graphs.

### Reproducibility

A given input should produce predictable results when the underlying
knowledge and configuration remain unchanged.

---

## 60. Final Architecture Principle

The ultimate backend objective is not simply:

    USER QUERY
         |
         v
    FORMULATION

Instead, the platform aims to provide:

    USER QUERY
         |
         v
    NORMALIZED INTERPRETATION
         |
         v
    DISEASE / CONDITION
         |
         v
    FORMULATION
         |
         v
    MATCH SCORE
         |
         v
    EXPLANATION
         |
         v
    EVIDENCE / REFERENCE
         |
         v
    TRACEABLE RESULT

The backend therefore acts as the intelligence and provenance layer of
Ayurveda Intelligence.

Its long-term goal is to transform the prototype from a simple
formulation search system into an:

    EVIDENCE-AWARE
    EXPLAINABLE
    TRACEABLE
    RESEARCH-ORIENTED
    AYURVEDIC KNOWLEDGE INTELLIGENCE PLATFORM
