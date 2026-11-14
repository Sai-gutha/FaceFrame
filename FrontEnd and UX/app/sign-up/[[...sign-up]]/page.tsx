"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function SignUpPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedName = name.trim();
    const trimmedEmail = email.trim();

    if (!trimmedName || !trimmedEmail || !password.trim()) {
      return;
    }

    const user = {
      name: trimmedName,
      email: trimmedEmail.toLowerCase(),
      password,
    };

    localStorage.setItem("faceframe-user", JSON.stringify(user));
    localStorage.setItem("faceframe-auth", JSON.stringify({ email: user.email }));
    router.push("/dashboard");
  };

  return (
    <main className="clerk-auth-page">
      <div className="auth-card">
        <h1>Create your FaceFrame account</h1>
        <p className="auth-subtitle">Join today and save your favorite frames.</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Full name
            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Alex Morgan"
              autoComplete="name"
            />
          </label>

          <label>
            Email address
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Create a password"
              autoComplete="new-password"
            />
          </label>

          <button type="submit" className="primary-button auth-submit">Create account</button>
        </form>

        <p className="auth-switch">
          Already have an account? <a href="/sign-in">Sign in</a>
        </p>
      </div>
    </main>
  );
}
