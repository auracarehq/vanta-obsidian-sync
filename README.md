# Vanta → Obsidian Sync

Automated Azure Function that syncs Vanta security tests & compliance checks to your Obsidian vault every 6 hours using Obsidian CLI and Obsidian Sync.

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Vanta API      │ ───▶ │  Azure Function  │ ───▶ │  Obsidian CLI   │
│  (OAuth 2.0)    │      │  (Timer: 6h)     │      │  → Vault Files  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                                             │
                                                             ▼
                                                    ┌─────────────────┐
                                                    │ Obsidian Sync   │
                                                    │ (All Devices)   │
                                                    └─────────────────┘
```

**Key Features:**
- ⏰ Automated sync every 6 hours
- ☁️ Fully cloud-based (no local dependencies)
- 🔄 Works with Obsidian Sync across all devices
- 📊 Beautiful markdown reports with test status
- 🔐 Secure OAuth 2.0 authentication with Vanta

## 📋 Prerequisites

1. **Azure Account** with CLI installed and logged in
2. **Vanta Account** with API access (OAuth client credentials)
3. **Obsidian Vault** with Obsidian CLI configured
4. **Docker** (for containerized deployment)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/auracarehq/vanta-obsidian-sync.git
cd vanta-obsidian-sync
```

### 2. Configure Environment

Copy the example environment file and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Vanta OAuth credentials and Obsidian vault details.

### 3. Test Locally

Run the test script to verify Obsidian CLI integration:

```bash
python3 test_obsidian_only.py
```

This creates mock Vanta data in your vault to test the sync mechanism.

### 4. Deploy to Azure

Use the automated deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

Or follow the manual deployment steps in [DEPLOYMENT.md](DEPLOYMENT.md).

## 📁 Output Structure

Files are synced to your Obsidian vault at:

```
Compliance/Vanta/
├── Vanta Security Tests.md              # Always the latest
├── Vanta Security Tests - 2026-07-20.md # Daily snapshot
└── Vanta Security Tests - 2026-07-21.md # Historical data
```

Each file contains:
- Summary statistics (passing/failing/warning tests)
- Failing tests with remediation steps
- Warning tests requiring attention
- Complete list of passing tests

## ⏰ Sync Schedule

The function runs on a cron schedule: `0 0 */6 * * *`

- **00:00 UTC** (8:00 PM ET / 5:00 PM PT)
- **06:00 UTC** (2:00 AM ET / 11:00 PM PT)
- **12:00 UTC** (8:00 AM ET / 5:00 AM PT)
- **18:00 UTC** (2:00 PM ET / 11:00 AM PT)

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VANTA_CLIENT_ID` | OAuth client ID from Vanta | ✅ |
| `VANTA_CLIENT_SECRET` | OAuth client secret from Vanta | ✅ |
| `OBSIDIAN_VAULT_PATH` | Path within vault (e.g., `Compliance/Vanta`) | ✅ |
| `OBSIDIAN_VAULT_NAME` | Name of your Obsidian vault | ✅ |

### Vanta API Setup

1. Log in to [Vanta](https://app.vanta.com)
2. Navigate to **Settings → API Keys**
3. Create a new OAuth application
4. Copy the Client ID and Client Secret
5. Grant `read:tests` permission

**Note:** The Vanta OAuth flow requires activation. After creating the credentials, you may need to complete an authorization step before the function will work.

## 🧪 Testing

### Test Obsidian CLI Only

```bash
python3 test_obsidian_only.py
```

This tests the Obsidian CLI integration with mock Vanta data. Useful for verifying vault access without hitting the Vanta API.

### Test Full Integration

```bash
python3 test_local.py
```

This tests:
1. Vanta OAuth authentication
2. Fetching security tests from Vanta API
3. Markdown generation
4. Writing to Obsidian vault via CLI

## 💰 Cost Estimate

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Azure Functions | Consumption Plan | ~$0.20 |
| Azure Storage | Standard LRS | ~$0.05 |
| Azure Container Registry | Basic | ~$5.00 |
| **Total** | | **~$5.25/month** |

## 📊 Monitoring

### View Function Logs

```bash
az functionapp log tail \
  --name vanta-obsidian-sync \
  --resource-group auracare-rg
```

### Check Function Status

```bash
az functionapp show \
  --name vanta-obsidian-sync \
  --resource-group auracare-rg \
  --query state
```

### Manual Trigger

```bash
az functionapp function show \
  --name vanta-obsidian-sync \
  --resource-group auracare-rg \
  --function-name vanta_sync_timer
```

## 🔒 Security

- OAuth credentials stored as encrypted Azure Function App Settings
- Consider using Azure Key Vault for enhanced secret management
- Rotate Vanta client secret regularly
- Use least-privilege permissions for Azure resources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/auracarehq/vanta-obsidian-sync/issues)
- **Documentation:** [Full Documentation](DEPLOYMENT.md)
- **Vanta API Docs:** [https://developer.vanta.com](https://developer.vanta.com)

## 🙏 Acknowledgments

Built with:
- [Azure Functions](https://azure.microsoft.com/en-us/services/functions/)
- [Obsidian CLI](https://github.com/obsidian-community/obsidian-cli)
- [Vanta API](https://developer.vanta.com)

---

Made with ❤️ by [Auracare](https://auracare.com)
