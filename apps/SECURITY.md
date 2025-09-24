# Security Configuration

## Environment Variables

This project uses environment variables to manage sensitive configuration data like passwords, tokens, and API keys. This approach follows security best practices by keeping secrets out of version control.

### Setup Instructions

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file with your secure values:**
   ```bash
   # Replace the example values with strong, unique passwords and tokens
   POSTGRES_PASSWORD=your_very_secure_postgres_password_here
   DEVICE_POSTGRES_PASSWORD=your_very_secure_device_password_here
   INFLUXDB_ADMIN_PASSWORD=your_very_secure_influxdb_password_here
   INFLUXDB_ADMIN_TOKEN=your_very_secure_influxdb_token_here
   ```

3. **Generate strong passwords and tokens:**
   - Use a password manager to generate strong, unique passwords
   - For tokens, use cryptographically secure random generators
   - Minimum 16 characters for passwords, 32+ characters for tokens

### Security Notes

- **Never commit `.env` files to version control** - they are excluded in `.gitignore`
- **Use different passwords for each service** - avoid password reuse
- **Rotate credentials regularly** - especially in production environments
- **Use strong, random passwords** - avoid dictionary words or predictable patterns

### Production Deployment

For production deployments, consider using:
- Docker secrets
- Kubernetes secrets
- Cloud provider secret management services (AWS Secrets Manager, Azure Key Vault, etc.)
- HashiCorp Vault

### Default Values

The docker-compose.yml file includes default values for development purposes. These defaults should **never** be used in production environments.

## GitGuardian Integration

This project has been configured to prevent hardcoded secrets from being committed. If GitGuardian detects any hardcoded secrets:

1. Remove the hardcoded values immediately
2. Replace them with environment variable references
3. Add the secrets to your `.env` file
4. Ensure `.env` is in `.gitignore`
5. Consider rewriting git history if secrets were already committed

## Remediation Checklist

- [x] Replaced hardcoded passwords with environment variables
- [x] Created `.env.example` with documentation
- [x] Updated `.gitignore` to exclude `.env` files
- [x] Documented security best practices
- [ ] Rotate any previously exposed credentials
- [ ] Review git history for any committed secrets