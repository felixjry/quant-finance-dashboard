import { Link, useLocation } from "react-router-dom";
import { BarChart3, PieChart, Home, Moon, Sun, Wallet } from "lucide-react";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";

export const Navigation = () => {
  const location = useLocation();
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return document.documentElement.classList.contains('dark');
    }
    return true;
  });

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  const links = [
    { to: "/", label: "Dashboard", icon: Home },
    { to: "/single-asset", label: "Single Asset", icon: BarChart3 },
    { to: "/portfolio", label: "Portfolio", icon: PieChart },
    { to: "/paper-trading", label: "Paper Trading", icon: Wallet },
  ];

  return (
    <nav className="border-b border-border bg-card">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-8 h-8 text-primary" />
            <span className="text-xl font-bold text-foreground">Quant Dashboard</span>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex gap-1">
              {links.map(({ to, label, icon: Icon }) => (
                <Link
                  key={to}
                  to={to}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-lg transition-colors",
                    location.pathname === to
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  )}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">{label}</span>
                </Link>
              ))}
            </div>

            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              title={isDark ? "Mode clair" : "Mode sombre"}
            >
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};
