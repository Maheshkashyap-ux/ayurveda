# API Design

## Purpose

The API separates the frontend from application and intelligence services.

## Suggested endpoints

```text
GET  /health
POST /search
POST /normalize
POST /recommend
GET  /formulations/{id}
GET  /ingredients/{id}
GET  /references/{id}
```

These are interface proposals; replace them with the actual implemented endpoints.

## Example request

```json
{
  "query": "user-entered requirement"
}
```

## Example response structure

```json
{
  "query": "user-entered requirement",
  "normalized_concepts": [],
  "results": [],
  "evidence": [],
  "safety_notes": []
}
```

## API requirements

- validate input
- return consistent errors
- avoid exposing secrets
- log useful technical events
- keep response schema versionable
