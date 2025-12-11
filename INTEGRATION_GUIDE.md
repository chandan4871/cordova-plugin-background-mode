# ePlanner LayerFactory Integration Guide

## Overview
This guide explains how to integrate the local LayerFactory instead of loading it from the external ePlanner application.

## Changes Made

### 1. Updated Overlays Component
**File**: `Containers/LeftMenu/Overlays/Overlays.js`

#### Removed:
- Dependency on `window.$eplannerLoaded` flag
- External script loading from ePlanner

#### Added:
```javascript
// Import local LayerFactory
import 'Layerfactory/layerfactory';
import 'Layerfactory/export-styles.css';
```

#### Updated Logic:
- Removed check for `window.$eplannerLoaded`
- Added `layerFactoryReady` state to manage LayerFactory availability
- Updated `useEffect` to initialize LayerFactory when ready
- Added error handling in `getEPlannerOverlays()`

### 2. Created LayerFactory Files

#### Core Files:
1. **`Layerfactory/layerfactory.js`** - Main LayerFactory class with corrected imports
2. **`Layerfactory/WebApi.ts`** - Web API utilities (you provided this)
3. **`Layerfactory/export-styles.css`** - Styles (replaces external CSS)

#### Entity Files:
1. **`Layerfactory/entities/mp19landuselayer.js`** - MP19 Land Use Layer with corrected imports

## Steps to Complete Integration

### Step 1: Remove External ePlanner Loading
Find and remove any code that:
- Loads external scripts from `https://eplanner.gov.sg/`
- Sets `window.$eplannerLoaded = true`
- Waits for ePlanner scripts to load

Example of code to remove:
```javascript
// REMOVE THIS:
const loadEPlannerScripts = () => {
    const script = document.createElement('script');
    script.src = 'https://eplanner.gov.sg/Scripts/js-built/layerfactory.js';
    script.onload = () => {
        window.$eplannerLoaded = true;
    };
    document.body.appendChild(script);
    
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://eplanner.gov.sg/Content/js/js-built/export-cssmin.css';
    document.head.appendChild(link);
};
```

### Step 2: Add Missing Files
You need to create these files in your `Layerfactory` folder:

1. **`Layerfactory/functions/util.js` or `util.ts`**
   - Contains: `ConfigStoreInt`, `arrayToList`, `reversePolygonLatLng`, `sqmToSqkm`, `getFeatureCenter`, `polygonsToMultiPolygon`, `convertSquareMetersToHa`, `buildToDeployServer`, `initDevEnv`, `reproject`, `appendUrlWithParams`, `getGeospaceToken`

2. **`Layerfactory/functions/layer.js`**
   - Base Layer class that all entity layers extend

3. **`Layerfactory/functions/configvalidator.ts`**
   - Contains: `isValidMapConfig`, `getErrorMsgs`, `clearErrorMsgs`

4. **`Layerfactory/wrapper/ajax.js` or `ajax.ts`**
   - Ajax utility wrapper

5. **`onetool.js` or `onetool.ts`** (in parent directory)
   - OneToolMapData configuration

6. **Entity layer files** (in `Layerfactory/entities/`):
   - `parkscorelayer.js`
   - `salessitelayer.js`
   - `rentalofstatelandlayer.js`
   - `retaildensitylayer.js`

### Step 3: Configure Build System

#### Webpack Configuration:
Add alias for Layerfactory path:

```javascript
// webpack.config.js
module.exports = {
    resolve: {
        alias: {
            'Layerfactory': path.resolve(__dirname, 'Layerfactory'),
            'Components': path.resolve(__dirname, 'Components'),
            'Constants': path.resolve(__dirname, 'Constants'),
            'Containers': path.resolve(__dirname, 'Containers'),
            'Store': path.resolve(__dirname, 'Store'),
            'Utils': path.resolve(__dirname, 'Utils'),
        },
        extensions: ['.js', '.jsx', '.ts', '.tsx']
    }
};
```

#### Package.json:
Ensure all required dependencies are installed:

```json
{
  "dependencies": {
    "@mui/material": "^5.x.x",
    "@mui/styles": "^5.x.x",
    "@emotion/react": "^11.x.x",
    "@emotion/cache": "^11.x.x",
    "esri-leaflet": "^3.x.x",
    "esri-loader": "^3.x.x",
    "leaflet": "^1.x.x",
    "react": "^18.x.x",
    "react-dom": "^18.x.x"
  }
}
```

### Step 4: Update Import Paths
Make sure all components that use LayerFactory import it from the local path:

```javascript
// Before:
// Loaded externally via script tag

// After:
import 'Layerfactory/layerfactory';
```

### Step 5: Test the Integration

1. **Verify LayerFactory is available**:
   ```javascript
   console.log('LayerFactory available:', !!window.LayerFactory);
   ```

2. **Test layer loading**:
   - Open the Overlays menu
   - Check if layers are displayed
   - Try selecting/unselecting layers
   - Test filter functionality

3. **Check for errors**:
   - Open browser console
   - Look for any import errors or missing modules
   - Verify no 404 errors for ePlanner URLs

## Benefits of Local Integration

1. **No External Dependencies**: Application works without external ePlanner server
2. **Faster Load Times**: No network calls to load scripts
3. **Version Control**: LayerFactory code is now in your repository
4. **Easier Debugging**: Full access to source code
5. **Customization**: Can modify LayerFactory behavior as needed
6. **No CORS Issues**: All resources are local
7. **Offline Support**: Application can work offline

## Troubleshooting

### Issue: "LayerFactory is not defined"
**Solution**: Check that `layerfactory.js` is properly imported at the top of the component file.

### Issue: Import errors for entity layers
**Solution**: Verify all entity layer files exist and have correct import paths.

### Issue: "Cannot find module 'Layerfactory/...'"
**Solution**: Add webpack alias for Layerfactory path or use relative paths.

### Issue: Styles not applying
**Solution**: Ensure `export-styles.css` is imported and contains necessary styles.

### Issue: WebApi errors
**Solution**: Check that `WebApi.ts` is in the correct location (`Layerfactory/WebApi.ts`) and all its dependencies are available.

## Next Steps

1. Create remaining utility files (`util.js`, `layer.js`, `ajax.js`, etc.)
2. Create remaining entity layer files
3. Test thoroughly in development environment
4. Remove all references to external ePlanner URLs
5. Update documentation for your team
6. Deploy to staging for testing

## Support

If you encounter issues:
1. Check browser console for errors
2. Verify all files are created with correct paths
3. Ensure webpack/build configuration is updated
4. Test with simplified configuration first
