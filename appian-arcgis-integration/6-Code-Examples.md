# Code Examples and Snippets

## Quick Reference for Implementation

### 1. Integration Object Expression Code

#### Request Body Configuration (Multipart Form Data)

In your integration object, the request will be automatically configured as multipart/form-data. Map the following:

**Body Parameters:**
```sail
/* These are configured in the Integration Designer UI */
file: ri!file          /* Type: Document */
f: ri!f                /* Type: Text, default "json" */
token: ri!token        /* Type: Text, your auth token */
```

#### Response Parsing Expression

```sail
/* In the Response tab of Integration Object */
a!fromJson(
  httpResponse.body
)
```

#### Output Mapping

```sail
/* Map parsed response to outputs */
success: response.success
itemID: response.item.itemID
itemName: response.item.itemName
errorMessage: if(
  response.success, 
  null, 
  if(
    isnull(response.error.message),
    "Upload failed - unknown error",
    response.error.message
  )
)
```

### 2. Process Model Smart Service Configuration

#### Integration Node - Input Configuration

```sail
/* Integration Smart Service Inputs */
file: pv!fileToUpload
filename: document(pv!fileToUpload, "name")
token: pv!arcgisToken
f: "json"
```

#### Integration Node - Output Configuration

```sail
/* Save integration results to process variables */
pv!uploadSuccess = ac!success
pv!arcgisItemID = ac!itemID
pv!arcgisItemName = ac!itemName
pv!errorMessage = ac!errorMessage
```

#### XOR Gateway Decision Expression

```sail
/* Route based on success */
=pv!uploadSuccess
```

### 3. Interface SAIL Code Examples

#### Complete File Upload Field

```sail
a!fileUploadField(
  label: "Upload DWG File",
  instructions: "Select a DWG file to upload to ArcGIS for conversion",
  target: cons!ARCGIS_UPLOAD_FOLDER,
  maxSelections: 1,
  value: ri!uploadedDocument,
  saveInto: ri!uploadedDocument,
  validations: {
    if(
      isnull(ri!uploadedDocument),
      "Please upload a file before submitting",
      {}
    ),
    if(
      not(
        contains(
          {"dwg", "dxf"},
          lower(document(ri!uploadedDocument, "extension"))
        )
      ),
      "Only DWG and DXF files are supported",
      {}
    )
  },
  required: true
)
```

#### Button with Process Start

```sail
a!buttonWidget(
  label: "Submit and Upload to ArcGIS",
  value: "submit",
  saveInto: {
    /* Save your form data to rule inputs */
    a!save(ri!buttonAction, "submit"),
    a!save(ri!fileSource, local!selectedFileSource),
    a!save(ri!fileType, local!selectedFileType),
    a!save(ri!description, local!currentDescription),
    a!save(ri!accessRights, local!currentAccessRights),
    a!save(ri!otherFileSourceText, local!otherFileSourceText),
    a!save(ri!otherFileTypeText, local!otherFileTypeText),
    a!save(ri!otherDocCategoryId, local!otherDocCategoryId),
    
    /* Start the upload process */
    a!startProcess(
      processModel: cons!PM_UPLOAD_FILE_TO_ARCGIS,
      processParameters: {
        fileToUpload: ri!uploadedDocument,
        fileSource: ri!fileSource,
        fileType: ri!fileType,
        description: ri!description,
        accessRights: ri!accessRights,
        otherFileSourceText: ri!otherFileSourceText,
        otherFileTypeText: ri!otherFileTypeText,
        otherDocCategoryId: ri!otherDocCategoryId,
        arcgisToken: cons!ARCGIS_AUTH_TOKEN
      },
      onSuccess: {
        a!save(local!uploadStatus, "success"),
        a!save(
          local!successMessage, 
          "File uploaded successfully to ArcGIS!"
        )
      },
      onError: {
        a!save(local!uploadStatus, "error"),
        a!save(
          local!errorMessage,
          "Upload failed: " & fv!error
        )
      }
    )
  },
  submit: true,
  style: "SOLID",
  color: "#38761d",
  loadingIndicator: true,
  disabled: or(
    isnull(ri!uploadedDocument),
    isnull(local!selectedFileSource),
    isnull(local!selectedFileType)
  )
)
```

