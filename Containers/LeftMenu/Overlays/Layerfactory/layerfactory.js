// To prefix dynamic styles from @mui components with "epl" in order to avoid conflict with onetool components
import { StylesProvider, createGenerateClassName } from '@mui/styles';
import { unstable_ClassNameGenerator as ClassNameGenerator } from "@mui/material/className";
import { CacheProvider } from "@emotion/react";
import createCache from "@emotion/cache";

const EPL_CSS_PREFIX = 'epl-exportjss';

const generateClassName = createGenerateClassName({
    productionPrefix: EPL_CSS_PREFIX
});
ClassNameGenerator.configure((componentName) => `${EPL_CSS_PREFIX}${componentName}`);
const cache = createCache({
    key: "epl",
    prepend: true,
});

import { loadModules } from 'esri-loader';

import React from 'react';
import WebApi from './WebApi';
import OneToolMapData from './onetool';
import { isValidMapConfig, getErrorMsgs, clearErrorMsgs } from "./functions/configvalidator";
import Layer from './functions/layer';
Layer.prototype.postIdentify = Layer.prototype.extPostIdentify

import mp19landuselayer from './entities/mp19landuselayer';
import parkscorelayer from './entities/parkscorelayer';
import salessitelayer from './entities/salessitelayer';
//import marinedatalayer from './entities/marinedatalayer';
import rentalofstatelandlayer from './entities/rentalofstatelandlayer';
//import parkinglotlayer from './entities/parkinglotlayer';
import retaildensitylayer from './entities/retaildensitylayer';
//import developmentchargerateslayer from './entities/developmentchargerateslayer';

import { initDevEnv, ConfigStoreInt, buildToDeployServer } from "./functions/util";


const hasFunc = (obj, funcName) => typeof obj[funcName] === 'function';

class LayerFactory {

    constructor() {
        this._rebuildUrls = false;
        this._classes = {};
        this._classes['mp19landuselayer'] = mp19landuselayer;
        this._classes['parkscorelayer'] = parkscorelayer;
        this._classes['salessitelayer'] = salessitelayer;
        //this._classes['marinedatalayer'] = marinedatalayer;
        this._classes['rentalofstatelandlayer'] = rentalofstatelandlayer;
        //this._classes['parkinglotlayer'] = parkinglotlayer;
        this._classes['retaildensitylayer'] = retaildensitylayer;
        //this._classes['developmentchargerateslayer'] = developmentchargerateslayer;

        Layer.prototype._getFilterbox = Layer.prototype.getFilterbox;
        Layer.prototype.getFilterbox = function getFilterbox() {
            const ret = this._getFilterbox();
            return ret == null ? ret :
                <CacheProvider value={cache}>
                    <StylesProvider generateClassName={generateClassName}>
                        {ret}
                    </StylesProvider>
                </CacheProvider>;
        }

        Layer.prototype._getIdentifyDisplay = Layer.prototype.getIdentifyDisplay;
        Layer.prototype.getIdentifyDisplay = function getIdentifyDisplay(...params) {
            const ret = this._getIdentifyDisplay(...params);
            return ret == null ? ret :
                <CacheProvider value={cache}>
                    <StylesProvider generateClassName={generateClassName}>
                        {ret}
                    </StylesProvider>
                </CacheProvider>;
        }
    }

    _getLayer(name, opts, token, messenger, layerWrapper) {
        //only empty name (which is default ArcGIS layers) and imported layers are allowed for now
        var layerClass = this._classes[name] ? this._classes[name] : Layer;
        opts.messenger = messenger;
        opts.wrapper = layerWrapper;

        return layerClass ? new layerClass(opts, token) : null;
    }

    typeOf(obj, cls) {
        return (obj === cls || obj.prototype instanceof cls);
    }

    setupDevelopmentEnvs(url, sr = 4326, env = "EXTRANET") {
        this._rebuildUrls = true;
        Object.assign(ConfigStoreInt, {
            export: true,
            server: url,
            sr: sr,
            environment: env,
        });

        initDevEnv();
    }

    getLayers(mapWrapper, layerWrapper, messenger, token) {
        if (!this._layers) {
            this._layers = this._getLayers(mapWrapper, layerWrapper, messenger, token);
        }

        return this._layers;
    }

    _getLayers(mapWrapper, layerWrapper, messenger, token) {

        WebApi.registerTokenGetter(() => token);

        if (!isValidMapConfig(OneToolMapData)) {
            console.error("Invalid MapData Config");
            console.error(getErrorMsgs());
            clearErrorMsgs();
        }

        return OneToolMapData.map(categoryConfig => {

            let layers = [];
            categoryConfig.layers.forEach(layerConfig => {
                try {
                    layerConfig.src = this._rebuildUrls ? buildToDeployServer(layerConfig.src) : layerConfig.src;

                    let layer = this._getLayer(layerConfig.class, layerConfig, token, messenger, layerWrapper);

                    if (layer) {
                        layer.setMap(mapWrapper);
                        layers.push(layer);
                    }

                } catch (ex) {
                    console.log("Error caught in creating layer - " + layerConfig.name); //TODO: rethink about the error handling strategy
                }
            });

            return {
                name: categoryConfig.category,
                icon: categoryConfig.icon,
                iconColor: categoryConfig.iconColor,
                isInfra: categoryConfig.isInfra,
                layers: layers,
            };
        }).filter(categoryConfig => {
            return categoryConfig.layers.length > 0;
        });
    }
}

//expose obj in window/global
var g = window || global;
g["LayerFactory"] = new LayerFactory();
