import React, { useState } from "react";
import { AuthState } from "../common/types";

interface LoginModalProps {
    authState: AuthState;
    sendAuth: (login: string, password: string) => void;
}

const LoginModal: React.FC<LoginModalProps> = ({
    authState,
    sendAuth,
}) => {
    const [login, setLogin] = useState("");
    const [password, setPassword] = useState("");

    // Hide modal completely if auth succeeded
    if (authState === "success") {
        return null;
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        sendAuth(login, password);
    };

    return (
        <div className="login-modal-backdrop">
            <div className="login-modal">
                <h2>Sign in</h2>

                <form onSubmit={handleSubmit}>
                    <div className="login-field">
                        <label htmlFor="login">Login</label>
                        <input
                            id="login"
                            type="text"
                            value={login}
                            onChange={(e) => setLogin(e.target.value)}
                            autoFocus
                            required
                        />
                    </div>

                    <div className="login-field">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    {authState === "error" && (
                        <div className="login-error">
                            Incorrect login or password
                        </div>
                    )}

                    <button type="submit" className="login-submit">
                        Log in
                    </button>
                </form>
            </div>
        </div>
    );
};

export default LoginModal;
