import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
    getLatestSensorData,
    getIrrigationPrediction,
    getWeatherByCoordinates,
} from "../services/api";

import "./Irrigation.css";


/* =========================================================
   TRANSLATIONS
========================================================= */

const translations = {
    en: {
        back: "← Back to Dashboard",
        eyebrow: "SMART WATER MANAGEMENT",
        title: "Irrigation Prediction",
        subtitle:
            "Analyze live soil, sensor and weather conditions to determine the irrigation requirement for your crop.",

        analysis: "Irrigation Analysis",
        analysisSubtitle: "Live farm conditions",
        live: "LIVE",

        sensors: "Sensor Data",
        soilMoisture: "Soil Moisture",
        temperature: "Temperature",
        humidity: "Humidity",
        rainfall: "Rainfall",
        soilTemperature: "Soil Temperature",
        windSpeed: "Wind Speed",
        nitrogen: "Nitrogen",
        phosphorus: "Phosphorus",
        potassium: "Potassium",

        location: "Farm Location",
        detecting: "Detecting location...",
        locationDetected: "Location detected",
        locationUnavailable: "Location unavailable",

        crop: "Select Crop",
        selectCrop: "Select your crop",

        weather: "Weather Preview",
        currentWeather: "Current weather conditions",
        rainForecast: "Rain Forecast",
        wind: "Wind",
        forecast: "Rain Probability",

        predict: "Predict Irrigation",
        predicting: "Analyzing...",

        result: "Irrigation Result",
        resultSubtitle: "AI-powered irrigation recommendation",

        waiting: "Waiting for prediction",
        waitingText:
            "Select your crop and analyze the current farm conditions to get an irrigation recommendation.",

        status: "Irrigation Status",
        waterNeed: "Water Need",
        reason: "Reason",
        score: "Irrigation Score",
        model: "Model",
        features: "Features Used",
        cropType: "Crop",

        moisture: "Soil Moisture",
        weatherTemperature: "Weather Temperature",
        weatherHumidity: "Weather Humidity",
        rainProbability: "Rain Probability",
        mlPrediction: "ML Prediction",
        modelPrediction: "Model Prediction",
        modelBased: "Machine learning output",

        advice: "Smart Advice",

        notification: "Notification",
        notificationSent: "Notification created",
        notificationNotRequired: "No notification required",
        notificationSuccess:
            "An irrigation notification has been created for your dashboard.",
        notificationNone:
            "Current conditions do not require an irrigation notification.",

        noData: "No sensor data available",
        loading: "Loading live farm data...",

        healthy: "Monitor",
        irrigateNow: "Irrigate now",
        irrigateSoon: "Irrigate soon",
        noIrrigation: "No irrigation",

        probabilityNow: "Irrigate Now",
        probabilitySoon: "Irrigate Soon",
        probabilityMonitor: "Monitor",
        probabilityNone: "No Irrigation",

        sensorUnavailable: "Unavailable",
        weatherUnavailable: "Weather unavailable",

        errorSensor:
            "Unable to load live sensor data.",
        errorWeather:
            "Unable to load weather information.",
        errorPrediction:
            "Unable to generate irrigation prediction.",
        selectCropError:
            "Please select a crop before predicting.",
    },


    kn: {
        back: "← ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಹಿಂತಿರುಗಿ",
        eyebrow: "ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ ನಿರ್ವಹಣೆ",
        title: "ನೀರಾವರಿ ಮುನ್ಸೂಚನೆ",
        subtitle:
            "ನಿಮ್ಮ ಬೆಳೆಗೆ ನೀರಾವರಿ ಅಗತ್ಯವನ್ನು ನಿರ್ಧರಿಸಲು ಮಣ್ಣು, ಸೆನ್ಸರ್ ಮತ್ತು ಹವಾಮಾನ ಮಾಹಿತಿಯನ್ನು ವಿಶ್ಲೇಷಿಸಿ.",

        analysis: "ನೀರಾವರಿ ವಿಶ್ಲೇಷಣೆ",
        analysisSubtitle: "ಲೈವ್ ಕೃಷಿ ಪರಿಸ್ಥಿತಿಗಳು",
        live: "ಲೈವ್",

        sensors: "ಸೆನ್ಸರ್ ಮಾಹಿತಿ",
        soilMoisture: "ಮಣ್ಣಿನ ತೇವಾಂಶ",
        temperature: "ತಾಪಮಾನ",
        humidity: "ಆರ್ದ್ರತೆ",
        rainfall: "ಮಳೆ",
        soilTemperature: "ಮಣ್ಣಿನ ತಾಪಮಾನ",
        windSpeed: "ಗಾಳಿಯ ವೇಗ",
        nitrogen: "ಸಾರಜನಕ",
        phosphorus: "ರಂಜಕ",
        potassium: "ಪೊಟ್ಯಾಸಿಯಮ್",
        location: "ಕೃಷಿ ಸ್ಥಳ",
        detecting: "ಸ್ಥಳ ಪತ್ತೆ ಮಾಡಲಾಗುತ್ತಿದೆ...",
        locationDetected: "ಸ್ಥಳ ಪತ್ತೆಯಾಗಿದೆ",
        locationUnavailable: "ಸ್ಥಳ ಲಭ್ಯವಿಲ್ಲ",

        crop: "ಬೆಳೆ ಆಯ್ಕೆಮಾಡಿ",
        selectCrop: "ನಿಮ್ಮ ಬೆಳೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",

        weather: "ಹವಾಮಾನ ಮಾಹಿತಿ",
        currentWeather: "ಪ್ರಸ್ತುತ ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿಗಳು",
        rainForecast: "ಮಳೆ ಮುನ್ಸೂಚನೆ",
        wind: "ಗಾಳಿ",
        forecast: "ಮಳೆಯ ಸಾಧ್ಯತೆ",

        predict: "ನೀರಾವರಿ ಮುನ್ಸೂಚನೆ",
        predicting: "ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...",

        result: "ನೀರಾವರಿ ಫಲಿತಾಂಶ",
        resultSubtitle: "AI ಆಧಾರಿತ ನೀರಾವರಿ ಶಿಫಾರಸು",

        waiting: "ಮುನ್ಸೂಚನೆಗಾಗಿ ಕಾಯಲಾಗುತ್ತಿದೆ",
        waitingText:
            "ನಿಮ್ಮ ಬೆಳೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ ಮತ್ತು ಪ್ರಸ್ತುತ ಕೃಷಿ ಪರಿಸ್ಥಿತಿಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಿ.",

        status: "ನೀರಾವರಿ ಸ್ಥಿತಿ",
        waterNeed: "ನೀರಿನ ಅಗತ್ಯ",
        reason: "ಕಾರಣ",
        score: "ನೀರಾವರಿ ಸ್ಕೋರ್",
        model: "ಮಾದರಿ",
        features: "ಬಳಸಿದ ವೈಶಿಷ್ಟ್ಯಗಳು",
        cropType: "ಬೆಳೆ",

        moisture: "ಮಣ್ಣಿನ ತೇವಾಂಶ",
        weatherTemperature: "ಹವಾಮಾನ ತಾಪಮಾನ",
        weatherHumidity: "ಹವಾಮಾನ ಆರ್ದ್ರತೆ",
        rainProbability: "ಮಳೆಯ ಸಾಧ್ಯತೆ",
        mlPrediction: "ML ಮುನ್ಸೂಚನೆ",
        modelPrediction: "ಮಾದರಿ ಮುನ್ಸೂಚನೆ",
        modelBased: "ಮಷಿನ್ ಲರ್ನಿಂಗ್ ಫಲಿತಾಂಶ",

        advice: "ಸ್ಮಾರ್ಟ್ ಸಲಹೆ",

        notification: "ಅಧಿಸೂಚನೆ",
        notificationSent: "ಅಧಿಸೂಚನೆ ರಚಿಸಲಾಗಿದೆ",
        notificationNotRequired:
            "ಅಧಿಸೂಚನೆ ಅಗತ್ಯವಿಲ್ಲ",
        notificationSuccess:
            "ನಿಮ್ಮ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗಾಗಿ ನೀರಾವರಿ ಅಧಿಸೂಚನೆಯನ್ನು ರಚಿಸಲಾಗಿದೆ.",
        notificationNone:
            "ಪ್ರಸ್ತುತ ಪರಿಸ್ಥಿತಿಗಳಿಗೆ ನೀರಾವರಿ ಅಧಿಸೂಚನೆಯ ಅಗತ್ಯವಿಲ್ಲ.",

        noData: "ಸೆನ್ಸರ್ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ",
        loading: "ಲೈವ್ ಕೃಷಿ ಮಾಹಿತಿ ಲೋಡ್ ಆಗುತ್ತಿದೆ...",

        healthy: "ಮೇಲ್ವಿಚಾರಣೆ",
        irrigateNow: "ಈಗ ನೀರಾವರಿ ಮಾಡಿ",
        irrigateSoon: "ಶೀಘ್ರದಲ್ಲೇ ನೀರಾವರಿ ಮಾಡಿ",
        noIrrigation: "ನೀರಾವರಿ ಅಗತ್ಯವಿಲ್ಲ",

        probabilityNow: "ಈಗ ನೀರಾವರಿ",
        probabilitySoon: "ಶೀಘ್ರದಲ್ಲೇ ನೀರಾವರಿ",
        probabilityMonitor: "ಮೇಲ್ವಿಚಾರಣೆ",
        probabilityNone: "ನೀರಾವರಿ ಇಲ್ಲ",

        sensorUnavailable: "ಲಭ್ಯವಿಲ್ಲ",
        weatherUnavailable: "ಹವಾಮಾನ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ",

        errorSensor:
            "ಲೈವ್ ಸೆನ್ಸರ್ ಮಾಹಿತಿಯನ್ನು ಪಡೆಯಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
        errorWeather:
            "ಹವಾಮಾನ ಮಾಹಿತಿಯನ್ನು ಪಡೆಯಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
        errorPrediction:
            "ನೀರಾವರಿ ಮುನ್ಸೂಚನೆ ನೀಡಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
        selectCropError:
            "ಮುನ್ಸೂಚನೆ ನೀಡುವ ಮೊದಲು ಬೆಳೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ.",
    },
};


