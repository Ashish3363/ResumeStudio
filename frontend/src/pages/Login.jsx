import { useState } from "react";
import "./Login.css";

const ILLUSTRATION_URL =
  "https://lh3.googleusercontent.com/aida-public/AB6AXuBeUr8vZQNtPSmAl-nK1GtDjB7ZANEBAR5wTCI8Ukg9G2UaWaCdrWF8GDQmx4U5R0hYrJgOM74Xh4ElGcj9UkEA_TA1VvOyscAwzyX6gdQXoFqbVrcBm__qRNm4h14L0xPTxLyhNvhvVs718uwWMdK21N0mJ9mGfVOiQ2te7drxM3mknqRz10e5YoxTcjoBvYKfkwfzK1NtWDgYj9iuLxDQqp82H3qfK9z6OuzHPCv8YloqH6DgV-BzS5-_Or8Ky3DxHDk1rvoFZ50";

const FEATURES = [
  { icon: "auto_awesome", label: "Smart Skill Extraction" },
  { icon: "analytics", label: "ATS Optimization Scoring" },
  { icon: "description", label: "100+ Professional Templates" },
];

function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        fill="#4285F4"
      />
      <path
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        fill="#34A853"
      />
      <path
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        fill="#FBBC05"
      />
      <path
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        fill="#EA4335"
      />
    </svg>
  );
}

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [focused, setFocused] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Wire up to the auth API later.
    console.log("login", { email, password });
  };

  const labelClass = (field) =>
    `login__label${focused === field ? " login__label--focused" : ""}`;

  return (
    <main className="login">
      {/* Left: marketing & illustration */}
      <section className="login__marketing">
        <div className="login__orb login__orb--top" />
        <div className="login__orb login__orb--bottom" />

        <div className="login__brand">
          <span className="login__brand-name">CareerPro AI</span>
        </div>

        <div className="login__marketing-body">
          <h1 className="login__headline">Land your dream job with AI</h1>
          <p className="login__lede">
            Build professional, recruiter-ready resumes in seconds. Our AI
            analyzes job descriptions to tailor your profile for maximum impact.
          </p>

          <ul className="login__features">
            {FEATURES.map((f) => (
              <li className="login__feature" key={f.label}>
                <div className="login__feature-icon">
                  <span className="material-symbols-outlined">{f.icon}</span>
                </div>
                <span className="login__feature-label">{f.label}</span>
              </li>
            ))}
          </ul>

          <div className="login__illustration">
            <div className="login__illustration-glow" />
            <div className="login__illustration-frame">
              <div className="login__illustration-inner">
                <div
                  className="login__illustration-img"
                  role="img"
                  aria-label="Abstract AI-themed illustration with glowing geometric nodes and data streams"
                  style={{ backgroundImage: `url('${ILLUSTRATION_URL}')` }}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="login__marketing-footer">
          Trusted by 50,000+ Professionals
        </div>
      </section>

      {/* Right: login card */}
      <section className="login__panel">
        <div className="login__mobile-brand">
          <span className="login__brand-name">CareerPro AI</span>
        </div>

        <div className="login__card">
          <div className="login__card-header">
            <h2 className="login__title">Welcome back</h2>
            <p className="login__subtitle">
              Please enter your details to sign in.
            </p>
          </div>

          <form className="login__form" onSubmit={handleSubmit}>
            <div className="login__field">
              <label className={labelClass("email")} htmlFor="email">
                Email Address
              </label>
              <input
                className="login__input"
                id="email"
                name="email"
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onFocus={() => setFocused("email")}
                onBlur={() => setFocused(null)}
              />
            </div>

            <div className="login__field">
              <div className="login__label-row">
                <label className={labelClass("password")} htmlFor="password">
                  Password
                </label>
                <a className="login__forgot" href="#">
                  Forgot Password?
                </a>
              </div>
              <input
                className="login__input"
                id="password"
                name="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onFocus={() => setFocused("password")}
                onBlur={() => setFocused(null)}
              />
            </div>

            <div className="login__submit-wrap">
              <button className="login__submit" type="submit">
                Login
                <span className="material-symbols-outlined">arrow_forward</span>
              </button>
            </div>
          </form>

          <div className="login__divider">
            <span>OR</span>
          </div>

          <button className="login__social" type="button">
            <GoogleIcon />
            Continue with Google
          </button>

          <p className="login__signup">
            Don't have an account?{" "}
            <a href="#">Create an account</a>
          </p>
        </div>
      </section>
    </main>
  );
}
