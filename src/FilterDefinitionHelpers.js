import { loadESRIModules, mapViewZoomToTarget } from 'Constants/Helpers/mapHelpers';

/** To set the definition query on the given layer.
     * SCF consultation has 2 sub layers - so pass the 3rd parameter when setting for SCF.
     * For other consultations, the 3rd parameter is not passed.
     */
var projectName = '';
export const setLayerDefinitionExpression = (layer, expression, scfCons) => {
    let _queryLayersForGraphics = [];

    if (layer?.sublayers?.length > 0) {
        if (scfCons) {
            if (scfCons === "SCF_POINTS" || scfCons === "NPARKS_LINES") {
                layer.findSublayerById(0).definitionExpression = expression;
                _queryLayersForGraphics.push({
                    url: layer.findSublayerById(0).url,
                    whereClause: expression
                })
            }
            else {
                layer.findSublayerById(1).definitionExpression = expression;
                _queryLayersForGraphics.push({
                    url: layer.findSublayerById(1).url,
                    whereClause: expression
                })
            }
        }
        else {
            for (var i = 0; i < layer.sublayers.length; i++) {
                if (layer.id === "SCF_CONS_R") {
                    if (i === 0) {
                        //Default def expression for SCF points.
                        layer.findSublayerById(0).definitionExpression = (expression === "" && "DELETED in ('NO')")
                            || (expression !== "" && "DELETED in ('NO') AND " + expression);

                        _queryLayersForGraphics.push({
                            url: layer.findSublayerById(0).url,
                            whereClause: (expression === "" && "DELETED in ('NO')")
                                || (expression !== "" && "DELETED in ('NO') AND " + expression)
                        })
                    }
                    else {
                        layer.findSublayerById(i).definitionExpression = expression;
                        _queryLayersForGraphics.push({
                            url: layer.findSublayerById(i).url,
                            whereClause: expression
                        })
                    }
                }
                else {
                    layer.findSublayerById(i).definitionExpression = expression;
                    _queryLayersForGraphics.push({
                        url: layer.findSublayerById(i).url,
                        whereClause: expression
                    })
                }
            }
        }
    }
    else {
        layer.findSublayerById(0).definitionExpression = expression;
        _queryLayersForGraphics.push({
            url: layer.findSublayerById(0).url,
            whereClause: expression
        })
    }

    return _queryLayersForGraphics;

}

/** Get the definition expressions of all the layers in the filter box and apply the definition queries on the layers.
 * 'All Inventories' Filters are to be applied on all development layers along with their own filters. 
 * To avoid overriding when working with definition queries, apply All Inventories filters first and then join them with the local filters as well.
 * Hence the condition checks below. 
 */
export const applyFilterSelectionAsDefinitionExpression = async (filterSelection, selectedMenus, mapView, setDefinitionExpression, parentMenuTypes, resetFilterSelection, _queryLayersForGraphics) => {
    // Apply All Inventories queries and then apply individual layers queries. Since All Inventories queries if executed later, will override the other queries.
    // Exclude infra layers from 'All Inventories' filter
    projectName = selectedMenus[0]?.PROJECT_NAME;
    let currentFilterSelection = Object.assign({}, filterSelection);
    let globalFilters = currentFilterSelection["All Inventories"];
    globalFilters && delete currentFilterSelection["All Inventories"];
    let otherFilters = currentFilterSelection;
    let ssCons = "";

    let defExpression = "";
    if (globalFilters) {
        defExpression = getDefinitionExpression(filterSelection, "All Inventories");
        defExpression && selectedMenus.filter(x => x !== 'All Inventories').forEach((prj) => {
            let lyr = prj.REMARKS === "INFRA_LAYERS"
                ? mapView.map.findLayerById(prj.PROJECT_NAME)
                : mapView.map.findLayerById(prj.MAPSERVICE_NAME);
            lyr && setDefinitionExpression(lyr, defExpression);
        });
    }
    if (otherFilters) {
        Object.keys(otherFilters).forEach((cons) => {
            defExpression = getDefinitionExpression(filterSelection, cons);

            if (globalFilters) {
                let globalDefExpression = getDefinitionExpression(filterSelection, "All Inventories");

                defExpression = (defExpression && globalDefExpression)
                    ? defExpression + " AND " + globalDefExpression
                    : (globalDefExpression || defExpression);
            }
            ssCons = cons;

            let serviceName = (cons === "SCF_POLYGONS" || cons === "SCF_POINTS")
                ? "SCF_CONS_R"
                : ((cons === "NPARKS_POLYGONS" || cons === "NPARKS_LINES")
                    ? "NPARKS_CONS_R"
                    : cons);

            defExpression && parentMenuTypes.filter(x => x.MAPSERVICE_NAME === serviceName).forEach((item, index) => {
                let lyr = item.REMARKS === "INFRA_LAYERS"
                    ? mapView.map.findLayerById(item.PROJECT_NAME)
                    : mapView.map.findLayerById(item.MAPSERVICE_NAME);
                lyr && setDefinitionExpression(lyr, defExpression, (serviceName === "SCF_CONS_R" || serviceName === "NPARKS_CONS_R") && cons);
            });
        });
    }
    projectName = '';
    if (!defExpression) {
        //resetFilterSelection();

    }
    else if (defExpression && (ssCons === "SLA_SS_CONS_R" || (selectedMenus && selectedMenus[0]?.MAPSERVICE_NAME == 'SLA_SS_CONS_R'))) {
        const graphicsLength = await SiteSearchZoomGraphicsExtent(_queryLayersForGraphics, mapView);
        return graphicsLength;
    }
    else {
        // perform query tasks on all the layers to get graphics and zoom to extent 
        const graphicsLength = await ZoomGraphicsExtent(_queryLayersForGraphics, mapView);
        return graphicsLength;
    }
};


