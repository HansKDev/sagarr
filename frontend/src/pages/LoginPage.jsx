const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function LoginPage() {
  const handleLogin = () => {
    window.location.href = `${API_BASE_URL}/api/auth/login`;
  };

  return (
    <section className="login">
      <h1>Sign in with Plex</h1>
      <p>
        Connect your Plex account so Sagarr can personalize recommendations
        based on your watch history.
      </p>
      <button type="button" className="login-button" onClick={handleLogin}>
        Sign in with Plex
      </button>
    </section>
  );
}

