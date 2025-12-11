/**-------------------------------------------------------------------------------------------------
 * PROGRAM ID      : webapi.js
 * DESCRIPTION     : static data file for web APIs
 * AUTHOR          : louisz
 * DATE            : May 17, 2016
 * VERSION NO      : 1.0
 * PARAMETERS      :
 * RETURN          :
 * USAGE NOTES     :
 * COMMENTS        :
---------------------------------------------------------------------------------------------------
 * CHANGE LOG      :
 * CHANGED BY      :
 * DATE            :
 * VERSION NO      :
 * CHANGES         :
--------------------------------------------------------------------------------------------------*/

//@ts-ignore
import Ajax from "./ajax";
//@ts-ignore
import { reproject, buildToDeployServer, reversePolygonLatLng, appendUrlWithParams, ConfigStoreInt, getGeospaceToken } from "./util";
//@ts-ignore
import UrlConstants, { ControllerUrl } from "./urlconstants";
import { LatLng } from "leaflet";
import * as Esri from 'esri-leaflet';

//@ts-ignore
import { Aggregations } from "./aggregationconstants";

class WebApi {
    _arcgisTokenGetter: () => string = () => "";

    registerTokenGetter(getter: () => string) {
        this._arcgisTokenGetter = getter;
    }

    getToken(): string { return this._arcgisTokenGetter(); }

    querySiteInfo(latLng: LatLng) {
        return this.queryGeoserverServices(latLng);
    }

    queryGeoserverServices(latLng: LatLng) {
        let viewParamsArr = [];
        viewParamsArr.push('x:' + latLng.lng);
        viewParamsArr.push('y:' + latLng.lat);

        return Ajax.call({
            url: buildToDeployServer("/Proxy/GeoserverAuth/ura/wms"),
            xhrFields: { withCredentials: true },
            crossDomain: true,
            type: "GET",
            data: {
                request: 'GetFeature',
                service: 'WFS',
                typeName: "ura:get_site_info",
                outputFormat: 'application/json',
                maxFeatures: 50,
                viewparams: viewParamsArr.join(';')
            }
        }).then((geoserverResponse: any) => {
            let results = {};
            if (geoserverResponse.totalFeatures > 0) {
                let properties = geoserverResponse.features[0].properties;
                results = {
                    [Aggregations.PlanningCommitment]: properties.plcm,
                    [Aggregations.PlanningArea]: properties.pa,
                    [Aggregations.UraSubBoundary]: properties.ura_subboundary,
                    [Aggregations.SubZone]: properties.sz,
                    [Aggregations.Constituency]: properties.grc,
                    [Aggregations.Constituency2025]: properties.grc_2025,
                    [Aggregations.Ward]: properties.ward,
                    mp: properties.mp,
                    [Aggregations.Cadastral]: properties.cada,
                    [Aggregations.HdbTownBoundary]: properties.hdb_town,
                    [Aggregations.SSOBoundary]: properties.sso,
                    [Aggregations.Hexagon250]: properties.h250,
                    [Aggregations.Hexagon500]: properties.h500,
                    hse_blk_no: properties.hse_blk_no,
                    name: properties.name,
                    [Aggregations.AddressPoint]: properties.postalcode,
                    [Aggregations.Region]: properties.region,
                    road_name: properties.road_name,
                    [Aggregations.SubMtz]: properties.submtz,
                    [Aggregations.JtcEstate]: properties.estate,
                    [Aggregations.JtcBuilding]: properties.building,
                    [Aggregations.FscBoundary]: properties.fsc,
                    [Aggregations.CA_OCA]: properties.ca_oca,
                };

            }

            return results;
        });
    }

    queryAddress(latLng: LatLng) {
        let wgs84 = '+proj=longlat +datum=WGS84 +no_defs';
        let svy21 = 'PROJCS["SVY21",GEOGCS["SVY21[WGS84]",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",28001.642],PARAMETER["False_Northing",38744.572],PARAMETER["Central_Meridian",103.8333333333333],PARAMETER["Scale_Factor",1.0],PARAMETER["Latitude_Of_Origin",1.366666666666667],UNIT["Meter",1.0]]';
        return Ajax.call({
            url: appendUrlWithParams(UrlConstants.GeoSpaceReverseAddressSearch, {
                accessKey: getGeospaceToken(),
                location: reproject([latLng.lng, latLng.lat], wgs84, svy21),
            }),
            crossDomain: true,
            dataType: 'jsonp',
        });
    }

