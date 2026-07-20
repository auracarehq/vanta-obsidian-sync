# Quick Start Guide

## Prerequisites

```bash
# Install Azure CLI
brew install azure-cli

# Login to Azure
az login

# Verify Docker is running
docker --version
```

## Deploy in 3 Commands

```bash
cd /Users/akn/projects/auracare/vanta-sync-function

# Option 1: Automated deployment
./deploy.sh

# Option 2: Manual step-by-step (see README.md)
```

## Configure Obsidian CLI

The Azure Function needs to write to your Obsidian vault. We need to set up Obsidian CLI authentication.

### Check if Obsidian CLI is installed locally

```bash
obsidian-cli --version
```

If not installed:
```bash
npm install -g obsidian-cli-unofficial
```

### Get Obsidian CLI Configuration

The function will use Obsidian CLI inside the Azure container. You may need to:

1. **Set up an API token or vault connection** in the Azure Function settings
2. **Configure the vault path** (already set to `Compliance/Vanta`)

### Add Obsidian CLI Auth to Azure Function

```bash
# If Obsidian CLI uses an API token
az functionapp config appsettings set \
  --name vanta-obsidian-sync \
  --resource-group auracare-rg \
  --settings "OBSIDIAN_API_TOKEN=your_token_here"

# Or if it uses vault connection string
az functionapp config appsettings set \
  --name vanta-obsidian-sync \
  --resource-group auracare-rg \
  --settings "OBSIDIAN_VAULT_CONNECTION=your_connection_string"
```

## Verify Deployment

```bash
# Watch the logs
az functionapp log tail \
  --name vanta-obsidian-sync \
  --resource-group auracare-rg

# Manually trigger (for testing)
az functionapp function show \
  --name vanta-obsidian-sync \
  --resource-group auracare-rg \
  --function-name vanta_sync_timer
```

## Check Your Obsidian Vault

After the first sync (or manual trigger), check:
```
/Users/akn/projects/auracare/dkg/Compliance/Vanta/
```

You should see:
- `Vanta Security Tests.md` (latest)
- `Vanta Security Tests - YYYY-MM-DD.md` (snapshot)

## Troubleshooting

### Function not running?
```bash
# Check function status
az functionapp show \
  --name vanta-obsidian-sync \
  --resource-group auracare-rg \
  --query state

# Restart it
az functionapp restart \
  --name vanta-obsidian-sync \
  --resource-group auracare-rg
```

### Obsidian CLI errors?
Check the function logs for authentication issues. The container includes Node.js and Obsidian CLI, but needs proper vault authentication.

### Vanta API errors?
Verify the OAuth credentials in the screenshot match what's in the function settings.

## Update the Function

When you make code changes:

```bash
# Rebuild and push
az acr login --name auracareacr
docker build -t auracareacr.azurecr.io/vanta-sync:latest .
docker push auracareacr.azurecr.io/vanta-sync:latest

# Restart function
az functionapp restart \
  --name vanta-obsidian-sync \
  --resource-group auracare-rg
```

## Cost

Estimated monthly cost: **~$5.25**
- Azure Function (Consumption): $0.20
- Storage Account: $0.05
- Container Registry (Basic): $5.00

## Support

- Azure Function issues: Check logs and Application Insights
- Obsidian CLI issues: Check container logs and authentication
- Vanta API issues: Verify OAuth credentials and permissions