/** Prepare the definition expression from the filterSelection state variable.
 * For SCF Polygons - FACILITY_TYPE is a 'comma' seperated list - so use the like operator to form the definition expression seperately.
 * For all NIP and INFRA - REGION_N and PLN_AREA_N is a 'comma' seperated list - so use the like operator
 * The other filters use the 'IN' operator to query the set of selected values.
 */
const getDefinitionExpression = (filterSelection, cons) => {
    try{
        let defExpression = "";
        Object.keys(filterSelection[cons]).forEach((fldName) => {
            let qryValues = filterSelection[cons][fldName];
            if (!qryValues || qryValues.length === 0) return;
            if (fldName === "FACILITY_TYPE" && (cons === "SCF_POLYGONS" || cons === "SCF_POINTS")) {
                const expr = qryValues.map(x => `FACILITY_TYPE LIKE '%${x.value}%'`).join(" OR ");
                defExpression = defExpression ? `${defExpression} AND (${expr})` : `(${expr})`;
            }
            else if(cons === "SLA_SS_CONS_R" && fldName === "SITE_AREA"){
                if(qryValues && qryValues.length > 0){
                    const fromVal = qryValues[0].from;
                    const toVal = qryValues[0].to;
                    const selectedValues = qryValues[0].selectedValues || [];
                    const exprParts = [];
                    if (fromVal !== '' && !isNaN(fromVal)) exprParts.push(`SITE_AREA >= ${Number(fromVal)}`);
                    if (toVal !== '' && !isNaN(toVal)) exprParts.push(`SITE_AREA < ${Number(toVal)}`);
                    if (selectedValues.length > 0) exprParts.push(`SITE_AREA IN (${selectedValues.map(Number).join(",")})`);
            
                    if (exprParts.length > 0) {
                        defExpression = defExpression
                            ? `${defExpression} AND (${exprParts.join(" AND ")})`
                            : `(${exprParts.join(" AND ")})`;
                    }
                }
            }
            else if(cons === "SLA_SS_CONS_R" && fldName === "TOTAL_GFA"){
                const fromVal = qryValues[0].from;
                const toVal = qryValues[0].to;
                const selectedValues = qryValues[0].selectedValues || [];
                const exprParts = [];

                if (fromVal !== '' && !isNaN(fromVal)) exprParts.push(`TOTAL_GFA >= ${Number(fromVal)}`);
                if (toVal !== '' && !isNaN(toVal)) exprParts.push(`TOTAL_GFA < ${Number(toVal)}`);
                if (selectedValues.length > 0) exprParts.push(`TOTAL_GFA IN (${selectedValues.map(Number).join(",")})`);

                if (exprParts.length > 0) {
                    defExpression = defExpression ? `${defExpression} AND (${exprParts.join(" AND ")})` : `(${exprParts.join(" AND ")})`;
                }
            }
            else if (cons === "SLA_SS_CONS_R" && fldName === "TENURE_DATE") {
                const filterStart = qryValues[0]?.start;
                const filterEnd = qryValues[0]?.end;
                if (filterStart && filterEnd) {
                    const overlapExpr = `(TENANT_STARTDATE <= '${filterEnd}' AND TENANT_ENDDATE >= '${filterStart}')`;
                    defExpression = defExpression ? `${defExpression} AND ${overlapExpr}` : overlapExpr;
                }
            }
            else if (cons === "SLA_SS_CONS_R" && fldName === "PAST_APPROVED_USERS") {
                const currentUseCondition = qryValues
                    .map(x => `CURRENT_USE_TYPE LIKE '%${x.value}%'`)
                    .join(" OR ");
                if (currentUseCondition) {
                    defExpression = defExpression ? `${defExpression} AND (${currentUseCondition})` : `(${currentUseCondition})`;
                }
            }
            else if (fldName === "REGION_N" || fldName === "PLN_AREA_N") {
                const expr = qryValues
                    .map(x => `${fldName} LIKE '${x.value}%' OR ${fldName} LIKE '%${x.value}%'`)
                    .join(" OR ");
                defExpression = defExpression ? `${defExpression} AND (${expr})` : `(${expr})`;
            }
            else if (
                (cons === "DORMS_CONS_R" && fldName === "FINAL_BEDS") ||
                (cons === "DORMITORY_CONS_R" && fldName === "FINAL_BEDS") ||
                fldName === "STAGE_YR_L"
            ) {
                const expr = `(${fldName} >= ${qryValues[0].value} AND ${fldName} <= ${qryValues[1].value})`;
                defExpression = defExpression ? `${defExpression} AND ${expr}` : expr;
            }
            else if ((fldName === "DISTANCE_FROM_BUS" || fldName === "DISTANCE_FROM_MRT") && qryValues.length === 2) {
                const minVal = qryValues[0].value;
                const maxVal = qryValues[1].value;
                const distField = fldName === "DISTANCE_FROM_BUS" ? "NEAREST_BUS_DIST" : "NEAREST_MRT_DIST";
                if (minVal != null && maxVal != null && (minVal !== 0 || maxVal !== 1000)) {
                    const expr = `(${distField} >= ${minVal} AND ${distField} <= ${maxVal})`;
                    defExpression = defExpression ? `${defExpression} AND ${expr}` : expr;
                }
            }
            else {
                const nonEmptyValues = qryValues.map(x => x.value).filter(v => v !== '' && v != null);
                if (nonEmptyValues.length > 0) {
                    const expr = `${fldName} IN ('${nonEmptyValues.join("','")}')`;
                    defExpression = defExpression ? `${defExpression} AND (${expr})` : `(${expr})`;
                }
            }
        });
        return defExpression;
    }
    catch(error){
        console.error("Error in getDefinitionExpression:", error);
        return "";
    }
}