#### Status Display Banner

```sail
a!columnsLayout(
  columns: {
    a!columnLayout(
      contents: {
        /* Success Banner */
        a!cardLayout(
          contents: {
            a!richTextDisplayField(
              value: {
                a!richTextIcon(
                  icon: "check-circle",
                  color: "POSITIVE",
                  size: "MEDIUM"
                ),
                " ",
                a!richTextItem(
                  text: local!successMessage,
                  color: "POSITIVE",
                  size: "MEDIUM",
                  style: "STRONG"
                )
              }
            )
          },
          height: "AUTO",
          style: "SUCCESS",
          marginBelow: "STANDARD"
        )
      },
      showWhen: local!uploadStatus = "success"
    ),
    a!columnLayout(
      contents: {
        /* Error Banner */
        a!cardLayout(
          contents: {
            a!richTextDisplayField(
              value: {
                a!richTextIcon(
                  icon: "exclamation-triangle",
                  color: "NEGATIVE",
                  size: "MEDIUM"
                ),
                " ",
                a!richTextItem(
                  text: local!errorMessage,
                  color: "NEGATIVE",
                  size: "MEDIUM",
                  style: "STRONG"
                )
              }
            )
          },
          height: "AUTO",
          style: "ERROR",
          marginBelow: "STANDARD"
        )
      },
      showWhen: local!uploadStatus = "error"
    )
  }
)
```

### 4. Alternative: Direct Integration Call (No Process Model)

If you want to call the integration directly from the interface without a process model:

```sail
a!buttonWidget(
  label: "Upload to ArcGIS",
  saveInto: {
    /* Call integration directly */
    a!save(
      local!integrationResult,
      rule!INT_ArcGIS_UploadFile(
        file: ri!uploadedDocument,
        token: cons!ARCGIS_AUTH_TOKEN,
        f: "json"
      )
    ),
    
    /* Handle the result */
    if(
      local!integrationResult.success,
      {
        a!save(local!uploadSuccess, true),
        a!save(local!arcgisItemID, local!integrationResult.itemID),
        a!save(
          local!successMessage,
          "File uploaded successfully! Item ID: " & local!integrationResult.itemID
        )
      },
      {
        a!save(local!uploadSuccess, false),
        a!save(
          local!errorMessage,
          "Upload failed: " & local!integrationResult.errorMessage
        )
      }
    )
  },
  submit: true,
  style: "SOLID",
  loadingIndicator: true
)
```

### 5. curl Command for Testing

Test your ArcGIS endpoint before implementing in Appian:

```bash
#!/bin/bash

# Variables
ARCGIS_URL="https://server.nparks.dev.sgps/arcgis/rest/services/Nparks/DWGtoPolygonFeatureClassConversion/GPServer/uploads/upload"
FILE_PATH="/path/to/your/file.dwg"
TOKEN="your_arcgis_token_here"

# Upload file
curl -X POST "$ARCGIS_URL" \
  -F "file=@$FILE_PATH" \
  -F "f=json" \
  -F "token=$TOKEN" \
  -v

# Expected successful response:
# {
#   "success": true,
#   "item": {
#     "itemID": "i12345678-1234-1234-1234-123456789012",
#     "itemName": "file.dwg",
#     "description": "",
#     "date": 1732454400000,
#     "committed": false
#   }
# }
```

### 6. Expression Rule for File Validation

Create a reusable expression rule: `rule!NMC_validateFileForArcGIS`

```sail
a!localVariables(
  local!extension: lower(document(ri!file, "extension")),
  local!size: document(ri!file, "size"),
  local!maxSize: 52428800, /* 50 MB in bytes */
  
  local!validExtensions: {"dwg", "dxf", "shp"},
  
  local!errors: reject(
    fn!isnull,
    {
      if(
        isnull(ri!file),
        "File is required",
        null
      ),
      if(
        not(contains(local!validExtensions, local!extension)),
        "File must be DWG, DXF, or SHP format",
        null
      ),
      if(
        local!size > local!maxSize,
        "File size must be less than 50 MB",
        null
      )
    }
  ),
  
  /* Return validation result */
  if(
    length(local!errors) > 0,
    {
      valid: false,
      errors: local!errors
    },
    {
      valid: true,
      errors: {}
    }
  )
)
```

