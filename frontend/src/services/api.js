// =========================================================
// API CONFIGURATION
// =========================================================

const API_URL =
    import.meta.env.VITE_API_URL ||
    "https://ai-smart-agriculture-production.up.railway.app";


// =========================================================
// RESPONSE HELPERS
// =========================================================

async function handleResponse(response) {
    let data;

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {
        throw new Error(
            data?.detail ||
            data?.message ||
            "Something went wrong"
        );
    }

    return data;
}


// =========================================================
// DEFAULT API OBJECT
// Used by IoT.jsx
// =========================================================

const api = {
    async get(endpoint, options = {}) {
        const response = await fetch(
            `${API_URL}${endpoint}`,
            {
                method: "GET",
                headers: {
                    ...getAuthHeaders(),
                    ...(options.headers || {})
                },
                ...options
            }
        );

        return {
            data: await handleResponse(response),
            status: response.status,
            ok: response.ok
        };
    },

    async post(endpoint, body = null, options = {}) {
        const response = await fetch(
            `${API_URL}${endpoint}`,
            {
                method: "POST",
                headers: {
                    ...getAuthHeaders(),
                    ...(options.headers || {})
                },
                body:
                    body instanceof FormData
                        ? body
                        : body !== null
                            ? JSON.stringify(body)
                            : undefined,
                ...options
            }
        );

        return {
            data: await handleResponse(response),
            status: response.status,
            ok: response.ok
        };
    }
};


// =========================================================
// AUTHENTICATION
// =========================================================

// REGISTER — REQUEST OTP

export async function registerUser(
    username,
    phoneNumber,
    password
) {
    const response = await fetch(
        `${API_URL}/auth/register`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                phone_number: phoneNumber,
                password
            })
        }
    );

    return handleResponse(response);
}


// VERIFY REGISTRATION OTP

export async function verifyRegistrationOTP(
    phoneNumber,
    otp
) {
    const params = new URLSearchParams({
        phone_number: phoneNumber,
        otp
    });

    const response = await fetch(
        `${API_URL}/auth/verify-registration-otp?${params.toString()}`,
        {
            method: "POST"
        }
    );

    return handleResponse(response);
}


// LOGIN — REQUEST OTP

export async function loginUser(
    phoneNumber,
    password
) {
    const formData = new URLSearchParams();

    formData.append("username", phoneNumber);
    formData.append("password", password);

    const response = await fetch(
        `${API_URL}/auth/login`,
        {
            method: "POST",
            headers: {
                "Content-Type":
                    "application/x-www-form-urlencoded"
            },
            body: formData.toString()
        }
    );

    return handleResponse(response);
}


// VERIFY LOGIN OTP

export async function verifyLoginOTP(
    phoneNumber,
    otp
) {
    const params = new URLSearchParams({
        phone_number: phoneNumber,
        otp
    });

    const response = await fetch(
        `${API_URL}/auth/verify-login-otp?${params.toString()}`,
        {
            method: "POST"
        }
    );

    return handleResponse(response);
}


// =========================================================
// FORGOT PASSWORD
// =========================================================

export async function forgotPassword(phoneNumber) {
    const params = new URLSearchParams({
        phone_number: phoneNumber
    });

    const response = await fetch(
        `${API_URL}/auth/forgot-password?${params.toString()}`,
        {
            method: "POST"
        }
    );

    return handleResponse(response);
}


// =========================================================
// VERIFY PASSWORD RESET OTP
// =========================================================

export async function verifyResetOTP(
    phoneNumber,
    otp
) {
    const params = new URLSearchParams({
        phone_number: phoneNumber,
        otp
    });

    const response = await fetch(
        `${API_URL}/auth/verify-reset-otp?${params.toString()}`,
        {
            method: "POST"
        }
    );

    return handleResponse(response);
}


// =========================================================
// RESET PASSWORD
// =========================================================

export async function resetPassword(
    phoneNumber,
    resetToken,
    newPassword
) {
    const params = new URLSearchParams({
        phone_number: phoneNumber,
        reset_token: resetToken,
        new_password: newPassword
    });

    const response = await fetch(
        `${API_URL}/auth/reset-password?${params.toString()}`,
        {
            method: "POST"
        }
    );

    return handleResponse(response);
}


// =========================================================
// TOKEN
// =========================================================

export function getToken() {
    return localStorage.getItem("token");
}


// =========================================================
// AUTH HEADERS
// =========================================================

export function getAuthHeaders() {
    const token = getToken();

    return {
        "Content-Type": "application/json",
        ...(token
            ? {
                Authorization: `Bearer ${token}`
            }
            : {})
    };
}


// =========================================================
// IoT SENSOR DATA
// =========================================================

