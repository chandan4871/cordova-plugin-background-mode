import Scrollbar from 'perfect-scrollbar-react';
import React, { Suspense, useState, useMemo, useEffect } from 'react';
import { TabContent, TabPane, Nav, NavItem, TabContainer } from 'react-bootstrap';
import { useSelector, useDispatch } from 'react-redux';
import { List, ListItem, ListItemText, Typography } from '@mui/material';
import DeleteForever from '@mui/icons-material/DeleteForever';
import DeleteSweep from '@mui/icons-material/DeleteSweep';
import IconButton from '@mui/material/IconButton';

import FilterBox from 'Components/Shared/FilterBox';
import { LogToACMAudit } from 'Constants/AuditConfig';
import { mapWrapper, layerWrapper, GetMessenger } from 'Constants/ePlanner';
import GenerateMenuFromProps from 'Containers/LeftMenu/Overlays/Menus';
import { selectOverlay, unselectOverlay, clearOverlays, getIdentifyOverlayResult } from 'Store/Actions/Overlay';
import { updateRefreshEPlanner } from 'Store/Actions/Variables';

// Import local LayerFactory instead of loading from external ePlanner
import 'Containers/LeftMenu/Overlays/Layerfactory/layerfactory';
// Import the CSS styles
import 'Containers/LeftMenu/Overlays/Layerfactory/export-css';

import './Overlays.css';
import { loadESRIModules } from 'Constants/Helpers/mapHelpers';
import { URL_InsertModuleUsageLog } from "Constants/API";
import { axiosInstance } from "Utils/axios";

const TAB_HEADER_STYLE = {
    width: '50%',
    height: '100%'
};