**Usage in Interface:**

```sail
a!fileUploadField(
  label: "Upload File",
  target: cons!ARCGIS_UPLOAD_FOLDER,
  value: ri!uploadedDocument,
  saveInto: {
    ri!uploadedDocument,
    a!save(
      local!fileValidation,
      rule!NMC_validateFileForArcGIS(file: ri!uploadedDocument)
    )
  },
  validations: if(
    local!fileValidation.valid,
    {},
    local!fileValidation.errors
  )
)
```

### 7. Error Handling in Process Model

#### Write to Database Entity (Error Log)

```sail
/* In a Write to Data Store Entity node */
Entity: NMC_ErrorLog

Data:
{
  errorType: "ARCGIS_UPLOAD_FAILURE",
  errorMessage: pv!errorMessage,
  fileName: document(pv!fileToUpload, "name"),
  fileSize: document(pv!fileToUpload, "size"),
  userId: pp!initiator,
  timestamp: now(),
  processInstanceId: pp!id,
  additionalInfo: {
    fileSource: pv!fileSource,
    fileType: pv!fileType
  }
}
```

#### Send Error Notification Email

```sail
/* In a Send E-Mail smart service node */
To: cons!ADMIN_EMAIL
Subject: "ArcGIS File Upload Failed - " & document(pv!fileToUpload, "name")
Body: "File upload to ArcGIS failed.

Details:
- File: " & document(pv!fileToUpload, "name") & "
- Size: " & document(pv!fileToUpload, "size") & " bytes
- User: " & user(pp!initiator, "displayName") & "
- Time: " & text(now(), "mmm dd, yyyy hh:mm AM/PM") & "
- Error: " & pv!errorMessage & "

Process Instance: " & pp!id
```

### 8. Constants to Create

```sail
/* In Appian Admin Console > Constants */

cons!ARCGIS_BASE_URL
Type: Text
Value: https://server.nparks.dev.sgps/arcgis/rest/services

cons!ARCGIS_AUTH_TOKEN
Type: Text (Sensitive)
Value: [Your ArcGIS Token]

cons!ARCGIS_UPLOAD_FOLDER
Type: Folder
Value: [Select folder]

cons!PM_UPLOAD_FILE_TO_ARCGIS
Type: Process Model
Value: [Select process model]

cons!ADMIN_EMAIL
Type: Text
Value: admin@yourdomain.com

cons!ARCGIS_MAX_FILE_SIZE_MB
Type: Number (Integer)
Value: 50
```

### 9. Database Schema for Upload Tracking

Create a data type: `NMC_ArcGISUploadLog`

```sql
-- Fields
id (Number - Integer, Primary Key, Auto-increment)
documentId (Number - Integer) -- Appian document ID
arcgisItemId (Text) -- ArcGIS returned itemID
fileName (Text)
fileSize (Number - Integer)
fileType (Text)
fileSource (Number - Integer)
uploadStatus (Text) -- "success" or "failed"
errorMessage (Text)
uploadedBy (User)
uploadTimestamp (Date and Time)
processInstanceId (Number - Integer)
```

### 10. Complete Interface Example

