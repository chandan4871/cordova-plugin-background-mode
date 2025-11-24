# Process Model Configuration for ArcGIS File Upload

## Overview
This process model receives a file from your interface and uploads it to ArcGIS.

## Step 1: Create Process Model

### In Appian Designer:
1. Navigate to **Build** > **Process Models**
2. Click **Create New Process Model**
3. Name it: `PM_UploadFileToArcGIS`

## Step 2: Configure Process Variables

### Input Variables:
```sail
pv!fileToUpload (Document)
  - Description: The document to upload to ArcGIS
  - Multiple: false

pv!fileSource (Number(Integer))
  - Description: File source ID from your form

pv!fileType (Number(Integer))
  - Description: File type ID from your form

pv!description (Text)
  - Description: File description

pv!accessRights (Text)
  - Description: Access rights information

pv!otherFileSourceText (Text)
  - Description: Other file source text if applicable

pv!otherFileTypeText (Text)
  - Description: Other file type text if applicable

pv!otherDocCategoryId (Number(Integer))
  - Description: Other document category ID

pv!arcgisToken (Text)
  - Description: ArcGIS authentication token (optional, configure in connected system)
```

### Output Variables:
```sail
pv!uploadSuccess (Boolean)
  - Description: Whether the upload was successful

pv!arcgisItemID (Text)
  - Description: The ArcGIS item ID of the uploaded file

pv!errorMessage (Text)
  - Description: Error message if upload failed
```

## Step 3: Add Integration Node

### Node Configuration:

1. **Add a Smart Service Node**
   - Drag **Integration** smart service onto the process flow

2. **Node Name**: `Upload File to ArcGIS`

3. **Integration Selection**:
   - Select: `INT_ArcGIS_UploadFile`

4. **Input Mapping**:
   ```sail
   file: pv!fileToUpload
   filename: document(pv!fileToUpload, "name")
   token: pv!arcgisToken
   f: "json"
   ```

5. **Output Mapping**:
   ```sail
   pv!uploadSuccess = ac!success
   pv!arcgisItemID = ac!itemID
   pv!errorMessage = ac!errorMessage
   ```

6. **Node Properties**:
   - **Assignment**: Attend (or unattended if no user interaction needed)
   - **Exception Flow**: Add error handling

## Step 4: Add Error Handling

### Add XOR Gateway after Integration Node:

**Condition 1: Success**
```sail
pv!uploadSuccess = true
```
→ Continue to next step or end node

**Condition 2: Failure**
```sail
pv!uploadSuccess = false
```
→ Route to error handling node

### Error Handling Node Options:

1. **Send Error Notification**
   - Use "Send E-Mail" smart service
   - Notify administrators

2. **Log Error**
   - Write to database or log table

3. **User Task for Retry**
   - Allow user to retry upload

## Step 5: Optional - Save Metadata

Add a node to save the uploaded file metadata to your database:

```sail
Node Name: Save File Metadata
Type: Write to Data Store Entity

Inputs:
  - fileSource: pv!fileSource
  - fileType: pv!fileType
  - description: pv!description
  - accessRights: pv!accessRights
  - arcgisItemID: pv!arcgisItemID
  - uploadDate: now()
  - uploadedBy: loggedInUser()
```

## Complete Process Flow:

```
[Start Node]
    ↓
[Upload File to ArcGIS]
    ↓
[XOR Gateway: Check Success]
    ├─ [Success] → [Save Metadata] → [End Node]
    └─ [Failure] → [Error Handler] → [End Node]
```

## Process Model Properties:

```yaml
Security: 
  - Viewer: [Your user groups]
  - Initiator: [Groups that can start the process]

Alerts & Notifications:
  - Enable process alerts
  - Configure SLA if needed

Process Start Form:
  - None (called from interface)
```

## Next Steps:
Update your interface to call this process model.
