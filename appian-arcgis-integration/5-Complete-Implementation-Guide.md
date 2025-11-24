# Complete ArcGIS File Upload Implementation Guide

## Overview
This guide provides step-by-step instructions to implement file upload from Appian to ArcGIS GPServer.

## Architecture Flow

```
[User Interface]
      ↓
   [Submit Button]
      ↓
[Start Process Model]
      ↓
[Integration Call]
      ↓
[ArcGIS REST API]
   /uploads/upload
      ↓
[Return itemID]
      ↓
[Save to Database]
      ↓
[Show Success Message]
```

## Implementation Checklist

### Phase 1: Setup (30 minutes)
- [ ] Create ArcGIS authentication credentials
- [ ] Test ArcGIS endpoint manually (Postman/curl)
- [ ] Create folder in Appian for file uploads
- [ ] Create constants for configuration

### Phase 2: Connected System (15 minutes)
- [ ] Create HTTP Connected System
- [ ] Configure base URL
- [ ] Set up authentication
- [ ] Test connection

### Phase 3: Integration Object (30 minutes)
- [ ] Create integration object
- [ ] Configure multipart/form-data request
- [ ] Set up response parsing
- [ ] Test with sample file

### Phase 4: Process Model (45 minutes)
- [ ] Create process model
- [ ] Add process variables
- [ ] Configure integration node
- [ ] Add error handling
- [ ] Test process execution

### Phase 5: Interface Update (30 minutes)
- [ ] Add file upload field
- [ ] Update button saveInto
- [ ] Add process start call
- [ ] Add status display
- [ ] Test end-to-end

## Detailed Implementation Steps

### 1. Test ArcGIS Endpoint Manually

Before implementing in Appian, verify the endpoint works:

#### Using curl:
```bash
curl -X POST \
  'https://server.nparks.dev.sgps/arcgis/rest/services/Nparks/DWGtoPolygonFeatureClassConversion/GPServer/uploads/upload' \
  -F 'file=@/path/to/your/file.dwg' \
  -F 'f=json' \
  -F 'token=YOUR_TOKEN'
```

Expected Response:
```json
{
  "success": true,
  "item": {
    "itemID": "i12345678-1234-1234-1234-123456789012",
    "itemName": "file.dwg",
    "description": "",
    "date": 1732454400000,
    "committed": false
  }
}
```

### 2. Create Appian Constants

Navigate to **Build** > **Constants** and create:

#### ARCGIS_BASE_URL
```yaml
Type: Text
Value: https://server.nparks.dev.sgps/arcgis/rest/services
```

#### ARCGIS_AUTH_TOKEN
```yaml
Type: Text (Sensitive)
Value: [Your ArcGIS token]
Description: Authentication token for ArcGIS services
```

#### PM_UPLOAD_FILE_TO_ARCGIS
```yaml
Type: Process Model
Value: [Select your process model after creation]
```

#### ARCGIS_UPLOAD_FOLDER
```yaml
Type: Folder
Value: [Select folder for temporary file storage]
```

### 3. Create Connected System

Follow: `1-ConnectedSystem-ArcGIS.md`

**Key Settings:**
- Name: `ArcGIS File Upload Connected System`
- Base URL: `cons!ARCGIS_BASE_URL`
- Timeout: 300 seconds (for large files)
- Authentication: Token or OAuth

### 4. Create Integration Object

Follow: `2-Integration-FileUpload.md`

**Key Configuration:**
```yaml
Name: INT_ArcGIS_UploadFile
Endpoint: /Nparks/DWGtoPolygonFeatureClassConversion/GPServer/uploads/upload
Method: POST
Content-Type: multipart/form-data
```

**Rule Inputs:**
- `ri!file` (Document)
- `ri!token` (Text)
- `ri!f` (Text) - default "json"

**Rule Outputs:**
- `success` (Boolean)
- `itemID` (Text)
- `itemName` (Text)
- `errorMessage` (Text)

### 5. Create Process Model

Follow: `3-ProcessModel-Configuration.md`

**Process Variables:**

Inputs:
- `pv!fileToUpload` (Document)
- `pv!fileSource` (Integer)
- `pv!fileType` (Integer)
- `pv!description` (Text)
- `pv!accessRights` (Text)
- `pv!arcgisToken` (Text)

Outputs:
- `pv!uploadSuccess` (Boolean)
- `pv!arcgisItemID` (Text)
- `pv!errorMessage` (Text)

**Process Flow:**
1. Start Node
2. Integration Node (Call INT_ArcGIS_UploadFile)
3. XOR Gateway (Check success)
4. Success Path: Save metadata → End
5. Failure Path: Error handling → End

### 6. Update Interface

Follow: `4-Interface-Update.md`

#### Add File Upload Field:
```sail
a!fileUploadField(
  label: "Upload File (DWG)",
  target: cons!ARCGIS_UPLOAD_FOLDER,
  maxSelections: 1,
  value: ri!uploadedDocument,
  saveInto: ri!uploadedDocument,
  required: true
)
```

