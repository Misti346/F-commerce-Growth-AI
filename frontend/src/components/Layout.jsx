import { Outlet, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeftRight, BarChart3, Boxes, CreditCard, LayoutDashboard, LogOut, MessageSquareText, PackageOpen, Settings, ShoppingCart, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { to: '/dashboard', label: 'Overview', icon: LayoutDashboard },
  { to: '/orders', label: 'Orders', icon: ShoppingCart },
  { to: '/customers', label: 'Customers', icon: Users },
  { to: '/products', label: 'Products', icon: Boxes },
  { to: '/ai-extraction', label: 'AI Extraction', icon: MessageSquareText },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/profile', label: 'Profile', icon: CreditCard },
  { to: '/settings', label: 'Settings', icon: Settings }
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-100 text-slate-800">
      <div className="flex min-h-screen">
        <aside className="hidden w-72 flex-col justify-between border-r border-slate-200 bg-slate-900 p-6 text-white lg:flex">
          <div>
            <div className="mb-8 flex items-center gap-3">
              <div className="rounded-xl bg-brand-500/20 p-2 text-brand-100">
                <PackageOpen className="h-6 w-6" />
              </div>
              <div>
                <p className="text-xl font-bold">F-commerce</p>
                <p className="text-xs text-slate-300">Growth AI</p>
              </div>
            </div>

            <nav className="space-y-2">
              {navItems.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                      isActive ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/20' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                    }`
                  }
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </NavLink>
              ))}
            </nav>
          </div>

          <div className="rounded-2xl border border-slate-700 bg-slate-800/70 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Seller</p>
            <p className="mt-2 font-semibold">{user?.name || 'Seller'}</p>
            <p className="text-sm text-slate-300">{user?.email || 'Not signed in'}</p>
            <button
              onClick={handleLogout}
              className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-slate-600 bg-slate-700 px-3 py-2 text-sm font-medium text-slate-100 transition hover:bg-slate-600"
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>
        </aside>

        <div className="flex-1">
          <header className="border-b border-slate-200 bg-white/80 px-4 py-4 backdrop-blur md:px-8">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Business overview</p>
                <h1 className="mt-1 text-2xl font-bold text-slate-900">
                  {navItems.find((item) => item.to === location.pathname)?.label || 'Dashboard'}
                </h1>
              </div>

              <div className="flex items-center gap-3">
                <div className="hidden rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium text-slate-600 md:block">
                  <span className="mr-1 text-slate-400">Live</span>
                  System status: Active
                </div>
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white shadow-soft transition hover:bg-slate-700"
                >
                  <ArrowLeftRight className="h-4 w-4" />
                  Logout
                </button>
              </div>
            </div>
          </header>

          <main className="p-4 md:p-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
