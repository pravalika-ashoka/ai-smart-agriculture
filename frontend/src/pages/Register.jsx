import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    registerUser,
    verifyRegistrationOTP,
} from "./api";
import "./Register.css";

function Register() {
    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [phoneNumber, setPhoneNumber] = useState("");
    const [password, setPassword] = useState("");
    const [otp, setOtp] = useState("");

    const [otpRequested, setOtpRequested] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    // Clear the form when the registration page opens.
    useEffect(() => {
        setUsername("");
        setPhoneNumber("");
        setPassword("");
        setOtp("");
        setOtpRequested(false);
        setLoading(false);
        setError("");
        setSuccess("");

        sessionStorage.removeItem("registerUsername");
        sessionStorage.removeItem("registerPhone");
        sessionStorage.removeItem("registerPassword");
    }, []);

    // ========================================
    // REQUEST REGISTRATION OTP
    // ========================================

    const handleRegister = async (e) => {
        e.preventDefault();

        setError("");
        setSuccess("");

        const cleanUsername = username.trim();
        const cleanPhoneNumber = phoneNumber.trim();

        if (!cleanUsername) {
            setError("Please enter your username.");
            return;
        }

        if (!/^\+?[0-9]{10,15}$/.test(cleanPhoneNumber)) {
            setError(
                "Please enter a valid phone number, including the country code if required."
            );
            return;
        }

        if (password.length < 8) {
            setError("Password must contain at least 8 characters.");
            return;
        }

        setLoading(true);

        try {
            const data = await registerUser(
                cleanUsername,
                cleanPhoneNumber,
                password
            );

            console.log("Registration OTP response:", data);

            setUsername(cleanUsername);
            setPhoneNumber(cleanPhoneNumber);
            setOtpRequested(true);

            setSuccess(
                data?.message ||
                "If the request was accepted, a registration OTP has been sent to your phone."
            );
        } catch (err) {
            console.error("Registration OTP error:", err);

            setError(
                err.message || "Unable to request a registration OTP."
            );
        } finally {
            setLoading(false);
        }
    };

    // ========================================
    // VERIFY OTP AND COMPLETE REGISTRATION
    // ========================================

    const handleVerifyOTP = async (e) => {
        e.preventDefault();

        setError("");
        setSuccess("");

        if (!/^\d{6}$/.test(otp)) {
            setError("Please enter the 6-digit OTP.");
            return;
        }

        setLoading(true);

        try {
            const data = await verifyRegistrationOTP(
                phoneNumber.trim(),
                otp.trim()
            );

            console.log("Registration verification response:", data);

            setSuccess(
                data?.message ||
                "Registration successful. Redirecting to login..."
            );

            setUsername("");
            setPhoneNumber("");
            setPassword("");
            setOtp("");
            setOtpRequested(false);

            sessionStorage.removeItem("registerUsername");
            sessionStorage.removeItem("registerPhone");
            sessionStorage.removeItem("registerPassword");

            setTimeout(() => {
                navigate("/");
            }, 1500);
        } catch (err) {
            console.error("Registration OTP verification error:", err);

            setError(
                err.message || "OTP verification failed. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };

    // ========================================
    // RETURN TO REGISTRATION FORM
    // ========================================

    const handleBack = () => {
        setOtp("");
        setOtpRequested(false);
        setError("");
        setSuccess("");
    };

    return (
        <div className="register-page">
            <div className="register-container">

                {/* BRANDING */}

                <div className="register-branding">
                    <img
                        src="/logo.png"
                        alt="AI Smart Agriculture"
                        className="register-logo-image"
                    />

                    <h1 className="register-brand-title">
                        AI Smart Agriculture
                    </h1>

                    <p className="register-brand-subtitle">
                        Smart Farming • Better Tomorrow
                    </p>
                </div>

                {/* HEADING */}

                <h2 className="register-heading">
                    {otpRequested ? "Verify Your Phone" : "Create Account"}
                </h2>

                <p className="register-subtitle">
                    {otpRequested
                        ? `Enter the 6-digit OTP sent to ${phoneNumber}.`
                        : "Register to access AI Smart Agriculture."}
                </p>

                {/* REGISTRATION FORM */}

                {!otpRequested ? (
                    <form
                        onSubmit={handleRegister}
                        autoComplete="off"
                    >
                        {/* USERNAME */}

                        <div className="register-form-group">
                            <label htmlFor="username">
                                Username
                            </label>

                            <input
                                id="username"
                                name="register-username"
                                type="text"
                                value={username}
                                onChange={(e) =>
                                    setUsername(e.target.value)
                                }
                                placeholder="Enter your username"
                                autoComplete="username"
                                maxLength={100}
                                required
                            />
                        </div>

                        {/* PHONE NUMBER */}

                        <div className="register-form-group">
                            <label htmlFor="phoneNumber">
                                Phone Number
                            </label>

                            <input
                                id="phoneNumber"
                                name="register-phone"
                                type="tel"
                                value={phoneNumber}
                                onChange={(e) =>
                                    setPhoneNumber(e.target.value)
                                }
                                placeholder="Enter your phone number"
                                autoComplete="tel"
                                inputMode="tel"
                                maxLength={16}
                                required
                            />
                        </div>

                        {/* PASSWORD */}

                        <div className="register-form-group">
                            <label htmlFor="password">
                                Password
                            </label>

                            <input
                                id="password"
                                name="register-password"
                                type="password"
                                value={password}
                                onChange={(e) =>
                                    setPassword(e.target.value)
                                }
                                placeholder="Create a password"
                                autoComplete="new-password"
                                minLength={8}
                                required
                            />
                        </div>

                        {/* ERROR */}

                        {error && (
                            <div
                                className="register-error"
                                role="alert"
                            >
                                {error}
                            </div>
                        )}

                        {/* SUCCESS */}

                        {success && (
                            <div
                                className="register-success"
                                role="status"
                            >
                                {success}
                            </div>
                        )}

                        {/* REQUEST OTP BUTTON */}

                        <button
                            type="submit"
                            disabled={loading}
                        >
                            {loading
                                ? "Sending OTP..."
                                : "Register"}
                        </button>
                    </form>
                ) : (
                    <form
                        onSubmit={handleVerifyOTP}
                        autoComplete="off"
                    >
                        {/* OTP */}

                        <div className="register-form-group">
                            <label htmlFor="registrationOtp">
                                Registration OTP
                            </label>

                            <input
                                id="registrationOtp"
                                name="registration-otp"
                                type="text"
                                className="register-otp-input"
                                value={otp}
                                onChange={(e) =>
                                    setOtp(
                                        e.target.value
                                            .replace(/\D/g, "")
                                            .slice(0, 6)
                                    )
                                }
                                placeholder="Enter 6-digit OTP"
                                inputMode="numeric"
                                autoComplete="one-time-code"
                                maxLength={6}
                                required
                            />
                        </div>

                        {/* ERROR */}

                        {error && (
                            <div
                                className="register-error"
                                role="alert"
                            >
                                {error}
                            </div>
                        )}

                        {/* SUCCESS */}

                        {success && (
                            <div
                                className="register-success"
                                role="status"
                            >
                                {success}
                            </div>
                        )}

                        {/* VERIFY BUTTON */}

                        <button
                            type="submit"
                            disabled={loading}
                        >
                            {loading
                                ? "Verifying..."
                                : "Verify OTP & Register"}
                        </button>

                        {/* BACK BUTTON */}

                        <button
                            type="button"
                            className="register-secondary-button"
                            onClick={handleBack}
                            disabled={loading}
                        >
                            Back to Registration
                        </button>
                    </form>
                )}

                {/* LOGIN LINK */}

                <p className="login-link">
                    Already have an account?{" "}

                    <Link to="/">
                        Login
                    </Link>
                </p>
            </div>
        </div>
    );
}

export default Register;