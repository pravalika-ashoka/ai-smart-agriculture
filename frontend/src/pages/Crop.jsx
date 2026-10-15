import React, { useEffect, useState } from "react";

import {
    getLatestSensorData,
    getCropRecommendation
} from "../services/api";

import { useNavigate } from "react-router-dom";

import "./Crop.css";


function Crop() {

    // =====================================================
    // NAVIGATION
    // =====================================================

    const navigate = useNavigate();


    // =====================================================
    // STATE
    // =====================================================

    const [sensorData, setSensorData] = useState(null);

    const [recommendation, setRecommendation] = useState(null);

    const [loading, setLoading] = useState(true);

    const [predicting, setPredicting] = useState(false);

    const [error, setError] = useState("");


    // =====================================================
    // LANGUAGE
    // =====================================================

    const [language, setLanguage] = useState(
        localStorage.getItem("language") || "en"
    );

    const isKannada = language === "kn";


    // =====================================================
    // LANGUAGE CHANGE
    // =====================================================

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

    useEffect(() => {

        loadSensorData();

    }, []);


    // =====================================================
    // GET LATEST SENSOR DATA
    // =====================================================

    const loadSensorData = async () => {

        try {

            setLoading(true);

            setError("");

            const response =
                await getLatestSensorData();


            console.log(
                "Latest IoT sensor API response:",
                JSON.stringify(
                    response,
                    null,
                    2
                )
            );


            const data = response.data;


            console.log(
                "Actual sensor data:",
                JSON.stringify(
                    data,
                    null,
                    2
                )
            );


            if (!data) {

                throw new Error(
                    "No sensor data received."
                );

            }


            setSensorData(data);

        }

        catch (err) {

            console.error(
                "Sensor data error:",
                err
            );


            const detail =
                err.response?.data?.detail;


            if (
                typeof detail === "string"
            ) {

                setError(detail);

            }

            else {

                setError(
                    err.message ||
                    (
                        isKannada
                            ? "ಸೆನ್ಸರ್ ಡೇಟಾವನ್ನು ಲೋಡ್ ಮಾಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ."
                            : "Unable to load sensor data."
                    )
                );

            }

        }

        finally {

            setLoading(false);

        }

    };


    // =====================================================
    // CROP RECOMMENDATION
    // =====================================================

    const handleRecommendation = async () => {

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
            // PREPARE DATA
            // =================================================

            const inputData = {

                nitrogen:
                    Number(
                        sensorData.nitrogen
                    ),

                phosphorus:
                    Number(
                        sensorData.phosphorus
                    ),

                potassium:
                    Number(
                        sensorData.potassium
                    ),

                temperature:
                    Number(
                        sensorData.temperature
                    ),

                humidity:
                    Number(
                        sensorData.humidity
                    ),

                rainfall:
                    Number(
                        sensorData.rainfall
                    )

            };


            console.log(
                "Crop recommendation input:",
                JSON.stringify(
                    inputData,
                    null,
                    2
                )
            );


            // =================================================
            // VALIDATE INPUT
            // =================================================

            const invalidFields =
                Object.entries(inputData)
                    .filter(
                        ([key, value]) =>
                            !Number.isFinite(value)
                    )
                    .map(
                        ([key]) => key
                    );


            if (
                invalidFields.length > 0
            ) {

                setError(
                    isKannada
                        ? `ಅಮಾನ್ಯ ಸೆನ್ಸರ್ ಮೌಲ್ಯಗಳು: ${invalidFields.join(", ")}`
                        : `Invalid sensor values: ${invalidFields.join(
                            ", "
                        )}`
                );

                return;

            }

            // =================================================
            // VALIDATE HUMIDITY
            // =================================================

            if (
                inputData.humidity < 0 ||
                inputData.humidity > 100
            ) {

                setError(
                    isKannada
                        ? "ಆರ್ದ್ರತೆಯ ಮೌಲ್ಯವು 0% ಮತ್ತು 100% ನಡುವೆ ಇರಬೇಕು."
                        : "Humidity value must be between 0% and 100%."
                );

                return;

            }


            // =================================================
            // CALL BACKEND
            // =================================================

            const result =
                await getCropRecommendation(
                    inputData
                );


            console.log(
                "Crop recommendation result:",
                JSON.stringify(
                    result,
                    null,
                    2
                )
            );


            setRecommendation(result);

        }

        catch (err) {

            console.error(
                "Crop recommendation error:",
                err
            );


            console.error(
                "Backend response:",
                JSON.stringify(
                    err.response?.data,
                    null,
                    2
                )
            );


            const detail =
                err.response?.data?.detail;


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
                                item.loc?.join(
                                    " → "
                                ) ||
                                "Field";

                            return (
                                `${field}: ${item.msg}`
                            );

                        }
                    );


                setError(
                    messages.join(" | ")
                );

            }


            // =================================================
            // NORMAL BACKEND ERROR
            // =================================================

            else if (
                typeof detail === "string"
            ) {

                setError(detail);

            }


            // =================================================
            // OTHER ERROR
            // =================================================

            else {

                setError(
                    err.message ||
                    (
                        isKannada
                            ? "ಬೆಳೆ ಶಿಫಾರಸನ್ನು ರಚಿಸಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ."
                            : "Unable to generate crop recommendation."
                    )
                );

            }

        }

        finally {

            setPredicting(false);

        }

    };


    // =====================================================
    // FORMAT CROP NAME
    // =====================================================

    const formatCropName = (crop) => {

        if (!crop) {

            return isKannada
                ? "ಶಿಫಾರಸು ಸ್ವೀಕರಿಸಲಾಗಿದೆ"
                : "Recommendation received";

        }


        return String(crop)
            .trim()
            .replace(
                /\b\w/g,
                (letter) =>
                    letter.toUpperCase()
            );

    };


    // =====================================================
    // PAGE
    // =====================================================

    return (

        <div className="crop-page">


            {/* =================================================
                LANGUAGE + BACK CONTROLS
            ================================================= */}

            <div className="crop-top-controls">

                <button
                    className="back-dashboard-button"
                    onClick={() =>
                        navigate("/dashboard")
                    }
                >
                    ←{" "}
                    {isKannada
                        ? "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಹಿಂತಿರುಗಿ"
                        : "Back to Dashboard"}
                </button>


                <div className="language-switcher">

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

            </div>


            {/* =================================================
                PAGE HEADER
            ================================================= */}

            <div className="crop-header">

                <div>

                    <div className="crop-title-icon">
                        🌱
                    </div>

                    <div>

                        <h1>
                            {isKannada
                                ? "ಬೆಳೆ ಶಿಫಾರಸು"
                                : "Crop Recommendation"}
                        </h1>

                        <p>
                            {isKannada
                                ? "ನೈಜ ಸಮಯದ ಕೃಷಿ ಪರಿಸ್ಥಿತಿಗಳನ್ನು ಬಳಸಿ AI ಆಧಾರಿತ ಬೆಳೆ ಆಯ್ಕೆ"
                                : "AI-powered crop selection using live farm conditions"}
                        </p>

                    </div>

                </div>


                <div className="dataset-badge">

                    <span>
                        ●
                    </span>

                    {isKannada
                        ? "AI ಮಾದರಿ ಸಕ್ರಿಯವಾಗಿದೆ"
                        : "AI Model Active"}

                </div>

            </div>


            {/* =================================================
                LOADING
            ================================================= */}

            {loading && (

                <div className="loading-card">

                    <div className="loading-spinner">
                        ⟳
                    </div>

                    <div>

                        <strong>
                            {isKannada
                                ? "ನೈಜ ಸಮಯದ ಸೆನ್ಸರ್ ಡೇಟಾ ಲೋಡ್ ಆಗುತ್ತಿದೆ"
                                : "Loading live sensor data"}
                        </strong>

                        <p>
                            {isKannada
                                ? "ನಿಮ್ಮ IoT ಸೆನ್ಸರ್‌ಗಳಿಗೆ ಸಂಪರ್ಕಿಸಲಾಗುತ್ತಿದೆ..."
                                : "Connecting to your IoT sensors..."}
                        </p>

                    </div>

                </div>

            )}


            {/* =================================================
                ERROR
            ================================================= */}

            {error && (

                <div className="sensor-error">

                    <div className="error-icon">
                        ⚠️
                    </div>

                    <div>

                        <strong>
                            {isKannada
                                ? "ಏನೋ ತಪ್ಪಾಗಿದೆ"
                                : "Something went wrong"}
                        </strong>

                        <p>
                            {error}
                        </p>

                    </div>

                </div>

            )}


            {/* =================================================
                SENSOR DATA
            ================================================= */}

            {!loading &&
                sensorData && (

                    <>

                        <div className="sensor-card">


                            {/* CARD HEADER */}

                            <div className="card-header">

                                <div>

                                    <h2>
                                        📡{" "}
                                        {isKannada
                                            ? "ನೈಜ ಸಮಯದ ಕೃಷಿ ಪರಿಸ್ಥಿತಿಗಳು"
                                            : "Live Farm Conditions"}
                                    </h2>

                                    <p>
                                        {isKannada
                                            ? "ನಿಮ್ಮ IoT ಸೆನ್ಸರ್‌ಗಳಿಂದ ಸಂಗ್ರಹಿಸಲಾದ ಪ್ರಸ್ತುತ ಮೌಲ್ಯಗಳು"
                                            : "Current values collected from your IoT sensors"}
                                    </p>

                                </div>

                                <div className="live-indicator">

                                    <span className="live-dot">
                                    </span>

                                    {isKannada
                                        ? "ನೈಜ ಸಮಯ"
                                        : "LIVE"}

                                </div>

                            </div>


                            {/* SENSOR GRID */}

                            <div className="sensor-grid">


                                {/* NITROGEN */}

                                <div className="sensor-item">

                                    <div className="sensor-icon">
                                        N
                                    </div>

                                    <div>

                                        <span>
                                            {isKannada
                                                ? "ಸಾರಜನಕ"
                                                : "Nitrogen"}
                                        </span>

                                        <strong>
                                            {sensorData.nitrogen ?? "N/A"}
                                        </strong>

                                        <small>
                                            mg/kg
                                        </small>

                                    </div>

                                </div>


                                {/* PHOSPHORUS */}

                                <div className="sensor-item">

                                    <div className="sensor-icon">
                                        P
                                    </div>

                                    <div>

                                        <span>
                                            {isKannada
                                                ? "ರಂಜಕ"
                                                : "Phosphorus"}
                                        </span>

                                        <strong>
                                            {sensorData.phosphorus ?? "N/A"}
                                        </strong>

                                        <small>
                                            mg/kg
                                        </small>

                                    </div>

                                </div>


                                {/* POTASSIUM */}

                                <div className="sensor-item">

                                    <div className="sensor-icon">
                                        K
                                    </div>

                                    <div>

                                        <span>
                                            {isKannada
                                                ? "ಪೊಟ್ಯಾಸಿಯಂ"
                                                : "Potassium"}
                                        </span>

                                        <strong>
                                            {sensorData.potassium ?? "N/A"}
                                        </strong>

                                        <small>
                                            mg/kg
                                        </small>

                                    </div>

                                </div>


                                {/* TEMPERATURE */}

                                <div className="sensor-item">

                                    <div className="sensor-icon">
                                        🌡️
                                    </div>

                                    <div>

                                        <span>
                                            {isKannada
                                                ? "ತಾಪಮಾನ"
                                                : "Temperature"}
                                        </span>

                                        <strong>

                                            {sensorData.temperature ?? "N/A"}

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

                                <div className="sensor-item">

                                    <div className="sensor-icon">
                                        💧
                                    </div>

                                    <div>

                                        <span>
                                            {isKannada
                                                ? "ಆರ್ದ್ರತೆ"
                                                : "Humidity"}
                                        </span>

                                        <strong>

                                            {sensorData.humidity ?? "N/A"}

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

                                <div className="sensor-item">

                                    <div className="sensor-icon">
                                        🌧️
                                    </div>

                                    <div>

                                        <span>
                                            {isKannada
                                                ? "ಮಳೆ ಪ್ರಮಾಣ"
                                                : "Rainfall"}
                                        </span>

                                        <strong>

                                            {sensorData.rainfall ?? "N/A"}

                                            {sensorData.rainfall != null
                                                ? " mm"
                                                : ""}

                                        </strong>

                                        <small>
                                            {isKannada
                                                ? "ಪ್ರಸ್ತುತ ಮಳೆ ಪ್ರಮಾಣ"
                                                : "Current rainfall"}
                                        </small>

                                    </div>

                                </div>


                                {/* SOIL MOISTURE */}

                                <div className="sensor-item sensor-item-secondary">

                                    <div className="sensor-icon">
                                        🌱
                                    </div>

                                    <div>

                                        <span>
                                            {isKannada
                                                ? "ಮಣ್ಣಿನ ತೇವಾಂಶ"
                                                : "Soil Moisture"}
                                        </span>

                                        <strong>

                                            {sensorData.soil_moisture ?? "N/A"}

                                            {sensorData.soil_moisture != null
                                                ? " %"
                                                : ""}

                                        </strong>

                                        <small>
                                            {isKannada
                                                ? "ನೀರಾವರಿ ವ್ಯವಸ್ಥೆಯಿಂದ ಬಳಸಲಾಗುತ್ತದೆ"
                                                : "Used by irrigation system"}
                                        </small>

                                    </div>

                                </div>

                            </div>

                        </div>


                        {/* =================================================
                            MODEL INFORMATION
                        ================================================= */}

                        <div className="model-info-card">

                            <div className="model-icon">
                                🤖
                            </div>

                            <div className="model-info-content">

                                <strong>
                                    {isKannada
                                        ? "Random Forest AI ಮಾದರಿ"
                                        : "Random Forest AI Model"}
                                </strong>

                                <p>
                                    {isKannada
                                        ? "ನಿಮ್ಮ ನೈಜ ಸಮಯದ ಪರಿಸರ ಮತ್ತು ಮಣ್ಣಿನ ಪರಿಸ್ಥಿತಿಗಳ ಆಧಾರದ ಮೇಲೆ ಶಿಫಾರಸು ರಚಿಸಲಾಗುತ್ತದೆ."
                                        : "Recommendation is generated from your live environmental and soil conditions."}
                                </p>

                            </div>

                            <div className="model-stats">

                                <span>
                                    50000
                                </span>

                                <small>
                                    {isKannada
                                        ? "ತರಬೇತಿ ದಾಖಲೆಗಳು"
                                        : "Training Records"}
                                </small>

                            </div>

                            <div className="model-stats">

                                <span>
                                    22
                                </span>

                                <small>
                                    {isKannada
                                        ? "ಬೆಳೆ ವರ್ಗಗಳು"
                                        : "Crop Classes"}
                                </small>

                            </div>

                        </div>


                        {/* =================================================
                            RECOMMEND BUTTON
                        ================================================= */}

                        <button
                            className="recommend-button"
                            onClick={
                                handleRecommendation
                            }
                            disabled={
                                predicting
                            }
                        >

                            {predicting ? (

                                <>

                                    <span className="button-spinner">
                                        ⟳
                                    </span>

                                    {isKannada
                                        ? "ಕೃಷಿ ಪರಿಸ್ಥಿತಿಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ..."
                                        : "Analyzing Farm Conditions..."}

                                </>

                            ) : (

                                <>
                                    🌾{" "}
                                    {isKannada
                                        ? "ಸೂಕ್ತವಾದ ಬೆಳೆ ಶಿಫಾರಸು ಮಾಡಿ"
                                        : "Recommend Suitable Crop"}
                                </>

                            )}

                        </button>


                    </>

                )}


            {/* =================================================
                RECOMMENDATION RESULT
            ================================================= */}

            {recommendation && (

                <div className="recommendation-result">


                    {/* RESULT HEADER */}

                    <div className="result-header">

                        <span className="result-icon">
                            🌱
                        </span>

                        <div>

                            <h2>
                                {isKannada
                                    ? "ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ"
                                    : "Recommended Crop"}
                            </h2>

                            <p>
                                {isKannada
                                    ? "ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಕೃಷಿ ಪರಿಸ್ಥಿತಿಗಳ ಆಧಾರದ ಮೇಲೆ"
                                    : "Based on your current farm conditions"}
                            </p>

                        </div>

                    </div>


                    {/* CROP NAME */}

                    <div className="crop-result">

                        <span className="crop-result-label">
                            {isKannada
                                ? "ಅತ್ಯುತ್ತಮ ಹೊಂದಾಣಿಕೆ"
                                : "Best Match"}
                        </span>

                        <strong>
                            {formatCropName(
                                recommendation.recommended_crop
                            )}
                        </strong>

                    </div>


                    {/* CONFIDENCE */}

                    {recommendation.confidence != null && (

                        <div className="confidence-section">

                            <div className="confidence-header">

                                <span>
                                    {isKannada
                                        ? "AI ವಿಶ್ವಾಸಾರ್ಹತೆ"
                                        : "AI Confidence"}
                                </span>

                                <strong>
                                    {recommendation.confidence}%
                                </strong>

                            </div>

                            <div className="confidence-bar">

                                <div
                                    className="confidence-fill"
                                    style={{
                                        width: `${Math.min(
                                            100,
                                            Math.max(
                                                0,
                                                Number(
                                                    recommendation.confidence
                                                )
                                            )
                                        )}%`
                                    }}
                                />

                            </div>

                        </div>

                    )}


                    {/* FARMING ADVICE */}

                    {recommendation.advice && (

                        <div className="crop-advice">

                            <div className="advice-icon">
                                💡
                            </div>

                            <div>

                                <h3>
                                    {isKannada
                                        ? "ಕೃಷಿ ಸಲಹೆ"
                                        : "Farming Advice"}
                                </h3>

                                <p>
                                    {recommendation.advice}
                                </p>

                            </div>

                        </div>

                    )}


                    {/* MODEL DETAILS */}

                    <div className="result-details">

                        <div>

                            <span>
                                {isKannada
                                    ? "ಮಾದರಿ"
                                    : "Model"}
                            </span>

                            <strong>
                                {
                                    recommendation.model ||
                                    "Random Forest"
                                }
                            </strong>

                        </div>

                        <div>

                            <span>
                                {isKannada
                                    ? "ಡೇಟಾಸೆಟ್"
                                    : "Dataset"}
                            </span>

                            <strong>
                                {
                                    recommendation.dataset_records ||
                                    2200
                                }{" "}
                                {isKannada
                                    ? "ದಾಖಲೆಗಳು"
                                    : "records"}
                            </strong>

                        </div>

                        <div>

                            <span>
                                {isKannada
                                    ? "ಬೆಳೆ ವರ್ಗಗಳು"
                                    : "Crop Classes"}
                            </span>

                            <strong>
                                {
                                    recommendation.crop_classes ||
                                    22
                                }
                            </strong>

                        </div>

                        {recommendation.model_accuracy != null && (

                            <div>

                                <span>
                                    {isKannada
                                        ? "ಪರೀಕ್ಷಾ ನಿಖರತೆ"
                                        : "Test Accuracy"}
                                </span>

                                <strong>
                                    {
                                        recommendation.model_accuracy
                                    }%
                                </strong>

                            </div>

                        )}

                    </div>

                </div>

            )}

        </div>

    );

}


export default Crop;