#!/bin/bash
set -e

echo "🚀 Deploying Vanta → Obsidian Sync Function to Azure"
echo "=================================================="

# Configuration
RESOURCE_GROUP="auracare-rg"
LOCATION="eastus"
STORAGE_ACCOUNT="auracarevantsync"
FUNCTION_APP="vanta-obsidian-sync"
CONTAINER_REGISTRY="auracareacr"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Creating Azure Resource Group${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION
echo -e "${GREEN}✓ Resource group created${NC}\n"

echo -e "${BLUE}Step 2: Creating Storage Account${NC}"
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS
echo -e "${GREEN}✓ Storage account created${NC}\n"

echo -e "${BLUE}Step 3: Creating Container Registry${NC}"
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_REGISTRY \
  --sku Basic \
  --admin-enabled true
echo -e "${GREEN}✓ Container registry created${NC}\n"

echo -e "${BLUE}Step 4: Building Docker Image${NC}"
az acr login --name $CONTAINER_REGISTRY
docker build -t $CONTAINER_REGISTRY.azurecr.io/vanta-sync:latest .
echo -e "${GREEN}✓ Docker image built${NC}\n"

echo -e "${BLUE}Step 5: Pushing Docker Image to ACR${NC}"
docker push $CONTAINER_REGISTRY.azurecr.io/vanta-sync:latest
echo -e "${GREEN}✓ Docker image pushed${NC}\n"

echo -e "${BLUE}Step 6: Getting ACR Credentials${NC}"
ACR_USERNAME=$(az acr credential show --name $CONTAINER_REGISTRY --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $CONTAINER_REGISTRY --query passwords[0].value -o tsv)
echo -e "${GREEN}✓ ACR credentials retrieved${NC}\n"

echo -e "${BLUE}Step 7: Creating Function App${NC}"
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --name $FUNCTION_APP \
  --storage-account $STORAGE_ACCOUNT \
  --plan $FUNCTION_APP-plan \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux \
  --deployment-container-image-name $CONTAINER_REGISTRY.azurecr.io/vanta-sync:latest

# Wait for function app to be ready
echo "Waiting for function app to be ready..."
sleep 30
echo -e "${GREEN}✓ Function app created${NC}\n"

echo -e "${BLUE}Step 8: Configuring Function App Settings${NC}"
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    "DOCKER_REGISTRY_SERVER_URL=https://$CONTAINER_REGISTRY.azurecr.io" \
    "DOCKER_REGISTRY_SERVER_USERNAME=$ACR_USERNAME" \
    "DOCKER_REGISTRY_SERVER_PASSWORD=$ACR_PASSWORD" \
    "VANTA_CLIENT_ID=vci_0c07415a383df9d0b51c0632cfd9054707cdb45b52c933d7" \
    "VANTA_CLIENT_SECRET=vcs_a7ddb1_29208354d0e18271e7dd588d690ce9081792e5cc19ee3c5c3f9ad2d347fdeb12" \
    "OBSIDIAN_VAULT_PATH=Compliance/Vanta"
echo -e "${GREEN}✓ Function app configured${NC}\n"

echo -e "${BLUE}Step 9: Restarting Function App${NC}"
az functionapp restart --name $FUNCTION_APP --resource-group $RESOURCE_GROUP
echo -e "${GREEN}✓ Function app restarted${NC}\n"

echo -e "${GREEN}=================================================="
echo "🎉 Deployment Complete!"
echo "==================================================${NC}"
echo ""
echo -e "${YELLOW}Function App Details:${NC}"
echo "  Name: $FUNCTION_APP"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  URL: https://$FUNCTION_APP.azurewebsites.net"
echo ""
echo -e "${YELLOW}Schedule:${NC} Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Configure Obsidian CLI authentication (see README.md)"
echo "  2. Monitor logs: az functionapp log tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP"
echo "  3. Check your Obsidian vault at: Compliance/Vanta/"
echo ""
echo -e "${YELLOW}Cost Estimate:${NC} ~$5.25/month"
