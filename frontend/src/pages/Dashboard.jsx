import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

const AVATAR_URL =
  "https://lh3.googleusercontent.com/aida-public/AB6AXuDRCxUpRRoPm4mNb0jQUKH9twFnAhWH4sx567Cbg7kQIbHNTORf5Xne9wd3i52wpxB9ZbxFwGHwqXj7ESBggL8cZP9qI7-ibYiw2F6-UBCdrorXsBY5dIVlJw2mwf-xg9q0MukghW_krmgjPw5F0Ou22AdcIl3icYBqIcaUk6NmoqfloDtkRau1mCfT35u5gxBUPF8GLSCHMZer6OnAOEXAZhRRtPRid-Gg-LasBlaaE3NVU601YdBsA8WTC0ZgKah3vsbUxWGiO-Y";

const NAV_ITEMS = [
  { icon: "dashboard", label: "Dashboard", active: true },
  { icon: "description", label: "My Resumes" },
  { icon: "auto_awesome", label: "Generator" },
  { icon: "history", label: "History" },
  { icon: "payments", label: "Subscription" },
  { icon: "settings", label: "Settings" },
];

const STATS = [
  {
    label: "Resume Library",
    value: "12",
    meta: { icon: "trending_up", text: "+2 this month" },
  },
  {
    label: "Avg ATS Score",
    value: "84%",
    meta: { icon: "verified", text: "Industry High" },
  },
  { label: "Credits Used", value: "14/50", progress: 28 },
];

const RESUMES = [
  {
    title: "Senior Product Designer",
    date: "Last edited 2 days ago",
    badge: "Top Match",
    percent: 92,
    status: "Optimized",
    statusColor: "var(--cyber-emerald)",
    ringColor: "var(--cyber-violet)",
    ringGlow: "drop-shadow(0 0 8px rgba(139,92,246,0.8))",
  },
  {
    title: "Creative Director",
    date: "Last edited Oct 14, 2023",
    percent: 75,
    status: "Improving",
    statusColor: "var(--on-surface)",
    ringColor: "rgba(139,92,246,0.6)",
    ringGlow: "drop-shadow(0 0 5px rgba(139,92,246,0.4))",
  },
  {
    title: "UX Research Strategist",
    date: "Last edited Oct 08, 2023",
    percent: 85,
    status: "Very Good",
    statusColor: "var(--cyber-violet)",
    ringColor: "rgba(139,92,246,0.8)",
    ringGlow: "drop-shadow(0 0 6px rgba(139,92,246,0.6))",
  },
];

const RING_RADIUS = 28;
const RING_CIRC = 2 * Math.PI * RING_RADIUS; // ~175.9

function ScoreRing({ percent, color, glow }) {
  const offset = RING_CIRC * (1 - percent / 100);
  return (
    <div className="dash-ring">
      <svg viewBox="0 0 64 64">
        <circle
          className="dash-ring__track"
          cx="32"
          cy="32"
          r={RING_RADIUS}
          fill="transparent"
          stroke="currentColor"
          strokeWidth="4"
        />
        <circle
          cx="32"
          cy="32"
          r={RING_RADIUS}
          fill="transparent"
          stroke={color}
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={RING_CIRC}
          strokeDashoffset={offset}
          style={{ filter: glow }}
        />
      </svg>
      <span className="dash-ring__value">{percent}%</span>
    </div>
  );
}

