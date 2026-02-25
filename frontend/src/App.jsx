import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header__inner">
          <div className="app-header__brand">
            <img
              src="/assets/uss-logo.png"
              alt="US Signal"
              className="app-header__logo"
              onError={(e) => {
                e.target.style.display = "none";
              }}
            />
            <span className="app-header__title">VME Analyzer</span>
          </div>
          <nav className="app-header__nav">
            <a href="/" className="app-header__nav-link">
              Analyze
            </a>
            <a href="/admin" className="app-header__nav-link">
              Admin
            </a>
          </nav>
        </div>
      </header>

      <main className="app-main">
        <p className="app-main__placeholder">
          Stage 1 skeleton — upload interface coming in Stage 8.
        </p>
      </main>
    </div>
  );
}

export default App;
