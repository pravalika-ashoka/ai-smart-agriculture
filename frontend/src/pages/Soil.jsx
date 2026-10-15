import React, {
    useCallback,
    useEffect,
    useState
} from "react";

import {
    getLatestSensorData,
    getSoilAnalysis
} from "../services/api";

import BackToDashboard from "../components/BackToDashboard";

import "./Soil.css";


// =========================================================
// TRANSLATIONS
// =========================================================

const translations = {

    en: {

        language: "Language",
        english: "English",
        kannada: "ಕನ್ನಡ",

        title: "Soil Analysis",
        subtitle:
            "AI-powered soil health analysis using live IoT sensor data.",

        liveSensorData: "Live Soil Sensor Data",
        refreshMessage:
            "Live sensor values are automatically refreshed every 5 seconds.",

        live: "LIVE",
        lastUpdated: "Last updated:",

        loading: "Loading live sensor data...",

        nitrogen: "Nitrogen",
        phosphorus: "Phosphorus",
        potassium: "Potassium",
        soilMoisture: "Soil Moisture",
        temperature: "Temperature",
        humidity: "Humidity",
        rainfall: "Rainfall",

        mgkg: "mg/kg",
        percent: "%",
        celsius: "°C",
        mm: "mm",

        analyzeSoil: "Analyze Soil",
        analyzingSoil: "Analyzing Soil...",

        noSensorData: "No Live Sensor Data",
        noSensorDescription:
            "The system could not receive data from the IoT sensor endpoint.",

        retry: "Retry",

        soilAnalysisResult: "Soil Analysis Result",
        resultDescription:
            "AI prediction based on the latest live soil readings.",

        soilHealth: "Soil Health",
        predictionConfidence: "Prediction Confidence",
        modelAccuracy: "Model Accuracy",

        probabilities: "Prediction Probabilities",

        recommendation: "Recommendation",

        explanation: "AI / SHAP Explanation",

        method: "Method:",
        importantFactors: "Important Soil Factors",
        impact: "Impact:",
        shapImportance: "SHAP importance:",

        authenticationExpired:
            "Authentication expired. Please login again.",

        endpointNotFound:
            "IoT endpoint /iot/latest was not found.",

        unableToFetch:
            "Unable to fetch live IoT sensor data.",

        liveDataMissing:
            "Live IoT data received, but these required values are missing:",

        liveDataUnavailable:
            "Live soil sensor data is not available.",

        cannotAnalyze:
            "Cannot analyze soil. Missing or invalid values:",

        unableToAnalyze:
            "Unable to analyze soil.",

        noAnalysis:
            "No Analysis Yet",

        noResultMessage:
            "Click Analyze Soil to generate the AI soil health result."
    },


    kn: {

        language: "ಭಾಷೆ",
        english: "English",
        kannada: "ಕನ್ನಡ",

        title: "ಮಣ್ಣಿನ ವಿಶ್ಲೇಷಣೆ",

        subtitle:
            "ಲೈವ್ IoT ಸೆನ್ಸರ್ ಡೇಟಾವನ್ನು ಬಳಸಿ AI ಆಧಾರಿತ ಮಣ್ಣಿನ ಆರೋಗ್ಯ ವಿಶ್ಲೇಷಣೆ.",

        liveSensorData:
            "ಲೈವ್ ಮಣ್ಣಿನ ಸೆನ್ಸರ್ ಡೇಟಾ",

        refreshMessage:
            "ಲೈವ್ ಸೆನ್ಸರ್ ಮೌಲ್ಯಗಳನ್ನು ಪ್ರತಿ 5 ಸೆಕೆಂಡಿಗೆ ಸ್ವಯಂಚಾಲಿತವಾಗಿ ನವೀಕರಿಸಲಾಗುತ್ತದೆ.",

        live: "ಲೈವ್",

        lastUpdated:
            "ಕೊನೆಯ ನವೀಕರಣ:",

        loading:
            "ಲೈವ್ ಸೆನ್ಸರ್ ಡೇಟಾ ಲೋಡ್ ಆಗುತ್ತಿದೆ...",

        nitrogen:
            "ಸಾರಜನಕ",

        phosphorus:
            "ರಂಜಕ",

        potassium:
            "ಪೊಟ್ಯಾಸಿಯಂ",

        soilMoisture:
            "ಮಣ್ಣಿನ ತೇವಾಂಶ",

        temperature:
            "ತಾಪಮಾನ",

        humidity:
            "ಆರ್ದ್ರತೆ",

        rainfall:
            "ಮಳೆ",

        mgkg:
            "mg/kg",

        percent:
            "%",

        celsius:
            "°C",

        mm:
            "mm",

        analyzeSoil:
            "ಮಣ್ಣನ್ನು ವಿಶ್ಲೇಷಿಸಿ",

        analyzingSoil:
            "ಮಣ್ಣನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...",

        noSensorData:
            "ಲೈವ್ ಸೆನ್ಸರ್ ಡೇಟಾ ಲಭ್ಯವಿಲ್ಲ",

        noSensorDescription:
            "IoT ಸೆನ್ಸರ್ ಎಂಡ್‌ಪಾಯಿಂಟ್‌ನಿಂದ ಡೇಟಾವನ್ನು ಸ್ವೀಕರಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",

        retry:
            "ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ",

        soilAnalysisResult:
            "ಮಣ್ಣಿನ ವಿಶ್ಲೇಷಣೆಯ ಫಲಿತಾಂಶ",

        resultDescription:
            "ಇತ್ತೀಚಿನ ಲೈವ್ ಮಣ್ಣಿನ ಮೌಲ್ಯಗಳನ್ನು ಆಧರಿಸಿದ AI ಮುನ್ಸೂಚನೆ.",

        soilHealth:
            "ಮಣ್ಣಿನ ಆರೋಗ್ಯ",

        predictionConfidence:
            "ಮುನ್ಸೂಚನೆಯ ವಿಶ್ವಾಸಾರ್ಹತೆ",

        modelAccuracy:
            "ಮಾದರಿ ನಿಖರತೆ",

        probabilities:
            "ಮುನ್ಸೂಚನೆಯ ಸಂಭವನೀಯತೆಗಳು",

        recommendation:
            "ಶಿಫಾರಸು",

        explanation:
            "AI / SHAP ವಿವರಣೆ",

        method:
            "ವಿಧಾನ:",

        importantFactors:
            "ಪ್ರಮುಖ ಮಣ್ಣಿನ ಅಂಶಗಳು",

        impact:
            "ಪರಿಣಾಮ:",

        shapImportance:
            "SHAP ಪ್ರಾಮುಖ್ಯತೆ:",

        authenticationExpired:
            "ದೃಢೀಕರಣದ ಅವಧಿ ಮುಗಿದಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಲಾಗಿನ್ ಮಾಡಿ.",

        endpointNotFound:
            "IoT ಎಂಡ್‌ಪಾಯಿಂಟ್ /iot/latest ಕಂಡುಬಂದಿಲ್ಲ.",

        unableToFetch:
            "ಲೈವ್ IoT ಸೆನ್ಸರ್ ಡೇಟಾವನ್ನು ಪಡೆಯಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",

        liveDataMissing:
            "ಲೈವ್ IoT ಡೇಟಾ ಸ್ವೀಕರಿಸಲಾಗಿದೆ, ಆದರೆ ಈ ಅಗತ್ಯ ಮೌಲ್ಯಗಳು ಲಭ್ಯವಿಲ್ಲ:",

        liveDataUnavailable:
            "ಲೈವ್ ಮಣ್ಣಿನ ಸೆನ್ಸರ್ ಡೇಟಾ ಲಭ್ಯವಿಲ್ಲ.",

        cannotAnalyze:
            "ಮಣ್ಣನ್ನು ವಿಶ್ಲೇಷಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ. ಕಾಣೆಯಾದ ಅಥವಾ ಅಮಾನ್ಯ ಮೌಲ್ಯಗಳು:",

        unableToAnalyze:
            "ಮಣ್ಣನ್ನು ವಿಶ್ಲೇಷಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",

        noAnalysis:
            "ಇನ್ನೂ ಯಾವುದೇ ವಿಶ್ಲೇಷಣೆ ಇಲ್ಲ",

        noResultMessage:
            "AI ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಫಲಿತಾಂಶವನ್ನು ಪಡೆಯಲು 'ಮಣ್ಣನ್ನು ವಿಶ್ಲೇಷಿಸಿ' ಬಟನ್ ಒತ್ತಿರಿ."
    }
};


