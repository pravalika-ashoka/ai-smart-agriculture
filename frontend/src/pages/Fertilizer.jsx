import React, {
    useEffect,
    useState
} from "react";

import BackToDashboard from "../components/BackToDashboard";

import {
    getLatestSensorData,
    getFertilizerRecommendation
} from "../services/api";

import "./Fertilizer.css";


function Fertilizer() {

    // =====================================================
    // SENSOR DATA
    // =====================================================

    const [sensorData, setSensorData] =
        useState(null);

    const [recommendation, setRecommendation] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [predicting, setPredicting] =
        useState(false);

    const [error, setError] =
        useState("");

    const [lastUpdated, setLastUpdated] =
        useState(null);


    // =====================================================
    // CROP
    // =====================================================

    const [selectedCrop, setSelectedCrop] =
        useState(
            localStorage.getItem("selectedCrop") || ""
        );


    const crops = [
        {
            value: "rice",
            english: "Rice",
            kannada: "ಭತ್ತ"
        },
        {
            value: "maize",
            english: "Maize",
            kannada: "ಮೆಕ್ಕೆಜೋಳ"
        },
        {
            value: "chickpea",
            english: "Chickpea",
            kannada: "ಕಡಲೆ"
        },
        {
            value: "cotton",
            english: "Cotton",
            kannada: "ಹತ್ತಿ"
        },
        {
            value: "wheat",
            english: "Wheat",
            kannada: "ಗೋಧಿ"
        },
        {
            value: "groundnut",
            english: "Groundnut",
            kannada: "ಕಡಲೆಕಾಯಿ"
        },
        {
            value: "banana",
            english: "Banana",
            kannada: "ಬಾಳೆ"
        }
    ];


    // =====================================================
    // CROP CHANGE
    // =====================================================

    const handleCropChange = (event) => {

        const crop =
            String(event.target.value || "")
                .trim()
                .toLowerCase();


        console.log(
            "Selected fertilizer crop:",
            crop
        );


        setSelectedCrop(crop);


        localStorage.setItem(
            "selectedCrop",
            crop
        );


        // Clear old recommendation
        setRecommendation(null);

        // Clear previous error
        setError("");

    };


    // =====================================================
    // LANGUAGE
    // =====================================================

    const [language, setLanguage] =
        useState(
            localStorage.getItem("language") || "en"
        );


    const isKannada =
        language === "kn";


    const changeLanguage = (lang) => {

        setLanguage(lang);

        localStorage.setItem(
            "language",
            lang
        );

    };


    // =====================================================
    // LOAD SENSOR DATA
    // =====================================================

    const loadSensorData = async () => {

        try {

            setError("");


            const response =
                await getLatestSensorData();


            console.log(
                "===================================="
            );

            console.log(
                "FERTILIZER IOT RESPONSE:"
            );

            console.log(
                response
            );

            console.log(
                "===================================="
            );


            /*
             * Backend response can be:
             *
             * {
             *     status: "success",
             *     data: {...}
             * }
             *
             * or directly:
             *
             * {
             *     nitrogen: 80,
             *     ...
             * }
             */


            const data =
                response?.data || response;


            // =================================================
            // NORMALIZE SENSOR DATA
            // =================================================

            const normalizedData = {

                nitrogen:
                    data?.nitrogen,

                phosphorus:
                    data?.phosphorus,

                potassium:
                    data?.potassium,

                soil_moisture:
                    data?.soil_moisture ??
                    data?.moisture,

                temperature:
                    data?.temperature,

                humidity:
                    data?.humidity,

                rainfall:
                    data?.rainfall

            };


            console.log(
                "Normalized fertilizer sensor data:",
                normalizedData
            );


            setSensorData(
                normalizedData
            );


            setLastUpdated(
                new Date()
            );


        }

        catch (err) {

            console.error(
                "Fertilizer sensor error:",
                err
            );


            const detail =
                err?.response?.data?.detail;


            if (
                typeof detail === "string"
            ) {

                setError(
                    detail
                );

            }

            else {

                setError(

                    isKannada

                        ? "ಲೈವ್ ಸೆನ್ಸರ್ ಡೇಟಾವನ್ನು ಲೋಡ್ ಮಾಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ."

                        : "Unable to load live sensor data."

                );

            }

        }

        finally {

            setLoading(false);

        }

    };


    // =====================================================
    // INITIAL SENSOR LOAD + REFRESH
    // =====================================================

    useEffect(() => {

        loadSensorData();


        /*
         * Refresh every 30 seconds.
         */

        const interval =
            setInterval(
                loadSensorData,
                30000
            );


        return () => {

            clearInterval(
                interval
            );

        };

    }, []);


    // =====================================================
    // FERTILIZER RECOMMENDATION
    // =====================================================

    const handleRecommendation = async () => {

        // =================================================
        // NORMALIZE CROP
        // =================================================

        const cropType =
            String(
                selectedCrop || ""
            )
                .trim()
                .toLowerCase();


        console.log(
            "===================================="
        );

        console.log(
            "SELECTED FERTILIZER CROP:"
        );

        console.log(
            cropType
        );

        console.log(
            "===================================="
        );


        // =================================================
        // CHECK CROP
        // =================================================

        if (!cropType) {

            setError(

                isKannada

                    ? "ದಯವಿಟ್ಟು ಬೆಳೆ ಆಯ್ಕೆಮಾಡಿ."

                    : "Please select a crop."

            );

            return;

        }


        // =================================================
        // CHECK VALID CROP
        // =================================================

        const validCrop =
            crops.some(
                crop =>
                    crop.value === cropType
            );


        if (!validCrop) {

            setError(

                isKannada

                    ? "ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ ಬೆಳೆ ಆಯ್ಕೆಮಾಡಿ."

                    : "Please select a valid crop."

            );

            return;

        }


        // =================================================
        // CHECK SENSOR DATA
        // =================================================

        if (!sensorData) {

            setError(

                isKannada

                    ? "ಸೆನ್ಸರ್ ಡೇಟಾ ಲಭ್ಯವಿಲ್ಲ."

                    : "Sensor data is not available."

            );

            return;

        }


        try {

            setPredicting(true);

            setRecommendation(null);

            setError("");


            // =================================================
            // CONVERT SENSOR VALUES TO NUMBERS
            // =================================================

            const nitrogen =
                Number(
                    sensorData.nitrogen
                );


            const phosphorus =
                Number(
                    sensorData.phosphorus
                );


            const potassium =
                Number(
                    sensorData.potassium
                );

            const moisture =
                Number(
                    sensorData.soil_moisture
                );


            const temperature =
                Number(
                    sensorData.temperature
                );


            // =================================================
            // SENSOR INPUT OBJECT
            // =================================================

            const sensorInput = {

                nitrogen,

                phosphorus,

                potassium,

                moisture,

                temperature

            };


            console.log(
                "Fertilizer sensor values:",
                sensorInput
            );


            // =================================================
            // VALIDATE SENSOR VALUES
            // =================================================

            const invalidFields =
                Object.entries(
                    sensorInput
                )
                    .filter(
                        ([, value]) =>
                            !Number.isFinite(value)
                    )
                    .map(
                        ([key]) =>
                            key
                    );


            if (
                invalidFields.length > 0
            ) {

                console.error(
                    "Invalid fertilizer sensor fields:",
                    invalidFields
                );


                setError(

                    isKannada

                        ? `ಅಮಾನ್ಯ ಸೆನ್ಸರ್ ಮೌಲ್ಯಗಳು: ${invalidFields.join(", ")}`

                        : `Invalid sensor values: ${invalidFields.join(", ")}`

                );

                return;

            }


            // =================================================
            // FINAL FERTILIZER API PAYLOAD
            // =================================================

            const inputData = {

                nitrogen:
                    nitrogen,

                phosphorus:
                    phosphorus,

                potassium:
                    potassium,

                moisture:
                    moisture,

                temperature:
                    temperature,

                /*
                 * IMPORTANT:
                 *
                 * FastAPI requires this field.
                 *
                 * crop_type is intentionally included
                 * in the final request body.
                 */

                crop_type:
                    cropType

            };


            // =================================================
            // DEBUG PAYLOAD
            // =================================================

            console.log(
                "===================================="
            );

            console.log(
                "FERTILIZER API REQUEST PAYLOAD:"
            );

            console.log(
                JSON.stringify(
                    inputData,
                    null,
                    2
                )
            );

            console.log(
                "===================================="
            );


            // =================================================
            // FINAL CROP CHECK
            // =================================================

            if (
                !inputData.crop_type
            ) {

                setError(

                    isKannada

                        ? "ಬೆಳೆ ಪ್ರಕಾರ ಲಭ್ಯವಿಲ್ಲ."

                        : "Crop type is missing."

                );

                return;

            }


            // =================================================
            // CALL FERTILIZER API
            // =================================================

            const result =
                await getFertilizerRecommendation(
                    inputData
                );


            // =================================================
            // DEBUG RESPONSE
            // =================================================

            console.log(
                "===================================="
            );

            console.log(
                "FERTILIZER API RESPONSE:"
            );

            console.log(
                result
            );

            console.log(
                "===================================="
            );


            setRecommendation(
                result
            );


        }

        catch (err) {

            console.error(
                "===================================="
            );

            console.error(
                "FERTILIZER RECOMMENDATION ERROR:"
            );

            console.error(
                err
            );

            console.error(
                "BACKEND RESPONSE:"
            );

            console.error(
                err?.response?.data
            );

            console.error(
                "===================================="
            );


            const detail =
                err?.response?.data?.detail;


            // =================================================
            // FASTAPI VALIDATION ERROR
            // =================================================

            if (
                Array.isArray(detail)
            ) {

                const messages =
                    detail.map(
                        (item) => {

                            const field =
                                item?.loc?.join(
                                    " → "
                                ) ||
                                "Field";


                            return `${field}: ${
                                item?.msg ||
                                "Invalid value"
                            }`;

                        }
                    );


                setError(
                    messages.join(
                        " | "
                    )
                );

            }


            // =================================================
            // STRING ERROR
            // =================================================

            else if (
                typeof detail === "string"
            ) {

                setError(
                    detail
                );

            }


            // =================================================
            // GENERAL ERROR
            // =================================================

            else {

                setError(

                    isKannada

                        ? "ರಸಗೊಬ್ಬರ ಶಿಫಾರಸನ್ನು ರಚಿಸಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ."

                        : "Unable to generate fertilizer recommendation."

                );

            }

        }

        finally {

            setPredicting(false);

        }

    };


    // =====================================================
    // SELECTED CROP DATA
    // =====================================================

    const selectedCropData =
        crops.find(
            crop =>
                crop.value === selectedCrop
        );


    // =====================================================
    // PAGE
    // =====================================================

    return (

        <div className="fertilizer-page">

            <div className="fertilizer-container">


                {/* =================================================
                    BACK TO DASHBOARD
                ================================================= */}

                <div className="fertilizer-back-wrapper">

                    <BackToDashboard />

                </div>


                {/* =================================================
                    LANGUAGE BAR
                ================================================= */}

                <div className="fertilizer-language-bar">

                    <button

                        className={
                            language === "en"
                                ? "language-button active"
                                : "language-button"
                        }

                        onClick={() =>
                            changeLanguage("en")
                        }

                    >

                        English

                    </button>


                    <button

                        className={
                            language === "kn"
                                ? "language-button active"
                                : "language-button"
                        }

                        onClick={() =>
                            changeLanguage("kn")
                        }

                    >

                        ಕನ್ನಡ

                    </button>

                </div>


                {/* =================================================
                    PAGE TITLE
                ================================================= */}

                <div className="fertilizer-page-heading">

                    <div className="fertilizer-title-area">

                        <div className="fertilizer-title-icon">

                            🌱

                        </div>


                        <div>

                            <h1>

                                {isKannada

                                    ? "ರಸಗೊಬ್ಬರ ಶಿಫಾರಸು"

                                    : "Fertilizer Recommendation"}

                            </h1>


                            <p>

                                {isKannada

                                    ? "ಆಯ್ಕೆ ಮಾಡಿದ ಬೆಳೆ ಮತ್ತು ಲೈವ್ ಕೃಷಿ ಪರಿಸ್ಥಿತಿಗಳನ್ನು ಬಳಸಿಕೊಂಡು AI ಆಧಾರಿತ ರಸಗೊಬ್ಬರ ಆಯ್ಕೆ."

                                    : "AI-powered fertilizer selection using your selected crop and live farm conditions"}

                            </p>

                        </div>

                    </div>


                    {/* AI STATUS */}

                    <div className="fertilizer-ai-status">

                        <span className="ai-status-dot"></span>

                        {isKannada

                            ? "AI ಮಾದರಿ ಸಕ್ರಿಯವಾಗಿದೆ"

                            : "AI Model Active"}

                    </div>

                </div>


                {/* =================================================
                    CROP SELECTION
                ================================================= */}

                <section className="fertilizer-crop-section">

                    <div className="fertilizer-section-header">

                        <div>

                            <h2>

                                🌾{" "}

                                {isKannada

                                    ? "ಬೆಳೆ ಆಯ್ಕೆ"

                                    : "Select Crop"}

                            </h2>


                            <p>

                                {isKannada

                                    ? "ರಸಗೊಬ್ಬರ ಶಿಫಾರಸಿಗಾಗಿ ನಿಮ್ಮ ಬೆಳೆ ಆಯ್ಕೆಮಾಡಿ"

                                    : "Select the crop for which fertilizer is required"}

                            </p>

                        </div>

                    </div>


                    <div className="crop-selection-wrapper">

                        <label htmlFor="crop-select">

                            {isKannada

                                ? "ಬೆಳೆ"

                                : "Crop"}

                        </label>


                        <select

                            id="crop-select"

                            value={selectedCrop}

                            onChange={
                                handleCropChange
                            }

                            className="crop-select"

                        >

                            <option value="">

                                {isKannada

                                    ? "ಬೆಳೆ ಆಯ್ಕೆಮಾಡಿ"

                                    : "Select a crop"}

                            </option>


                            {crops.map(
                                crop => (

                                    <option

                                        key={
                                            crop.value
                                        }

                                        value={
                                            crop.value
                                        }

                                    >

                                        {isKannada

                                            ? crop.kannada

                                            : crop.english}

                                    </option>

                                )
                            )}

                        </select>


                        {selectedCropData && (

                            <div className="selected-crop-display">

                                <span>
                                    🌱
                                </span>


                                <div>

                                    <strong>

                                        {isKannada

                                            ? selectedCropData.kannada

                                            : selectedCropData.english}

                                    </strong>


                                    <small>

                                        {isKannada

                                            ? "ಆಯ್ಕೆ ಮಾಡಿದ ಬೆಳೆ"

                                            : "Selected crop"}

                                    </small>

                                </div>

                            </div>

                        )}

                    </div>

                </section>


                {/* =================================================
                    ERROR
                ================================================= */}

                {error && (

                    <div className="fertilizer-error">

                        <span className="error-icon">
                            ⚠️
                        </span>


                        <div>

                            <strong>

                                {isKannada
                                    ? "ದೋಷ"
                                    : "Error"}

                            </strong>


                            <p>
                                {error}
                            </p>

                        </div>

                    </div>

                )}


                {/* =================================================
                    LOADING
                ================================================= */}

                {loading && (

                    <div className="fertilizer-loading">

                        <div className="loading-spinner"></div>


                        <span>

                            {isKannada

                                ? "ಲೈವ್ ಸೆನ್ಸರ್ ಡೇಟಾವನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ..."

                                : "Loading live sensor data..."}

                        </span>

                    </div>

                )}


                {/* =================================================
                    LIVE FARM CONDITIONS
                ================================================= */}

                {!loading &&
                    sensorData && (

                        <section className="fertilizer-sensor-section">


                            {/* HEADER */}

                            <div className="fertilizer-section-header">

                                <div>

                                    <h2>

                                        📡{" "}

                                        {isKannada

                                            ? "ಲೈವ್ ಕೃಷಿ ಪರಿಸ್ಥಿತಿಗಳು"

                                            : "Live Farm Conditions"}

                                    </h2>


                                    <p>

                                        {isKannada

                                            ? "ನಿಮ್ಮ IoT ಸೆನ್ಸರ್‌ಗಳಿಂದ ಸಂಗ್ರಹಿಸಲಾದ ಪ್ರಸ್ತುತ ಮೌಲ್ಯಗಳು"

                                            : "Current values collected from your IoT sensors"}

                                    </p>

                                </div>


                                <div className="live-badge">

                                    <span></span>

                                    {isKannada
                                        ? "ಲೈವ್"
                                        : "LIVE"}

                                </div>

                            </div>


                            {/* SENSOR GRID */}

                            <div className="fertilizer-sensor-grid">


                                {/* NITROGEN */}

                                <div className="fertilizer-sensor-card">

                                    <div className="sensor-icon">
                                        N
                                    </div>


                                    <div className="sensor-info">

                                        <span>

                                            {isKannada
                                                ? "ಸಾರಜನಕ"
                                                : "Nitrogen"}

                                        </span>


                                        <strong>

                                            {sensorData.nitrogen ??
                                                "N/A"}

                                        </strong>


                                        <small>
                                            mg/kg
                                        </small>

                                    </div>

                                </div>


                                {/* PHOSPHORUS */}

                                <div className="fertilizer-sensor-card">

                                    <div className="sensor-icon">
                                        P
                                    </div>


                                    <div className="sensor-info">

                                        <span>

                                            {isKannada
                                                ? "ರಂಜಕ"
                                                : "Phosphorus"}

                                        </span>


                                        <strong>

                                            {sensorData.phosphorus ??
                                                "N/A"}

                                        </strong>


                                        <small>
                                            mg/kg
                                        </small>

                                    </div>

                                </div>


                                {/* POTASSIUM */}

                                <div className="fertilizer-sensor-card">

                                    <div className="sensor-icon">
                                        K
                                    </div>


                                    <div className="sensor-info">

                                        <span>

                                            {isKannada
                                                ? "ಪೊಟ್ಯಾಸಿಯಂ"
                                                : "Potassium"}

                                        </span>


                                        <strong>

                                            {sensorData.potassium ??
                                                "N/A"}

                                        </strong>


                                        <small>
                                            mg/kg
                                        </small>

                                    </div>

                                </div>


                                {/* TEMPERATURE */}

                                <div className="fertilizer-sensor-card">

                                    <div className="sensor-icon">
                                        🌡️
                                    </div>


                                    <div className="sensor-info">

                                        <span>

                                            {isKannada
                                                ? "ತಾಪಮಾನ"
                                                : "Temperature"}

                                        </span>


                                        <strong>

                                            {sensorData.temperature ??
                                                "N/A"}

                                            {sensorData.temperature != null
                                                ? " °C"
                                                : ""}

                                        </strong>


                                        <small>

                                            {isKannada
                                                ? "ಗಾಳಿಯ ತಾಪಮಾನ"
                                                : "Air temperature"}

                                        </small>

                                    </div>

                                </div>


                                {/* HUMIDITY */}

                                <div className="fertilizer-sensor-card">

                                    <div className="sensor-icon">
                                        💧
                                    </div>


                                    <div className="sensor-info">

                                        <span>

                                            {isKannada
                                                ? "ಆರ್ದ್ರತೆ"
                                                : "Humidity"}

                                        </span>


                                        <strong>

                                            {sensorData.humidity ??
                                                "N/A"}

                                            {sensorData.humidity != null
                                                ? " %"
                                                : ""}

                                        </strong>


                                        <small>

                                            {isKannada
                                                ? "ಸಾಪೇಕ್ಷ ಆರ್ದ್ರತೆ"
                                                : "Relative humidity"}

                                        </small>

                                    </div>

                                </div>

                                {/* RAINFALL */}

                                <div className="fertilizer-sensor-card">

                                    <div className="sensor-icon">
                                        🌧️
                                    </div>


                                    <div className="sensor-info">

                                        <span>

                                            {isKannada
                                                ? "ಮಳೆ"
                                                : "Rainfall"}

                                        </span>


                                        <strong>

                                            {sensorData.rainfall ??
                                                "N/A"}

                                            {sensorData.rainfall != null
                                                ? " mm"
                                                : ""}

                                        </strong>


                                        <small>

                                            {isKannada
                                                ? "ಪ್ರಸ್ತುತ ಮಳೆ"
                                                : "Current rainfall"}

                                        </small>

                                    </div>

                                </div>


                                {/* SOIL MOISTURE */}

                                <div className="fertilizer-sensor-card moisture-card">

                                    <div className="sensor-icon">
                                        🌱
                                    </div>


                                    <div className="sensor-info">

                                        <span>

                                            {isKannada
                                                ? "ಮಣ್ಣಿನ ತೇವಾಂಶ"
                                                : "Soil Moisture"}

                                        </span>


                                        <strong>

                                            {sensorData.soil_moisture ??
                                                "N/A"}

                                            {sensorData.soil_moisture != null
                                                ? " %"
                                                : ""}

                                        </strong>


                                        <small>

                                            {isKannada
                                                ? "ನೀರಾವರಿ ವ್ಯವಸ್ಥೆಯಲ್ಲಿ ಬಳಸಲಾಗುತ್ತದೆ"
                                                : "Used by irrigation system"}

                                        </small>

                                    </div>

                                </div>


                            </div>


                            {/* LAST UPDATED */}

                            <div className="fertilizer-last-updated">

                                <span className="update-dot"></span>


                                <span>

                                    {lastUpdated

                                        ? (

                                            isKannada

                                                ? `ಕೊನೆಯ ನವೀಕರಣ: ${lastUpdated.toLocaleTimeString()}`

                                                : `Last updated: ${lastUpdated.toLocaleTimeString()}`

                                        )

                                        : (

                                            isKannada

                                                ? "ಡೇಟಾ ನವೀಕರಣಕ್ಕಾಗಿ ಕಾಯುತ್ತಿದೆ..."

                                                : "Waiting for data update..."

                                        )}

                                </span>

                            </div>


                        </section>

                    )}


                {/* =================================================
                    NO SENSOR DATA
                ================================================= */}

                {!loading &&
                    !sensorData && (

                        <div className="fertilizer-no-data">

                            <div className="no-data-icon">
                                📡
                            </div>


                            <h2>

                                {isKannada

                                    ? "ಸೆನ್ಸರ್ ಡೇಟಾ ಲಭ್ಯವಿಲ್ಲ"

                                    : "No Sensor Data"}

                            </h2>


                            <p>

                                {isKannada

                                    ? "ನಿಮ್ಮ IoT ಸೆನ್ಸರ್ ಸಂಪರ್ಕವನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."

                                    : "Check your IoT sensor connection and try again."}

                            </p>


                            <button

                                className="retry-button"

                                onClick={
                                    loadSensorData
                                }

                            >

                                {isKannada
                                    ? "ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ"
                                    : "Retry"}

                            </button>

                        </div>

                    )}


                {/* =================================================
                    AI MODEL INFORMATION
                ================================================= */}

                {!loading &&
                    sensorData && (

                        <section className="fertilizer-model-card">


                            <div className="model-icon">
                                🤖
                            </div>


                            <div className="model-information">

                                <h3>
                                    Random Forest AI Model
                                </h3>


                                <p>

                                    {isKannada

                                        ? "ನಿಮ್ಮ ಆಯ್ಕೆ ಮಾಡಿದ ಬೆಳೆ ಮತ್ತು ಲೈವ್ ಮಣ್ಣು ಮತ್ತು ಪರಿಸರ ಪರಿಸ್ಥಿತಿಗಳ ಆಧಾರದ ಮೇಲೆ ಶಿಫಾರಸು ರಚಿಸಲಾಗುತ್ತದೆ."

                                        : "Recommendation is generated using your selected crop and live soil and environmental conditions."}

                                </p>

                            </div>


                            <div className="model-stat">

                                <strong>
                                    50,001
                                </strong>

                                <span>
                                    Training Records
                                </span>

                            </div>


                            <div className="model-stat">

                                <strong>
                                    6
                                </strong>

                                <span>
                                    Fertilizer Classes
                                </span>

                            </div>


                        </section>

                    )}


                {/* =================================================
                    RECOMMEND BUTTON
                ================================================= */}

                {!loading &&
                    sensorData && (

                        <button

                            className="fertilizer-button"

                            onClick={
                                handleRecommendation
                            }

                            disabled={
                                predicting ||
                                !sensorData ||
                                !selectedCrop
                            }

                        >

                            {predicting ? (

                                <>

                                    <span className="button-spinner"></span>

                                    {isKannada

                                        ? "ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ..."

                                        : "Analyzing Soil..."}

                                </>

                            ) : (

                                <>

                                    🌱{" "}

                                    {isKannada

                                        ? "ಸೂಕ್ತ ರಸಗೊಬ್ಬರವನ್ನು ಶಿಫಾರಸು ಮಾಡಿ"

                                        : "Recommend Suitable Fertilizer"}

                                </>

                            )}

                        </button>

                    )}


                {/* =================================================
                    RECOMMENDATION RESULT
                ================================================= */}

                {recommendation && (

                    <section className="fertilizer-result">


                        {/* RESULT HEADER */}

                        <div className="result-header">

                            <div className="result-icon">
                                🌾
                            </div>


                            <div>

                                <h2>

                                    {isKannada

                                        ? "ಶಿಫಾರಸು ಮಾಡಿದ ರಸಗೊಬ್ಬರ"

                                        : "Recommended Fertilizer"}

                                </h2>


                                <p>

                                    {isKannada

                                        ? "ಆಯ್ಕೆ ಮಾಡಿದ ಬೆಳೆ ಮತ್ತು ಪ್ರಸ್ತುತ ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳ ಸ್ಥಿತಿಯನ್ನು ಆಧರಿಸಿದೆ"

                                        : "Based on the selected crop and current soil nutrient conditions"}

                                </p>

                            </div>

                        </div>


                        {/* SELECTED CROP */}

                        <div className="fertilizer-product">

                            <span>

                                {isKannada
                                    ? "ಆಯ್ಕೆ ಮಾಡಿದ ಬೆಳೆ"
                                    : "Selected Crop"}

                            </span>


                            <strong>

                                {selectedCropData

                                    ? (

                                        isKannada

                                            ? selectedCropData.kannada

                                            : selectedCropData.english

                                    )

                                    : selectedCrop}

                            </strong>

                        </div>


                        {/* RECOMMENDED FERTILIZER */}

                        <div className="fertilizer-product">

                            <span>

                                {isKannada
                                    ? "ಶಿಫಾರಸು ಮಾಡಿದ ರಸಗೊಬ್ಬರ"
                                    : "Recommended Fertilizer"}

                            </span>


                            <strong>

                                {recommendation.recommended_fertilizer

                                    ||

                                    (
                                        isKannada

                                            ? "ಶಿಫಾರಸು ಸ್ವೀಕರಿಸಲಾಗಿದೆ"

                                            : "Recommendation received"
                                    )}

                            </strong>

                        </div>


                        {/* MODEL ACCURACY */}

                        {recommendation.accuracy != null && (

                            <div className="fertilizer-accuracy">

                                <div>

                                    <span>

                                        {isKannada
                                            ? "ಮಾದರಿ ನಿಖರತೆ"
                                            : "Model Accuracy"}

                                    </span>


                                    <small>

                                        {isKannada
                                            ? "ತರಬೇತಿ ಪರೀಕ್ಷಾ ಫಲಿತಾಂಶ"
                                            : "Training test result"}

                                    </small>

                                </div>


                                <strong>

                                    {Number(
                                        recommendation.accuracy
                                    ).toFixed(1)}%

                                </strong>

                            </div>

                        )}


                        {/* ADVICE */}

                        {recommendation.advice && (

                            <div className="fertilizer-advice">

                                <div className="advice-icon">
                                    💡
                                </div>


                                <div>

                                    <h3>

                                        {isKannada
                                            ? "ರಸಗೊಬ್ಬರ ಸಲಹೆ"
                                            : "Fertilizer Advice"}

                                    </h3>


                                    <p>

                                        {recommendation.advice}

                                    </p>

                                </div>

                            </div>

                        )}


                        {/* ANALYSIS SUMMARY */}

                        <div className="recommendation-summary">


                            <h3>

                                📊{" "}

                                {isKannada
                                    ? "ವಿಶ್ಲೇಷಣೆಯ ಆಧಾರ"
                                    : "Analysis Based On"}

                            </h3>


                            <p className="summary-description">

                                {isKannada

                                    ? "ಈ ಶಿಫಾರಸನ್ನು ಆಯ್ಕೆ ಮಾಡಿದ ಬೆಳೆ ಮತ್ತು ಕೆಳಗಿನ ಮಣ್ಣು ಮತ್ತು ಪರಿಸರದ ಮೌಲ್ಯಗಳನ್ನು ಬಳಸಿ ರಚಿಸಲಾಗಿದೆ."

                                    : "This recommendation was generated using the selected crop and the following soil and environmental values."}

                            </p>


                            <div className="summary-grid">


                                {/* CROP */}

                                <div>

                                    <span>

                                        🌾{" "}

                                        {isKannada
                                            ? "ಬೆಳೆ"
                                            : "Crop"}

                                    </span>


                                    <strong>

                                        {selectedCropData

                                            ? (

                                                isKannada

                                                    ? selectedCropData.kannada

                                                    : selectedCropData.english

                                            )

                                            : "--"}

                                    </strong>


                                    <small>

                                        {isKannada
                                            ? "ಆಯ್ಕೆ ಮಾಡಿದ ಬೆಳೆ"
                                            : "Selected crop"}

                                    </small>

                                </div>


                                {/* N */}

                                <div>

                                    <span>
                                        N
                                    </span>


                                    <strong>

                                        {sensorData?.nitrogen ??
                                            "--"}

                                    </strong>


                                    <small>
                                        mg/kg
                                    </small>

                                </div>


                                {/* P */}

                                <div>

                                    <span>
                                        P
                                    </span>


                                    <strong>

                                        {sensorData?.phosphorus ??
                                            "--"}

                                    </strong>


                                    <small>
                                        mg/kg
                                    </small>

                                </div>


                                {/* K */}

                                <div>

                                    <span>
                                        K
                                    </span>


                                    <strong>

                                        {sensorData?.potassium ??
                                            "--"}

                                    </strong>


                                    <small>
                                        mg/kg
                                    </small>

                                </div>

                                {/* MOISTURE */}

                                <div>

                                    <span>

                                        {isKannada
                                            ? "ತೇವಾಂಶ"
                                            : "Moisture"}

                                    </span>


                                    <strong>

                                        {sensorData?.soil_moisture ??
                                            "--"}%

                                    </strong>


                                    <small>

                                        {isKannada
                                            ? "ಮಣ್ಣಿನ ತೇವಾಂಶ"
                                            : "Soil moisture"}

                                    </small>

                                </div>


                                {/* TEMPERATURE */}

                                <div>

                                    <span>

                                        {isKannada
                                            ? "ತಾಪಮಾನ"
                                            : "Temperature"}

                                    </span>


                                    <strong>

                                        {sensorData?.temperature ??
                                            "--"}°C

                                    </strong>


                                    <small>

                                        {isKannada
                                            ? "ತಾಪಮಾನ"
                                            : "Temperature"}

                                    </small>

                                </div>


                            </div>


                        </div>


                    </section>

                )}

            </div>

        </div>

    );

}


export default Fertilizer;