const ZoomGraphicsExtent = async (_queryLayersForGraphics, mapView) => {
    let promises = _queryLayersForGraphics.map(async layer => {
        const res = await queryGraphics(layer);
        return res;
    });
    let allGraphicsArrays = await Promise.all(promises);
    let allGraphics = [].concat.apply([], allGraphicsArrays);
    mapViewZoomToTarget(mapView, allGraphics);
    const graphicLength = allGraphics.length;
    return graphicLength;
}

const SiteSearchZoomGraphicsExtent = async (_queryLayersForGraphics, mapView) => {
    const esriModules = await loadESRIModules([
        "esri/geometry/Extent"
    ]);
    
    let promises = _queryLayersForGraphics.map(async layer => {
        const res = await queryGraphics(layer);
        return res;
    });
    let allGraphicsArrays = await Promise.all(promises);
    let allGraphics = [].concat.apply([], allGraphicsArrays);
    
    // Calculate the combined extent of all graphics
    let extent = null;
    allGraphics.forEach(graphic => {
        if (graphic.geometry && graphic.geometry.extent) {
            if (!extent) {
                extent = graphic.geometry.extent.clone();
            } else {
                extent = extent.union(graphic.geometry.extent);
            }
        }
    });
    
    // Apply zoom with expanded extent for better visibility
    if (extent) {
        // Adjust this value to control zoom level:
        // 1.0 = no padding, 1.5 = 50% more area, 2.0 = 100% more area, etc.
        const expandFactor = 1.5;
        const expandedExtent = extent.expand(expandFactor);
        
        mapView.goTo(expandedExtent, {
            duration: 1000 // Animation duration in milliseconds
        }).catch((err) => {
            console.error("Zoom Error: ", err.message);
        });
    } else if (allGraphics.length > 0) {
        // Fallback to original method if extent calculation fails
        mapViewZoomToTarget(mapView, allGraphics);
    }
    
    const graphicLength = allGraphics.length;
    return allGraphicsArrays != [] ? allGraphicsArrays[allGraphicsArrays.length - 1] : [];
}


export const queryGraphics = async (layer) => {
    const esriModules = await loadESRIModules([
        "esri/rest/query/executeQueryJSON",
        "esri/rest/support/Query",
    ]);

    let query = new esriModules.Query();
    query.returnGeometry = true;
    query.outFields = ["*"];
    query.where = layer.whereClause;

    // Execute the query to get the filtered features
    const response = await esriModules.executeQueryJSON.executeQueryJSON(
        layer.url,
        query
    );
    const features = response.features;
    const filterfeaturescount = features.length;
    return response.features;
}