// =========================================================
// SENSOR CARD
// =========================================================

function SensorCard({
    label,
    value,
    unit,
    icon,
    accent
}) {

    const hasValue =
        value !== undefined &&
        value !== null &&
        value !== "" &&
        Number.isFinite(Number(value));

    const decimals = 1;

    return (
        <div
            className={`soil-sensor-item ${accent || ""}`}
        >

            <div className="soil-sensor-top">

                <div className="soil-sensor-icon">
                    {icon}
                </div>

                <span className="soil-sensor-label">
                    {label}
                </span>

            </div>

            <div className="soil-sensor-value">

                {hasValue
                    ? Number(value).toFixed(decimals)
                    : "--"}

            </div>

            <div className="soil-sensor-unit">
                {unit}
            </div>

        </div>
    );
}


// =========================================================
// NUMBER HELPER
// =========================================================

function getNumber(...values) {

    for (const value of values) {

        if (
            value !== undefined &&
            value !== null &&
            value !== ""
        ) {

            const number =
                Number(value);

            if (
                Number.isFinite(number)
            ) {

                return number;
            }
        }
    }

    return null;
}


// =========================================================
// NORMALIZE IOT RESPONSE
// =========================================================

function normalizeSensorData(response) {

    console.log(
        "RAW IOT RESPONSE:",
        response
    );

    let source = response;

    if (
        source?.data &&
        typeof source.data === "object"
    ) {
        source = source.data;
    }

    if (
        source?.sensor_data &&
        typeof source.sensor_data === "object"
    ) {
        source = source.sensor_data;
    }

    if (
        source?.latest &&
        typeof source.latest === "object"
    ) {
        source = source.latest;
    }

    if (
        source?.latest_sensor_data &&
        typeof source.latest_sensor_data === "object"
    ) {

        source =
            source.latest_sensor_data;
    }

    console.log(
        "NORMALIZED IOT SOURCE:",
        source
    );


    const nitrogen =
        getNumber(
            source?.nitrogen,
            source?.N,
            source?.n
        );


    const phosphorus =
        getNumber(
            source?.phosphorus,
            source?.P,
            source?.p
        );


    const potassium =
        getNumber(
            source?.potassium,
            source?.K,
            source?.k
        );



    const moisture =
        getNumber(
            source?.soil_moisture,
            source?.moisture,
            source?.soilMoisture
        );


    const temperature =
        getNumber(
            source?.temperature,
            source?.soil_temperature,
            source?.soilTemperature
        );


    const humidity =
        getNumber(
            source?.humidity,
            source?.air_humidity,
            source?.airHumidity
        );


    const rainfall =
        getNumber(
            source?.rainfall,
            source?.rain,
            source?.rainfall_amount
        );


    return {

        nitrogen,

        phosphorus,

        potassium,

        soil_moisture:
            moisture,

        moisture,

        temperature,

        humidity,

        rainfall
    };
}


