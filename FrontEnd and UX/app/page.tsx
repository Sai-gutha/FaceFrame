"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

type Panel = "login" | "register" | null;

export default function Home() {
  const router = useRouter();
  const [panel, setPanel] = useState<Panel>(null);
  const [loginValue, setLoginValue] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleLoginSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!loginValue.trim() || !loginPassword.trim()) return;
    router.push("/dashboard");
  };

  const handleRegisterSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!firstName.trim() || !lastName.trim() || !phone.trim() || !email.trim() || !username.trim() || !registerPassword.trim() || !confirmPassword.trim()) return;
    if (registerPassword !== confirmPassword) return;
    router.push("/dashboard");
  };

  return (
    <main className="page-shell landing-shell">
      <div className="brand-watermark" aria-hidden="true">
        <img src="/faceframe-logo.jpg" alt="" />
      </div>

      <div className="landing-panel">
        <header className="landing-header" aria-label="FaceFrame brand">
          <div className="brand-mark-wrap">
            <img src="/faceframe-logo.jpg" alt="FaceFrame logo" className="brand-mark" />
          </div>
          <div>
            <p className="eyebrow">Eyewear, made personal</p>
            <h1>FaceFrame<span>.</span></h1>
          </div>
        </header>

        <div className="intro-copy">
          <h2>Find your perfect frame.</h2>
          <p>Sign in to pick up where you left off, or start exploring in seconds.</p>
        </div>

        <div className="choice-grid">
          <article className="choice-card returning-card">
            <div className="card-copy">
              <span className="step-label">Welcome back</span>
              <h3>Returning user</h3>
              <p>Access your saved frames, favorites, and personalized picks.</p>
            </div>

            <div className="customer-photo returning-photo">
              <img src="/returning-customer.jpg" alt="Customer wearing round eyeglasses" />
              <span className="photo-label">Your frames, waiting</span>
            </div>

            <button className="primary-button" type="button" onClick={() => setPanel("login")}>
              Log in <span aria-hidden="true">→</span>
            </button>
          </article>

          <article className="choice-card new-card">
            <div className="card-copy">
              <span className="step-label">New here?</span>
              <h3>Discover FaceFrame</h3>
              <p>Build your profile and save the frames that feel like you.</p>
            </div>

            <div className="customer-photo signup-photo">
              <img src="/new-customer.jpg" alt="New customer wearing rectangular eyeglasses" />
              <span className="photo-label">Meet your next look</span>
            </div>

            <button className="primary-button accent-button" type="button" onClick={() => setPanel("register")}>
              Create an account <span aria-hidden="true">→</span>
            </button>
            <button className="guest-button" type="button" onClick={() => router.push("/dashboard?mode=guest")}>
              Continue as guest
            </button>
            <small>No account needed to browse.</small>
          </article>
        </div>

        <p className="privacy-note"><span aria-hidden="true">◆</span> Your style profile stays private and secure.</p>
      </div>

      <div className="landing-blob" aria-hidden="true">
        <img src="/faceframe-logo-premium.png" alt="" />
      </div>

      {panel && (
        <div className="modal-backdrop" role="presentation" onMouseDown={() => setPanel(null)}>
          <div className="auth-modal" role="dialog" aria-modal="true" aria-labelledby="auth-title" onMouseDown={(event) => event.stopPropagation()}>
            <button className="close-button" type="button" aria-label="Close" onClick={() => setPanel(null)}>×</button>

            <div className="auth-header">
              <img src="/faceframe-logo.jpg" alt="" className="modal-logo" />
              <p className="step-label auth-step">{panel === "login" ? "Welcome back" : "Join FaceFrame"}</p>
              <h2 id="auth-title">{panel === "login" ? "Log in to your account" : "Create your account"}</h2>
            </div>

            {panel === "login" ? (
              <form className="auth-form" onSubmit={handleLoginSubmit}>
                <label>
                  Username / Email / Phone Number
                  <input
                    type="text"
                    value={loginValue}
                    onChange={(event) => setLoginValue(event.target.value)}
                    placeholder="username or email or phone number"
                    autoComplete="username"
                    required
                  />
                </label>

                <label>
                  Password
                  <input
                    type="password"
                    value={loginPassword}
                    onChange={(event) => setLoginPassword(event.target.value)}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    required
                  />
                </label>

                <button type="submit" className="primary-button auth-submit">Continue securely</button>
              </form>
            ) : (
              <form className="auth-form register-form" onSubmit={handleRegisterSubmit}>
                <div className="auth-grid">
                  <label>
                    First Name
                    <input type="text" value={firstName} onChange={(event) => setFirstName(event.target.value)} placeholder="First Name" autoComplete="given-name" required />
                  </label>
                  <label>
                    Last Name
                    <input type="text" value={lastName} onChange={(event) => setLastName(event.target.value)} placeholder="Last Name" autoComplete="family-name" required />
                  </label>
                </div>

                <label>
                  Email
                  <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" autoComplete="email" required />
                </label>

                <label>
                  Phone Number
                  <input type="tel" value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="Phone Number" autoComplete="tel" required />
                </label>

                <label>
                  Username
                  <input type="text" value={username} onChange={(event) => setUsername(event.target.value)} placeholder="Username" autoComplete="username" required />
                </label>

                <div className="auth-grid">
                  <label>
                    Password
                    <input type="password" value={registerPassword} onChange={(event) => setRegisterPassword(event.target.value)} placeholder="Password" autoComplete="new-password" required />
                  </label>
                  <label>
                    Confirm Password
                    <input type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} placeholder="Confirm password" autoComplete="new-password" required />
                  </label>
                </div>

                <button type="submit" className="primary-button auth-submit">Continue securely</button>
              </form>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
