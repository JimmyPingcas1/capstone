import type { ReactNode } from 'react';
import './AdminLayout.css';

export type AdminPage = 'dashboard' | 'ponds' | 'users' | 'data';

interface AdminLayoutProps {
  currentPage: AdminPage;
  onNavigate: (page: AdminPage) => void;
  onLogout: () => void;
  children: ReactNode;
}

const PAGE_META: Record<AdminPage, { label: string; subtitle: string; icon: string }> = {
  dashboard: {
    label: 'Dashboard',
    subtitle: 'Real-time fishpond monitoring overview',
    icon: '📊',
  },
  ponds: {
    label: 'Pond Management',
    subtitle: 'Manage fishpond profiles and assignments',
    icon: '🐟',
  },
  users: {
    label: 'User Management',
    subtitle: 'Manage user roles and access levels',
    icon: '👥',
  },
  data: {
    label: 'Data Records',
    subtitle: 'Track and review historical sensor records',
    icon: '📄',
  },
};

const NAV_ITEMS: Array<{ key: AdminPage; label: string; icon: string }> = [
  { key: 'dashboard', label: 'Dashboard', icon: '📊' },
  { key: 'ponds', label: 'Pond Management', icon: '🐟' },
  { key: 'users', label: 'User Management', icon: '👥' },
  { key: 'data', label: 'Data Records', icon: '📄' },
];

export default function AdminLayout({ currentPage, onNavigate, onLogout, children }: AdminLayoutProps) {
  const pageMeta = PAGE_META[currentPage];

  return (
    <div className="admin-layout-shell">
      <aside className="admin-layout-sidebar">
        <div className="admin-layout-brand">
          <div className="admin-layout-brand-row">
            <div className="admin-layout-logo-frame">
              <img src="/fishpond-logo.png" alt="Fishpond logo" className="admin-layout-logo-image" />
            </div>
            <div>
              <h1 className="admin-layout-brand-title">Fishpond Admin</h1>
              <p className="admin-layout-brand-subtitle">Website Control Panel</p>
            </div>
          </div>
        </div>

        <nav className="admin-layout-nav">
          <p className="admin-layout-nav-label">Menu</p>
          {NAV_ITEMS.map((item) => (
            <button
              key={item.key}
              onClick={() => onNavigate(item.key)}
              className={`admin-layout-nav-link ${currentPage === item.key ? 'active' : ''}`}
            >
              <span className="admin-layout-nav-icon">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="admin-layout-footer">
          <div className="admin-layout-profile-card">
            <div className="admin-layout-profile-row">
              <div className="admin-layout-avatar">A</div>
              <div>
                <p className="admin-layout-profile-name">Admin</p>
                <p className="admin-layout-profile-role">Administrator</p>
              </div>
            </div>
          </div>

          <button onClick={onLogout} className="admin-layout-logout-button">
            <svg className="admin-layout-logout-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Logout
          </button>
        </div>
      </aside>

      <main className="admin-layout-main">
        <header className="admin-layout-topbar">
          <div>
            <h2 className="admin-layout-page-title">{pageMeta.label}</h2>
            <p className="admin-layout-page-subtitle">{pageMeta.subtitle}</p>
          </div>
          <div className="admin-layout-page-badge">
            <span className="admin-layout-page-badge-icon">{pageMeta.icon}</span>
            <span>Admin Website</span>
          </div>
        </header>

        <section className="admin-layout-content">{children}</section>
      </main>
    </div>
  );
}
