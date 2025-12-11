# LayerFactory Setup Guide

## Overview

All the LayerFactory files have been created with placeholder implementations. Now you need to integrate them with your existing application.

## Current Status: ✅ Files Created, 🔧 Integration Needed

## Step-by-Step Integration

### Step 1: Fix Import Paths in Wrapper/Functions Files

The following files currently have placeholder implementations and need to be updated to import from your actual application:

#### 1.1 `wrapper/ajax.js`
**Current**: Placeholder Ajax implementation
**Action Needed**: 
- Find your actual Ajax utility file (probably in `src/Utils/ajax.js` or similar)
- Update the import:
```javascript
// Replace placeholder with:
import Ajax from 'Utils/ajax';
export default Ajax;
```

#### 1.2 `functions/util.js`
**Current**: Placeholder utility functions
**Action Needed**:
- Find your actual utility functions file (probably in `src/Utils/helpers.js` or similar)
- Update the imports:
```javascript
import {
    appendUrlWithParams,
    generateCSVString,
    reversePolygonLatLng,
    getFeatureCenter,
    isInt,
    logout,
    reproject,
    buildToDeployServer,
    sqmToSqkm,
    polygonsToMultiPolygon,
    convertSquareMetersToHa,
    initDevEnv,
    arrayToList,
    getGeospaceToken
} from 'Utils/helpers';  // Adjust path as needed

export { /* all functions */ };
```

#### 1.3 `functions/layer.js`
**Current**: Minimal placeholder Layer class
**Action Needed**:
- The layer.js file you provided earlier appears to be your actual Layer class
- Copy your actual Layer class into this file, OR
- Import and re-export it from its actual location:
```javascript
import Layer from 'path/to/your/actual/Layer';
export default Layer;
```

#### 1.4 `constants/urlconstants.js`
**Current**: Placeholder URLs
**Action Needed**:
- Update with actual ArcGIS server URLs:
```javascript
import UrlConstants from 'Constants/urlconstants';
export const ControllerUrl = UrlConstants.ControllerUrl;
export default UrlConstants;
```

#### 1.5 `constants/aggregationconstants.js`
**Current**: Placeholder constants
**Action Needed**:
- Update with actual planning areas and land use types:
```javascript
import { Aggregations, PlanningArea, LandUseType } from 'Constants/aggregationconstants';
export { Aggregations, PlanningArea, LandUseType };
```

### Step 2: Configure OneTool Map Data

**File**: `onetool.js`

**Action Needed**:
Replace the placeholder with your actual layer configuration:

```javascript
const OneToolMapData = [
    {
        category: "Planning",
        icon: "map",
        iconColor: "blue",
        isInfra: false,
        layers: [
            {
                name: "MP19 Land Use",
                class: "mp19landuselayer",
                src: "https://your-arcgis-server.com/arcgis/rest/services/Planning/MapServer",
                layers: [0],
                identifyid: [0],
                legend: [0],
                queryId: 0
            },
            // Add more layers...
        ]
    },
    // Add more categories...
];

export default OneToolMapData;
```

### Step 3: Implement Entity Layers

The following entity layer files have been created as stubs. Implement them based on `mp19landuselayer.js` as a template:

- `entities/parkscorelayer.js`
- `entities/salessitelayer.js`
- `entities/rentalofstatelandlayer.js`
- `entities/retaildensitylayer.js`

**Template to follow**:
```javascript
import Layer from '../functions/layer';
import WebApi from '../WebApi';
import Ajax from "../wrapper/ajax";
// ... other imports

export default class YourLayer extends Layer {
    constructor(opts, token) {
        super(opts, token);
        // Initialize your layer
    }

    getFilterbox() {
        // Return React component for filters
    }

    getInfographics(featureCollection) {
        // Return charts/visualizations
    }

    // Add other methods as needed
}
```

### Step 4: Update ConfigStoreInt

**File**: `functions/util.js`