/* =========================================================
   CROPS
========================================================= */

const CROPS = [
    {
        value: "rice",
        en: "Rice",
        kn: "ಭತ್ತ",
    },
    {
        value: "maize",
        en: "Maize",
        kn: "ಮೆಕ್ಕೆಜೋಳ",
    },
    {
        value: "chickpea",
        en: "Chickpea",
        kn: "ಕಡಲೆ",
    },
    {
        value: "cotton",
        en: "Cotton",
        kn: "ಹತ್ತಿ",
    },
    {
        value: "wheat",
        en: "Wheat",
        kn: "ಗೋಧಿ",
    },
    {
        value: "groundnut",
        en: "Groundnut",
        kn: "ಕಡಲೆಕಾಯಿ",
    },
    {
        value: "banana",
        en: "Banana",
        kn: "ಬಾಳೆಹಣ್ಣು",
    },
    {
        value: "sugarcane",
        en: "Sugarcane",
        kn: "ಕಬ್ಬು",
    },
    {
        value: "tomato",
        en: "Tomato",
        kn: "ಟೊಮೇಟೊ",
    },
    {
        value: "potato",
        en: "Potato",
        kn: "ಆಲೂಗಡ್ಡೆ",
    },
    {
        value: "onion",
        en: "Onion",
        kn: "ಈರುಳ್ಳಿ",
    },
    {
        value: "turmeric",
        en: "Turmeric",
        kn: "ಅರಿಶಿನ",
    },
    {
        value: "chilli",
        en: "Chilli",
        kn: "ಮೆಣಸಿನಕಾಯಿ",
    },
    {
        value: "sorghum",
        en: "Sorghum",
        kn: "ಜೋಳ",
    },
    {
        value: "millet",
        en: "Millet",
        kn: "ಸಿರಿಧಾನ್ಯ",
    },
    {
        value: "ragi",
        en: "Ragi",
        kn: "ರಾಗಿ",
    },
    {
        value: "soybean",
        en: "Soybean",
        kn: "ಸೋಯಾಬೀನ್",
    },
    {
        value: "pigeon_pea",
        en: "Pigeon Pea",
        kn: "ತೊಗರಿ ಬೇಳೆ",
    },
    {
        value: "okra",
        en: "Okra",
        kn: "ಬೆಂಡೆಕಾಯಿ",
    },
    {
        value: "cabbage",
        en: "Cabbage",
        kn: "ಎಲೆಕೋಸು",
    },
    {
        value: "carrot",
        en: "Carrot",
        kn: "ಕ್ಯಾರೆಟ್",
    },
];


