# ArcGIS File Upload Integration Object

## Overview
This integration handles uploading files to the ArcGIS GPServer upload service.

## Step 1: Create Integration Object

### In Appian Designer:
1. Navigate to **Build** > **Integration Objects**
2. Click **Create New Integration**
3. Select your **ArcGIS File Upload Connected System**
4. Name it: `INT_ArcGIS_UploadFile`

## Step 2: Configure Integration

### Basic Configuration:

```yaml
Name: INT_ArcGIS_UploadFile
Description: Upload file to ArcGIS GP Server for DWG to Polygon conversion
Connected System: ArcGIS File Upload Connected System
Endpoint Path: /Nparks/DWGtoPolygonFeatureClassConversion/GPServer/uploads/upload
HTTP Method: POST
```

### Request Configuration:

#### Request Body:
- **Content Type**: `multipart/form-data`
- **Body**: Use the following structure

#### Rule Inputs (Create these):
```sail
ri!file (Document) - The file to upload
ri!filename (Text) - Optional filename override
ri!token (Text) - ArcGIS authentication token (if using token auth)
ri!f (Text) - Format parameter (default: "json")
```

#### Request Parameters/Body Fields:

In the **Body** tab, configure as multipart/form-data:

1. **file field**:
   - Parameter Name: `file`
   - Parameter Type: `Document`
   - Value: `ri!file`

2. **f field** (format):
   - Parameter Name: `f`
   - Parameter Type: `Text`
   - Value: `if(isnull(ri!f), "json", ri!f)`

3. **token field** (if using token auth):
   - Parameter Name: `token`
   - Parameter Type: `Text`
   - Value: `ri!token`

### Response Configuration:

#### Result Structure:
```json
{
  "success": true,
  "item": {
    "itemID": "i12345678-1234-1234-1234-123456789012",
    "itemName": "uploaded_file.dwg",
    "description": "",
    "date": 1732454400000,
    "committed": false
  }
}
```

#### Create Rule Outputs:
```sail
success (Boolean) - Upload success status
itemID (Text) - Unique identifier for uploaded file
itemName (Text) - Name of uploaded file
errorMessage (Text) - Error message if failed
```

#### Response Parsing:

In the **Response** tab:

```sail
a!fromJson(
  httpResponse.body
)
```

Map the outputs:
- `success`: `response.success`
- `itemID`: `response.item.itemID`
- `itemName`: `response.item.itemName`
- `errorMessage`: `if(response.success, null, response.error.message)`

## Step 3: Test Integration

1. Click **Test Request**
2. Upload a test file
3. Verify the response contains `itemID`

## Important Notes:

- The `itemID` returned is crucial - you'll need it for subsequent GP service calls
- The file upload has a maximum size limit (check with ArcGIS admin)
- Files are uncommitted after upload - they need to be processed by the GP service

## Next Steps:
Configure the Process Model to call this integration.