#### Update Button:
```sail
a!buttonWidget(
  label: "Submit and Upload to ArcGIS",
  saveInto: {
    /* Your existing data saves */
    ri!buttonAction,
    a!save(ri!fileSource, local!selectedFileSource),
    /* ... other saves ... */
    
    /* Start process model */
    a!startProcess(
      processModel: cons!PM_UPLOAD_FILE_TO_ARCGIS,
      processParameters: {
        fileToUpload: ri!uploadedDocument,
        fileSource: local!selectedFileSource,
        fileType: local!selectedFileType,
        description: local!currentDescription,
        accessRights: local!currentAccessRights,
        arcgisToken: cons!ARCGIS_AUTH_TOKEN
      },
      onSuccess: a!save(local!uploadStatus, "Success"),
      onError: a!save(local!uploadError, fv!error)
    )
  },
  submit: true,
  loadingIndicator: true
)
```

## Testing

### Unit Testing

#### 1. Test Connected System
- Use "Test Connection" in Connected System
- Verify authentication works

#### 2. Test Integration
- Use "Test Request" in Integration Object
- Upload a small test file
- Verify response contains `itemID`

#### 3. Test Process Model
- Use "Test Process" in Process Model
- Provide test inputs
- Verify process completes successfully

### Integration Testing

#### 1. End-to-End Test
1. Open your interface
2. Fill in all required fields
3. Upload a test file
4. Click submit button
5. Verify:
   - Process starts successfully
   - File uploads to ArcGIS
   - `itemID` is returned
   - Success message displays

#### 2. Error Testing
1. Test with invalid file types
2. Test with oversized files
3. Test with invalid authentication
4. Verify error handling works

## Troubleshooting

### Common Issues

#### 1. Authentication Failures
**Symptom:** 401 Unauthorized error

**Solutions:**
- Verify token is valid and not expired
- Check token has correct permissions
- Ensure token is passed correctly in request

#### 2. File Upload Fails
**Symptom:** 400 Bad Request or timeout

**Solutions:**
- Check file size is within limits
- Verify multipart/form-data is configured correctly
- Increase timeout in connected system
- Check file format is supported by ArcGIS

#### 3. Process Model Doesn't Start
**Symptom:** Button click has no effect

**Solutions:**
- Verify process model constant is set correctly
- Check process model security settings
- Ensure user has permission to start process
- Check process parameters match variable names

#### 4. Integration Returns Null
**Symptom:** Response parsing fails

**Solutions:**
- Check endpoint URL is correct
- Verify response format matches expected structure
- Check response parsing expression
- Enable logging to see raw response

### Logging and Debugging

#### Enable Integration Logging:
1. Go to Connected System
2. Enable "Log Requests and Responses"
3. Check logs in **Admin Console** > **Logs** > **Integration**

#### Process Model Debugging:
1. Enable "Process History" in process model
2. Use **Monitor** > **Process Instances**
3. Check activity chaining and variable values

## Security Considerations

### 1. Token Management
- Store tokens in sensitive constants
- Rotate tokens regularly
- Don't log tokens in error messages

### 2. File Validation
- Validate file types before upload
- Check file size limits
- Scan for malware if required

### 3. Access Control
- Restrict process model initiation to authorized users
- Implement folder-level security
- Audit file uploads

## Performance Optimization

### 1. Asynchronous Processing
- Use attended/unattended nodes appropriately
- Consider async processing for large files

### 2. Timeout Configuration
- Set appropriate timeouts based on file sizes
- Small files: 30 seconds
- Large files: 300+ seconds

### 3. Error Retry Logic
- Implement retry mechanism for transient failures
- Use exponential backoff

## Next Steps After Upload

The uploaded file is **uncommitted** after upload. To process it:

### 1. Call GP Service with itemID
Create another integration to call the GP service with the returned `itemID`:

```yaml
Endpoint: /Nparks/DWGtoPolygonFeatureClassConversion/GPServer/DWGtoPolygonConversion/submitJob
Method: POST
Parameters:
  - inputFile: [itemID from upload]
  - f: json
  - token: [auth token]
```

### 2. Monitor Job Status
Poll the job status endpoint:

```yaml
Endpoint: /Nparks/DWGtoPolygonFeatureClassConversion/GPServer/DWGtoPolygonConversion/jobs/[jobID]
Method: GET
```

### 3. Retrieve Results
Once job completes, retrieve the results from the output parameters.

## Support and Resources

### Appian Documentation
- [Connected Systems](https://docs.appian.com/suite/help/latest/Connected_Systems.html)
- [Integration Objects](https://docs.appian.com/suite/help/latest/Integration_Object.html)
- [Process Models](https://docs.appian.com/suite/help/latest/Process_Models.html)

### ArcGIS REST API Documentation
- [Upload File](https://developers.arcgis.com/rest/services-reference/enterprise/upload.htm)
- [GP Services](https://developers.arcgis.com/rest/services-reference/enterprise/gp-task.htm)

## Summary

You now have a complete implementation for uploading files from Appian to ArcGIS GPServer:

1. ✅ Connected System for ArcGIS authentication
2. ✅ Integration Object for file upload
3. ✅ Process Model for orchestration
4. ✅ Interface button integration
5. ✅ Error handling and logging
6. ✅ Testing procedures

The `itemID` returned from the upload can be used in subsequent GP service calls to process the file.
