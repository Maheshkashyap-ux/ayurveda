# Deployment

## Environments

Maintain separate configuration for:
- local development
- demo/staging
- production-like deployment if required

## Configuration

Store environment-specific values in environment variables.

## Deployment checklist

- frontend build succeeds
- backend starts
- database is reachable
- seed data exists
- health endpoint responds
- CORS/configuration is correct
- secrets are not committed
- logs do not expose sensitive values

## Reproducibility

Document:
- runtime version
- dependency installation
- environment variables
- startup commands
- database initialization
