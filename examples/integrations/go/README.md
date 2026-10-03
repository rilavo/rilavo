# my-rilavo-app

Rilavo-protected go application.

## Quick Start

1. Configure your issuer and audience in the source code
2. Install dependencies: `go mod tidy`
3. Run: `go run .`

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIENCE` | Your verifier identifier | `YOUR_AUDIENCE_HERE` |
| `ISSUER_KEY` | Issuer public key (PEM) | `issuer_public_key.pem` |

## Development

```bash
air
```

## Production

```bash
docker build -t my-rilavo-app .
docker run -p 8080:8080 my-rilavo-app
```

## Rilavo Integration

This application uses Rilavo for agent authorization verification.
See [Rilavo Documentation](https://docs.rilavo.org) for details.
