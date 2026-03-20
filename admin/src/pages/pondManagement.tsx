import { useEffect, useState } from 'react';
import '../styles/pondManagement.css';
import { AdminApiService, type AdminPond } from '../services/adminApiService';

export default function PondManagement() {
  const [ponds, setPonds] = useState<AdminPond[]>([]);
  const [loadError, setLoadError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [modalUserId, setModalUserId] = useState<string | null>(null);
  const [modalPondId, setModalPondId] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loadPonds = async () => {
      try {
        const data = await AdminApiService.getPonds();
        if (!isMounted) return;
        setPonds(data);
      } catch {
        if (!isMounted) return;
        setLoadError('Unable to load ponds from server.');
      }
    };
    loadPonds();
    return () => {
      isMounted = false;
    };
  }, []);


  // Pagination logic
  const PONDS_PER_PAGE = 10;
  const [currentPage, setCurrentPage] = useState(1);
  const filteredPonds = ponds.filter(
    (pond) =>
      pond.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      pond.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (pond.user_name?.toLowerCase() || '').includes(searchTerm.toLowerCase())
  );
  const totalPages = Math.max(1, Math.ceil(filteredPonds.length / PONDS_PER_PAGE));
  const paginatedPonds = filteredPonds.slice((currentPage - 1) * PONDS_PER_PAGE, currentPage * PONDS_PER_PAGE);
  const showingFrom = filteredPonds.length === 0 ? 0 : (currentPage - 1) * PONDS_PER_PAGE + 1;
  const showingTo = Math.min(currentPage * PONDS_PER_PAGE, filteredPonds.length);
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

  // Reset page on filter/search change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);
  useEffect(() => {
    setCurrentPage((previousPage) => Math.min(previousPage, totalPages));
  }, [totalPages]);

  return (
    <div className="pond-management-container">
      {/* Only one header, info button moved next to title */}
      <header className="pond-management-header" style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
        <button className="pond-management-add-button">+ Add New Pond</button>
      </header>

      {/* Error message if loadError is set */}
      {loadError && (
        <div className="pond-management-error-message" style={{ color: '#e53935', margin: '12px 0', textAlign: 'center' }}>
          {loadError}
        </div>
      )}

      {showModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(0,0,0,0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
        >
          <div
            style={{
              background: '#fff',
              padding: 32,
              borderRadius: 8,
              minWidth: 320,
              boxShadow: '0 2px 16px rgba(0,0,0,0.2)',
              position: 'relative',
              textAlign: 'center',
            }}
          >
            {/* Close X button */}
            <button
              onClick={() => setShowModal(false)}
              style={{
                position: 'absolute',
                top: 12,
                right: 12,
                background: 'none',
                border: 'none',
                fontSize: 22,
                color: '#e53935',
                cursor: 'pointer',
                fontWeight: 'bold',
                lineHeight: 1,
              }}
              aria-label="Close"
              title="Close"
            >
              ×
            </button>
            <h3>ESP32 Credentials</h3>
            <div style={{ margin: '16px 0', fontSize: 16 }}>
              <div><strong>userId:</strong> <span style={{ fontFamily: 'monospace' }}>{modalUserId}</span></div>
              <div><strong>pondId:</strong> <span style={{ fontFamily: 'monospace' }}>{modalPondId}</span></div>
            </div>
          </div>
        </div>
      )}
      {/* ...existing code... */}

      {/* Search and Filter */}
      <div className="pond-management-controls-bar">
        <div className="pond-management-search-box">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            placeholder="Search ponds by name, location, or user..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pond-management-search-input"
          />
        </div>
        <div className="pond-management-filter-group">

          <select className="pond-management-filter-select">
            <option>All Sections</option>
            <option>Section A</option>
            <option>Section B</option>
            <option>Section C</option>
            <option>Section D</option>
          </select>
          <select className="pond-management-filter-select">
            <option>All Status</option>
            <option>Active</option>
            <option>Inactive</option>
          </select>
        </div>
      </div>

      {/* Ponds Table */}
      <div className="pond-management-card">
        <div className="pond-management-table-container">
          <table className="pond-management-table">
            <thead>
              <tr className="pond-management-table-header-row">
                <th className="pond-management-table-header">Pond Name</th>
                <th className="pond-management-table-header">Owner</th>
                <th className="pond-management-table-header">Location</th>
                <th className="pond-management-table-header">Status</th>
                <th className="pond-management-table-header">Actions</th>
              </tr>
            </thead>
            <tbody>
              {paginatedPonds.map((pond, index) => (
                <tr key={pond.id} className={index % 2 === 0 ? 'pond-management-table-row-even' : 'pond-management-table-row-odd'}>
                  <td className="pond-management-table-cell">
                    <span className="pond-management-pond-name">{pond.name}</span>
                  </td>
                  <td className="pond-management-table-cell">{pond.user_name || ''}</td>
                  <td className="pond-management-table-cell">{pond.location}</td>
                  <td className="pond-management-table-cell">
                    <span className="pond-management-status-badge">{pond.status || 'Active'}</span>
                  </td>

                  <td className="pond-management-table-cell">
                    <div className="pond-management-action-buttons">
                      <button
                        className="pond-management-action-button"
                        title="View"
                        onClick={() => {
                          // Use the real user_id and pond_id if available
                          setModalUserId((pond as any).user_id || "69a39acc56b522b28deec4a9");
                          setModalPondId((pond as any).pond_id || "69a39f9cbb28dfc1b9a307fb");
                          setShowModal(true);
                        }}
                      >
                        👁️
                      </button>
                      <button className="pond-management-action-button" title="Edit">
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
        <div className="pond-management-pagination">
          <p className="pond-management-pagination-text">
            Showing {showingFrom}-{showingTo} of {filteredPonds.length} ponds
          </p>
          <div className="pond-management-pagination-buttons">
            <button
              className="pond-management-page-button"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            {visiblePageNumbers.map((page) => (
              <button
                key={page}
                className={`pond-management-page-button${page === currentPage ? ' pond-management-active-page-button' : ''}`}
                onClick={() => setCurrentPage(page)}
              >
                {page}
              </button>
            ))}
            <button
              className="pond-management-page-button"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages || filteredPonds.length === 0}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}