// =========================================================
// FORMAT VALUE
// =========================================================

function formatValue(
    value,
    decimals = 2
) {

    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {

        return "--";
    }

    const number =
        Number(value);

    if (
        !Number.isFinite(number)
    ) {

        return String(value);
    }

    return number.toFixed(
        decimals
    );
}


// =========================================================
// STATUS CLASS
// =========================================================

function getStatusClass(status) {

    if (!status) {
        return "";
    }

    return `soil-health-${String(status)
        .toLowerCase()
        .replace(/\s+/g, "-")}`;
}


// =========================================================
// PROBABILITY BAR
// =========================================================

function ProbabilityCard({
    label,
    value
}) {

    const number =
        Number(value);

    const safeValue =
        Number.isFinite(number)
            ? Math.max(
                0,
                Math.min(100, number)
            )
            : 0;

    return (

        <div className="soil-probability-card">

            <div className="soil-probability-header">

                <span>
                    {label}
                </span>

                <strong>
                    {formatValue(value, 2)}%
                </strong>

            </div>

            <div className="soil-progress">

                <div
                    className="soil-progress-fill"
                    style={{
                        width: `${safeValue}%`
                    }}
                />

            </div>

        </div>
    );
}


// =========================================================
// SOIL PAGE
// =========================================================

