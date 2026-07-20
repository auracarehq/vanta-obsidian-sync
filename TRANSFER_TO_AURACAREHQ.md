# Transfer Repository to auracarehq Organization

The repository is currently at: **https://github.com/akn101/vanta-obsidian-sync**

## Why It's Under Personal Account

The `auracarehq` organization has SAML SSO enabled, which requires additional authentication:

```
remote: The 'auracarehq' organization has enabled or enforced SAML SSO.
remote: To access this repository, you must re-authorize the OAuth Application 'GitHub CLI'.
```

## How to Transfer

### Option 1: Re-authenticate GitHub CLI with SAML SSO

1. **Re-authorize GitHub CLI:**
   ```bash
   gh auth login
   ```
   
2. **Select HTTPS protocol and authorize with SSO**

3. **Transfer the repository:**
   ```bash
   # From the repo directory
   gh repo transfer akn101/vanta-obsidian-sync auracarehq
   ```

### Option 2: Use GitHub Web UI

1. Go to https://github.com/akn101/vanta-obsidian-sync
2. Click **Settings** → **General**
3. Scroll to **Danger Zone**
4. Click **Transfer ownership**
5. Enter `auracarehq` as the new owner
6. Confirm the transfer

### Option 3: Clone and Re-create Under Organization

If transfer doesn't work:

```bash
# Clone the current repo
git clone https://github.com/akn101/vanta-obsidian-sync.git
cd vanta-obsidian-sync

# Remove old remote
git remote remove origin

# Create new repo under auracarehq (via web UI or after SAML auth)
# Then add new remote
git remote add origin https://github.com/auracarehq/vanta-obsidian-sync.git
git push -u origin main
```

## After Transfer

Update Azure Function deployment settings if the container registry or deployment pipeline references the GitHub repo URL.

## Current Status

✅ **Repository Created:** https://github.com/akn101/vanta-obsidian-sync  
✅ **Code Pushed:** All files committed and pushed  
✅ **CI/CD Workflows:** Included (will need secrets configured)  
⏳ **Transfer Pending:** Awaiting SAML SSO re-authentication  

## Files Included

- Azure Function code (`function_app.py`)
- Docker configuration with Node.js + Python + Obsidian CLI
- Deployment automation (`deploy.sh`)
- Test scripts (`test_local.py`, `test_obsidian_only.py`)
- GitHub Actions workflows (CI/CD)
- Comprehensive documentation