**Action Needed**:
Make sure `ConfigStoreInt` is properly initialized:

```javascript
export const ConfigStoreInt = {
    export: false,
    server: '',  // Will be set by setupDevelopmentEnvs()
    sr: 4326,    // Spatial reference
    environment: 'EXTRANET'
};
```

### Step 5: Test the Integration

1. **Start your development server**
   ```bash
   npm start
   ```

2. **Open browser console** and check for:
   - ✅ No import errors
   - ✅ `window.LayerFactory` is defined
   - ✅ No 404 errors for ePlanner URLs (should be gone)

3. **Test LayerFactory**:
   ```javascript
   // In browser console:
   console.log('LayerFactory:', window.LayerFactory);
   console.log('LayerFactory available:', !!window.LayerFactory);
   ```

4. **Navigate to Overlays menu** and verify:
   - Layers are displayed
   - Layers can be selected/unselected
   - Filters work correctly
   - Identify/query works

### Step 6: Troubleshooting

#### Error: "Cannot find module 'Utils/ajax'"
**Solution**: Update the import path in `wrapper/ajax.js` to match your project structure.

#### Error: "Cannot find module 'Constants/urlconstants'"
**Solution**: Update the import path in `constants/urlconstants.js` to match your project structure.

#### Error: "ConfigStoreInt.sr is undefined"
**Solution**: Ensure `setupDevelopmentEnvs()` is called in `Overlays.js` before `getLayers()`.

#### Error: "Aggregations is not defined"
**Solution**: Update `constants/aggregationconstants.js` with actual values from your application.

#### Layers not displaying
**Solution**: 
1. Check `onetool.js` configuration
2. Verify ArcGIS server URLs are correct
3. Check user has valid ArcGIS token

#### Filters not working
**Solution**:
1. Verify utility functions in `functions/util.js` are properly imported
2. Check Ajax wrapper is working correctly
3. Verify layer definitions in `onetool.js`

## Verification Checklist

Before considering the integration complete, verify:

- [ ] All import errors resolved
- [ ] `window.LayerFactory` is available
- [ ] No external ePlanner calls being made
- [ ] Layers load and display correctly
- [ ] Layer selection/deselection works
- [ ] Filter functionality works
- [ ] Identify/query functionality works
- [ ] Legend displays correctly
- [ ] Charts/infographics display (if applicable)
- [ ] No console errors
- [ ] Performance is acceptable

## Next Steps After Integration

1. **Remove external ePlanner code**:
   - Remove any script tags loading from ePlanner
   - Remove `window.$eplannerLoaded` checks
   - Clean up any ePlanner-related code

2. **Optimize**:
   - Replace placeholder functions with actual implementations
   - Add error handling
   - Add loading states
   - Optimize bundle size

3. **Document**:
   - Update team documentation
   - Add comments to custom implementations
   - Document any deviations from original ePlanner behavior

## Support

If you encounter issues:
1. Check browser console for detailed error messages
2. Verify all file paths are correct for your project structure
3. Ensure webpack aliases (`Components`, `Constants`, `Utils`) are configured
4. Check that all required npm packages are installed

## File Structure Reference

```
src/
├── Containers/
│   └── LeftMenu/
│       └── Overlays/
│           ├── Overlays.js (imports LayerFactory)
│           └── Layerfactory/
│               ├── layerfactory.js
│               ├── WebApi.ts
│               ├── onetool.js
│               ├── functions/
│               │   ├── util.js (re-exports from Utils/)
│               │   ├── layer.js (re-exports from your Layer)
│               │   └── configvalidator.ts
│               ├── entities/
│               │   └── *.js (layer implementations)
│               ├── wrapper/
│               │   └── ajax.js (re-exports from Utils/)
│               └── constants/
│                   └── *.js (re-exports from Constants/)
├── Utils/ (your actual utilities)
├── Constants/ (your actual constants)
└── Components/ (your actual components)
```

Good luck with the integration! 🚀