/* =========================================================
   HELPERS
========================================================= */

const numberValue = (value, fallback = 0) => {
    const n = Number(value);

    return Number.isFinite(n)
        ? n
        : fallback;
};


const formatNumber = (value, digits = 1) => {
    const n = Number(value);

    if (!Number.isFinite(n)) {
        return "--";
    }

    return n.toFixed(digits);
};


/* =========================================================
   STATUS CLASS
========================================================= */

const getStatusClass = (status = "") => {
    const value =
        String(status).toLowerCase().trim();

    if (
        value.includes("irrigate now") ||
        value === "now"
    ) {
        return "status-now";
    }

    if (
        value.includes("irrigate soon") ||
        value === "soon"
    ) {
        return "status-soon";
    }

    if (
        value.includes("monitor")
    ) {
        return "status-monitor";
    }

    return "status-none";
};


/* =========================================================
   STATUS TRANSLATION
========================================================= */

const translateStatus = (status, t) => {
    if (!status) {
        return "--";
    }

    const value =
        String(status).toLowerCase();

    if (
        value.includes("irrigate now")
    ) {
        return t.irrigateNow;
    }

    if (
        value.includes("irrigate soon")
    ) {
        return t.irrigateSoon;
    }

    if (
        value.includes("monitor")
    ) {
        return t.healthy;
    }

    if (
        value.includes("no irrigation")
    ) {
        return t.noIrrigation;
    }

    return status;
};


/* =========================================================
   ML STATUS TRANSLATION
========================================================= */

const translateMLPrediction = (
    prediction,
    t
) => {
    if (
        prediction === null ||
        prediction === undefined ||
        prediction === ""
    ) {
        return "--";
    }

    const value =
        String(prediction).toLowerCase();

    if (
        value.includes("irrigate now")
    ) {
        return t.irrigateNow;
    }

    if (
        value.includes("irrigate soon")
    ) {
        return t.irrigateSoon;
    }

    if (
        value.includes("monitor")
    ) {
        return t.healthy;
    }

    if (
        value.includes("no irrigation")
    ) {
        return t.noIrrigation;
    }

    return prediction;
};


