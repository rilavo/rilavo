# my-rilavo-app

Rilavo-protected fastapi application.

## Quick Start

1. Configure your issuer and audience in the source code
2. Install dependencies: `pip install -e .`
3. Run: `uvicorn main:app --reload`

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIENCE` | Your verifier identifier | `YOUR_AUDIENCE_HERE` |
| `ISSUER_KEY` | Issuer public key (PEM) | `issuer_public_key.pem` |

## Development

```bash
uvicorn main:app --reload
```

## Production

```bash
docker build -t my-rilavo-app .
docker run -p 8000:8000 my-rilavo-app
```

## Rilavo Integration

This application uses Rilavo for agent authorization verification.
See [Rilavo Documentation](https://docs.rilavo.org) for details.
