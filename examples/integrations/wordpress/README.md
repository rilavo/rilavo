# my-rilavo-app

Rilavo-protected wordpress application.

## Quick Start

1. Configure your issuer and audience in the source code
2. Install dependencies: `composer install`
3. Run: `N/A (WordPress plugin)`

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIENCE` | Your verifier identifier | `YOUR_AUDIENCE_HERE` |
| `ISSUER_KEY` | Issuer public key (PEM) | `issuer_public_key.pem` |

## Development

```bash
N/A (WordPress plugin)
```

## Production

```bash
docker build -t my-rilavo-app .
docker run -p 80:80 my-rilavo-app
```

## Rilavo Integration

This application uses Rilavo for agent authorization verification.
See [Rilavo Documentation](https://docs.rilavo.org) for details.
