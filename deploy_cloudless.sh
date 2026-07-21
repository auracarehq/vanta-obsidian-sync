#!/bin/bash
set -e

echo "🚀 Deploying Vanta → Obsidian Sync Function to Azure (Cloud Build)"
echo "=================================================="

# Configuration
RESOURCE_GROUP="auracare-rg"
LOCATION="uksouth"
STORAGE_ACCOUNT="auracarevantsync"
FUNCTION_APP="vanta-obsidian-sync"
CONTAINER_REGISTRY="auracareacr"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Verifying Azure Resources${NC}"
az group show --name $RESOURCE_GROUP > /dev/null 2>&1 || az group create --name $RESOURCE_GROUP --location $LOCATION
az storage account show --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP > /dev/null 2>&1 || \
  az storage account create --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --location $LOCATION --sku Standard_LRS
az acr show --name $CONTAINER_REGISTRY --resource-group $RESOURCE_GROUP > /dev/null 2>&1 || \
  az acr create --resource-group $RESOURCE_GROUP --name $CONTAINER_REGISTRY --sku Basic --admin-enabled true
echo -e "${GREEN}✓ Azure resources ready${NC}\n"

echo -e "${BLUE}Step 2: Building Docker Image in Azure (ACR Task)${NC}"
# Build image in Azure Container Registry (no local Docker needed!)
az acr build \
  --registry $CONTAINER_REGISTRY \
  --image vanta-sync:latest \
  --file Dockerfile \
  .
echo -e "${GREEN}✓ Docker image built in Azure${NC}\n"

echo -e "${BLUE}Step 3: Getting ACR Credentials${NC}"
ACR_USERNAME=$(az acr credential show --name $CONTAINER_REGISTRY --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $CONTAINER_REGISTRY --query passwords[0].value -o tsv)
echo -e "${GREEN}✓ ACR credentials retrieved${NC}\n"

echo -e "${BLUE}Step 4: Creating Function App${NC}"
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --name $FUNCTION_APP \
  --storage-account $STORAGE_ACCOUNT \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux \
  --deployment-container-image-name $CONTAINER_REGISTRY.azurecr.io/vanta-sync:latest \
  --docker-registry-server-url https://$CONTAINER_REGISTRY.azurecr.io \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD

sleep 15
echo -e "${GREEN}✓ Function app created${NC}\n"

echo -e "${BLUE}Step 5: Configuring Function App Settings${NC}"
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    "VANTA_CLIENT_ID=vci_0c07415a383df9d0b51c0632cfd9054707cab45b52c933d7" \
    "VANTA_CLIENT_SECRET=vcs_0f13cb_9cc81e1480ccf46bd9143d4c81e557e23008a0a915568b1c98b680c4dd89a666" \
    "OBSIDIAN_VAULT_PATH=Compliance/Vanta" \
    "OBSIDIAN_VAULT_NAME=dkg" \
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE=false"
echo -e "${GREEN}✓ Function app configured${NC}\n"

echo -e "${BLUE}Step 6: Restarting Function App${NC}"
az functionapp restart --name $FUNCTION_APP --resource-group $RESOURCE_GROUP
echo -e "${GREEN}✓ Function app restarted${NC}\n"

echo -e "${GREEN}=================================================="
echo "🎉 Deployment Complete!"
echo "==================================================${NC}"
echo ""
echo "Function App: $FUNCTION_APP"
echo "Resource Group: $RESOURCE_GROUP"
echo "URL: https://$FUNCTION_APP.azurewebsites.net"
echo ""
echo "Schedule: Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)"
echo ""
echo "Monitor logs:"
echo "  az functionapp log tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP"
echo ""
echo "Check vault: Compliance/Vanta/ and Projects/Compliance_tasks/"
