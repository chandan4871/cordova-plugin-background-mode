/**
 * Re-export URL constants from the main application
 * This wrapper allows Layerfactory to use the application's URL constants
 */

// Import from the main application's constants
// Adjust the path based on your actual project structure
// import UrlConstants from 'Constants/urlconstants';

// Placeholder URLs - replace with actual URLs from your application
const UrlConstants = {
    GeoSpaceReverseAddressSearch: '/api/geospace/reverse',
    GrcSearch: '/arcgis/rest/services/GRC/MapServer',
    PlanningAreaSearch: '/arcgis/rest/services/PlanningArea/MapServer',
    SubZoneSearch: '/arcgis/rest/services/SubZone/MapServer',
    PlanningArea19Search: '/arcgis/rest/services/PlanningArea19/MapServer',
    SubZone19Search: '/arcgis/rest/services/SubZone19/MapServer',
};

export const ControllerUrl = {
    DcgAreaOic: '/api/dcg/area/oic',
    LogLayer: '/api/log/layer',
    // Add other controller URLs as needed
};

export default UrlConstants;
