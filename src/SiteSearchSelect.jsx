import {
    Box,
    Button, Toolbar,
    Typography, FormControl, Select, MenuItem, Chip
} from '@mui/material';
import { loadESRIModules, mapViewGraphics_AddGraphic, mapViewGraphics_RemoveAll, mapViewZoomToTarget } from 'Constants/Helpers/mapHelpers';
import { consSelectionMarker } from 'Constants/Maps';
import 'Containers/LeftMenu/NIP/NIPResults/AttributesPage/ConsultationRender/SLASiteSearch/slaSiteSearch.css';
import AlertDialog from 'Containers/LeftMenu/NIP/SLASSAlertDialog';
import WarningDialog from 'Containers/LeftMenu/NIP/SLASSWarningDialog';
import MUIDataTable from 'mui-datatables';
import React, { useContext, useEffect, useState, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { addResultsToRightbar, removeResultsFromRightbar, clearResultsFromRightbar } from 'Store/Actions/Results';
import { createNewCase, getCaseByPropertyView,getPropertyDetails } from '../ApiHelpers';
import CaseCreationForm from '../CaseCreationForm/CaseCreationForm';
import LoadingBackDrop from '../SubComponents/LoadingBackDrop/LoadingBackDrop';
import SLASSDialog from 'Containers/LeftMenu/NIP/SLASSAlertDialog.js';;
import ViewDetails from '../ViewDetails';
import SiteDetails from '../SiteDetails';
import { SLASiteSearchContext } from '../Context/SLASiteSearchContext';
import {SLASiteSearchProvider} from '../Context/SLASiteSearchContext';
import { TabContext, TabPanel } from '@mui/lab';

const SiteSearchSelect = ({ properties }) => {
    const userInfo = useSelector(state => state.authentication.user);
    const isUraUser = userInfo["AgencyName"] === "URA";
    const dispatch = useDispatch();

    const mapView = useSelector(state => state.mapView);
    const [warningDialog, setWarningDialog] = useState({
        open: false, title: "", msgBody: "",
        btnNname: "",
        handleClose: () => closeWarningDiaglog(),
        handleSubmit: () => closeWarningDiaglog(),
    });
    const [alertDialog, setAlertDialog] = useState({ show: false, title: "", message: "", buttonNameOK: "", confirmationType: "" });
    const { caseDetail, updateCaseDetail } = useContext(SLASiteSearchContext);
    const [tabView, setTabView] = useState("SiteSearchSelect");
    const [selectedRows, setSelectedRows] = useState([]);
    const [selectedProperties, setSelectedProperties] = useState([]);
    const [loadingBackDrop, setLoadingBackDrop] = useState({ isLoading: false, message: "" });
    const [triggerTabChange, setTriggerTabChange] = useState(false);
    const [viewDetails, setViewDetails] = useState(null);
    const [propertyDataId, setPropertyId] = useState();
    const [propertyIndex, setPropertyIndex] = useState();
    const [existInTACompleted, setExistInTACompleted] = useState(false);
    const [filterColumn, setFilterColumn] = useState('');
    const [filterValue, setFilterValue] = useState(''); 
    const [originalData, setOriginalData] = useState([]);
    const [data, setData] = useState([]);
    const [confirmConsultAlert, setConfirmConsultAlert] = useState({
        open: false,
        handleClose: () => setConfirmConsultAlert({ ...confirmConsultAlert, open: false }),
        handleSubmit: () => null,
        title: "Site Search Consulation",
        msgBody: null,
        btnNname: "Create Case"
    });

    useEffect(() => {
        const loadData = async () => {
            const casedetails = await getPropertyDetails(properties);
            console.log("casedetails", casedetails);
            const rows = properties.map((property) => {
                const match = casedetails.find(d => d.PROPERTY_ID === property.attributes.PROPERTYID);
                console.log("match", match);
                let consultationStatus = "";
                let caseIds = "";
                if (
                    !match?.WORKFLOW_STAGE
                ) {
                    consultationStatus = "None";
                    caseIds = "None";
                }                
                else {
                    consultationStatus = match?.CODE_VALUE ;
                    caseIds = match?.CASE_ID || "";
                }
                return {
                    propertyId: property.attributes.PROPERTYID === null || property.attributes.PROPERTYID === '' ? property.attributes.PARCEL_ID : property.attributes.PROPERTYID,
                    parcelId: property.attributes.PARCEL_ID === null || property.attributes.PARCEL_ID === '' ? null : property.attributes.PARCEL_ID,
                    availability: property.attributes.CURRENT_STATUS,
                    consultationStatus,
                    caseIds,
                    attributes: property.attributes,
                    geometry: property.geometry
                };
            });
            // setFilteredData(rows);
            setOriginalData(rows);
            setData(rows);
        };
        if (properties?.length) loadData();
    }, [properties]);

    const columns = [
        { name: "propertyId", label: "Property", options: { sort: true } },
        { name: "availability", label: "Availability", options: { sort: true } },
        {
            name: "consultationStatus",
            label: "Consultation Status",
            options: {
                sort: true,
                customBodyRender: (value) => {
                    let color = "default";

                    if (value.toLowerCase() === "none" || value.toLowerCase() === "completed" || value.toLowerCase() === "withdrawn") color = "success";       // green                    
                    else if (value === "DRAFT") color = "warning"; // orange
                    else color = "error"; // red

                    return (
                        <div style={{ display: 'flex', justifyContent: 'center' }}>
                            <Chip
                                label={value}
                                color={color}
                                size="small"
                                sx={{
                                    fontWeight: 600,
                                    color: color === "default" ? "grey.800" : "white",
                                }}
                            />
                        </div>
                    );
                },
            },
        },
        { name: "caseIds", label: "Case IDs", options: { sort: true } },
    ];

    const options = {
        filterType: 'checkbox',
        filter: false,
        download: false,
        print: false,
        viewColumns: false,
        rowsPerPage: 100,
        rowsSelected: selectedRows,
        onRowClick: (rowData, rowMeta) => {
            onRowPropertyClick(rowData);
        },
        // setRowProps: (row) => {
        //     const consultationStatus = row[3]?.toLowerCase(); // Safe conversion to string
        //     const isOngoingOrDraft = !(consultationStatus === "none" || consultationStatus === "completed" || consultationStatus === "withdrawn")
        //     return {
        //         style: {
        //             cursor: isOngoingOrDraft ? "not-allowed" : "pointer",
        //             opacity: isOngoingOrDraft ? 0.5 : 1, // visual hint
        //         },
        //     };
        // },
        
        setCellProps: () => ({
            className: 'siteSearchLinks',
        }),
        headerHeight: 0,
        customFooter: () => null,
        customToolbarSelect: () => (
            <Toolbar>
                {!isUraUser && (
                    <div>
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={() => consultSelectedProperties()}
                        >
                            Consult
                        </Button>
                    </div>
                )}
            </Toolbar>
        ),

      //Disable selection for rows where consultationStatus = "Ongoing"

        selectableRows: "multiple",
        isRowSelectable: (dataIndex) => {
            const row = data[dataIndex];
            const consultationStatus = row?.consultationStatus.toLowerCase();
            return consultationStatus === "none" || consultationStatus === "completed" || consultationStatus === "withdrawn"
        },

        onRowSelectionChange: (currentRowsSelected, allRowsSelected) => {
            const rows = allRowsSelected.map((row) => row.dataIndex);
            setSelectedRows(rows);
            const selectedData = rows.map((selectedRow) => data[selectedRow]);
            setSelectedProperties(selectedData);
            zoomToSelectedProperties(selectedData);
        },
        setRespondent: true,
    };

    const zoomToSelectedProperties = async (selectedData) => {
        const esriModules = await loadESRIModules([
            'esri/Graphic',
            'esri/geometry/Polygon',
            'esri/geometry/Polyline',
            'esri/geometry/Extent', // Ensure extent is available
        ]);
    
        mapViewGraphics_RemoveAll(mapView);  // Remove previous graphics
        const mapGraphics = [];
    
        let extent;  // This will store the combined extent for all selected graphics
    
        selectedData.forEach(property => {
            let mapGraphic = new esriModules.Graphic();
            let geometry;
    
            // Check the geometry type and create the appropriate geometry object
            if (property.geometry.type === "polygon") {
                geometry = new esriModules.Polygon(property.geometry);  // Polygon geometry
            } else if (property.geometry.type === "polyline") {
                geometry = new esriModules.Polyline(property.geometry);  // Polyline geometry
            }
    
            mapGraphic.geometry = geometry;
            mapGraphic.symbol = consSelectionMarker;
    
            mapViewGraphics_AddGraphic(mapView, mapGraphic);  // Add the graphic to the map
            mapGraphics.push(mapGraphic);
    
            // Calculate the extent for multiple graphics
            if (!extent) {
                extent = geometry.extent;  // Initialize the extent with the first geometry's extent
            } else {
                extent = extent.union(geometry.extent);  // Union with subsequent geometries to include all
            }
        });
    
        // Adjust the zoom behavior:
        if (selectedData.length === 1) {
            // If only one graphic is selected, zoom to that single graphic using mapViewZoomToTarget
            mapViewZoomToTarget(mapView, mapGraphics[0].geometry); // Zoom to the single geometry
        } else {
            // If multiple graphics are selected, zoom to the combined extent using mapViewZoomToTarget
            mapViewZoomToTarget(mapView, extent); // Zoom to the combined extent
        }
    
        // Adjust the zoom level further (use this after `goTo` to adjust the zoom)
        const zoomLevel = 9; // Adjust this number for more zoomed-in or zoomed-out
        mapView.goTo(extent, {
            zoom: zoomLevel, // Set the zoom level
        }).catch((err) => {
            console.error("Zoom Error: ", err.message);
        });
    };
    


    // Handles filter application
    const handleCustomFilter = () => {
        if (!filterColumn || !filterValue) return;
        const filtered = data.filter((item) => {
            const val = item[filterColumn];
            return val && val.toString().toLowerCase() === filterValue.toLowerCase();
        });
        setData(filtered);
    };

    // Clear filter
    const clearCustomFilter = () => {
        setFilterColumn('');
        setFilterValue('');
        setData(originalData);
    };
    const consultSelectedProperties = async () => {
        const selectedData = selectedRows.map(selectedRow => data[selectedRow]);
        setConfirmConsultAlert({
            ...confirmConsultAlert,
            open: true,
            msgBody: (
                <div style={{ padding: '16px 24px' }}>
                    <Typography gutterBottom>
                        You have selected the following sites for site search consultation
                    </Typography>
                    <Typography gutterBottom component="ul" style={{ paddingLeft: '20px' }}>
                        {selectedData.map((property, index) => (
                            <li key={index}>{property.propertyId}</li>
                        ))}
                    </Typography>
                    <Typography gutterBottom>
                        If you proceed, a case ID will be created for you to carry on with the consultation.
                    </Typography>
                </div>
            ),
            btnNname: "Create Case",
            handleSubmit: () => createCase()
        });
    };

    const closeDiaglog = () => {
        setAlertDialog({ ...warningDialog, show: false });
    }

    const closeWarningDiaglog = () => {
        setWarningDialog({ ...warningDialog, open: false });
    }

    const closeConfirmConsultDialog = () => {
        setConfirmConsultAlert(false);
    }

    const goBackToSiteSearchSelectView = async () => {
        setTabView("SiteSearchSelect");
    }


    const onRowPropertyClick = async (rowData) => {
        let updatedCase;
        let propIndex;
    
        try{
            var propertId = rowData[0];
            await setPropertyId(propertId);
            const viewCaseDetails = await getCaseByPropertyView(propertId);
            if(propertId === viewCaseDetails){
                setExistInTACompleted(true);
                setTabView("ViewDetails");
            }
            if (viewCaseDetails !== null && viewCaseDetails !== undefined) {
                propIndex = viewCaseDetails.properties.findIndex(property => property.propertyId === rowData[0]);
                updatedCase = {
                    ...viewCaseDetails,
                    properties: [viewCaseDetails.properties[propIndex]]
                };
                setPropertyIndex(propIndex);
                setViewDetails(viewCaseDetails);
                setTabView("SiteDetails");
            }
            else{
                setTabView("ViewDetails");
            }
        } catch(error) {
            console.error(error);
        }
    };
    
    useEffect(() => {
    }, [caseDetail]);

    const createCase = async () => {
        try {
            setLoadingBackDrop({ isLoading: true, message: 'Creating a case' })
            closeConfirmConsultDialog();

            const response = await createNewCase(userInfo["Email"], selectedProperties);
                dispatch(removeResultsFromRightbar([`CR#SLA_SS_CONS_R`]))
                dispatch(addResultsToRightbar(
                    [`Enhanced SLA TA Consultation`],
                    [`CR#SLA_SS_CONS_R`],
                    [
                        <SLASiteSearchProvider>
                            <CaseCreationForm caseId={response.data.CASE_ID} />
                        </SLASiteSearchProvider>
                    ]
                    , 1)
                );

        } catch (error) {
            console.error(error);
        } finally {

        }
    }

    return (
        <div>
            <div>
                <TabContext value={tabView}>
                    <TabPanel value="SiteSearchSelect" style={{ padding: 0 }}>
                        <Box sx={{ px: 2, pt: 1 }}>
                            <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
                                Site Search Consultation
                            </Typography>
                            <Box className="filter-toolbar">
                                <Typography className="filter-label">Filter:</Typography>

                                <FormControl variant="standard" className="filter-control">
                                    <Select
                                        value={filterColumn}
                                        onChange={(e) => {
                                            setFilterColumn(e.target.value);
                                            setFilterValue("");
                                        }}
                                        displayEmpty
                                    >
                                        <MenuItem value="">
                                            <em>Column</em>
                                        </MenuItem>
                                        {columns.map((col, idx) => (
                                            <MenuItem key={idx} value={col.name}>
                                                {col.label || col.name}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>

                                <FormControl variant="standard" className="filter-control">
                                    <Select
                                        value={filterValue}
                                        onChange={(e) => setFilterValue(e.target.value)}
                                        displayEmpty
                                        disabled={!filterColumn}
                                    >
                                        <MenuItem value="">
                                            <em>Value</em>
                                        </MenuItem>
                                        {filterColumn &&
                                            [...new Set(data.map((d) => d[filterColumn]))]
                                                .filter((v) => v)
                                                .map((val, i) => (
                                                    <MenuItem key={i} value={val}>
                                                        {val}
                                                    </MenuItem>
                                                ))}
                                    </Select>
                                </FormControl>

                                <Box className="filter-buttons">
                                    <Button
                                        size="small"
                                        variant="contained"
                                        color="primary"
                                        disabled={!filterColumn || !filterValue}
                                        onClick={handleCustomFilter}
                                    >
                                        Apply
                                    </Button>
                                    <Button
                                        size="small"
                                        variant="outlined"
                                        color="error"
                                        onClick={clearCustomFilter}
                                    >
                                        Clear
                                    </Button>
                                </Box>
                            </Box>
                            <MUIDataTable
                                title={""}
                                data={data}
                                columns={columns}
                                options={{
                                    ...options,
                                    responsive: "simple",
                                    tableBodyMaxHeight: "none",
                                    setTableProps: () => ({ style: { overflowX: "hidden", cursor : "pointer" } }),
                                }}
                            />
                        </Box>
                    </TabPanel>
                    <TabPanel value="SiteDetails" style={{ padding: 0 }}>
                        <SiteDetails goBack={() => goBackToSiteSearchSelectView()} propertyIndex={propertyIndex} viewDetails={viewDetails} fromSearchResult={true}/>
                    </TabPanel>

                    <TabPanel value="ViewDetails" style={{ padding: 0 }}>
                        <ViewDetails goBack={() => goBackToSiteSearchSelectView()} propertyId={propertyDataId} existInTACompleted={existInTACompleted} />
                    </TabPanel>
                </TabContext>
            </div>
            <AlertDialog {...confirmConsultAlert} />
            <WarningDialog {...warningDialog} />
            <LoadingBackDrop {...loadingBackDrop} />
            <SLASSDialog open={alertDialog.show} title={alertDialog.title} msgBody={alertDialog.message} btnNname={alertDialog.buttonNameOK} handleClose={closeDiaglog} handleSubmit={closeDiaglog} />
        </div>
    )
}

export default SiteSearchSelect;