const GenerateOverlayMenu = ({ openDashboard }) => {
    const currentOverlays = useSelector(state => state.overlays);// this is the name from the combine reducers
    const mapView = useSelector(state => state.mapView);
    const userInfo = useSelector(state => state.authentication.user);
    const appConfig = useSelector(state => state.configuration.appConfig);

    const dispatch = useDispatch();

    const [filterOpened, setFilterOpened] = useState(true);
    const [overlaysList, setOverlaysList] = useState([]);
    const [layerFactoryReady, setLayerFactoryReady] = useState(false);

    const logModuleUsage = (inputOverlayName, inputOverlaySource) => {
        let form = new FormData();
        form.append("OFFICER_EMAIL", userInfo["Email"]);
        form.append("OFFICER_AGENCY", userInfo["AgencyName"]);
        form.append("ONETOOL_MODULE", "OVERLAYS");
        form.append("ADDITIONAL_INFO", inputOverlayName + "; [" + new URL(inputOverlaySource).pathname + "]");
        axiosInstance.post(URL_InsertModuleUsageLog, form);
    }

    const overlaySelectedHandler = (overlay, addToMap) => {
        if (addToMap) {
            dispatch(selectOverlay(overlay, mapView));
            LogToACMAudit(userInfo.Email, "OVERLAYS", "300001", overlay.opts.name || overlay.opts.label);
            
            if (overlay.opts.hasOwnProperty('label')) {
                overlay.opts.name = overlay.opts.label;
            }
            logModuleUsage(overlay.opts.name, overlay.opts.src);
        } else {
            dispatch(unselectOverlay(overlay, mapView));
        }
    }

    const clearOverlaysHandler = () => {
        dispatch(clearOverlays(mapView, currentOverlays.selectedOverlays));
    }

    const refreshEPlannerResultsDispatch = () => {
        dispatch(updateRefreshEPlanner());
    }

    const getIdentifyOverlayResultDispatch = (layer) => {
        dispatch(getIdentifyOverlayResult(layer));
    }

    const navs = useMemo(() => (
        <Nav variant="tabs" className="overlayTabs">
            <NavItem style={TAB_HEADER_STYLE}>
                <Nav.Link eventKey="1">
                    <Typography variant="h6">{`All`}</Typography>
                </Nav.Link>
            </NavItem>
            <NavItem style={TAB_HEADER_STYLE}>
                <Nav.Link eventKey="2">
                    <Typography variant="h6">{`Selected`}{<span>&nbsp;({currentOverlays.counter})</span>}</Typography>
                </Nav.Link>
            </NavItem>
        </Nav>
    ), [currentOverlays.selectedOverlays])

    const reversePolygonLatLng = (obj) => {
        let geometry;
        let type = obj.type;
        let switchFunc = coordinates => {
            return [coordinates[1], coordinates[0]];
        };

        if (type === 'Point') {
            geometry = switchFunc(obj.coordinates);
        } else {
            geometry = obj.coordinates.map((region, i) => {
                switch (type) {
                    case 'Line':
                        return switchFunc(region);
                        break;
                    case 'LineString':
                    case 'MultiPoint':
                        return switchFunc(region);
                        break;
                    case 'Polygon':
                        return region.map(switchFunc);
                        break;
                    case 'MultiLine':
                    case 'MultiLineString':  //bad code example of allowing switch fall through
                        return region.map(coordinates => {
                            return switchFunc(coordinates);
                        });
                        break;
                    case 'MultiPolygon':
                        return region.map(switchFunc);
                        break;
                }
            });
        }

        return {
            coordinates: geometry,
            type: type
        }
    }

    const getEPlannerOverlays = async () => {
        // Check if LayerFactory is available (loaded from local file)
        if (window.LayerFactory && mapView && overlaysList.length === 0) {
            try {
                const mapWrap = mapWrapper(mapView.map, mapView);
                const esriModules = await loadESRIModules(['esri/layers/MapImageLayer', 'esri/Graphic', 'esri/geometry/Point', 'esri/layers/support/Sublayer']);
                
                // Setup LayerFactory with local configuration
                window.LayerFactory.setupDevelopmentEnvs(appConfig.ArcGISServerHost + "/", 3414);
                
                // Get layers from LayerFactory
                const categories = window.LayerFactory.getLayers(
                    mapWrap, 
                    layerWrapper(esriModules.MapImageLayer, esriModules.Sublayer), 
                    GetMessenger(
                        mapView, 
                        esriModules.Graphic, 
                        esriModules.Point, 
                        reversePolygonLatLng, 
                        refreshEPlannerResultsDispatch, 
                        getIdentifyOverlayResultDispatch
                    ), 
                    userInfo.ArcGisToken
                );
                
                if (categories) {
                    setOverlaysList(categories);
                    refreshEPlannerResultsDispatch();
                }
            } catch (error) {
                console.error('Error loading ePlanner overlays:', error);
            }
        }
    }

    useEffect(() => {
        // LayerFactory is now imported directly, so it's available immediately
        if (window.LayerFactory) {
            setLayerFactoryReady(true);
            getEPlannerOverlays();
        }
    }, [mapView]); // Depend on mapView to reload when map is ready

    useEffect(() => {
        if (layerFactoryReady && mapView) {
            getEPlannerOverlays();
        }
    }, [layerFactoryReady, mapView]);

    return (
        <TabContainer defaultActiveKey="1">
            {navs}
            <Scrollbar>
                <TabContent>
                    <TabPane eventKey="1">
                        <GenerateMenuFromProps selectedList={currentOverlays.selectedOverlays}
                            onOverlaySelected={overlaySelectedHandler}
                            menuList={overlaysList}
                            userInfo={userInfo}
                            mapView={mapView}
                            openDashboard={openDashboard} />
                    </TabPane>
                    <TabPane eventKey="2">
                        {currentOverlays.counter > 0
                            && <IconButton aria-label="Delete" className="clearAllOverlays"
                                onClick={clearOverlaysHandler}>
                                Clear All<DeleteSweep style={{ marginLeft: '5px' }} />
                            </IconButton>}
                        <List id="selectedOverlays">
                            {currentOverlays.selectedOverlays.map((lyr, index) => {
                                return (
                                    <ListItem key={index}>
                                        <ListItemText disableTypography
                                            primary={<Typography>{lyr.opts.name || lyr.opts.label}</Typography>} />
                                        <IconButton aria-label="Delete"
                                            onClick={() => overlaySelectedHandler(lyr, false)}>
                                            <DeleteForever />
                                        </IconButton>
                                    </ListItem>
                                );
                            })}
                        </List>
                    </TabPane>
                </TabContent>
            </Scrollbar>
            <Suspense fallback={<div className="Spinner" />} >
                {currentOverlays.selectedOverlays.length > 0
                    ? <FilterBox filterType="Overlays" parentMenuTypes={overlaysList}
                        selectedMenus={currentOverlays.selectedOverlays} mapView={mapView} isOpen={filterOpened}
                        toggleFilter={(event) => setFilterOpened(!filterOpened)} />
                    : null}
            </Suspense>
        </TabContainer>
    )
}

export default GenerateOverlayMenu;
