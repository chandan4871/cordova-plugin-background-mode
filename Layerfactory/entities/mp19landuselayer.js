/**-------------------------------------------------------------------------------------------------
 * PROGRAM ID      : mp19landuselayer.js
 * DESCRIPTION     : basic class for layer Gazetted Land Use
 * AUTHOR          : louisz
 * DATE            : Jan 5, 2016
 * VERSION NO      : 1.0
 * PARAMETERS      :
 * RETURN          :
 * USAGE NOTES     :
 * COMMENTS        :
---------------------------------------------------------------------------------------------------
 * CHANGE LOG      : Added layer infographic
 * CHANGED BY      : jianmin
 * DATE            : Jul 15, 2016
 * VERSION NO      :
 * CHANGES         :
--------------------------------------------------------------------------------------------------*/

import L from 'leaflet';
import * as Esri from 'esri-leaflet';
import {ConfigStoreInt, arrayToList, reversePolygonLatLng, sqmToSqkm, getFeatureCenter, polygonsToMultiPolygon, convertSquareMetersToHa, buildToDeployServer} from "../functions/util";
import React from 'react';
import Layer from '../functions/layer';
import WebApi from '../WebApi';
import DropDownList from '../../components/v2/stateless/dropdownlist';

import UrlConstants from "../../constants/urlconstants";
import { PlanningArea, LandUseType } from "../../constants/aggregationconstants";
import BarChart from '../../components/charts/barchart';
import { GazettedLandUseColors } from "../../constants/chartconstants";
import Ajax from "../wrapper/ajax";
import Grid from "@mui/material/Grid";
import TextField from "@mui/material/TextField";
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';

const ALL = 'ALL';
const MAX_RECORDS = 1000; //due to ArcGIS REST max records
const DEFAULT_GPR_VALUE = 3;
const styles = {
    textField: {
        marginTop: 10
    }
};

export default class MP19LandUseLayer extends Layer {

    constructor(opts, token) {
        super(opts, token);
        //setup initial values
        this.defaultPlngAreas = Object.values(PlanningArea);
        this.defaultPlngAreas.unshift(ALL);
        this.defaultPlngAreas = arrayToList(this.defaultPlngAreas);

        this.defaultLandUseTypes = Object.values(LandUseType);
        this.defaultLandUseTypes.unshift(ALL);
        this.defaultLandUseTypes = arrayToList(this.defaultLandUseTypes);

        this.defaultSubzones = [ALL];
        this.comparisons = ['GPR >=', 'GPR >', 'GPR =', 'GPR <=', 'GPR <'];
        this.queryUrl = opts.src + '/' + opts.queryId;
        this.includeNullGpr = false;

        this.resetFilterbox();

        this.QueryLayerId = opts.queryId;
    }

    retrieveInfographics(){
        return Ajax.wait(
            [this.retrieveData()],
            (featureCollection) => {
                return featureCollection;
            }, error => {
                this.showErrorModal("Error retrieving Gazetted land use layer data.");
            }
        );
    }

    retrieveData(){
        var deferred = Ajax.deferred();
        
        this.map.query({
            layer: this.QueryLayerId,
            where: 'LU_DESC is not null',
            returnGeometry: false,
            order: 'LU_DESC',
            outStatistics: [{
                "statisticType": "sum",
                "onStatisticField": "Shape_Area",
                "outStatisticFieldName": "TotalAreaByLandUse"
            }],
            groupByFieldsForStatistics: 'LU_DESC'
        }, (error, featureCollection, response) => {
            deferred.resolve([featureCollection]);
        });

        return deferred.promise();
    }

    getInfographics(featureCollection){

        let results = featureCollection.features.map((feature) => {
            const {TotalAreaByLandUse, LU_DESC} = feature.properties;

            return {
                name: LU_DESC,
                area: sqmToSqkm(TotalAreaByLandUse, 2),
            };
        });

        //sort
        results.sort((a, b) => {
            return b.area - a.area;
        });

        let barData = results.map(row => {
            return [
                row.name,
                +row.area,
            ];
        });

        return (<BarChart 
            title={'Updated Gazetted Land Use By Land Area (km2)'} 
            header={['Land Use']} 
            data={barData} 
            orientation={1} 
            chartTooltip={{show: false}}
            labels={true}
            chartPadding={{ 
                top: 30,
                right: 150,
                bottom: 30,
                left: 120
            }}
            chartColor={GazettedLandUseColors}
            chartSize={{
                width:750,
                height:700
            }}
            barWidthRatio={1}
            exportCSV={this.defaultSettings.exportCSV}
        />);
    }

    postProcessDisplayRow(row, properties) {
        //fix sqmeters to ha for site area
        row[1] = convertSquareMetersToHa(row[1]);

        return row;
    }

    resetFilterbox() {
        this.planningAreas = this.defaultPlngAreas;
        this.subzones = this.defaultSubzones;
        this.landUseTypes = this.defaultLandUseTypes;
        this.gprValue = DEFAULT_GPR_VALUE;

        this.selectedPlngArea = ALL;
        this.selectedSubZone = ALL;
        this.selectedLandUse = ALL;
        this.selectedEquation = this.comparisons[0];
        this.includeNullGpr = false;

        this.found = -1;
    }