function Soil() {

    // =====================================================
    // LANGUAGE
    // =====================================================

    const [
        language,
        setLanguage
    ] = useState(
        localStorage.getItem(
            "soilLanguage"
        ) || "en"
    );


    const t =
        translations[language];


    const changeLanguage =
        (newLanguage) => {

            setLanguage(
                newLanguage
            );

            localStorage.setItem(
                "soilLanguage",
                newLanguage
            );
        };


    // =====================================================
    // STATE
    // =====================================================

    const [
        sensorData,
        setSensorData
    ] = useState(null);


    const [
        analysis,
        setAnalysis
    ] = useState(null);


    const [
        loading,
        setLoading
    ] = useState(true);


    const [
        analyzing,
        setAnalyzing
    ] = useState(false);


    const [
        error,
        setError
    ] = useState("");


    const [
        lastUpdated,
        setLastUpdated
    ] = useState(null);


    // =====================================================
    // LOAD SENSOR DATA
    // =====================================================

    const loadSensorData =
        useCallback(async () => {

            try {

                const response =
                    await getLatestSensorData();

                console.log(
                    "Soil API response:",
                    response
                );


                const normalized =
                    normalizeSensorData(
                        response
                    );


                const requiredFields = {

                    nitrogen:
                        normalized.nitrogen,

                    phosphorus:
                        normalized.phosphorus,

                    potassium:
                        normalized.potassium,

                    moisture:
                        normalized.moisture,

                    temperature:
                        normalized.temperature
                };


                const missingFields =
                    Object.entries(
                        requiredFields
                    )
                        .filter(
                            ([, value]) =>
                                value === null
                        )
                        .map(
                            ([key]) =>
                                key
                        );


                setSensorData(
                    normalized
                );


                setLastUpdated(
                    new Date()
                );


                if (
                    missingFields.length > 0
                ) {

                    setError(
                        `${t.liveDataMissing} ${missingFields.join(", ")}`
                    );

                } else {

                    setError("");
                }

            }

            catch (err) {

                console.error(
                    "SOIL IOT ERROR:",
                    err
                );


                let message =
                    t.unableToFetch;


                if (
                    err?.response?.status === 401
                ) {

                    message =
                        t.authenticationExpired;

                }

                else if (
                    err?.response?.status === 404
                ) {

                    message =
                        t.endpointNotFound;

                }

                else if (
                    err?.response?.data?.detail
                ) {

                    message =
                        typeof err.response.data.detail ===
                            "string"
                            ? err.response.data.detail
                            : JSON.stringify(
                                err.response.data.detail
                            );

                }

                else if (
                    err?.message
                ) {

                    message =
                        err.message;
                }


                setError(
                    message
                );

            }

            finally {

                setLoading(false);
            }

        }, [language]);


    // =====================================================
    // INITIAL LOAD + 5 SECOND REFRESH
    // =====================================================

    useEffect(() => {

        loadSensorData();

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

    }, [loadSensorData]);


    // =====================================================
    // SOIL ANALYSIS
    // =====================================================

    const handleSoilAnalysis =
        async () => {

            if (!sensorData) {

                setError(
                    t.liveDataUnavailable
                );

                return;
            }


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

                moisture:
                    Number(
                        sensorData.moisture
                    ),

                temperature:
                    Number(
                        sensorData.temperature
                    )
            };


            const invalidFields =
                Object.entries(
                    inputData
                )
                    .filter(
                        ([, value]) =>
                            !Number.isFinite(
                                value
                            )
                    )
                    .map(
                        ([key]) =>
                            key
                    );


            if (
                invalidFields.length > 0
            ) {

                setError(
                    `${t.cannotAnalyze} ${invalidFields.join(", ")}`
                );

                return;
            }


            try {

                setAnalyzing(
                    true
                );

                setAnalysis(
                    null
                );

                setError("");


                console.log(
                    "SOIL ANALYSIS INPUT:",
                    inputData
                );


                const result =
                    await getSoilAnalysis(
                        inputData
                    );


                console.log(
                    "SOIL ANALYSIS RESULT:",
                    result
                );


                setAnalysis(
                    result
                );

            }

            catch (err) {

                console.error(
                    "SOIL ANALYSIS ERROR:",
                    err
                );


                const detail =
                    err?.response?.data?.detail;


                if (
                    Array.isArray(detail)
                ) {

                    setError(
                        detail
                            .map(
                                item =>
                                    `${item.loc?.join(" → ") || "Field"}: ${item.msg}`
                            )
                            .join(" | ")
                    );

                }

                else if (
                    typeof detail ===
                    "string"
                ) {

                    setError(
                        detail
                    );

                }

                else {

                    setError(
                        err?.message ||
                        t.unableToAnalyze
                    );
                }

            }

            finally {

                setAnalyzing(
                    false
                );
            }
        };


    // =====================================================
    // PAGE
    // =====================================================

    return (

        <div
            className={`soil-page ${
                language === "kn"
                    ? "soil-kannada"
                    : ""
            }`}
        >

            {/* =================================================
                TOP BAR
            ================================================= */}

            <div className="soil-top-bar">

                <BackToDashboard />

                <button
                    type="button"
                    className="soil-language-button"
                    onClick={() =>
                        changeLanguage(
                            language === "en"
                                ? "kn"
                                : "en"
                        )
                    }
                    title={
                        language === "en"
                            ? "ಕನ್ನಡಕ್ಕೆ ಬದಲಾಯಿಸಿ"
                            : "Switch to English"
                    }
                >

                    <span className="soil-language-icon">
                        🌐
                    </span>

                    {language === "en"
                        ? "ಕನ್ನಡ"
                        : "English"}

                </button>

            </div>


            {/* =================================================
                HEADER
            ================================================= */}

            <header className="soil-header">

                <div className="soil-title-row">

                    <div>

                        <div className="soil-title-icon">
                            🌱
                        </div>

                    </div>

                    <div>

                        <h1>
                            {t.title}
                        </h1>

                        <p>
                            {t.subtitle}
                        </p>

                    </div>

                </div>

            </header>


            {/* =================================================
                ERROR
            ================================================= */}

            {!loading &&
                error && (

                    <div className="soil-error">

                        <span className="soil-error-icon">
                            ⚠️
                        </span>

                        <div>
                            {error}
                        </div>

                    </div>
                )}


            {/* =================================================
                LIVE SENSOR SECTION
            ================================================= */}

            <section className="soil-analysis-card">

                <div className="soil-sensor-header">

                    <div>

                        <div className="soil-section-title">

                            <span className="soil-section-icon">
                                📡
                            </span>

                            <div>

                                <h2>
                                    {t.liveSensorData}
                                </h2>

                                <p>
                                    {t.refreshMessage}
                                </p>

                            </div>

                        </div>

                    </div>


                    <div className="soil-live-indicator">

                        <span className="soil-live-dot" />

                        {t.live}

                    </div>

                </div>


                {lastUpdated && (

                    <div className="soil-last-updated">

                        <span>
                            {t.lastUpdated}
                        </span>

                        <strong>
                            {lastUpdated.toLocaleTimeString()}
                        </strong>

                    </div>

                )}


                {/* LOADING */}

                {loading && (

                    <div className="soil-loading">

                        <div className="soil-spinner" />

                        <span>
                            {t.loading}
                        </span>

                    </div>

                )}


                {/* SENSOR DATA */}

                {!loading &&
                    sensorData && (

                        <div className="soil-sensor-grid">

                            <SensorCard
                                label={t.nitrogen}
                                value={
                                    sensorData.nitrogen
                                }
                                unit={t.mgkg}
                                icon="N"
                                accent="soil-accent-n"
                            />

                            <SensorCard
                                label={t.phosphorus}
                                value={
                                    sensorData.phosphorus
                                }
                                unit={t.mgkg}
                                icon="P"
                                accent="soil-accent-p"
                            />

                            <SensorCard
                                label={t.potassium}
                                value={
                                    sensorData.potassium
                                }
                                unit={t.mgkg}
                                icon="K"
                                accent="soil-accent-k"
                            />

                            <SensorCard
                                label={t.soilMoisture}
                                value={
                                    sensorData.moisture
                                }
                                unit={t.percent}
                                icon="💧"
                                accent="soil-accent-moisture"
                            />

                            <SensorCard
                                label={t.temperature}
                                value={
                                    sensorData.temperature
                                }
                                unit={t.celsius}
                                icon="🌡️"
                                accent="soil-accent-temperature"
                            />

                            <SensorCard
                                label={t.humidity}
                                value={
                                    sensorData.humidity
                                }
                                unit={t.percent}
                                icon="💨"
                                accent="soil-accent-humidity"
                            />

                            <SensorCard
                                label={t.rainfall}
                                value={
                                    sensorData.rainfall
                                }
                                unit={t.mm}
                                icon="🌧️"
                                accent="soil-accent-rainfall"
                            />

                        </div>
                    )}


                {/* NO SENSOR DATA */}

                {!loading &&
                    !sensorData && (

                        <div className="soil-empty-result">

                            <div className="soil-result-icon">
                                📡
                            </div>

                            <strong>
                                {t.noSensorData}
                            </strong>

                            <p>
                                {t.noSensorDescription}
                            </p>

                            <button
                                type="button"
                                className="soil-refresh-button"
                                onClick={
                                    loadSensorData
                                }
                            >
                                {t.retry}
                            </button>

                        </div>
                    )}


                {/* ANALYZE */}

                {sensorData && (

                    <button
                        type="button"
                        className="soil-analyze-button"
                        onClick={
                            handleSoilAnalysis
                        }
                        disabled={
                            analyzing
                        }
                    >

                        {analyzing ? (
                            <>
                                <span className="soil-button-spinner" />
                                {t.analyzingSoil}
                            </>
                        ) : (
                            <>
                                <span>
                                    🔬
                                </span>
                                {t.analyzeSoil}
                            </>
                        )}

                    </button>

                )}

            </section>


            {/* =================================================
                RESULT SECTION
            ================================================= */}

            <section className="soil-result-card">

                <div className="soil-result-header">

                    <div className="soil-section-title">

                        <span className="soil-section-icon">
                            🌱
                        </span>

                        <div>

                            <h2>
                                {t.soilAnalysisResult}
                            </h2>

                            <p>
                                {t.resultDescription}
                            </p>

                        </div>

                    </div>

                </div>


                {!analysis && (

                    <div className="soil-empty-result">

                        <div className="soil-result-icon">
                            🌱
                        </div>

                        <strong>
                            {t.noAnalysis}
                        </strong>

                        <p>
                            {t.noResultMessage}
                        </p>

                    </div>
                )}


                {analysis && (

                    <div className="soil-result-content">

                        {/* =================================================
                            HEALTH
                        ================================================= */}

                        <div className="soil-health-summary">

                            <div className="soil-health-left">

                                <span className="soil-result-label">
                                    {t.soilHealth}
                                </span>

                                <div
                                    className={`soil-health-badge ${
                                        getStatusClass(
                                            analysis.soil_health
                                        )
                                    }`}
                                >

                                    <span>
                                        ●
                                    </span>

                                    {analysis.soil_health ||
                                        "N/A"}

                                </div>

                            </div>


                            <div className="soil-health-emoji">
                                🌱
                            </div>

                        </div>


                        {/* =================================================
                            CONFIDENCE + ACCURACY
                        ================================================= */}

                        <div className="soil-result-details">

                            <div className="soil-detail-card">

                                <span>
                                    {t.predictionConfidence}
                                </span>

                                <strong>

                                    {formatValue(
                                        analysis.confidence,
                                        2
                                    )}

                                    {analysis.confidence != null
                                        ? "%"
                                        : ""}

                                </strong>

                            </div>


                            <div className="soil-detail-card">

                                <span>
                                    {t.modelAccuracy}
                                </span>

                                <strong>

                                    {formatValue(
                                        analysis.accuracy ??
                                        analysis.model_accuracy,
                                        2
                                    )}

                                    {(analysis.accuracy ??
                                        analysis.model_accuracy) != null
                                        ? "%"
                                        : ""}

                                </strong>

                            </div>

                        </div>


                        {/* =================================================
                            PROBABILITIES
                        ================================================= */}

                        {analysis.probabilities && (

                            <div className="soil-recommendation">

                                <div className="soil-subsection-heading">

                                    <span>
                                        📊
                                    </span>

                                    <h3>
                                        {t.probabilities}
                                    </h3>

                                </div>


                                <div className="soil-probability-grid">

                                    {Object.entries(
                                        analysis.probabilities
                                    ).map(
                                        ([label, value]) => (

                                            <ProbabilityCard
                                                key={label}
                                                label={label}
                                                value={value}
                                            />

                                        )
                                    )}

                                </div>

                            </div>
                        )}


                        {/* =================================================
                            RECOMMENDATION
                        ================================================= */}

                        {analysis.recommendation && (

                            <div className="soil-recommendation soil-recommendation-highlight">

                                <div className="soil-subsection-heading">

                                    <span>
                                        🌾
                                    </span>

                                    <h3>
                                        {t.recommendation}
                                    </h3>

                                </div>

                                <p>
                                    {analysis.recommendation}
                                </p>

                            </div>
                        )}


                        {/* =================================================
                            SHAP EXPLANATION
                        ================================================= */}

                        {analysis.explanation && (

                            <div className="soil-explanation">

                                <div className="soil-subsection-heading">

                                    <span>
                                        🤖
                                    </span>

                                    <h3>
                                        {t.explanation}
                                    </h3>

                                </div>


                                {analysis.explanation.method && (

                                    <div className="soil-method">

                                        <strong>
                                            {t.method}
                                        </strong>

                                        <span>
                                            {analysis.explanation.method}
                                        </span>

                                    </div>
                                )}


                                {Array.isArray(
                                    analysis.explanation.features
                                ) && (

                                    <>

                                        <h4>
                                            {t.importantFactors}
                                        </h4>

                                        <div className="soil-features">

                                            {analysis
                                                .explanation
                                                .features
                                                .map(
                                                    (
                                                        feature,
                                                        index
                                                    ) => (

                                                        <div
                                                            className="soil-feature"
                                                            key={
                                                                index
                                                            }
                                                        >

                                                            <div className="soil-feature-header">

                                                                <span>
                                                                    {feature.feature}
                                                                </span>

                                                                <strong>
                                                                    {feature.value}
                                                                </strong>

                                                            </div>


                                                            {feature.impact && (

                                                                <small>

                                                                    <b>
                                                                        {t.impact}
                                                                    </b>{" "}

                                                                    {feature.impact}

                                                                </small>
                                                            )}


                                                            {feature.importance !==
                                                                undefined && (

                                                                <small>

                                                                    <b>
                                                                        {t.shapImportance}
                                                                    </b>{" "}

                                                                    {feature.importance}

                                                                </small>
                                                            )}


                                                            {feature.description && (

                                                                <small>
                                                                    {
                                                                        feature.description
                                                                    }
                                                                </small>
                                                            )}

                                                        </div>

                                                    )
                                                )}

                                        </div>

                                    </>
                                )}

                            </div>
                        )}

                    </div>
                )}

            </section>

        </div>
    );
}


export default Soil;