import { useCallback, useEffect, useState } from "react";
import api from "../services/api";
import "./IoT.css";

function IoT() {
    const [sensorData, setSensorData] = useState({
        soil_moisture: "",
        temperature: "",
        humidity: "",
        nitrogen: "",
        phosphorus: "",
        potassium: ""
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [lastUpdated, setLastUpdated] = useState(null);

    // ================================================
    // SENSOR HISTORY - NEW
    // ================================================

    const [sensorHistory, setSensorHistory] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [historyError, setHistoryError] = useState("");

    // =====================================================
    // FETCH LATEST SENSOR DATA
    // =====================================================

    const fetchSensorData = useCallback(async () => {
        try {
            const response = await api.get("/iot/latest");

            console.log("IoT response:", response.data);

            const data = response.data;

            // -------------------------------------------------
            // Support possible backend response structures
            // -------------------------------------------------

            const sensor =
                data?.data ||
                data?.sensor_data ||
                data?.sensor ||
                data;

            if (!sensor || typeof sensor !== "object") {
                throw new Error("Invalid sensor response");
            }

            setSensorData({
                soil_moisture:
                    sensor.soil_moisture ??
                    sensor.moisture ??
                    "",

                temperature:
                    sensor.temperature ??
                    "",

                humidity:
                    sensor.humidity ??
                    "",

                nitrogen:
                    sensor.nitrogen ??
                    "",

                phosphorus:
                    sensor.phosphorus ??
                    "",

                potassium:
                    sensor.potassium ??
                    ""
            });

            setLastUpdated(new Date());
            setError("");

        } catch (err) {
            console.error(
                "Failed to fetch IoT sensor data:",
                err
            );

            if (err.response) {

                if (err.response.status === 401) {
                    setError(
                        "Authentication expired. Please login again."
                    );

                } else if (err.response.status === 429) {
                    setError(
                        "Too many sensor requests. Please wait a moment."
                    );

                } else if (err.response.status === 503) {
                    setError(
                        "Agriculture backend is temporarily unavailable."
                    );

                } else {
                    setError(
                        err.response.data?.detail ||
                        "Unable to fetch live IoT sensor data."
                    );
                }

            } else {
                setError(
                    "Unable to connect to the agriculture backend."
                );
            }
        } finally {
            setLoading(false);
        }
    }, []);

    // =====================================================
    // FETCH SENSOR HISTORY - NEW
    // =====================================================

    const fetchSensorHistory = useCallback(async () => {
        try {
            setHistoryLoading(true);
            setHistoryError("");

            const response = await api.get(
                "/iot/history",
                {
                    params: {
                        limit: 50
                    }
                }
            );

            console.log(
                "IoT history response:",
                response.data
            );

            const result = response.data;

            setSensorHistory(
                Array.isArray(result?.data)
                    ? result.data
                    : []
            );

        } catch (err) {
            console.error(
                "Failed to fetch IoT sensor history:",
                err
            );

            if (err.response) {

                if (err.response.status === 401) {
                    setHistoryError(
                        "Authentication expired. Please login again."
                    );

                } else if (err.response.status === 429) {
                    setHistoryError(
                        "Too many requests. Please wait a moment."
                    );

                } else {
                    setHistoryError(
                        err.response.data?.detail ||
                        "Unable to fetch sensor history."
                    );
                }

            } else {
                setHistoryError(
                    "Unable to connect to the agriculture backend for sensor history."
                );
            }

        } finally {
            setHistoryLoading(false);
        }
    }, []);

    // =====================================================
    // INITIAL FETCH + SAFE POLLING
    // =====================================================

    useEffect(() => {

        let active = true;
        let interval = null;

        const loadData = async () => {

            if (!active) {
                return;
            }

            // Existing live sensor request.
            await fetchSensorData();

            // NEW: Load previously saved database readings.
            if (active) {
                await fetchSensorHistory();
            }
        };

        // Fetch immediately.
        loadData();

        // Existing polling interval remains 30 seconds.
        interval = setInterval(() => {
            loadData();
        }, 30000);

        return () => {

            active = false;

            if (interval) {
                clearInterval(interval);
            }
        };

    }, [fetchSensorData, fetchSensorHistory]);

    // =====================================================
    // MANUAL REFRESH
    // =====================================================

    const handleRefresh = async () => {

        setLoading(true);

        // Preserve the existing live-data refresh and
        // additionally refresh the saved reading history.
        await Promise.all([
            fetchSensorData(),
            fetchSensorHistory()
        ]);
    };

    // =====================================================
    // FORMAT LAST UPDATED
    // =====================================================

    const formatLastUpdated = () => {

        if (!lastUpdated) {
            return "Waiting for sensor data...";
        }

        return lastUpdated.toLocaleTimeString();
    };

    // =====================================================
    // FORMAT HISTORY TIMESTAMP - NEW
    // =====================================================

    const formatRecordedAt = (value) => {

        if (!value) {
            return "--";
        }

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return value;
        }

        return date.toLocaleString();
    };

    // =====================================================
    // CHECK SENSOR AVAILABILITY
    // =====================================================

    const hasSensorData =
        Object.values(sensorData).some(
            value =>
                value !== "" &&
                value !== null &&
                value !== undefined
        );

    // =====================================================
    // UI
    // =====================================================

    return (
        <div className="iot-page">

            <div className="iot-header">

                <h1>
                    IoT Sensor Monitoring
                </h1>

                <p>
                    Monitor soil and environmental sensor
                    values for smart agriculture.
                </p>

            </div>


            <div className="iot-container">

                {/* =================================================
                    EXISTING SENSOR FORM / DATA
                ================================================= */}

                <div className="iot-form">

                    <h2>
                        Live Sensor Data
                    </h2>

                    <div className="iot-grid">

                        {/* SOIL MOISTURE */}

                        <div className="iot-field">

                            <label>
                                Soil Moisture (%)
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.soil_moisture !== ""
                                        ? sensorData.soil_moisture
                                        : "--"
                                }
                                readOnly
                            />

                        </div>


                        {/* TEMPERATURE */}

                        <div className="iot-field">

                            <label>
                                Temperature (°C)
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.temperature !== ""
                                        ? sensorData.temperature
                                        : "--"
                                }
                                readOnly
                            />

                        </div>


                        {/* HUMIDITY */}

                        <div className="iot-field">

                            <label>
                                Humidity (%)
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.humidity !== ""
                                        ? sensorData.humidity
                                        : "--"
                                }
                                readOnly
                            />

                        </div>


                        {/* NITROGEN */}

                        <div className="iot-field">

                            <label>
                                Nitrogen (N)
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.nitrogen !== ""
                                        ? sensorData.nitrogen
                                        : "--"
                                }
                                readOnly
                            />

                        </div>


                        {/* PHOSPHORUS */}

                        <div className="iot-field">

                            <label>
                                Phosphorus (P)
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.phosphorus !== ""
                                        ? sensorData.phosphorus
                                        : "--"
                                }
                                readOnly
                            />

                        </div>


                        {/* POTASSIUM */}

                        <div className="iot-field">

                            <label>
                                Potassium (K)
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.potassium !== ""
                                        ? sensorData.potassium
                                        : "--"
                                }
                                readOnly
                            />

                        </div>

                    </div>


                    {/* EXISTING REFRESH BUTTON */}

                    <button
                        type="button"
                        className="iot-button"
                        onClick={handleRefresh}
                        disabled={loading}
                    >

                        {loading
                            ? "Loading Sensors..."
                            : "Refresh Sensor Data"
                        }

                    </button>

                </div>


                {/* =================================================
                    EXISTING STATUS
                ================================================= */}

                <div className="iot-status">

                    <h2>
                        Live Sensor Status
                    </h2>


                    <div className="status-indicator">

                        <span
                            className={
                                hasSensorData
                                    ? "status-dot active"
                                    : "status-dot"
                            }
                        />

                        <span>
                            {hasSensorData
                                ? "Sensor System Active"
                                : "Waiting for Sensors"
                            }
                        </span>

                    </div>


                    {/* EXISTING SENSOR CARDS */}

                    <div className="sensor-cards">

                        <div className="sensor-card">

                            <span>
                                Soil Moisture
                            </span>

                            <strong>
                                {sensorData.soil_moisture !== ""
                                    ? `${sensorData.soil_moisture} %`
                                    : "--"
                                }
                            </strong>

                        </div>


                        <div className="sensor-card">

                            <span>
                                Temperature
                            </span>

                            <strong>
                                {sensorData.temperature !== ""
                                    ? `${sensorData.temperature} °C`
                                    : "--"
                                }
                            </strong>

                        </div>


                        <div className="sensor-card">

                            <span>
                                Humidity
                            </span>

                            <strong>
                                {sensorData.humidity !== ""
                                    ? `${sensorData.humidity} %`
                                    : "--"
                                }
                            </strong>

                        </div>


                        <div className="sensor-card">

                            <span>
                                Nitrogen
                            </span>

                            <strong>
                                {sensorData.nitrogen !== ""
                                    ? sensorData.nitrogen
                                    : "--"
                                }
                            </strong>

                        </div>


                        <div className="sensor-card">

                            <span>
                                Phosphorus
                            </span>

                            <strong>
                                {sensorData.phosphorus !== ""
                                    ? sensorData.phosphorus
                                    : "--"
                                }
                            </strong>

                        </div>


                        <div className="sensor-card">

                            <span>
                                Potassium
                            </span>

                            <strong>
                                {sensorData.potassium !== ""
                                    ? sensorData.potassium
                                    : "--"
                                }
                            </strong>

                        </div>

                    </div>


                    {/* EXISTING LAST UPDATED */}

                    <div className="last-updated">

                        Last updated:{" "}

                        <strong>
                            {formatLastUpdated()}
                        </strong>

                    </div>


                    {/* EXISTING ERROR */}

                    {error && (

                        <div className="iot-error">
                            {error}
                        </div>

                    )}

                </div>


                {/* =================================================
                    NEW SENSOR HISTORY SECTION
                ================================================= */}

                <section className="iot-history">

                    <h2>
                        📊 Sensor Reading History
                    </h2>

                    <p>
                        Previously saved sensor readings from the database.
                    </p>


                    <button
                        type="button"
                        className="iot-button"
                        onClick={fetchSensorHistory}
                        disabled={historyLoading}
                    >
                        {historyLoading
                            ? "Loading History..."
                            : "Refresh History"
                        }
                    </button>


                    {historyError && (

                        <div className="iot-error" role="alert">
                            {historyError}
                        </div>

                    )}


                    {historyLoading && (

                        <p>
                            Loading sensor history...
                        </p>

                    )}


                    {!historyLoading &&
                        !historyError &&
                        sensorHistory.length === 0 && (

                            <p>
                                No historical sensor readings available.
                            </p>

                        )}


                    {sensorHistory.length > 0 && (

                        <div className="iot-history-table-wrapper">

                            <table className="iot-history-table">

                                <thead>

                                    <tr>
                                        <th>ID</th>
                                        <th>Recorded At</th>
                                        <th>Soil Moisture (%)</th>
                                        <th>Temperature (°C)</th>
                                        <th>Humidity (%)</th>
                                        <th>Rainfall</th>
                                        <th>Nitrogen</th>
                                        <th>Phosphorus</th>
                                        <th>Potassium</th>
                                    </tr>

                                </thead>


                                <tbody>

                                    {sensorHistory.map((reading) => (

                                        <tr key={reading.id}>

                                            <td>
                                                {reading.id}
                                            </td>

                                            <td>
                                                {formatRecordedAt(
                                                    reading.recorded_at
                                                )}
                                            </td>

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

                                        </tr>

                                    ))}

                                </tbody>

                            </table>

                        </div>

                    )}


                    <p className="sensor-history-count">
                        Total readings displayed: {sensorHistory.length}
                    </p>

                </section>

            </div>

        </div>
    );
}

export default IoT;