export async function getLatestSensorData() {
    const response = await fetch(
        `${API_URL}/iot/latest`,
        {
            method: "GET",
            headers: getAuthHeaders()
        }
    );

    return handleResponse(response);
}


// =========================================================
// CROP RECOMMENDATION
// =========================================================

export async function getCropRecommendation(data) {
    const response = await fetch(
        `${API_URL}/crop/recommend`,
        {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        }
    );

    return handleResponse(response);
}


// =========================================================
// SOIL ANALYSIS
// =========================================================

export async function getSoilAnalysis(data) {
    const response = await fetch(
        `${API_URL}/soil/analyze`,
        {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        }
    );

    return handleResponse(response);
}


// =========================================================
// FERTILIZER RECOMMENDATION
// =========================================================

export async function getFertilizerRecommendation(data) {
    const response = await fetch(
        `${API_URL}/fertilizer/recommend`,
        {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        }
    );

    return handleResponse(response);
}


// =========================================================
// IRRIGATION PREDICTION
// =========================================================

export async function getIrrigationPrediction(data) {
    const response = await fetch(
        `${API_URL}/irrigation/predict`,
        {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        }
    );

    return handleResponse(response);
}


// =========================================================
// WEATHER BY COORDINATES
// =========================================================

export async function getWeatherByCoordinates(
    latitude,
    longitude
) {
    const response = await fetch(
        `${API_URL}/weather/current-by-coordinates`,
        {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                latitude,
                longitude
            })
        }
    );

    return handleResponse(response);
}


// =========================================================
// MARKET PRICES
// =========================================================

export async function getMarketPrices(params = {}) {
    const query = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
        if (
            value !== undefined &&
            value !== null &&
            value !== ""
        ) {
            query.append(key, value);
        }
    });

    const queryString = query.toString();

    const response = await fetch(
        `${API_URL}/market/prices${
            queryString
                ? `?${queryString}`
                : ""
        }`,
        {
            method: "GET",
            headers: getAuthHeaders()
        }
    );

    return handleResponse(response);
}


// =========================================================
// PLANT DISEASE PREDICTION
// =========================================================

export async function predictPlantDisease(imageFile) {
    const formData = new FormData();

    formData.append("file", imageFile);

    const token = getToken();

    const response = await fetch(
        `${API_URL}/disease/predict`,
        {
            method: "POST",
            headers: {
                ...(token
                    ? {
                        Authorization: `Bearer ${token}`
                    }
                    : {})
            },
            body: formData
        }
    );

    return handleResponse(response);
}


// =========================================================
// CROP YIELD PREDICTION
// =========================================================

export async function predictCropYield(data) {
    const response = await fetch(
        `${API_URL}/yield/predict`,
        {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        }
    );

    return handleResponse(response);
}


// =========================================================
// AI ASSISTANT
// =========================================================

export async function sendAssistantMessage(
    message,
    language
) {
    const response = await fetch(
        `${API_URL}/assistant/chat`,
        {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                message,
                language
            })
        }
    );

    return handleResponse(response);
}


// =========================================================
// AI ASSISTANT TEXT-TO-SPEECH
// =========================================================

export async function generateAssistantSpeech(
    text,
    language
) {
    const response = await fetch(
        `${API_URL}/tts/speak`,
        {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                text,
                language
            })
        }
    );

    if (!response.ok) {
        let errorMessage =
            "Text-to-speech request failed.";

        try {
            const data = await response.json();

            errorMessage =
                data?.detail ||
                data?.message ||
                errorMessage;
        } catch {
            // Response was not JSON.
        }

        throw new Error(errorMessage);
    }

    return await response.blob();
}


// =========================================================
// NOTIFICATIONS
// =========================================================

// GET UNREAD NOTIFICATIONS

export async function getUnreadNotifications() {
    const response = await fetch(
        `${API_URL}/notifications/unread`,
        {
            method: "GET",
            headers: getAuthHeaders()
        }
    );

    return handleResponse(response);
}


// MARK ONE NOTIFICATION AS READ

export async function markNotificationAsRead(
    notificationId
) {
    const response = await fetch(
        `${API_URL}/notifications/${notificationId}/read`,
        {
            method: "PUT",
            headers: getAuthHeaders()
        }
    );

    return handleResponse(response);
}


// MARK ALL NOTIFICATIONS AS READ

export async function markAllNotificationsAsRead() {
    const response = await fetch(
        `${API_URL}/notifications/read-all`,
        {
            method: "PUT",
            headers: getAuthHeaders()
        }
    );

    return handleResponse(response);
}


// =========================================================
// API URL
// =========================================================

export { API_URL };


// =========================================================
// DEFAULT EXPORT
// =========================================================

export default api;