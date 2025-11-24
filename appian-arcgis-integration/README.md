# Appian to ArcGIS File Upload Integration

## Quick Start

This guide helps you integrate Appian with ArcGIS REST API to upload files directly from your Appian interface to ArcGIS GPServer.

## Target Endpoint
```
https://server.nparks.dev.sgps/arcgis/rest/services/Nparks/DWGtoPolygonFeatureClassConversion/GPServer/uploads/upload
```

## Documentation Files

Follow these guides in order:

### 1. [Connected System Configuration](./1-ConnectedSystem-ArcGIS.md)
Set up the HTTP connected system for ArcGIS authentication and connectivity.

**Time Required:** 15 minutes

### 2. [Integration Object Configuration](./2-Integration-FileUpload.md)
Create the integration object to handle file uploads with multipart/form-data.

**Time Required:** 30 minutes

### 3. [Process Model Configuration](./3-ProcessModel-Configuration.md)
Build the process model to orchestrate the file upload and handle responses.

**Time Required:** 45 minutes

### 4. [Interface Update](./4-Interface-Update.md)
Update your interface button to trigger the file upload process.

**Time Required:** 30 minutes

### 5. [Complete Implementation Guide](./5-Complete-Implementation-Guide.md)
Comprehensive guide with testing, troubleshooting, and best practices.

**Reference:** As needed

## Architecture Overview

```
┌─────────────────┐
│  Appian UI      │
│  (File Upload   │
│   + Form Data)  │
└────────┬────────┘
         │
         │ Submit Button Click
         ▼
┌─────────────────┐
│ Process Model   │
│ PM_UploadFile   │
│ ToArcGIS        │
└────────┬────────┘
         │
         │ Call Integration
         ▼
┌─────────────────┐
│ Integration     │
│ INT_ArcGIS_     │
│ UploadFile      │
└────────┬────────┘
         │
         │ HTTP POST (multipart/form-data)
         ▼
┌─────────────────┐
│ ArcGIS GPServer │
│ /uploads/upload │
└────────┬────────┘
         │
         │ Return itemID
         ▼
┌─────────────────┐
│ Success Handler │
│ (Save metadata) │
└─────────────────┘
```

## Key Components

### 1. **Connected System**
- Handles authentication with ArcGIS
- Manages base URL configuration
- Supports token-based or OAuth authentication

### 2. **Integration Object**
- Configures multipart/form-data request
- Maps file and parameters
- Parses ArcGIS response

### 3. **Process Model**
- Orchestrates the upload flow
- Handles errors gracefully
- Saves metadata after successful upload

### 4. **Interface Updates**
- File upload field
- Submit button with process start
- Status display for user feedback

## Prerequisites

Before starting, ensure you have:

- [ ] Appian environment access (Designer role)
- [ ] ArcGIS REST API endpoint URL
- [ ] ArcGIS authentication credentials (token or OAuth)
- [ ] Permission to create:
  - Connected Systems
  - Integration Objects
  - Process Models
  - Constants

## Quick Implementation (TL;DR)

For experienced Appian developers:

1. **Create Connected System:**
   - Type: HTTP
   - Base URL: `https://server.nparks.dev.sgps/arcgis/rest/services`
   - Auth: Token or OAuth

2. **Create Integration:**
   - Endpoint: `/Nparks/DWGtoPolygonFeatureClassConversion/GPServer/uploads/upload`
   - Method: POST
   - Content-Type: multipart/form-data
   - Body: `file` (Document), `f` (Text), `token` (Text)

3. **Create Process Model:**
   - Input: fileToUpload (Document)
   - Integration Node: Call upload integration
   - Output: arcgisItemID (Text)

4. **Update Interface:**
   - Add file upload field
   - Update button to call `a!startProcess()`
   - Pass uploaded document to process

## Response Format

Successful upload returns:

```json
{
  "success": true,
  "item": {
    "itemID": "i12345678-1234-1234-1234-123456789012",
    "itemName": "filename.dwg",
    "description": "",
    "date": 1732454400000,
    "committed": false
  }
}
```

**Important:** Save the `itemID` - you'll need it for GP service processing.

## Common Issues

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check token validity and permissions |
| 400 Bad Request | Verify multipart/form-data configuration |
| Timeout | Increase connected system timeout for large files |
| Empty response | Check endpoint URL and response parsing |

## Testing Checklist

- [ ] Connected system test passes
- [ ] Integration test with sample file succeeds
- [ ] Process model executes without errors
- [ ] Interface button triggers upload
- [ ] itemID is returned and saved
- [ ] Error handling works as expected

## Support

For issues or questions:
1. Check the [Complete Implementation Guide](./5-Complete-Implementation-Guide.md)
2. Review Appian logs in Admin Console
3. Verify ArcGIS endpoint with curl/Postman
4. Check ArcGIS REST API documentation

## File Structure

```
appian-arcgis-integration/
├── README.md                              # This file
├── 1-ConnectedSystem-ArcGIS.md           # Connected System setup
├── 2-Integration-FileUpload.md           # Integration configuration
├── 3-ProcessModel-Configuration.md       # Process Model setup
├── 4-Interface-Update.md                 # Interface modifications
└── 5-Complete-Implementation-Guide.md    # Comprehensive guide
```

## Estimated Time

- **Total Implementation:** 2-3 hours
- **Testing & Debugging:** 1-2 hours
- **Documentation Review:** 30 minutes

## Next Steps

1. Read through [Connected System Configuration](./1-ConnectedSystem-ArcGIS.md)
2. Follow each guide sequentially
3. Test at each step
4. Refer to the [Complete Implementation Guide](./5-Complete-Implementation-Guide.md) for troubleshooting

Good luck with your integration! 🚀
