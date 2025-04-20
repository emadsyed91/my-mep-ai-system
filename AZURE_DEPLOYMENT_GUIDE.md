# MEP Design Automation System - Azure Deployment Guide

This guide walks through deploying the MEP Design Automation System to Azure using GitHub integration.

## Prerequisites

1. GitHub account
2. Azure account (free tier available)
3. Azure CLI installed locally (optional)

## Step 1: Prepare Your Repository

1. Push your code to a GitHub repository
2. Ensure the following files are in your repository:
   - `azure-requirements.txt`: Python dependencies
   - `runtime.txt`: Python version specification
   - `web.config`: IIS configuration for Azure
   - `.github/workflows/azure-deploy.yml`: GitHub Actions workflow
   - `startup.txt`: Command to run your app

## Step 2: Set Up Azure Resources

### Create Azure Web App

1. Sign in to the [Azure Portal](https://portal.azure.com/)
2. Click "Create a resource" > "Web App"
3. Fill in the following details:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new (e.g., "mep-design-automation-rg")
   - **Name**: A unique name (e.g., "mep-design-automation")
   - **Publish**: Code
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: Choose a region close to your users
   - **App Service Plan**: Create new (B1 tier or higher recommended)
4. Click "Review + create" > "Create"

### Create Azure PostgreSQL Database

1. In the Azure Portal, search for "Azure Database for PostgreSQL"
2. Choose "Flexible server" (recommended)
3. Fill in the details:
   - **Subscription**: Same as your web app
   - **Resource Group**: Same as your web app
   - **Server name**: A unique name (e.g., "mep-design-db")
   - **Admin username**: Create a username
   - **Password**: Create a strong password
   - **Location**: Same as your web app
   - **Version**: PostgreSQL 13 or higher
4. Click "Review + create" > "Create"

### Create Azure Storage Account (for file uploads)

1. In the Azure Portal, search for "Storage account"
2. Click "Create"
3. Fill in the details:
   - **Subscription**: Same as your web app
   - **Resource Group**: Same as your web app
   - **Storage account name**: A unique name (e.g., "mepdesignstorage")
   - **Region**: Same as your web app
   - **Performance**: Standard
   - **Redundancy**: Locally-redundant storage (LRS)
4. Click "Review + create" > "Create"
5. After creation, go to the storage account, click on "Containers", and create a new container called "blueprints" with "Container" access level

## Step 3: Configure Your Web App

1. Go to your Web App in the Azure Portal
2. Under "Settings", click on "Configuration"
3. Add the following Application settings:
   - `SQLALCHEMY_DATABASE_URI`: Your PostgreSQL connection string
     Format: `postgresql://username:password@servername.postgres.database.azure.com/mepdesigndb?sslmode=require`
   - `FLASK_ENV`: production
   - `SECRET_KEY`: a random string for security
   - `STORAGE_CONNECTION_STRING`: Your Azure Storage connection string (find in the Storage Account's "Access keys" section)
   - `STORAGE_CONTAINER_NAME`: blueprints
4. Click "Save"

## Step 4: Set Up GitHub Deployment

### Method 1: GitHub Actions (Recommended)

1. In your GitHub repository, go to "Settings" > "Secrets" > "Actions"
2. Add a new repository secret:
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Value: The publish profile from your Azure Web App
     (Download from Azure Portal > Your Web App > Overview > "Get publish profile")
3. Push your code to the main branch to trigger deployment

### Method 2: Azure App Service Deployment Center

1. Go to your Web App in the Azure Portal
2. Click on "Deployment Center"
3. Source: Select "GitHub"
4. Sign in to your GitHub account 
5. Choose your organization, repository, and branch
6. Click "Save"

## Step 5: Initialize Database

After deployment, you need to initialize your database:

1. In the Azure Portal, go to your Web App
2. Click on "SSH" under "Development Tools"
3. In the SSH terminal, run:
   ```bash
   cd site/wwwroot
   python -c "from app import db; db.create_all()"
   ```

## Step 6: Configure Custom Domain (Optional)

1. Go to your Web App
2. Click on "Custom domains" in the menu
3. Click "Add custom domain"
4. Follow the instructions to add your domain

## Step 7: Set Up Monitoring

1. Go to your Web App
2. Click on "Application Insights" in the menu
3. Enable Application Insights
4. Configure alerts as needed

## Troubleshooting

### Application Errors
- Check Application Insights logs
- View the log stream in the Azure Portal (Web App > Monitoring > Log stream)

### Deployment Failures
- Check GitHub Actions logs
- Verify that all required secrets are set correctly
- Check for Python version compatibility

## Security Considerations

1. **Database**: Ensure the firewall is configured to only allow your web app to connect
2. **Storage**: Use SAS tokens for limited-time access
3. **Web App**: Configure SSL settings and enable HTTPS-only

## Scaling Your Application

- **Scale Up**: Go to your App Service Plan > Scale up (Change pricing tier)
- **Scale Out**: Go to your App Service Plan > Scale out (Add instances)

## Monitoring and Maintenance

- Set up Azure Monitor alerts for performance metrics
- Configure regular backups for your database
- Set up diagnostic settings to capture logs

## Cost Optimization

- Consider using reserved instances for production workloads
- Use auto-scaling rules to scale down during off-hours
- Monitor costs in the Azure Cost Management + Billing section