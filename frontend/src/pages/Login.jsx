import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    loginUser,
    verifyLoginOTP
} from "../services/api";
import "./Login.css";

function Login() {
    const navigate = useNavigate();

    const [phoneNumber, setPhoneNumber] = useState("");
    const [password, setPassword] = useState("");
    const [otp, setOtp] = useState("");

    const [otpRequested, setOtpRequested] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    // ========================================
    // CLEAR LOGIN FORM WHEN PAGE OPENS
    // ========================================

    useEffect(() => {
        setPhoneNumber("");
        setPassword("");
        setOtp("");
        setOtpRequested(false);
        setError("");
        setSuccess("");

        sessionStorage.removeItem("loginPhone");
        sessionStorage.removeItem("loginPassword");
    }, []);

    // ========================================
    // REQUEST LOGIN OTP
    // ========================================

    const handleLogin = async (e) => {
        e.preventDefault();

        setError("");
        setSuccess("");

        if (!phoneNumber.trim()) {
            setError("Please enter your phone number.");
            return;
        }

        if (!password) {
            setError("Please enter your password.");
            return;
        }

        setLoading(true);

        try {
            const data = await loginUser(
                phoneNumber.trim(),
                password
            );

            setOtpRequested(true);
            setOtp("");
            setSuccess(
                data.message ||
                "OTP request processed. Enter the OTP sent to your phone."
            );
        } catch (err) {
            console.error("Login OTP request error:", err);
            setError(err.message || "Unable to request login OTP.");
        } finally {
            setLoading(false);
        }
    };

    // ========================================
    // VERIFY LOGIN OTP
    // ========================================

    const handleVerifyOTP = async (e) => {
        e.preventDefault();

        setError("");
        setSuccess("");

        if (!/^\d{6}$/.test(otp.trim())) {
            setError("Please enter the 6-digit OTP.");
            return;
        }

        setLoading(true);

        try {
            const data = await verifyLoginOTP(
                phoneNumber.trim(),
                otp.trim()
            );

            if (!data.access_token) {
                setError(
                    "OTP verification succeeded, but no access token was received."
                );
                return;
            }

            // Save token only after OTP verification.
            localStorage.setItem(
                "token",
                data.access_token
            );

            // Clear authentication form values.
            setPhoneNumber("");
            setPassword("");
            setOtp("");
            setOtpRequested(false);
            setError("");
            setSuccess("");

            navigate("/dashboard");
        } catch (err) {
            console.error("OTP verification error:", err);
            setError(
                err.message ||
                "OTP verification failed. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };

    // ========================================
    // RETURN TO PASSWORD FORM
    // ========================================

    const handleChangePhoneOrPassword = () => {
        setOtpRequested(false);
        setOtp("");
        setError("");
        setSuccess("");
    };

    // ========================================
    // LOGIN PAGE
    // ========================================

    return (
        <div className="login-page">
            <div className="login-container">

                {/* BRANDING */}

                <div className="login-branding">
                    <img
                        src="/logo.png"
                        alt="AI Smart Agriculture"
                        className="login-logo-image"
                    />

                    <h1 className="login-brand-title">
                        AI Smart Agriculture
                    </h1>

                    <p className="login-brand-subtitle">
                        Smart Farming • Better Tomorrow
                    </p>
                </div>

                {/* TITLE */}

                <h2 className="login-heading">
                    {otpRequested
                        ? "Verify Login OTP"
                        : "Login"}
                </h2>

                {/* REQUEST OTP FORM */}

                {!otpRequested && (
                    <form
                        onSubmit={handleLogin}
                        autoComplete="off"
                    >
                        <div className="form-group">
                            <label htmlFor="phoneNumber">
                                Phone Number
                            </label>

                            <input
                                id="phoneNumber"
                                name="login-phone"
                                type="tel"
                                value={phoneNumber}
                                onChange={(e) =>
                                    setPhoneNumber(e.target.value)
                                }
                                placeholder="Enter your phone number"
                                autoComplete="off"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">
                                Password
                            </label>

                            <input
                                id="password"
                                name="login-password"
                                type="password"
                                value={password}
                                onChange={(e) =>
                                    setPassword(e.target.value)
                                }
                                placeholder="Enter your password"
                                autoComplete="current-password"
                                required
                            />
                        </div>

                        {/* FORGOT PASSWORD */}

                        <div className="forgot-password-link">
                            <Link to="/forgot-password">
                                Forgot Password?
                            </Link>
                        </div>

                        {error && (
                            <div
                                className="login-error"
                                role="alert"
                            >
                                {error}
                            </div>
                        )}

                        {success && (
                            <div
                                className="login-success"
                                role="status"
                            >
                                {success}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                        >
                            {loading
                                ? "Requesting OTP..."
                                : "Send Login OTP"}
                        </button>
                    </form>
                )}

                {/* OTP VERIFICATION FORM */}

                {otpRequested && (
                    <form
                        onSubmit={handleVerifyOTP}
                        autoComplete="off"
                    >
                        <p>
                            Enter the 6-digit OTP sent to your
                            registered phone number.
                        </p>

                        <div className="form-group">
                            <label htmlFor="loginOtp">
                                Verification OTP
                            </label>

                            <input
                                id="loginOtp"
                                name="login-otp"
                                type="text"
                                inputMode="numeric"
                                autoComplete="one-time-code"
                                value={otp}
                                onChange={(e) =>
                                    setOtp(
                                        e.target.value
                                            .replace(/\D/g, "")
                                            .slice(0, 6)
                                    )
                                }
                                placeholder="Enter 6-digit OTP"
                                maxLength={6}
                                required
                            />
                        </div>

                        {error && (
                            <div
                                className="login-error"
                                role="alert"
                            >
                                {error}
                            </div>
                        )}

                        {success && (
                            <div
                                className="login-success"
                                role="status"
                            >
                                {success}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                        >
                            {loading
                                ? "Verifying..."
                                : "Verify OTP & Login"}
                        </button>

                        <button
                            type="button"
                            onClick={handleChangePhoneOrPassword}
                            disabled={loading}
                            className="secondary-button"
                        >
                            Back to Login
                        </button>
                    </form>
                )}

                {/* REGISTER LINK */}

                <p className="register-link">
                    New Farmer?{" "}

                    <Link to="/register">
                        Register
                    </Link>
                </p>
            </div>
        </div>
    );
}

export default Login;