import { useEffect, useState } from "react";
import Home from "./pages/Home";

function App() {
  // Global theme state
  const [theme, setTheme] = useState(
    localStorage.getItem("theme") || "dark"
  );

  // Apply theme to <html>
  useEffect(() => {
    const root = document.documentElement;

    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }

    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <div
      className="min-h-screen
                 bg-neutral-100 text-neutral-900
                 dark:bg-neutral-950 dark:text-neutral-100
                 transition-colors duration-300"
    >
      <Home theme={theme} setTheme={setTheme} />
    </div>
  );
}

export default App;
