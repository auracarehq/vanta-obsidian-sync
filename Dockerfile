# Use Azure Functions Python base image
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

# Install Node.js for Obsidian CLI
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Obsidian CLI globally
# Note: This assumes the obsidian-cli package from npm
# If using a different package, adjust accordingly
RUN npm install -g obsidian-cli || npm install -g @obsidian-cli/core || echo "Install Obsidian CLI manually"

# Copy function code
ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY requirements.txt /home/site/wwwroot/
RUN cd /home/site/wwwroot && \
    pip install --no-cache-dir -r requirements.txt

COPY . /home/site/wwwroot
