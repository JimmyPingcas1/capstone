import { useEffect, useMemo, useState } from 'react';
import { MdOutlineGroups, MdOutlineCheckCircle, MdOutlinePauseCircle } from 'react-icons/md';
import '../styles/user.css';
import { AdminApiService, type AdminUser } from '../services/adminApiService';

import type { AdminPond } from '../services/adminApiService';

export default function UserManagement() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [ponds, setPonds] = useState<AdminPond[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    let isMounted = true;

    const loadUsersAndPonds = async () => {
      try {
        const [usersData, pondsData] = await Promise.all([
          AdminApiService.getUsers(),
          AdminApiService.getPonds(),
        ]);
        if (!isMounted) return;
        setUsers(usersData);
        setPonds(pondsData);
      } catch {
        // Optionally handle error, e.g., show a toast or log
      }
    };

    loadUsersAndPonds();
    return () => {
      isMounted = false;
    };
  }, []);

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const activeCount = useMemo(() => users.filter((user) => user.status === 'Active').length, [users]);
  const inactiveCount = users.length - activeCount;

  // Pagination logic
  const USERS_PER_PAGE = 10;
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(filteredUsers.length / USERS_PER_PAGE));
  const paginatedUsers = filteredUsers.slice((currentPage - 1) * USERS_PER_PAGE, currentPage * USERS_PER_PAGE);
  const showingFrom = filteredUsers.length === 0 ? 0 : (currentPage - 1) * USERS_PER_PAGE + 1;
  const showingTo = Math.min(currentPage * USERS_PER_PAGE, filteredUsers.length);
  const visiblePageNumbers = (() => {
    const MAX_PAGE_BUTTONS = 5;
    const pages = [];
    const halfWindow = Math.floor(MAX_PAGE_BUTTONS / 2);
    let start = Math.max(1, currentPage - halfWindow);
    let end = Math.min(totalPages, start + MAX_PAGE_BUTTONS - 1);
    start = Math.max(1, end - MAX_PAGE_BUTTONS + 1);
    for (let page = start; page <= end; page += 1) {
      pages.push(page);
    }
    return pages;
  })();

  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  useEffect(() => {
    setCurrentPage((previousPage) => Math.min(previousPage, totalPages));
  }, [totalPages]);

  return (
    <div className="user-management-container">

      {/* Search and Filter */}
      <div className="user-management-controls-bar">
        <div className="user-management-search-box">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            placeholder="Search by name, email, or pond ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="user-management-search-input"
          />
        </div>
        <div className="user-management-filter-group">
          <select className="user-management-filter-select">
            <option>All Ponds</option>
            {Array.from(new Set(users.map((user) => user.pondId))).map((pondId) => (
              <option key={pondId}>{pondId}</option>
            ))}
          </select>
          <select className="user-management-filter-select">
            <option>All Status</option>
            <option>Active</option>
            <option>Inactive</option>
          </select>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="user-management-stats-grid">
        <div className="user-management-stat-card">
          <div className="user-management-stat-icon-box">
            <MdOutlineGroups size={28} color="#1976d2" />
          </div>
          <div>
            <p className="user-management-stat-value">{users.length}</p>
            <p className="user-management-stat-label">Total Users</p>
          </div>
        </div>
        <div className="user-management-stat-card">
          <div className="user-management-stat-icon-box">
            <MdOutlineCheckCircle size={28} color="#1976d2" />
          </div>
          <div>
            <p className="user-management-stat-value">{activeCount}</p>
            <p className="user-management-stat-label">Active Users</p>
          </div>
        </div>
        <div className="user-management-stat-card">
          <div className="user-management-stat-icon-box">
            <MdOutlinePauseCircle size={28} color="#1976d2" />
          </div>
          <div>
            <p className="user-management-stat-value">{inactiveCount}</p>
            <p className="user-management-stat-label">Inactive Users</p>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="user-management-card">
        <div className="user-management-table-container">
          <table className="user-management-table">
            <thead>
              <tr className="user-management-table-header-row">
                <th className="user-management-table-header">Name</th>
                <th className="user-management-table-header">Email</th>
                <th className="user-management-table-header">Status</th>
                <th className="user-management-table-header">Pond No</th>
                <th className="user-management-table-header">Actions</th>
              </tr>
            </thead>
            <tbody>
              {paginatedUsers.map((user, index) => (
                <tr key={user.id} className={index % 2 === 0 ? 'user-management-table-row-even' : 'user-management-table-row-odd'}>
                  <td className="user-management-table-cell">
                    <div className="user-management-user-info">
                      <span className="user-management-user-name">{user.name}</span>
                    </div>
                  </td>
                  <td className="user-management-table-cell">
                    <span className="user-management-email">{user.email}</span>
                  </td>
                  <td className="user-management-table-cell">
                    <span
                      className={`user-management-status-badge ${
                        user.status === 'Active' ? 'user-management-status-active' : 'user-management-status-inactive'
                      }`}
                    >
                      {user.status}
                    </span>
                  </td>
                  <td className="user-management-table-cell">
                    {/* Pond No: count of ponds for this user by matching user.id to pond.user_id */}
                    <span className="user-management-pond-count-badge">
                      {ponds.filter((pond) => pond.user_id === user.id).length}
                    </span>
                  </td>
                  <td className="user-management-table-cell">
                    <div className="user-management-action-buttons">
                      <button className="user-management-action-button" title="View">
                        👁️
                      </button>
                      <button className="user-management-action-button" title="Edit">
                        ✏️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="user-management-pagination">
          <p className="user-management-pagination-text">
            Showing {showingFrom}-{showingTo} of {filteredUsers.length} users
          </p>
          <div className="user-management-pagination-buttons">
            <button
              className="user-management-page-button"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            {visiblePageNumbers.map((page) => (
              <button
                key={page}
                className={`user-management-page-button${page === currentPage ? ' user-management-active-page-button' : ''}`}
                onClick={() => setCurrentPage(page)}
              >
                {page}
              </button>
            ))}
            <button
              className="user-management-page-button"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages || filteredUsers.length === 0}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}