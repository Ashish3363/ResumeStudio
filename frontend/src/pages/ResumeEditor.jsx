import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./ResumeEditor.css";

const AVATAR_URL =
  "https://lh3.googleusercontent.com/aida-public/AB6AXuAcJXKlR2MWNckOZvj6A1FNVgKWDT6k-O5pQkghlYnYpH5YPJ0nhn59hSreaJu3P69iwx6nkg-tZ6fFHpbmVS-5_OUDFZdDMCRj0dzAOanmNEELZ7E_P5cTkorNgu-xLPqyHPiv5hLVsjkFtCKWE1gtSD_LZ-WB-L9RYtHdAnHv4x1DuO7Fo3EO-WOnl8Jh9lDnaP5ldcgVfoCWq8t0wMhs_GnGR1OOMDW5sNEyNNUnAhp-UmFKE17BOKodTFqqRmnUAQ684xM2Sss";

const NAV_ITEMS = [
  { icon: "dashboard", label: "Dashboard", to: "/dashboard" },
  { icon: "description", label: "My Resumes", active: true },
  { icon: "auto_awesome", label: "Generator" },
  { icon: "history", label: "History" },
  { icon: "payments", label: "Subscription" },
  { icon: "settings", label: "Settings" },
];

const METRICS = [
  { label: "ATS Score", value: 85, color: "var(--primary)" },
  { label: "Match", value: 92, color: "var(--secondary)" },
];

const SUGGESTIONS = [
  {
    keyword: "CI/CD",
    sub: "Recommended for Cloud Infrastructure roles.",
  },
  {
    keyword: "Team Leadership",
    sub: "Boosts Senior-level visibility by 25%.",
  },
];

function MetricRing({ value, color }) {
  // r=16 → circumference ≈ 100; offset = 100 - value
  return (
    <div className="ed-metric__ring">
      <svg viewBox="0 0 40 40">
        <circle
          className="ed-metric__ring-track"
          cx="20"
          cy="20"
          r="16"
          fill="transparent"
          stroke="currentColor"
          strokeWidth="4"
        />
        <circle
          cx="20"
          cy="20"
          r="16"
          fill="transparent"
          stroke={color}
          strokeWidth="4"
          strokeDasharray="100"
          strokeDashoffset={100 - value}
        />
      </svg>
      <span className="ed-metric__value">{value}</span>
    </div>
  );
}

function Accordion({ title, open, onToggle, children }) {
  return (
    <div className={`ed-accordion${open ? " ed-accordion--open" : ""}`}>
      <button className="ed-accordion__trigger" onClick={onToggle} type="button">
        <span className="ed-accordion__title">{title}</span>
        <span className="material-symbols-outlined ed-accordion__icon">
          expand_more
        </span>
      </button>
      <div className="ed-accordion__content">
        <div className="ed-accordion__inner">{children}</div>
      </div>
    </div>
  );
}

