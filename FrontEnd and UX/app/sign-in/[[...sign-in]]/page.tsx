"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedEmail = email.trim();
    if (!trimmedEmail || !password.trim()) {
      setError("Please enter both your email and password.");
      return;
    }

    localStorage.setItem("faceframe-auth", JSON.stringify({ email: trimmedEmail.toLowerCase() }));
    setError("");
    router.push("/dashboard");
  };

  return (
    <main className="clerk-auth-page">
      <div className="auth-card">
        <h1>Sign in to FaceFrame</h1>
        <p className="auth-subtitle">Welcome back! Please sign in to continue.</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Email address
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="Enter your email address"
              autoComplete="email"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              autoComplete="current-password"
            />
          </label>

          {error ? <p className="auth-error">{error}</p> : null}

          <button type="submit" className="primary-button auth-submit">Login</button>
        </form>

        <p className="auth-switch">
          Don&apos;t have an account? <a href="/sign-up">Sign up</a>
        </p>
      </div>
    </main>
  );
}
