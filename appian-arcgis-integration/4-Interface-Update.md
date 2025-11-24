# Interface Update to Trigger File Upload Process

## Overview
Update your button widget to trigger the process model that uploads files to ArcGIS.

## Step 1: Add Process Model Rule Input

In your interface, add a new rule input:

```sail
ri!processModel (Process Model)
  - Default: cons!PM_UPLOAD_FILE_TO_ARCGIS
```

## Step 2: Update Button Widget

### Original Button Code (Your Current Implementation):
Your button currently saves data to rule inputs. We need to modify it to also trigger the process model.

### Updated Button Code:

```sail
primaryButtons: {
  a!buttonWidget(
    label: cons!NMC_TEXT_BUTTON_NAMES[9],
    value: cons!NMC_TEXT_BUTTON_NAMES[9],
    saveInto: {
      /* Save all your existing data */
      ri!buttonAction,
      a!save(ri!fileSource, local!selectedFileSource),
      a!save(ri!fileType, local!selectedFileType),
      a!save(ri!description, local!currentDescription),
      a!save(ri!accessRights, local!currentAccessRights),
      
      /* File source logic */
      if(
        a!isNotNullOrEmpty(local!otherFileSourceText),
        a!save(ri!fileSource, local!selectedFileSource),
        a!save(
          ri!otherFileSourceText,
          index(
            local!fileSourceData,
            wherecontains(
              local!selectedFileSource,
              local!fileSourceData['recordType!{5e01b380-2070-4fcb-b0c4-74064b646c96}NMC Lookup Data.fields.{9239246a-6dbf-4827-b911-3a662bf90d7e}pId']
            ),
            {}
          )['recordType!{5e01b380-2070-4fcb-b0c4-74064b646c96}NMC Lookup Data.fields.{4630b0f0-0be5-4dce-acd4-608a7cda35e4}displayValue']
        )
      ),
      
      /* Other file source text */
      if(
        a!isNotNullOrEmpty(local!otherFileSourceText),
        a!save(ri!otherFileSourceText, local!otherFileSourceText),
        a!save(
          ri!otherFileTypeText,
          index(
            local!fileTypeData,
            wherecontains(
              tointeger(local!selectedFileType),
              local!fileTypeData['recordType!{5e01b380-2070-4fcb-b0c4-74064b646c96}NMC Lookup Data.fields.{9239246a-6dbf-4827-b911-3a662bf90d7e}pId']
            ),
            {}
          )['recordType!{5e01b380-2070-4fcb-b0c4-74064b646c96}NMC Lookup Data.fields.{4630b0f0-0be5-4dce-acd4-608a7cda35e4}displayValue']
        )
      ),
      
      /* File type logic */
      if(
        a!isNotNullOrEmpty(local!otherFileTypeText),
        a!save(ri!fileType, local!selectedFileType),
        {}
      ),
      
      /* Other file type text */
      if(
        a!isNotNullOrEmpty(local!otherFileTypeText),
        a!save(ri!otherFileTypeText, local!otherFileTypeText),
        {}
      ),
      
      a!save(ri!otherDocCategoryId, local!otherDocCategoryId),
      
      /* ===== NEW: Start Process Model to Upload to ArcGIS ===== */
      a!startProcess(
        processModel: cons!PM_UPLOAD_FILE_TO_ARCGIS,
        processParameters: {
          fileToUpload: ri!uploadedDocument,  /* Your file upload field */
          fileSource: local!selectedFileSource,
          fileType: local!selectedFileType,
          description: local!currentDescription,
          accessRights: local!currentAccessRights,
          otherFileSourceText: local!otherFileSourceText,
          otherFileTypeText: local!otherFileTypeText,
          otherDocCategoryId: local!otherDocCategoryId,
          arcgisToken: cons!ARCGIS_AUTH_TOKEN  /* Create this constant */
        },
        onSuccess: a!save(
          local!uploadStatus,
          "File uploaded successfully to ArcGIS"
        ),
        onError: a!save(
          local!uploadError,
          "Failed to upload file to ArcGIS: " & fv!error
        )
      )
    },
    submit: true,
    style: "SOLID",
    color: "#38761d",
    loadingIndicator: true
  )
}
```

## Step 3: Add File Upload Field (if not present)

Ensure your interface has a file upload field:

```sail
a!fileUploadField(
  label: "Upload File",
  labelPosition: "ABOVE",
  target: cons!ARCGIS_UPLOAD_FOLDER,  /* Create a constant for upload folder */
  maxSelections: 1,
  value: ri!uploadedDocument,
  saveInto: ri!uploadedDocument,
  validations: {
    if(
      isnull(ri!uploadedDocument),
      "Please upload a file",
      null
    )
  },
  required: true
)
```

## Step 4: Add Status Display (Optional)

Add a section to show upload status:

```sail
a!sectionLayout(
  label: "Upload Status",
  contents: {
    a!textField(
      label: "Status",
      value: if(
        a!isNotNullOrEmpty(local!uploadStatus),
        local!uploadStatus,
        if(
          a!isNotNullOrEmpty(local!uploadError),
          local!uploadError,
          "Ready to upload"
        )
      ),
      readOnly: true,
      labelPosition: "ADJACENT"
    )
  },
  showWhen: or(
    a!isNotNullOrEmpty(local!uploadStatus),
    a!isNotNullOrEmpty(local!uploadError)
  )
)
```

## Alternative: Direct Integration Call (Without Process Model)

If you prefer to call the integration directly from the interface:

```sail
primaryButtons: {
  a!buttonWidget(
    label: cons!NMC_TEXT_BUTTON_NAMES[9],
    saveInto: {
      /* Your existing saveInto logic here */
      
      /* Direct integration call */
      a!save(
        local!arcgisResponse,
        rule!INT_ArcGIS_UploadFile(
          file: ri!uploadedDocument,
          filename: document(ri!uploadedDocument, "name"),
          token: cons!ARCGIS_AUTH_TOKEN,
          f: "json"
        )
      ),
      
      /* Handle response */
      if(
        local!arcgisResponse.success,
        {
          a!save(local!uploadStatus, "Success!"),
          a!save(local!arcgisItemID, local!arcgisResponse.itemID)
        },
        a!save(local!uploadError, local!arcgisResponse.errorMessage)
      )
    },
    submit: true,
    style: "SOLID",
    color: "#38761d",
    loadingIndicator: true
  )
}
```

## Required Constants

Create these constants in Appian:

```yaml
cons!PM_UPLOAD_FILE_TO_ARCGIS
  - Type: Process Model
  - Value: [Select your process model]

cons!ARCGIS_AUTH_TOKEN
  - Type: Text
  - Value: [Your ArcGIS token or leave empty if using OAuth in connected system]

cons!ARCGIS_UPLOAD_FOLDER
  - Type: Folder
  - Value: [Select upload folder]
```

## Important Notes:

1. **File Size Limits**: ArcGIS has upload size limits - check with your admin
2. **Authentication**: Ensure token is valid and not expired
3. **Error Handling**: Always handle errors gracefully
4. **User Feedback**: Show loading indicators and success/error messages

## Next Steps:
Test the complete flow end-to-end with a sample file.