/* =========================================================
   PROBABILITY NORMALIZER
========================================================= */

const normalizeProbability = (value) => {
    const n = Number(value);

    if (!Number.isFinite(n)) {
        return 0;
    }

    const percentage =
        n <= 1
            ? n * 100
            : n;

    return Math.min(
        Math.max(
            percentage,
            0
        ),
        100
    );
};


/* =========================================================
   COMPONENT
========================================================= */

export default function Irrigation() {

    const navigate =
        useNavigate();


    /* =====================================================
       LANGUAGE
    ===================================================== */

    const [language, setLanguage] =
        useState("en");

    const t =
        translations[language];


    /* =====================================================
       STATE
    ===================================================== */

    const [cropType, setCropType] =
        useState("");

    const [sensorData, setSensorData] =
        useState(null);

    const [weatherData, setWeatherData] =
        useState(null);

    const [location, setLocation] =
        useState("");

    const [coordinates, setCoordinates] =
        useState(null);

    const [result, setResult] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [predicting, setPredicting] =
        useState(false);

    const [error, setError] =
        useState("");

    const [locationLoading, setLocationLoading] =
        useState(true);


    /* =====================================================
       FETCH SENSOR DATA
    ===================================================== */

    const loadSensorData = async () => {

        try {

            const response =
                await getLatestSensorData();

            const raw =
                response?.data ?? response;

            const data =
                raw?.data ??
                raw?.sensor_data ??
                raw?.latest ??
                raw;

            setSensorData(
                data || null
            );

        } catch (err) {

            console.error(
                "Irrigation sensor error:",
                err
            );

            setError(
                t.errorSensor
            );

        }

    };


    /* =====================================================
       FETCH WEATHER
    ===================================================== */

    const loadWeather = async (
        latitude,
        longitude
    ) => {

        try {

            const response =
                await getWeatherByCoordinates(
                    latitude,
                    longitude
                );

            const raw =
                response?.data ?? response;

            const data =
                raw?.data ??
                raw?.weather ??
                raw;

            setWeatherData(
                data || null
            );

        } catch (err) {

            console.error(
                "Irrigation weather error:",
                err
            );

            /*
             * Weather failure should not
             * destroy sensor data.
             */

        }

    };


    /* =====================================================
       LOCATION
    ===================================================== */

    const detectLocation = () => {

        setLocationLoading(true);

        if (!navigator.geolocation) {

            setLocation(
                t.locationUnavailable
            );

            setLocationLoading(false);

            return;
        }


        navigator.geolocation.getCurrentPosition(

            async (position) => {

                const latitude =
                    position.coords.latitude;

                const longitude =
                    position.coords.longitude;


                setCoordinates({
                    latitude,
                    longitude,
                });


                const locationText =
                    `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;


                setLocation(
                    locationText
                );


                setLocationLoading(false);


                await loadWeather(
                    latitude,
                    longitude
                );

            },


            (err) => {

                console.error(
                    "Location error:",
                    err
                );

                setLocation(
                    t.locationUnavailable
                );

                setLocationLoading(false);

            },


            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000,
            }
        );
    };


    /* =====================================================
       INITIAL LOAD
    ===================================================== */

    useEffect(() => {

        let mounted = true;


        const initialize = async () => {

            setLoading(true);

            await loadSensorData();


            if (mounted) {

                detectLocation();

                setLoading(false);

            }

        };


        initialize();


        return () => {

            mounted = false;

        };

    }, []);


    /* =====================================================
       LIVE SENSOR REFRESH
    ===================================================== */

    useEffect(() => {

        const interval =
            setInterval(() => {

                loadSensorData();

            }, 30000);


        return () => {

            clearInterval(interval);

        };

    }, []);


    /* =====================================================
       WEATHER REFRESH
    ===================================================== */

    useEffect(() => {

        if (!coordinates) {
            return;
        }


        const interval =
            setInterval(() => {

                loadWeather(
                    coordinates.latitude,
                    coordinates.longitude
                );

            }, 30000);


        return () => {

            clearInterval(interval);

        };

    }, [coordinates]);


    /* =====================================================
       SENSOR VALUES
    ===================================================== */

    const values = useMemo(() => {

        const data =
            sensorData || {};


        return {

            soilMoisture:
                numberValue(
                    data.soil_moisture ??
                    data.soilMoisture ??
                    data.moisture
                ),

            temperature:
                numberValue(
                    data.temperature
                ),

            humidity:
                numberValue(
                    data.humidity
                ),

            rainfall:
                numberValue(
                    data.rainfall ??
                    data.rain
                ),

            soilTemperature:
                numberValue(
                    data.soil_temperature ??
                    data.soil_temp ??
                    data.temperature
                ),

            windSpeed:
                numberValue(
                    data.wind_speed ??
                    data.wind
                ),

            nitrogen:
                numberValue(
                    data.nitrogen
                ),

            phosphorus:
                numberValue(
                    data.phosphorus
                ),

            potassium:
                numberValue(
                    data.potassium
                )
        };

    }, [sensorData]);


    /* =====================================================
       WEATHER VALUES
    ===================================================== */

    const weather = useMemo(() => {

        const data =
            weatherData || {};


        const current =
            data.current ||
            data.current_weather ||
            data.weather ||
            data;


        return {

            temperature:
                numberValue(
                    current.temperature ??
                    current.temperature_2m ??
                    values.temperature
                ),

            humidity:
                numberValue(
                    current.humidity ??
                    current.relative_humidity_2m ??
                    values.humidity
                ),

            rainfall:
                numberValue(
                    current.rainfall ??
                    current.rain ??
                    current.precipitation ??
                    values.rainfall
                ),

            windSpeed:
                numberValue(
                    current.wind_speed ??
                    current.wind_speed_10m ??
                    values.windSpeed
                ),

            rainProbability:
                numberValue(
                    current.rain_probability ??
                    current.precipitation_probability ??
                    data.rain_probability ??
                    data.rain_forecast ??
                    0
                ),

        };

    }, [weatherData, values]);


    /* =====================================================
       PREDICT IRRIGATION
    ===================================================== */

    const handlePrediction = async () => {

        if (!cropType) {

            setError(
                t.selectCropError
            );

            return;
        }


        if (!sensorData) {

            setError(
                t.errorSensor
            );

            return;
        }


        setError("");
        setPredicting(true);


        try {

            /*
             * Field names match IrrigationInput.
             */

            const payload = {

                crop_type:
                    cropType,

                location:
                    location &&
                    location !== t.locationUnavailable
                        ? location
                        : "Unknown",

                soil_moisture:
                    values.soilMoisture,

                humidity:
                    values.humidity,

                temperature:
                    values.temperature,

                rainfall:
                    values.rainfall,

                soil_temperature:
                    values.soilTemperature,

                wind_speed:
                    values.windSpeed,

                rain_forecast:
                    weather.rainProbability,

                nitrogen:
                    values.nitrogen,

                phosphorus:
                    values.phosphorus,

                potassium:
                    values.potassium
            };


            console.log(
                "===================================="
            );

            console.log(
                "IRRIGATION PAYLOAD:",
                payload
            );

            console.log(
                "===================================="
            );


            const response =
                await getIrrigationPrediction(
                    payload
                );


            const raw =
                response?.data ?? response;


            const data =
                raw?.data ??
                raw;


            console.log(
                "===================================="
            );

            console.log(
                "IRRIGATION RESPONSE:",
                data
            );

            console.log(
                "===================================="
            );


            setResult(
                data
            );

        } catch (err) {

            console.error(
                "Irrigation prediction error:",
                err
            );


            const backendMessage =
                err?.response?.data?.detail;


            setError(
                backendMessage ||
                t.errorPrediction
            );

        } finally {

            setPredicting(false);

        }

    };


    /* =====================================================
       PROBABILITIES
    ===================================================== */

    const probabilities = useMemo(() => {

        if (!result) {
            return [];
        }


        const possible =
            result.prediction_probabilities ||
            result.probabilities ||
            result.class_probabilities;


        if (
            possible &&
            typeof possible === "object"
        ) {

            return [

                {
                    label:
                        t.probabilityNow,

                    value:
                        normalizeProbability(
                            possible["Irrigate now"] ??
                            possible["irrigate_now"] ??
                            possible["now"] ??
                            0
                        ),
                },


                {
                    label:
                        t.probabilitySoon,

                    value:
                        normalizeProbability(
                            possible["Irrigate soon"] ??
                            possible["irrigate_soon"] ??
                            possible["soon"] ??
                            0
                        ),
                },


                {
                    label:
                        t.probabilityMonitor,

                    value:
                        normalizeProbability(
                            possible["Monitor"] ??
                            possible["monitor"] ??
                            0
                        ),
                },


                {
                    label:
                        t.probabilityNone,

                    value:
                        normalizeProbability(
                            possible["No irrigation"] ??
                            possible["no_irrigation"] ??
                            possible["none"] ??
                            0
                        ),
                },

            ];

        }


        return [];

    }, [result, t]);


    /* =====================================================
       SELECTED CROP
    ===================================================== */

    const selectedCrop =
        CROPS.find(
            (crop) =>
                crop.value === cropType
        );


    /* =====================================================
       RENDER
    ===================================================== */

    return (

        <div className="irrigation-page">


            {/* =================================================
               TOP BAR
            ================================================= */}

            <div className="irrigation-top-bar">

                <button
                    type="button"
                    className="irrigation-language-button"
                    onClick={() =>
                        navigate("/dashboard")
                    }
                >
                    {t.back}
                </button>


                <button
                    type="button"
                    className="irrigation-language-button"
                    onClick={() =>
                        setLanguage(
                            language === "en"
                                ? "kn"
                                : "en"
                        )
                    }
                >
                    {language === "en"
                        ? "ಕನ್ನಡ"
                        : "English"}
                </button>

            </div>


            {/* =================================================
               HEADER
            ================================================= */}

            <header className="irrigation-header">

                <span className="irrigation-eyebrow">

                    {t.eyebrow}

                </span>


                <h1>

                    💧 {t.title}

                </h1>


                <p>

                    {t.subtitle}

                </p>

            </header>


            {/* =================================================
               ERROR
            ================================================= */}

            {error && (

                <div
                    className="irrigation-error"
                    role="alert"
                >

                    <span>
                        ⚠️
                    </span>

                    <span>
                        {error}
                    </span>

                </div>

            )}


            {/* =================================================
               MAIN CONTAINER
            ================================================= */}

            <div className="irrigation-container">


                {/* =================================================
                   ANALYSIS CARD
                ================================================= */}

                <section className="irrigation-analysis-card">


                    {/* CARD HEADING */}

                    <div className="irrigation-card-heading">

                        <div>

                            <span>
                                💧
                            </span>


                            <div>

                                <h2>
                                    {t.analysis}
                                </h2>

                                <p>
                                    {t.analysisSubtitle}
                                </p>

                            </div>

                        </div>


                        <div className="irrigation-live-indicator">

                            <i />

                            {t.live}

                        </div>

                    </div>


                    {/* =================================================
                       SENSOR GRID
                    ================================================= */}

                    <div className="irrigation-sensor-grid">


                        <SensorCard
                            icon="💧"
                            label={t.soilMoisture}
                            value={
                                sensorData
                                    ? formatNumber(
                                        values.soilMoisture
                                    )
                                    : "--"
                            }
                            unit="%"
                            important
                        />


                        <SensorCard
                            icon="🌡️"
                            label={t.temperature}
                            value={
                                sensorData
                                    ? formatNumber(
                                        values.temperature
                                    )
                                    : "--"
                            }
                            unit="°C"
                        />


                        <SensorCard
                            icon="💦"
                            label={t.humidity}
                            value={
                                sensorData
                                    ? formatNumber(
                                        values.humidity
                                    )
                                    : "--"
                            }
                            unit="%"
                        />


                        <SensorCard
                            icon="🌧️"
                            label={t.rainfall}
                            value={
                                sensorData
                                    ? formatNumber(
                                        values.rainfall
                                    )
                                    : "--"
                            }
                            unit="mm"
                        />


                        <SensorCard
                            icon="🌱"
                            label={t.soilTemperature}
                            value={
                                sensorData
                                    ? formatNumber(
                                        values.soilTemperature
                                    )
                                    : "--"
                            }
                            unit="°C"
                        />


                        <SensorCard
                            icon="💨"
                            label={t.windSpeed}
                            value={
                                sensorData
                                    ? formatNumber(
                                        values.windSpeed
                                    )
                                    : "--"
                            }
                            unit="m/s"
                        />


                        <SensorCard
                            icon="🧪"
                            label={t.nitrogen}
                            value={
                                sensorData
                                    ? formatNumber(
                                        values.nitrogen
                                    )
                                    : "--"
                            }
                            unit="N"
                        />


                        <SensorCard
                            icon="🧪"
                            label={t.phosphorus}
                            value={
                                sensorData
                                    ? formatNumber(
                                        values.phosphorus
                                    )
                                    : "--"
                            }
                            unit="P"
                        />


                        <SensorCard
                            icon="🧪"
                            label={t.potassium}
                            value={
                                sensorData
                                    ? formatNumber(
                                        values.potassium
                                    )
                                    : "--"
                            }
                            unit="K"
                        />
                    </div>


                    {/* =================================================
                       LOCATION
                    ================================================= */}

                    <div className="irrigation-location-box">

                        <div className="irrigation-location-icon">
                            📍
                        </div>


                        <div>

                            <strong>
                                {t.location}
                            </strong>


                            <p
                                className={
                                    location &&
                                    !locationLoading &&
                                    location !== t.locationUnavailable
                                        ? "location-detected"
                                        : ""
                                }
                            >

                                {locationLoading
                                    ? t.detecting
                                    : location ||
                                      t.locationUnavailable}

                            </p>


                            {!locationLoading &&
                                location &&
                                location !== t.locationUnavailable && (

                                    <small>
                                        GPS location used
                                    </small>

                                )}

                        </div>

                    </div>


                    {/* =================================================
                       CROP SELECT
                    ================================================= */}

                    <div className="irrigation-input-section">

                        <label htmlFor="irrigation-crop">

                            {t.crop}

                        </label>


                        <select
                            id="irrigation-crop"
                            value={cropType}
                            onChange={(e) => {

                                setCropType(
                                    e.target.value
                                );

                                setError("");
                                setResult(null);

                            }}
                        >

                            <option value="">

                                {t.selectCrop}

                            </option>


                            {CROPS.map(
                                (crop) => (

                                    <option
                                        key={crop.value}
                                        value={crop.value}
                                    >

                                        {language === "kn"
                                            ? crop.kn
                                            : crop.en}

                                    </option>

                                )
                            )}

                        </select>

                    </div>


                    {/* =================================================
                       WEATHER PREVIEW
                    ================================================= */}

                    <div className="irrigation-weather-preview">

                        <div>

                            <span>
                                🌤️
                            </span>


                            <div>

                                <strong>
                                    {t.weather}
                                </strong>

                                <small>
                                    {t.currentWeather}
                                </small>

                            </div>

                        </div>


                        <div className="irrigation-weather-values">


                            <div>

                                <span>
                                    {t.temperature}
                                </span>

                                <strong>

                                    {weatherData
                                        ? `${formatNumber(
                                            weather.temperature
                                        )} °C`
                                        : "--"}

                                </strong>

                            </div>


                            <div>

                                <span>
                                    {t.humidity}
                                </span>

                                <strong>

                                    {weatherData
                                        ? `${formatNumber(
                                            weather.humidity
                                        )} %`
                                        : "--"}

                                </strong>

                            </div>


                            <div>

                                <span>
                                    {t.forecast}
                                </span>

                                <strong>

                                    {weatherData
                                        ? `${formatNumber(
                                            weather.rainProbability
                                        )} %`
                                        : "--"}

                                </strong>

                            </div>

                        </div>

                    </div>


                    {/* =================================================
                       PREDICT BUTTON
                    ================================================= */}

                    <button
                        type="button"
                        className="irrigation-predict-button"
                        onClick={handlePrediction}
                        disabled={
                            predicting ||
                            loading ||
                            !cropType ||
                            !sensorData
                        }
                    >

                        {predicting
                            ? `⏳ ${t.predicting}`
                            : `💧 ${t.predict}`}

                    </button>

                </section>


                {/* =================================================
                   RESULT CARD
                ================================================= */}

                <section className="irrigation-result-card">


                    {/* RESULT HEADING */}

                    <div className="result-heading">

                        <span>
                            📊
                        </span>


                        <div>

                            <h2>
                                {t.result}
                            </h2>

                            <p>
                                {t.resultSubtitle}
                            </p>

                        </div>

                    </div>


                    {/* =================================================
                       NO RESULT
                    ================================================= */}

                    {!result &&
                        !predicting && (

                            <div className="irrigation-empty-result">

                                <div>
                                    💧
                                </div>


                                <strong>
                                    {t.waiting}
                                </strong>


                                <p>
                                    {t.waitingText}
                                </p>

                            </div>

                        )}


                    {/* =================================================
                       LOADING
                    ================================================= */}

                    {predicting && (

                        <div className="irrigation-loading">

                            ⏳ {t.predicting}

                        </div>

                    )}


                    {/* =================================================
                       RESULT
                    ================================================= */}

                    {result &&
                        !predicting && (

                            <>


                                {/* STATUS */}

                                <div
                                    className={`irrigation-status-badge ${getStatusClass(
                                        result.irrigation_status
                                    )}`}
                                >

                                    {translateStatus(
                                        result.irrigation_status,
                                        t
                                    )}

                                </div>


                                {/* =================================================
                                   RESULT GRID
                                ================================================= */}

                                <div className="irrigation-result-grid">


                                    <ResultItem
                                        label={t.status}
                                        value={
                                            translateStatus(
                                                result.irrigation_status,
                                                t
                                            )
                                        }
                                    />


                                    <ResultItem
                                        label={t.waterNeed}
                                        value={
                                            result.water_need
                                        }
                                    />


                                    <ResultItem
                                        label={t.score}
                                        value={
                                            formatNumber(
                                                result.irrigation_score,
                                                3
                                            )
                                        }
                                    />


                                    <ResultItem
                                        label={t.model}
                                        value={
                                            result.model
                                        }
                                    />


                                    <ResultItem
                                        label={t.features}
                                        value={
                                            result.features_used
                                        }
                                    />


                                    <ResultItem
                                        label={t.cropType}
                                        value={
                                            selectedCrop
                                                ? language === "kn"
                                                    ? selectedCrop.kn
                                                    : selectedCrop.en
                                                : result.crop_type
                                        }
                                    />


                                    <ResultItem
                                        label={t.moisture}
                                        value={
                                            `${formatNumber(
                                                result.soil_moisture
                                            )} %`
                                        }
                                    />


                                    <ResultItem
                                        label={
                                            t.weatherTemperature
                                        }
                                        value={
                                            result.weather_temperature !==
                                                null &&
                                            result.weather_temperature !==
                                                undefined
                                                ? `${formatNumber(
                                                    result.weather_temperature
                                                )} °C`
                                                : "--"
                                        }
                                    />


                                    <ResultItem
                                        label={
                                            t.weatherHumidity
                                        }
                                        value={
                                            result.weather_humidity !==
                                                null &&
                                            result.weather_humidity !==
                                                undefined
                                                ? `${formatNumber(
                                                    result.weather_humidity
                                                )} %`
                                                : "--"
                                        }
                                    />


                                    <ResultItem
                                        label={t.rainfall}
                                        value={
                                            `${formatNumber(
                                                result.rainfall
                                            )} mm`
                                        }
                                    />


                                    <ResultItem
                                        label={
                                            t.rainProbability
                                        }
                                        value={
                                            `${formatNumber(
                                                result.rain_probability
                                            )} %`
                                        }
                                    />


                                    <ResultItem
                                        label={t.mlPrediction}
                                        value={
                                            translateMLPrediction(
                                                result.ml_prediction,
                                                t
                                            )
                                        }
                                    />

                                </div>


                                {/* =================================================
                                   REASON
                                ================================================= */}

                                <div className="irrigation-advice">

                                    <h3>
                                        💡 {t.reason}
                                    </h3>


                                    <p>
                                        {result.reason ||
                                            "--"}
                                    </p>

                                </div>


                                {/* =================================================
                                   MODEL PREDICTION
                                ================================================= */}

                                <div className="irrigation-model-prediction">

                                    <div className="irrigation-model-prediction-header">

                                        <h3>
                                            📈 {t.modelPrediction}
                                        </h3>


                                        <span className="irrigation-model-prediction-badge">
                                            ML
                                        </span>

                                    </div>


                                    <div
                                        style={{
                                            color:
                                                "#465249",

                                            fontSize:
                                                "12px",

                                            lineHeight:
                                                "1.5",

                                            marginBottom:
                                                probabilities.length
                                                    ? "14px"
                                                    : "0",
                                        }}
                                    >

                                        {t.modelBased}

                                    </div>


                                    {/* =================================================
                                       ML DECISION
                                    ================================================= */}

                                    {result.ml_prediction && (

                                        <div
                                            className={`irrigation-ml-decision ${getStatusClass(
                                                result.ml_prediction
                                            )}`}
                                        >

                                            <span>
                                                {t.mlPrediction}
                                            </span>


                                            <strong>

                                                {translateMLPrediction(
                                                    result.ml_prediction,
                                                    t
                                                )}

                                            </strong>

                                        </div>

                                    )}


                                    {/* =================================================
                                       PROBABILITIES
                                    ================================================= */}

                                    {probabilities.length > 0 && (

                                        <div className="irrigation-probability-list">

                                            {probabilities.map(
                                                (
                                                    item,
                                                    index
                                                ) => {

                                                    const safePercentage =
                                                        normalizeProbability(
                                                            item.value
                                                        );


                                                    return (

                                                        <div
                                                            className="irrigation-probability-row"
                                                            key={`${item.label}-${index}`}
                                                        >

                                                            <span className="irrigation-probability-label">

                                                                {item.label}

                                                            </span>


                                                            <div className="irrigation-probability-bar">

                                                                <div
                                                                    className="irrigation-probability-fill"
                                                                    style={{
                                                                        width:
                                                                            `${safePercentage}%`,
                                                                    }}
                                                                />

                                                            </div>


                                                            <span className="irrigation-probability-value">

                                                                {formatNumber(
                                                                    safePercentage
                                                                )}

                                                                %

                                                            </span>

                                                        </div>

                                                    );

                                                }
                                            )}

                                        </div>

                                    )}

                                </div>


                                {/* =================================================
                                   ADVICE
                                ================================================= */}

                                <div className="irrigation-advice">

                                    <h3>
                                        🌱 {t.advice}
                                    </h3>


                                    <p>
                                        {result.advice ||
                                            "--"}
                                    </p>

                                </div>


                                {/* =================================================
                                   NOTIFICATION
                                ================================================= */}

                                <div
                                    className={`irrigation-notification ${
                                        result.notification_created
                                            ? "sent"
                                            : ""
                                    }`}
                                >

                                    <strong>
                                        🔔 {t.notification}
                                    </strong>


                                    {result.notification_created ? (

                                        <>

                                            <span>
                                                {t.notificationSent}
                                            </span>


                                            <small>
                                                {t.notificationSuccess}
                                            </small>

                                        </>

                                    ) : (

                                        <>

                                            <span>
                                                {t.notificationNotRequired}
                                            </span>


                                            <small>
                                                {t.notificationNone}
                                            </small>

                                        </>

                                    )}

                                </div>

                            </>

                        )}

                </section>

            </div>

        </div>

    );

}


/* =========================================================
   SENSOR CARD
========================================================= */

function SensorCard({
    icon,
    label,
    value,
    unit,
    important = false,
}) {

    return (

        <div
            className={`irrigation-sensor-card ${
                important
                    ? "important"
                    : ""
            }`}
        >

            <div className="sensor-icon">

                {icon}

            </div>


            <span>

                {label}

            </span>


            <strong>

                {value}

            </strong>


            <small>

                {unit}

            </small>

        </div>

    );

}


/* =========================================================
   RESULT ITEM
========================================================= */

function ResultItem({
    label,
    value,
}) {

    return (

        <div className="irrigation-result-item">

            <span>

                {label}

            </span>


            <strong>

                {value ?? "--"}

            </strong>

        </div>

    );

}