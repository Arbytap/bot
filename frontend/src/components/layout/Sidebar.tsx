import { NavLink } from "react-router-dom";
import { useAuthStore } from "../../lib/store";

const navItems = [
  { to: "/projects", icon: "🏗️", label: "Проекты" },
  { to: "/letters/incoming", icon: "📥", label: "Входящие" },
  { to: "/letters/outgoing", icon: "📤", label: "Исходящие" },
  { to: "/chains", icon: "🔗", label: "Цепочки" },
  { to: "/documents", icon: "📄", label: "Документы" },
  { to: "/approval", icon: "✅", label: "Согласование" },
];

export function Sidebar() {
  const { user, currentCompany } = useAuthStore();

  return (
    <aside className="flex flex-col w-56 min-h-screen bg-gray-900 text-gray-100">
      <div className="px-4 py-5 border-b border-gray-700">
        <div className="font-bold text-white text-base leading-tight">Project SED</div>
        <div className="text-xs text-gray-400 mt-0.5">Система документооборота</div>
      </div>

      {/* Current company */}
      <div className="px-4 py-3 border-b border-gray-700">
        <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Организация</div>
        {currentCompany ? (
          <NavLink
            to="/companies/switch"
            className="block text-sm text-white font-medium hover:text-blue-300 transition-colors truncate"
            title={currentCompany.name}
          >
            {currentCompany.short_name}
          </NavLink>
        ) : (
          <NavLink
            to="/companies/switch"
            className="block text-sm text-yellow-400 hover:text-yellow-300"
          >
            Выбрать организацию →
          </NavLink>
        )}
      </div>

      <nav className="flex-1 px-2 py-3 space-y-0.5">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-blue-600 text-white"
                  : "text-gray-300 hover:bg-gray-700 hover:text-white"
              }`
            }
          >
            <span className="text-base">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="px-4 py-4 border-t border-gray-700">
        <div className="text-xs text-gray-400 truncate">{user?.full_name}</div>
        <NavLink
          to="/logout"
          className="text-xs text-gray-500 hover:text-gray-300 mt-1 block"
        >
          Выйти
        </NavLink>
      </div>
    </aside>
  );
}