function ResumeCard({ resume, onEdit }) {
  return (
    <div className="dash-resume glass-card glow-effect">
      {resume.badge && <span className="dash-resume__badge">{resume.badge}</span>}
      <h4 className="dash-resume__title">{resume.title}</h4>
      <p className="dash-resume__date">{resume.date}</p>

      <div className="dash-resume__score">
        <ScoreRing
          percent={resume.percent}
          color={resume.ringColor}
          glow={resume.ringGlow}
        />
        <div className="dash-resume__score-meta">
          <span className="dash-resume__score-label">ATS Compatibility</span>
          <span
            className="dash-resume__score-status"
            style={{ color: resume.statusColor }}
          >
            {resume.status}
          </span>
        </div>
      </div>

      <div className="dash-resume__actions">
        <button
          className="dash-resume__action"
          type="button"
          aria-label="Edit"
          onClick={onEdit}
        >
          <span className="material-symbols-outlined">edit</span>
        </button>
        <button
          className="dash-resume__action"
          type="button"
          aria-label="Download"
        >
          <span className="material-symbols-outlined">download</span>
        </button>
        <button
          className="dash-resume__action dash-resume__action--danger"
          type="button"
          aria-label="Delete"
        >
          <span className="material-symbols-outlined">delete</span>
        </button>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  return (
    <div className="dashboard">
      {/* Sidebar */}
      <aside className="dash-sidebar">
        <div className="dash-sidebar__brand">
          <span className="dash-sidebar__brand-name">CareerPro AI</span>
          <p className="dash-sidebar__plan">Premium Plan</p>
        </div>

        <nav className="dash-sidebar__nav">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.label}
              href="#"
              className={`dash-nav-item${
                item.active ? " dash-nav-item--active" : ""
              }`}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span>{item.label}</span>
            </a>
          ))}
        </nav>

        <div className="dash-sidebar__cta">
          <button className="dash-sidebar__cta-btn cyber-gradient" type="button">
            <span className="material-symbols-outlined">add</span>
            Tailor New Resume
          </button>
        </div>

        <div className="dash-sidebar__user">
          <div className="dash-sidebar__avatar">
            <img src={AVATAR_URL} alt="Alex Rivera" />
          </div>
          <div>
            <div className="dash-sidebar__user-name">Alex Rivera</div>
            <div className="dash-sidebar__user-role">Workspace</div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="dash-main">
        <header className="dash-topbar">
          <h1 className="dash-topbar__title">Welcome back, Alex</h1>
          <div className="dash-topbar__right">
            <div className="dash-search">
              <span className="material-symbols-outlined">search</span>
              <input type="text" placeholder="Search resumes..." />
            </div>
            <div className="dash-topbar__icons">
              <button className="dash-icon-btn" type="button" aria-label="Notifications">
                <span className="material-symbols-outlined">notifications</span>
              </button>
              <button className="dash-icon-btn" type="button" aria-label="Help">
                <span className="material-symbols-outlined">help</span>
              </button>
            </div>
            <div className="dash-avatar-badge">AR</div>
          </div>
        </header>

        <main className="dash-canvas">
          {/* Stats */}
          <section className="dash-stats">
            {STATS.map((stat) => (
              <div key={stat.label} className="dash-stat glass-card glow-effect">
                <div>
                  <span className="dash-stat__label">{stat.label}</span>
                  <h3 className="dash-stat__value">{stat.value}</h3>
                </div>
                {stat.meta ? (
                  <div className="dash-stat__meta">
                    <span className="material-symbols-outlined">
                      {stat.meta.icon}
                    </span>
                    <span>{stat.meta.text}</span>
                  </div>
                ) : (
                  <div className="dash-progress">
                    <div
                      className="dash-progress__fill"
                      style={{ width: `${stat.progress}%` }}
                    />
                  </div>
                )}
              </div>
            ))}
          </section>

          {/* Actions */}
          <section className="dash-actions">
            <h2 className="dash-actions__title">Recent Resumes</h2>
            <div className="dash-actions__buttons">
              <button className="dash-btn dash-btn--ghost" type="button">
                <span className="material-symbols-outlined">upload_file</span>
                Upload Resume
              </button>
              <button className="dash-btn dash-btn--primary" type="button">
                <span className="material-symbols-outlined">add</span>
                Generate New
              </button>
            </div>
          </section>

          {/* Resume cards */}
          <section className="dash-resumes">
            {RESUMES.map((resume) => (
              <ResumeCard
                key={resume.title}
                resume={resume}
                onEdit={() => navigate("/editor")}
              />
            ))}
          </section>

          {/* Insights CTA */}
          <section>
            <div className="dash-insights glass-card">
              <div className="dash-insights__copy">
                <h3 className="dash-insights__title">
                  Unlock AI-Powered Insights
                </h3>
                <p className="dash-insights__text">
                  Connect your LinkedIn profile or target job description to see
                  how your resumes stack up against specific market requirements.
                </p>
                <button className="dash-insights__btn" type="button">
                  Explore Career Matcher
                </button>
              </div>
              <div className="dash-insights__visual">
                <div className="dash-insights__visual-glow" />
                <div className="dash-insights__visual-icon">
                  <span className="material-symbols-outlined">analytics</span>
                </div>
                <div className="dash-insights__toast">
                  <div className="dash-insights__toast-icon">
                    <span className="material-symbols-outlined">check</span>
                  </div>
                  <div className="dash-insights__toast-bars">
                    <div className="dash-bar dash-bar--lg">
                      <div />
                    </div>
                    <div className="dash-bar dash-bar--sm" />
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
