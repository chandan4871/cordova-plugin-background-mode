# ArcGIS File Upload Connected System Configuration

## Overview
This guide explains how to set up an Appian Connected System to integrate with ArcGIS REST API for file uploads.

## Step 1: Create Connected System

### In Appian Designer:
1. Navigate to **Build** > **Connected Systems**
2. Click **Create New** > **HTTP Connected System**
3. Name it: `ArcGIS File Upload System`

### Configuration:

```yaml
Name: ArcGIS File Upload Connected System
Description: Connected system for uploading files to ArcGIS GP Server
Base URL: https://server.nparks.dev.sgps/arcgis/rest/services
```

### Authentication Setup:

#### Option 1: Token-Based Authentication (Recommended)
```yaml
Authentication Type: Custom Authentication
```

**Request Template:**
- Add a custom header for token authentication
- Header Name: `Authorization`
- Header Value: `Bearer [token]`

#### Option 2: OAuth 2.0
```yaml
Authentication Type: OAuth 2.0
Token Endpoint: https://server.nparks.dev.sgps/arcgis/tokens/generateToken
Client ID: [Your ArcGIS Client ID]
Client Secret: [Your ArcGIS Client Secret]
```

## Step 2: Test Connection

1. Click **Test Connection**
2. Ensure connectivity to the base URL
3. Save the Connected System

## Important Notes:

- **Base URL**: Set the base URL to the root of your ArcGIS services
- **Timeout**: Consider increasing timeout for large file uploads (e.g., 300 seconds)
- **SSL Certificate**: Ensure SSL certificate is trusted or configure accordingly

## Next Steps:
Proceed to create the Integration Object for file upload.
