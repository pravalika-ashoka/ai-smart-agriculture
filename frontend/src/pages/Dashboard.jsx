import React, {
    useEffect,
    useState
} from "react";

import {
    Link,
    useNavigate
} from "react-router-dom";

import NotificationBell from "../components/NotificationBell";

import "./Dashboard.css";


const API_URL =
    import.meta.env.VITE_API_URL ||
    "https://ai-smart-agriculture-production.up.railway.app";


function Dashboard() {

    const navigate = useNavigate();

    const [username, setUsername] =
        useState("");

    const [sensorData, setSensorData] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [refreshing, setRefreshing] =
        useState(false);

    const [sensorError, setSensorError] =
        useState("");

    const [lastUpdated, setLastUpdated] =
        useState(null);


    // ========================================
    // SENSOR HISTORY - NEW
    // ========================================

    const [sensorHistory, setSensorHistory] =
        useState([]);

    const [historyLoading, setHistoryLoading] =
        useState(false);

    const [historyError, setHistoryError] =
        useState("");


    // ========================================
    // LANGUAGE
    // ========================================

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


    // ========================================
    // LOAD DASHBOARD
    // ========================================

    useEffect(() => {

        loadDashboard();

        // NEW: Fetch saved sensor history.
        fetchSensorHistory();

        const interval = setInterval(() => {

            refreshSensorData();

            // NEW: Refresh history independently.
            fetchSensorHistory();

        }, 60000);

        return () => {

            clearInterval(interval);

        };

    }, []);


    // ========================================
    // GET TOKEN
    // ========================================

    const getToken = () => {

        return localStorage.getItem(
            "token"
        );

    };


    // ========================================
    // LOAD DASHBOARD
    // ========================================

    const loadDashboard = async () => {

        const token = getToken();

        if (!token) {

            navigate("/");

            return;

        }


        try {

            setLoading(true);

            setSensorError("");


            // ========================================
            // USER PROFILE
            // ========================================

            const profileResponse =
                await fetch(
                    `${API_URL}/users/me`,
                    {
                        headers: {
                            Authorization:
                                `Bearer ${token}`,
                        },
                    }
                );


            // ========================================
            // TOKEN EXPIRED / INVALID
            // ========================================

            if (
                profileResponse.status === 401
            ) {

                localStorage.removeItem(
                    "token"
                );

                navigate("/");

                return;

            }


            if (profileResponse.ok) {

                const profile =
                    await profileResponse.json();

                setUsername(
                    profile.username ||
                    profile.full_name ||
                    ""
                );

            }


            // ========================================
            // SENSOR DATA
            // ========================================

            await fetchSensorData(token);

        }

        catch (error) {

            console.error(
                "Dashboard error:",
                error
            );

            setSensorError(
                isKannada
                    ? "ಕೃಷಿ ಬ್ಯಾಕೆಂಡ್‌ಗೆ ಸಂಪರ್ಕಿಸಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ."
                    : "Unable to connect to the agriculture backend."
            );

        }

        finally {

            setLoading(false);

        }

    };


    // ========================================
    // FETCH SENSOR DATA
    // ========================================

    const fetchSensorData = async (
        token
    ) => {

        const sensorResponse =
            await fetch(
                `${API_URL}/iot/latest`,
                {
                    headers: {
                        Authorization:
                            `Bearer ${token}`,
                    },
                }
            );


        // ========================================
        // SENSOR API ERROR
        // ========================================

        if (!sensorResponse.ok) {

            const data =
                await sensorResponse
                    .json()
                    .catch(() => ({}));


            setSensorError(
                data.detail ||
                (
                    isKannada
                        ? "ಸೆನ್ಸರ್ ಡೇಟಾ ಲಭ್ಯವಿಲ್ಲ."
                        : "Sensor data is not available."
                )
            );

            return;

        }


        // ========================================
        // SENSOR API RESPONSE
        // ========================================

        const sensors =
            await sensorResponse.json();


        console.log(
            "Sensor API response:",
            sensors
        );


        const data =
            sensors.data || sensors;


        setSensorData(data);

        setLastUpdated(
            new Date()
        );

        setSensorError("");

    };


    // ========================================
    // REFRESH SENSOR DATA
    // ========================================

    const refreshSensorData = async () => {

        const token = getToken();

        if (!token) {

            navigate("/");

            return;

        }


        try {

            setRefreshing(true);

            console.log(
                "Refreshing latest sensor values..."
            );


            await fetchSensorData(
                token
            );

        }

        catch (error) {

            console.error(
                "Sensor refresh error:",
                error
            );

            setSensorError(
                isKannada
                    ? "ಸೆನ್ಸರ್ ಡೇಟಾವನ್ನು ನವೀಕರಿಸಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ."
                    : "Unable to refresh sensor data."
            );

        }

        finally {

            setRefreshing(false);

        }

    };


    // ========================================
    // FETCH SENSOR HISTORY - NEW
    // ========================================

    const fetchSensorHistory = async () => {

        const token = getToken();

        if (!token) {
            return;
        }

        try {

            setHistoryLoading(true);

            setHistoryError("");

            const response = await fetch(
                `${API_URL}/iot/history?limit=50`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            if (response.status === 401) {

                localStorage.removeItem("token");

                navigate("/");

                return;

            }

            if (!response.ok) {

                const errorData = await response
                    .json()
                    .catch(() => ({}));

                throw new Error(
                    errorData.detail ||
                    "Unable to fetch sensor history."
                );

            }

            const result = await response.json();

            setSensorHistory(
                Array.isArray(result.data)
                    ? result.data
                    : []
            );

        }

        catch (error) {

            console.error(
                "Sensor history error:",
                error
            );

            setHistoryError(
                isKannada
                    ? "ಸೆನ್ಸರ್ ಇತಿಹಾಸವನ್ನು ಲೋಡ್ ಮಾಡಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ."
                    : "Unable to load sensor history."
            );

        }

        finally {

            setHistoryLoading(false);

        }

    };


    // ========================================
    // LOGOUT
    // ========================================

    const handleLogout = () => {

        localStorage.removeItem(
            "token"
        );

        navigate("/");

    };


    // ========================================
    // MODULES
    // ========================================

    const modules = [

        {
            title: isKannada
                ? "ಬೆಳೆ ಶಿಫಾರಸು"
                : "Crop Recommendation",

            icon: "🌱",

            description: isKannada
                ? "ಸೆನ್ಸರ್ ಮತ್ತು ಪರಿಸರದ ಡೇಟಾವನ್ನು ಬಳಸಿ ಸೂಕ್ತವಾದ ಬೆಳೆಯನ್ನು ಪಡೆಯಿರಿ."
                : "Get the most suitable crop using sensor and environmental data.",

            path: "/crop",
        },

        {
            title: isKannada
                ? "ಮಣ್ಣಿನ ವಿಶ್ಲೇಷಣೆ"
                : "Soil Analysis",

            icon: "🌿",

            description: isKannada
                ? "ನೈಜ ಸಮಯದ ಸೆನ್ಸರ್ ಮಾಹಿತಿಯನ್ನು ಬಳಸಿ ಮಣ್ಣಿನ ಆರೋಗ್ಯವನ್ನು ವಿಶ್ಲೇಷಿಸಿ."
                : "Analyze soil health using real-time sensor readings.",

            path: "/soil",
        },

        {
            title: isKannada
                ? "ರಸಗೊಬ್ಬರ ಶಿಫಾರಸು"
                : "Fertilizer Recommendation",

            icon: "🧪",

            description: isKannada
                ? "ಮಣ್ಣಿನ ಪರಿಸ್ಥಿತಿಗಳ ಆಧಾರದ ಮೇಲೆ ಸೂಕ್ತವಾದ ರಸಗೊಬ್ಬರವನ್ನು ಪಡೆಯಿರಿ."
                : "Get fertilizer recommendations based on soil conditions.",

            path: "/fertilizer",
        },

        {
            title: isKannada
                ? "ನೀರಾವರಿ"
                : "Irrigation",

            icon: "💧",

            description: isKannada
                ? "ಮಣ್ಣು ಮತ್ತು ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿಗಳನ್ನು ಬಳಸಿ ನೀರಾವರಿ ಅಗತ್ಯವನ್ನು ಊಹಿಸಿ."
                : "Predict irrigation requirements using soil and weather conditions.",

            path: "/irrigation",
        },

        {
            title: isKannada
                ? "ಬೆಳೆ ಇಳುವರಿ ಮುನ್ಸೂಚನೆ"
                : "Crop Yield Prediction",

            icon: "🌾",

            description: isKannada
                ? "ಬೆಳೆ, ಪ್ರದೇಶ, ಮಳೆ ಮತ್ತು ಕೃಷಿ ಇನ್‌ಪುಟ್‌ಗಳ ಆಧಾರದ ಮೇಲೆ ಇಳುವರಿಯನ್ನು ಊಹಿಸಿ."
                : "Predict crop yield using crop, area, rainfall and agricultural inputs.",

            path: "/yield",
        },

        {
            title: isKannada
                ? "ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ವಿಶ್ಲೇಷಣೆ"
                : "Market Price Analysis",

            icon: "📈",

            description: isKannada
                ? "ವಿವಿಧ ಮಂಡಿಗಳ ಇತ್ತೀಚಿನ ಬೆಲೆಗಳನ್ನು ವೀಕ್ಷಿಸಿ ಮತ್ತು ಉತ್ತಮ ಮಾರುಕಟ್ಟೆಯನ್ನು ಕಂಡುಹಿಡಿಯಿರಿ."
                : "View latest mandi prices and find the best market for your crop.",

            path: "/market",
        },

        {
            title: isKannada
                ? "ಸಸ್ಯ ರೋಗ ಪತ್ತೆ"
                : "Plant Disease Detection",

            icon: "🔬",

            description: isKannada
                ? "ಸಸ್ಯದ ಎಲೆಯ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಮತ್ತು ಸಸ್ಯದ ರೋಗವನ್ನು ಪತ್ತೆಹಚ್ಚಿ."
                : "Upload a plant leaf image to detect plant diseases using AI.",

            path: "/disease",
        },

        {
            title: isKannada
                ? "ಹವಾಮಾನ"
                : "Weather",

            icon: "🌦️",

            description: isKannada
                ? "ಪ್ರಸ್ತುತ ಹವಾಮಾನ ಮತ್ತು ಮುನ್ಸೂಚನೆ ಮಾಹಿತಿಯನ್ನು ವೀಕ್ಷಿಸಿ."
                : "View current weather and forecast information.",

            path: "/weather",
        },

        {
            title: isKannada
                ? "AI ಕೃಷಿ ಸಹಾಯಕ"
                : "AI Agriculture Assistant",

            icon: "🤖",

            description: isKannada
                ? "ಬೆಳೆ, ಮಣ್ಣು, ರಸಗೊಬ್ಬರ, ನೀರಾವರಿ ಮತ್ತು ಕೃಷಿಯ ಬಗ್ಗೆ AI ಜೊತೆ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ."
                : "Ask AI questions about crops, soil, fertilizer, irrigation and farming.",

            path: "/assistant",
        },

    ];


    // ========================================
    // PAGE
    // ========================================

    return (

        <div className="dashboard-page">

            {/* HEADER */}

            <header className="dashboard-header">

                <div className="dashboard-brand">

                    <img
                        src="/logo.png"
                        alt="AI Smart Agriculture"
                        className="dashboard-brand-logo"
                    />

                    <div className="dashboard-brand-text">

                        <span className="dashboard-brand-title">
                            AI Smart Agriculture
                        </span>

                        <span className="dashboard-brand-subtitle">
                            Smart Farming • Better Tomorrow
                        </span>

                    </div>

                </div>


                <div className="dashboard-header-actions">

                    {/* LANGUAGE SWITCH */}

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


                    {/* AI ASSISTANT */}

                    <button
                        className="ai-assistant-button"
                        onClick={() =>
                            navigate("/assistant")
                        }
                        title={
                            isKannada
                                ? "AI ಕೃಷಿ ಸಹಾಯಕ"
                                : "AI Agriculture Assistant"
                        }
                        aria-label={
                            isKannada
                                ? "AI ಕೃಷಿ ಸಹಾಯಕ"
                                : "AI Agriculture Assistant"
                        }
                    >
                        🤖
                    </button>


                    {/* PROFILE */}

                    <button
                        className="dashboard-profile-button"
                        onClick={() =>
                            navigate("/profile")
                        }
                        title={
                            isKannada
                                ? "ಪ್ರೊಫೈಲ್"
                                : "Profile"
                        }
                        aria-label={
                            isKannada
                                ? "ಪ್ರೊಫೈಲ್"
                                : "Profile"
                        }
                    >
                        👤
                    </button>


                    {/* NOTIFICATIONS */}

                    <NotificationBell />


                    {/* LOGOUT */}

                    <button
                        className="dashboard-logout"
                        onClick={handleLogout}
                    >
                        {isKannada
                            ? "ಲಾಗ್‌ಔಟ್"
                            : "Logout"}
                    </button>

                </div>

            </header>


            <main>

                {/* WELCOME */}

                <section className="dashboard-welcome">

                    <h2>

                        {isKannada
                            ? "ಸ್ವಾಗತ"
                            : "Welcome"}

                        {username
                            ? `, ${username}`
                            : ""}

                        {" "}👨‍🌾

                    </h2>


                    <p>

                        {isKannada
                            ? "ನಿಮ್ಮ ಕೃಷಿ ಕ್ಷೇತ್ರವನ್ನು ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಿ ಮತ್ತು AI ಆಧಾರಿತ ಕೃಷಿ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ."
                            : "Monitor your farm and get AI-powered agricultural recommendations."}

                    </p>

                </section>


                {/* SENSOR SECTION */}

                <section className="sensor-section">

                    <div className="section-title">

                        <div>

                            <h2>

                                📡{" "}

                                {isKannada
                                    ? "ಲೈವ್ ಸೆನ್ಸರ್ ಡೇಟಾ"
                                    : "Live Sensor Data"}

                            </h2>


                            <p>

                                {isKannada
                                    ? "ನಿಮ್ಮ ಕೃಷಿ ಕ್ಷೇತ್ರದ ಸೆನ್ಸರ್‌ಗಳಿಂದ ನೈಜ ಸಮಯದ ಮಾಹಿತಿ."
                                    : "Real-time information from your field sensors."}

                            </p>

                        </div>


                        <div
                            className={
                                sensorData
                                    ? "sensor-status connected"
                                    : "sensor-status"
                            }
                        >

                            {sensorData
                                ? (
                                    isKannada
                                        ? "● ಸೆನ್ಸರ್‌ಗಳು ಸಂಪರ್ಕಗೊಂಡಿವೆ"
                                        : "● Sensors Connected"
                                )
                                : (
                                    isKannada
                                        ? "● ಸೆನ್ಸರ್‌ಗಳಿಗಾಗಿ ಕಾಯುತ್ತಿದೆ"
                                        : "● Waiting for Sensors"
                                )}

                        </div>

                    </div>


                    {/* REFRESH CONTROLS */}

                    <div className="sensor-refresh-bar">

                        <div className="last-updated">

                            {lastUpdated
                                ? (
                                    isKannada
                                        ? `ಕೊನೆಯ ನವೀಕರಣ: ${lastUpdated.toLocaleTimeString()}`
                                        : `Last updated: ${lastUpdated.toLocaleTimeString()}`
                                )
                                : (
                                    isKannada
                                        ? "ಸೆನ್ಸರ್ ಡೇಟಾಕ್ಕಾಗಿ ಕಾಯುತ್ತಿದೆ..."
                                        : "Waiting for sensor data..."
                                )}

                        </div>


                        <button
                            className="refresh-sensor-button"
                            onClick={refreshSensorData}
                            disabled={refreshing}
                        >

                            {refreshing
                                ? (
                                    isKannada
                                        ? "🔄 ನವೀಕರಿಸಲಾಗುತ್ತಿದೆ..."
                                        : "🔄 Refreshing..."
                                )
                                : (
                                    isKannada
                                        ? "🔄 ಸೆನ್ಸರ್‌ಗಳನ್ನು ನವೀಕರಿಸಿ"
                                        : "🔄 Refresh Sensors"
                                )}

                        </button>

                    </div>


                    {/* LOADING */}

                    {loading && (

                        <div className="sensor-message">

                            {isKannada
                                ? "ಸೆನ್ಸರ್ ಡೇಟಾವನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ..."
                                : "Loading sensor data..."}

                        </div>

                    )}


                    {/* ERROR */}

                    {!loading &&
                        sensorError && (

                            <div className="sensor-message error">

                                {sensorError}

                            </div>

                        )}


                    {/* SENSOR DATA */}

                    {sensorData && (

                        <div className="sensor-grid">

                            <div className="sensor-card">

                                <span className="sensor-icon">
                                    🌡️
                                </span>

                                <span className="sensor-label">

                                    {isKannada
                                        ? "ತಾಪಮಾನ"
                                        : "Temperature"}

                                </span>

                                <strong>
                                    {sensorData.temperature ?? "--"} °C
                                </strong>

                            </div>


                            <div className="sensor-card">

                                <span className="sensor-icon">
                                    💧
                                </span>

                                <span className="sensor-label">

                                    {isKannada
                                        ? "ಆರ್ದ್ರತೆ"
                                        : "Humidity"}

                                </span>

                                <strong>
                                    {sensorData.humidity ?? "--"} %
                                </strong>

                            </div>


                            <div className="sensor-card">

                                <span className="sensor-icon">
                                    🌱
                                </span>

                                <span className="sensor-label">

                                    {isKannada
                                        ? "ಮಣ್ಣಿನ ತೇವಾಂಶ"
                                        : "Soil Moisture"}

                                </span>

                                <strong>
                                    {sensorData.soil_moisture ?? "--"} %
                                </strong>

                            </div>

                            <div className="sensor-card">

                                <span className="sensor-icon">
                                    N
                                </span>

                                <span className="sensor-label">

                                    {isKannada
                                        ? "ಸಾರಜನಕ"
                                        : "Nitrogen"}

                                </span>

                                <strong>
                                    {sensorData.nitrogen ?? "--"}
                                </strong>

                            </div>


                            <div className="sensor-card">

                                <span className="sensor-icon">
                                    P
                                </span>

                                <span className="sensor-label">

                                    {isKannada
                                        ? "ರಂಜಕ"
                                        : "Phosphorus"}

                                </span>

                                <strong>
                                    {sensorData.phosphorus ?? "--"}
                                </strong>

                            </div>


                            <div className="sensor-card">

                                <span className="sensor-icon">
                                    K
                                </span>

                                <span className="sensor-label">

                                    {isKannada
                                        ? "ಪೊಟ್ಯಾಸಿಯಂ"
                                        : "Potassium"}

                                </span>

                                <strong>
                                    {sensorData.potassium ?? "--"}
                                </strong>

                            </div>


                            <div className="sensor-card">

                                <span className="sensor-icon">
                                    🌧️
                                </span>

                                <span className="sensor-label">

                                    {isKannada
                                        ? "ಮಳೆ ಪ್ರಮಾಣ"
                                        : "Rainfall"}

                                </span>

                                <strong>
                                    {sensorData.rainfall ?? "--"} mm
                                </strong>

                            </div>


                            <div className="sensor-card">

                                <span className="sensor-icon">
                                    🕒
                                </span>

                                <span className="sensor-label">

                                    {isKannada
                                        ? "ಸೆನ್ಸರ್ ಸ್ಥಿತಿ"
                                        : "Sensor Status"}

                                </span>

                                <strong>

                                    {isKannada
                                        ? "ಲಭ್ಯವಿದೆ"
                                        : "Available"}

                                </strong>

                            </div>

                        </div>

                    )}

                </section>


                {/* ========================================
                    SENSOR HISTORY - NEW
                ======================================== */}

                <section className="sensor-history-section">

                    <div className="section-title">

                        <div>

                            <h2>
                                📊{" "}
                                {isKannada
                                    ? "ಸೆನ್ಸರ್ ಇತಿಹಾಸ"
                                    : "Sensor Reading History"}
                            </h2>

                            <p>
                                {isKannada
                                    ? "ಡೇಟಾಬೇಸ್‌ನಲ್ಲಿ ಉಳಿಸಿದ ಹಿಂದಿನ ಸೆನ್ಸರ್ ರೀಡಿಂಗ್‌ಗಳು."
                                    : "Previously saved sensor readings from the database."}
                            </p>

                        </div>

                        <button
                            type="button"
                            className="refresh-sensor-button"
                            onClick={fetchSensorHistory}
                            disabled={historyLoading}
                        >
                            {historyLoading
                                ? (
                                    isKannada
                                        ? "ಲೋಡ್ ಆಗುತ್ತಿದೆ..."
                                        : "Loading..."
                                )
                                : (
                                    isKannada
                                        ? "ಇತಿಹಾಸ ನವೀಕರಿಸಿ"
                                        : "Refresh History"
                                )}
                        </button>

                    </div>


                    {historyError && (

                        <div className="sensor-message error">
                            {historyError}
                        </div>

                    )}


                    {!historyError &&
                        !historyLoading &&
                        sensorHistory.length === 0 && (

                            <p>
                                {isKannada
                                    ? "ಯಾವುದೇ ಹಿಂದಿನ ರೀಡಿಂಗ್‌ಗಳು ಲಭ್ಯವಿಲ್ಲ."
                                    : "No historical readings available."}
                            </p>

                        )}


                    {sensorHistory.length > 0 && (

                        <div className="sensor-history-table-wrapper">

                            <table className="sensor-history-table">

                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Moisture (%)</th>
                                        <th>Temperature (°C)</th>
                                        <th>Humidity (%)</th>
                                        <th>Rainfall</th>
                                        <th>N</th>
                                        <th>P</th>
                                        <th>K</th>
                                        <th>Recorded At</th>
                                    </tr>
                                </thead>

                                <tbody>

                                    {sensorHistory.map((reading) => (

                                        <tr key={reading.id}>

                                            <td>{reading.id}</td>

                                            <td>
                                                {reading.soil_moisture ?? "--"}
                                            </td>

                                            <td>
                                                {reading.temperature ?? "--"}
                                            </td>

                                            <td>
                                                {reading.humidity ?? "--"}
                                            </td>

                                            <td>
                                                {reading.rainfall ?? "--"}
                                            </td>

                                            <td>
                                                {reading.nitrogen ?? "--"}
                                            </td>

                                            <td>
                                                {reading.phosphorus ?? "--"}
                                            </td>

                                            <td>
                                                {reading.potassium ?? "--"}
                                            </td>

                                            <td>
                                                {reading.recorded_at
                                                    ? new Date(
                                                        reading.recorded_at
                                                    ).toLocaleString()
                                                    : "--"}
                                            </td>

                                        </tr>

                                    ))}

                                </tbody>

                            </table>

                        </div>

                    )}


                    <p className="sensor-history-count">

                        {isKannada
                            ? `ತೋರಿಸಲಾದ ಒಟ್ಟು ರೀಡಿಂಗ್‌ಗಳು: ${sensorHistory.length}`
                            : `Total readings displayed: ${sensorHistory.length}`}

                    </p>

                </section>


                {/* SMART AGRICULTURE MODULES */}

                <section className="module-section">

                    <div className="section-title">

                        <div>

                            <h2>

                                🌾{" "}

                                {isKannada
                                    ? "ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಘಟಕಗಳು"
                                    : "Smart Agriculture Modules"}

                            </h2>


                            <p>

                                {isKannada
                                    ? "AI ಆಧಾರಿತ ಫಲಿತಾಂಶಗಳನ್ನು ನೋಡಲು ಘಟಕವನ್ನು ಆಯ್ಕೆಮಾಡಿ."
                                    : "Select a module to view AI-powered results."}

                            </p>

                        </div>

                    </div>


                    <div className="cards">

                        {modules.map(
                            (module) => (

                                <Link
                                    to={module.path}
                                    className="card"
                                    key={module.path}
                                >

                                    <div className="icon">
                                        {module.icon}
                                    </div>


                                    <h3>
                                        {module.title}
                                    </h3>


                                    <p>
                                        {module.description}
                                    </p>


                                    <span className="card-arrow">

                                        {isKannada
                                            ? "ಘಟಕವನ್ನು ವೀಕ್ಷಿಸಿ →"
                                            : "View Module →"}

                                    </span>

                                </Link>

                            )
                        )}

                    </div>

                </section>

            </main>

        </div>
    );
}


export default Dashboard;