```sail
a!formLayout(
  label: "Upload File to ArcGIS",
  contents: {
    a!sectionLayout(
      label: "File Information",
      contents: {
        a!fileUploadField(
          label: "Select File",
          instructions: "Upload DWG, DXF, or SHP file",
          target: cons!ARCGIS_UPLOAD_FOLDER,
          maxSelections: 1,
          value: ri!uploadedDocument,
          saveInto: ri!uploadedDocument,
          required: true
        ),
        a!dropdownField(
          label: "File Source",
          choiceLabels: local!fileSourceData.displayValue,
          choiceValues: local!fileSourceData.pId,
          value: local!selectedFileSource,
          saveInto: local!selectedFileSource,
          required: true
        ),
        a!dropdownField(
          label: "File Type",
          choiceLabels: local!fileTypeData.displayValue,
          choiceValues: local!fileTypeData.pId,
          value: local!selectedFileType,
          saveInto: local!selectedFileType,
          required: true
        ),
        a!textField(
          label: "Description",
          value: local!currentDescription,
          saveInto: local!currentDescription,
          characterLimit: 500
        ),
        a!textField(
          label: "Access Rights",
          value: local!currentAccessRights,
          saveInto: local!currentAccessRights
        )
      }
    ),
    
    /* Status Display */
    a!columnsLayout(
      columns: {
        a!columnLayout(
          contents: {
            a!cardLayout(
              contents: {
                a!richTextDisplayField(
                  value: {
                    a!richTextIcon(
                      icon: "check-circle",
                      color: "POSITIVE"
                    ),
                    " ",
                    a!richTextItem(
                      text: "File uploaded successfully!",
                      color: "POSITIVE",
                      style: "STRONG"
                    )
                  }
                )
              },
              style: "SUCCESS",
              showWhen: local!uploadStatus = "success"
            ),
            a!cardLayout(
              contents: {
                a!richTextDisplayField(
                  value: {
                    a!richTextIcon(
                      icon: "exclamation-triangle",
                      color: "NEGATIVE"
                    ),
                    " ",
                    a!richTextItem(
                      text: local!errorMessage,
                      color: "NEGATIVE",
                      style: "STRONG"
                    )
                  }
                )
              },
              style: "ERROR",
              showWhen: local!uploadStatus = "error"
            )
          }
        )
      }
    )
  },
  buttons: a!buttonLayout(
    primaryButtons: {
      a!buttonWidget(
        label: cons!NMC_TEXT_BUTTON_NAMES[9],
        value: cons!NMC_TEXT_BUTTON_NAMES[9],
        saveInto: {
          a!save(ri!buttonAction, cons!NMC_TEXT_BUTTON_NAMES[9]),
          a!save(ri!fileSource, local!selectedFileSource),
          a!save(ri!fileType, local!selectedFileType),
          a!save(ri!description, local!currentDescription),
          a!save(ri!accessRights, local!currentAccessRights),
          
          /* Your existing file source/type logic */
          if(
            a!isNotNullOrEmpty(local!otherFileSourceText),
            a!save(ri!otherFileSourceText, local!otherFileSourceText),
            {}
          ),
          if(
            a!isNotNullOrEmpty(local!otherFileTypeText),
            a!save(ri!otherFileTypeText, local!otherFileTypeText),
            {}
          ),
          a!save(ri!otherDocCategoryId, local!otherDocCategoryId),
          
          /* Start ArcGIS upload process */
          a!startProcess(
            processModel: cons!PM_UPLOAD_FILE_TO_ARCGIS,
            processParameters: {
              fileToUpload: ri!uploadedDocument,
              fileSource: local!selectedFileSource,
              fileType: local!selectedFileType,
              description: local!currentDescription,
              accessRights: local!currentAccessRights,
              otherFileSourceText: local!otherFileSourceText,
              otherFileTypeText: local!otherFileTypeText,
              otherDocCategoryId: local!otherDocCategoryId,
              arcgisToken: cons!ARCGIS_AUTH_TOKEN
            },
            onSuccess: {
              a!save(local!uploadStatus, "success")
            },
            onError: {
              a!save(local!uploadStatus, "error"),
              a!save(local!errorMessage, fv!error)
            }
          )
        },
        submit: true,
        style: "SOLID",
        color: "#38761d",
        loadingIndicator: true,
        disabled: or(
          isnull(ri!uploadedDocument),
          isnull(local!selectedFileSource),
          isnull(local!selectedFileType)
        )
      )
    },
    secondaryButtons: {
      a!buttonWidget(
        label: "Cancel",
        value: "cancel",
        saveInto: a!save(ri!buttonAction, "cancel"),
        style: "OUTLINE"
      )
    }
  )
)
```

## Summary

These code examples provide ready-to-use snippets for implementing the ArcGIS file upload integration in Appian. Copy and adapt them to your specific needs, ensuring you replace placeholder values with your actual constants and configurations.