export default function ResumeEditor() {
  const navigate = useNavigate();
  const [open, setOpen] = useState({
    summary: true,
    experience: false,
    skills: false,
  });
  const [skills, setSkills] = useState(["Figma", "Prototyping", "User Research"]);

  const toggle = (key) => setOpen((o) => ({ ...o, [key]: !o[key] }));
  const removeSkill = (name) =>
    setSkills((s) => s.filter((skill) => skill !== name));

  return (
    <div className="editor">
      {/* Sidebar */}
      <aside className="ed-sidebar">
        <div className="ed-sidebar__brand">
          <h1>CareerPro AI</h1>
          <p>Premium Plan</p>
        </div>
        <nav className="ed-sidebar__nav">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.label}
              href="#"
              className={`ed-nav-item${
                item.active ? " ed-nav-item--active" : ""
              }`}
              onClick={(e) => {
                if (item.to) {
                  e.preventDefault();
                  navigate(item.to);
                }
              }}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span>{item.label}</span>
            </a>
          ))}
        </nav>
        <div className="ed-sidebar__cta">
          <button className="primary-gradient" type="button">
            Tailor New Resume
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="ed-main">
        <header className="ed-topbar">
          <div className="ed-topbar__left">
            <h2 className="ed-topbar__title">Resume Editor</h2>
            <div className="ed-topbar__search">
              <span className="material-symbols-outlined">search</span>
              <input type="text" placeholder="Search templates..." />
            </div>
          </div>

          <div className="ed-topbar__right">
            <div className="ed-metrics">
              {METRICS.map((m) => (
                <div className="ed-metric" key={m.label}>
                  <MetricRing value={m.value} color={m.color} />
                  <span className="ed-metric__label">{m.label}</span>
                </div>
              ))}
            </div>
            <div className="ed-topbar__icons">
              <span className="material-symbols-outlined">notifications</span>
              <span className="material-symbols-outlined">help</span>
              <div className="ed-topbar__avatar">
                <img src={AVATAR_URL} alt="User" />
              </div>
            </div>
          </div>
        </header>

        {/* Split content */}
        <div className="ed-split">
          {/* Left: PDF preview */}
          <section className="ed-preview">
            <div className="ed-preview__toolbar">
              <div className="ed-zoom">
                <button type="button" aria-label="Zoom out">
                  <span className="material-symbols-outlined">zoom_out</span>
                </button>
                <span>100%</span>
                <button type="button" aria-label="Zoom in">
                  <span className="material-symbols-outlined">zoom_in</span>
                </button>
              </div>
              <button className="ed-download-btn" type="button">
                <span className="material-symbols-outlined">download</span>
                Download PDF
              </button>
            </div>

            <div className="ed-paper">
              <div className="ed-paper__header">
                <h3 className="ed-paper__name">Alex Thompson</h3>
                <p className="ed-paper__role">Senior Product Designer</p>
              </div>

              <div className="ed-paper__grid">
                <div className="ed-paper__main">
                  <div className="ed-paper__section">
                    <h4 className="ed-paper__heading">Professional Summary</h4>
                    <p className="ed-paper__text">
                      Ambitious Senior Product Designer with 8+ years of
                      experience leading cross-functional teams in the FinTech
                      space. Proven track record of increasing user engagement by
                      40% through human-centered design iterations...
                    </p>
                  </div>

                  <div className="ed-paper__section">
                    <h4 className="ed-paper__heading">Experience</h4>
                    <div>
                      <div className="ed-paper__job-head">
                        <span>Lead UI/UX Designer • Global Finance Hub</span>
                        <span>2021 - Present</span>
                      </div>
                      <ul className="ed-paper__bullets">
                        <li>
                          Orchestrated the redesign of the core mobile
                          application, serving 2M active users globally.
                        </li>
                        <li>
                          Implemented a comprehensive design system that reduced
                          front-end development time by 30%.
                        </li>
                      </ul>
                    </div>
                    <div style={{ marginTop: 16 }}>
                      <div className="ed-paper__job-head">
                        <span>Senior UI Designer • Creative Pulse</span>
                        <span>2018 - 2021</span>
                      </div>
                      <ul className="ed-paper__bullets">
                        <li>
                          Led visual strategy for over 15 client projects,
                          ranging from startups to Fortune 500 companies.
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="ed-paper__aside">
                  <div className="ed-paper__section">
                    <h4 className="ed-paper__heading">Contact</h4>
                    <div className="ed-paper__contact">
                      <p>
                        <span className="material-symbols-outlined">mail</span>
                        alex.t@careerpro.ai
                      </p>
                      <p>
                        <span className="material-symbols-outlined">
                          location_on
                        </span>
                        San Francisco, CA
                      </p>
                      <p>
                        <span className="material-symbols-outlined">
                          language
                        </span>
                        alexportfolio.com
                      </p>
                    </div>
                  </div>

                  <div className="ed-paper__section">
                    <h4 className="ed-paper__heading">Skills</h4>
                    <div className="ed-paper__skills">
                      {["Figma", "Atomic Design", "Prototyping", "User Research"].map(
                        (s) => (
                          <span className="ed-paper__skill" key={s}>
                            {s}
                          </span>
                        )
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Right: interactive editor */}
          <section className="ed-panel">
            <div className="ed-panel__head">
              <div className="ed-panel__head-title">
                <span className="material-symbols-outlined">edit_note</span>
                <h3>Content Editor</h3>
              </div>
              <button className="ed-improve-btn" type="button">
                <span className="material-symbols-outlined">auto_awesome</span>
                Improve All
              </button>
            </div>

            <div className="ed-scroll">
              {/* Summary */}
              <Accordion
                title="Professional Summary"
                open={open.summary}
                onToggle={() => toggle("summary")}
              >
                <textarea
                  className="ed-textarea ed-textarea--summary"
                  defaultValue="Ambitious Senior Product Designer with 8+ years of experience leading cross-functional teams in the FinTech space. Proven track record of increasing user engagement by 40% through human-centered design iterations and data-driven visual strategy."
                />
                <button className="ed-regenerate" type="button">
                  <span className="material-symbols-outlined">auto_awesome</span>
                  Regenerate by AI
                </button>
              </Accordion>

              {/* Experience */}
              <Accordion
                title="Experience"
                open={open.experience}
                onToggle={() => toggle("experience")}
              >
                <div className="ed-exp">
                  <div className="ed-exp__head">
                    <h5>Lead UI/UX Designer</h5>
                    <button
                      className="ed-exp__delete"
                      type="button"
                      aria-label="Delete"
                    >
                      <span className="material-symbols-outlined">delete</span>
                    </button>
                  </div>
                  <input
                    className="ed-input"
                    type="text"
                    defaultValue="Global Finance Hub"
                  />
                  <textarea
                    className="ed-exp__textarea"
                    defaultValue="Orchestrated the redesign of the core mobile application, serving 2M active users globally. Implemented a comprehensive design system that reduced development time by 30%."
                  />
                </div>
                <button className="ed-add-btn" type="button">
                  <span className="material-symbols-outlined">add</span>
                  Add Experience
                </button>
              </Accordion>

              {/* Skills */}
              <Accordion
                title="Skills"
                open={open.skills}
                onToggle={() => toggle("skills")}
              >
                <div className="ed-chips">
                  {skills.map((skill) => (
                    <span className="ed-chip" key={skill}>
                      {skill}
                      <button
                        type="button"
                        aria-label={`Remove ${skill}`}
                        onClick={() => removeSkill(skill)}
                      >
                        <span className="material-symbols-outlined">close</span>
                      </button>
                    </span>
                  ))}
                  <input
                    className="ed-chip-input"
                    type="text"
                    placeholder="+ Add Skill"
                  />
                </div>
              </Accordion>

              {/* AI Suggestions */}
              <div className="ed-suggestions glass-panel">
                <div className="ed-suggestions__head">
                  <span className="material-symbols-outlined">
                    tips_and_updates
                  </span>
                  <h4>AI Suggestions</h4>
                </div>
                <div className="ed-suggestions__list">
                  {SUGGESTIONS.map((s) => (
                    <div className="ed-suggestion" key={s.keyword}>
                      <div>
                        <p className="ed-suggestion__title">
                          Missing Keyword: <span>{s.keyword}</span>
                        </p>
                        <p className="ed-suggestion__sub">{s.sub}</p>
                      </div>
                      <button className="ed-suggestion__accept" type="button">
                        Accept
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Footer actions */}
            <div className="ed-footer">
              <button
                className="ed-footer__back"
                type="button"
                onClick={() => navigate("/dashboard")}
              >
                <span className="material-symbols-outlined">arrow_back</span>
                Return to Dashboard
              </button>
              <button
                className="ed-footer__download primary-gradient"
                type="button"
              >
                <span className="material-symbols-outlined">download</span>
                Download Resume
              </button>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