    getFilterbox() {
        let plngAreaChangeFunc = e => {
                let plngArea = e.target.value;
                this.selectedPlngArea = plngArea;
                
                //TODO: Migrate to Webapi
                let query = Esri.query({
                    url: buildToDeployServer(UrlConstants.SubZone19Search),
                    useCors: false
                });
                query.params.outSR = ConfigStoreInt.sr;

                query
                .token(this.getToken())
                .returnGeometry(false)
                .fields(['SUBZONE_N'])
                .where("PLN_AREA_N = '" + plngArea + "'")
                .distinct()
                .run((error, featureCollection, response) => {
                    //Query, highlight and zoom to planning area geometry
                    WebApi.queryPlngAreaGeom19(plngArea, false)
                    .done(plngArea => {
                        if (plngArea && plngArea.geometry){
                            this.highlightZoomCenterMap(plngArea.geometry, 14, getFeatureCenter(plngArea.geometry));
                        }
                    });

                    //Query, update subzone list
                    let subzones = featureCollection.features.map(feature => {
                        return feature.properties.SUBZONE_N;
                    });

                    subzones.unshift(ALL);
                    this.subzones = subzones;
                    this.selectedSubZone = ALL;
                    this.refreshFilterbox();
                });

                this.refreshFilterbox();
            },
            subzoneChangeFunc = e => {
                let subZone = e.target.value;
                this.selectedSubZone = subZone;
                WebApi.querySubZoneGeom19(subZone, false)
                .done(subZone => {
                    if(subZone && subZone.geometry){
                        this.highlightZoomCenterMap(subZone.geometry, 14, getFeatureCenter(subZone.geometry));
                    }
                });
                this.refreshFilterbox();
            },
            landUseChangeFunc = e => {
                this.selectedLandUse = e.target.value;
                this.refreshFilterbox();
            },
            equationChangeFunc = e => {
                this.selectedEquation = e.target.value;
                this.refreshFilterbox();
            },
            inputChangeFunc = (e) => {
                this.gprValue = e.target.value;
                this.refreshFilterbox();
            },
            invalidValue = (value) => {
                return isNaN(value) || value < 0;
            },
            searchFilterFunc = (e) => {
                let plngArea = this.selectedPlngArea === ALL ? '1=1' : "PLN_AREA_N='" + this.selectedPlngArea + "'",
                    subZone = this.selectedSubZone === ALL ? '1=1' : "SUBZONE_N='" + this.selectedSubZone + "'",
                    landUse = this.selectedLandUse === ALL ? '1=1' : "LU_DESC='" + this.selectedLandUse + "'",
                    gpr = ("(GPR_NUM" + this.selectedEquation.substring(3) + this.gprValue + (this.includeNullGpr ? " OR GPR_NUM IS NULL)" : ")")),
                    where = [gpr, plngArea, subZone, landUse].join(" AND ");

                if (invalidValue(this.gprValue)){
                    this.displayMessage('GPR value is not valid.');
                    return;
                }

                let query = Esri.query({
                    url: this.queryUrl,
                    useCors: false
                });
                query.params.outSR = ConfigStoreInt.sr;
                
                query
                .token(this.getToken())
                .where(where)
                .run((error, featureCollection, response) => {
                    this.found = featureCollection.features.length;
                    if (this.found >= MAX_RECORDS){
                        this.found = 'More than ' + MAX_RECORDS;
                    }

                    let latLngs = featureCollection.features.map(feature => {
                        return reversePolygonLatLng(feature.geometry);
                    }),
                    multipolygon = polygonsToMultiPolygon(latLngs);
                    this.highlightZoomCenterMap(multipolygon);
                    this.refreshFilterbox();
                });
            },
            clearFunc = (e) => {
                this.resetFilterbox();
                this.clearHighlights();
                this.refreshFilterbox();
            },
            handleMissingGpr = (evt) => {
                this.includeNullGpr = evt.target.checked;
                this.refreshFilterbox();
            };
      
        return (<React.Fragment>
            <DropDownList title='Planning Area: ' selected={this.selectedPlngArea} options={this.defaultPlngAreas} onChange={plngAreaChangeFunc} />
            <DropDownList title='Subzones: ' selected={this.selectedSubZone} options={arrayToList(this.subzones)} onChange={subzoneChangeFunc} />
            <DropDownList title='Land Use Type: ' selected={this.selectedLandUse} options={this.defaultLandUseTypes} onChange={landUseChangeFunc} />
            
            <Grid container spacing={1}>
                <Grid item xs={6} sm={6} md={6} lg={6}>
                    <DropDownList 
                        title='Gross Plot Ratio:' 
                        selected={this.selectedEquation}
                        options={arrayToList(this.comparisons)} 
                        onChange={equationChangeFunc} 
                    />
                </Grid>

                <Grid item xs={5} sm={5} md={5} lg={5} style={styles.textField}>
                    <TextField
                        type="number"
                        value={this.gprValue}
                        onChange={inputChangeFunc}
                        variant="outlined"
                        size="small"
                        sx={{
                            '& .MuiInputBase-input': {
                                paddingTop: "10.5px",
                                paddingBottom: "10.5px",
                            }
                        }}
                    />
                </Grid>
            </Grid>

            <FormControlLabel control={<Checkbox checked={this.includeNullGpr} onChange={handleMissingGpr} />} label="Include parcels with missing GPR" />
            <div>
                <div className="calc_results">{ this.found === -1 ? '' : 'Total Results:' + this.found }</div>
                <div className="calc_btns">
                    <button className="calc_btn_clear" onClick={clearFunc}>Reset</button>
                    <button className="calc_btn_primary" onClick={searchFilterFunc}>Apply</button>
                </div>
            </div>
        </React.Fragment>);
    }
}