    queryDivisonalWard(latLng: LatLng) {
        let def = Ajax.deferred();

        Esri.query({
            url: buildToDeployServer(UrlConstants.GrcSearch),
            useCors: false
        })
            .token(this.getToken())
            .intersects(latLng)
            .where("1=1")
            //.returnGeometry(true)
            .fields(["WARD_NAME", "CONST_NAME", "MP_NAME"])
            .run((error?: any, featureCollection?: any, response?: any) => {
                if (error) {
                    def.reject(error);
                } else {

                    var results = featureCollection.features.map((row: any, i: number) => {

                        let properties = row.properties;

                        return {
                            ward: properties.WARD_NAME,
                            constituency: properties.CONST_NAME,
                            mp: properties.MP_NAME
                        };
                    });

                    def.resolve(results.length > 0 ? results[0] : {});
                }
            });

        return def.promise();
    }

    queryPlngAreaGeom(plngArea: string) {
        let def = Ajax.deferred(),
            query = Esri.query({
                url: buildToDeployServer(UrlConstants.PlanningAreaSearch),
                useCors: false
            });

        //@ts-ignore
        query.outSpatialReference = { "wkid": ConfigStoreInt.sr };

        query
            .token(this.getToken())
            .where("PLN_AREA_N = '" + plngArea + "'")
            .run((error?: any, featureCollection?: any, response?: any) => {
                if (error) {
                    def.reject(error);
                } else {
                    let results = featureCollection.features.map((row: any, i: number) => {
                        return {
                            plngArea: plngArea,
                            geometry: reversePolygonLatLng(row.geometry)
                        };
                    });

                    def.resolve(results.length > 0 ? results[0] : {});
                }
            });

        return def.promise();
    }

    querySubZoneGeom(subZone: string) {
        let def = Ajax.deferred();

        Esri.query({
            url: UrlConstants.SubZoneSearch,
            useCors: false
        })
            .token(this.getToken())
            .where("SUBZONE_N = '" + subZone + "'")
            .run((error?: any, featureCollection?: any, response?: any) => {
                if (error) {
                    def.reject(error);
                } else {
                    let results = featureCollection.features.map((row: any, i: number) => {
                        return {
                            subZone: subZone,
                            geometry: reversePolygonLatLng(row.geometry)
                        };
                    });

                    def.resolve(results.length > 0 ? results[0] : {});
                }
            });

        return def.promise();
    }

    queryPlngAreaGeom19(plngArea: string, token: boolean = true) {
        let def = Ajax.deferred(),
            query = Esri.query({
                url: buildToDeployServer(UrlConstants.PlanningArea19Search),
                useCors: false,
            });
        //@ts-ignore
        query.params.outSR = ConfigStoreInt.sr;

        query
            .token(this.getToken())
            .where("PLN_AREA_N = '" + plngArea + "'")
            .distinct()
            .run((error: any, featureCollection: any, response: any) => {
                if (error) {
                    def.reject(error);
                } else {
                    let results = featureCollection.features.map((row: any, i: number) => {
                        return {
                            plngArea: plngArea,
                            geometry: reversePolygonLatLng(row.geometry)
                        };
                    });

                    def.resolve(results.length > 0 ? results[0] : {});
                }
            });

        return def.promise();
    }

    querySubZoneGeom19(subZone: string, token: boolean = true) {
        let def = Ajax.deferred();
        let query = Esri.query({
            url: buildToDeployServer(UrlConstants.SubZone19Search),
            useCors: false
        });
        //@ts-ignore
        query.params.outSR = ConfigStoreInt.sr;
        //@ts-ignore
        query.outSpatialReference = { "outSR": ConfigStoreInt.sr };

        query
            .token(this.getToken())
            .where("SUBZONE_N = '" + subZone + "'")
            .run((error?: any, featureCollection?: any, response?: any) => {
                if (error) {
                    def.reject(error);
                } else {
                    let results = featureCollection.features.map((row: any, i: number) => {
                        return {
                            subZone: subZone,
                            geometry: reversePolygonLatLng(row.geometry)
                        };
                    });

                    def.resolve(results.length > 0 ? results[0] : {});
                }
            });

        return def.promise();
    }
}

export default (new WebApi());

//TODO: standardise backend response format
type DcgAreaOicResponse = {
    status: "success",
    result: string,
} & {
    status: string,
};

/**
 * To query backend for OICs for DCG Area based on `areaCode`.
 * @param areaCode
 * @param attributes Attributes to be spread over the features before return
 */
export const queryDcgAreaOic = (areaCode: string, attributes: any = {}) => {

    //Note: areaCode needs to be in url instead of body for the API to work
    return fetch(appendUrlWithParams(ControllerUrl.DcgAreaOic, {
        "areaCode": encodeURIComponent(areaCode)
    }), {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        }
    })
        .then(response => response.json())
        .then(data => {
            const json = JSON.parse(data);
            let features = [];
            if (json.status === "success") {
                features = json.result.map((feature: any) => {
                    return {
                        ...attributes,
                        properties: feature
                    };
                });
            } else {
                console.error(data.status);
            }

            return features
        });
}
