import { useEffect, useMemo, useState } from 'react';
import { MdOutlineWater, MdOutlineStorage, MdOutlineCheckCircle } from 'react-icons/md';
import '../styles/dataRecord.css';
import '../styles/ModalComponents.css';
import { AdminApiService, type DataRecord } from '../services/adminApiService';
import ModalComponentLogs from '../components/ModalComponentLogs';
import ModalComponentDoPrediction from '../components/ModalComponentDoPrediction';
import ModalComponentDevicePrediction from '../components/ModalComponentDevicePrediction';
import ModalComponentStatistics from '../components/ModalComponentStatistics';

const DEFAULT_VISIBLE_SERIES = {
  temperature: true,
  ph: true,
  ammonia: true,
  turbidity: true,
  do: true,
};

const MAX_MODAL_ROWS = 20;
const PONDS_PER_PAGE = 5;
const MAX_PAGE_BUTTONS = 5;

const toRecordTimestamp = (record: DataRecord) => {
  const timePart = record.time || '00:00:00';
  const parsed = Date.parse(`${record.date}T${timePart}`);
  return Number.isNaN(parsed) ? 0 : parsed;
};

const sortByNewest = (a: DataRecord, b: DataRecord) => toRecordTimestamp(b) - toRecordTimestamp(a);

export default function DataRecords() {

  const [searchTerm, setSearchTerm] = useState('');
  // Removed unused loadError state
  const [modalRecord, setModalRecord] = useState<DataRecord | null>(null);
  const [records, setRecords] = useState<DataRecord[]>([]);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
      let isMounted = true;

      const loadRecords = async () => {
        try {
          const data = await AdminApiService.getRecords(500);
          if (!isMounted) return;
          if (data.length > 0) {
            setRecords(data);
          }
        } catch {
          if (!isMounted) return;
          // setLoadError('Unable to load records from server. Showing fallback values.');
        }
      };

      loadRecords();
      return () => {
        isMounted = false;
      };
    }, []);

  const [activeTab, setActiveTab] = useState<'logs' | 'doPrediction' | 'devicePrediction' | 'statistics'>('logs');
  const [visibleSeries, setVisibleSeries] = useState({ ...DEFAULT_VISIBLE_SERIES });

  const sortedRecords = useMemo(() => [...records].sort(sortByNewest), [records]);

  const ponds = useMemo(() => {
    const pondMap = new Map<string, { pondId: string; pondName: string; owner: string; latestRecord: DataRecord }>();
    
    sortedRecords.forEach((record) => {
      if (!pondMap.has(record.pondId)) {
        pondMap.set(record.pondId, {
          pondId: record.pondId,
          pondName: record.pondName,
          owner: (record as any).owner || 'Unknown',
          latestRecord: record,
        });
      } else {
        const existing = pondMap.get(record.pondId)!;
        if (toRecordTimestamp(record) > toRecordTimestamp(existing.latestRecord)) {
          existing.latestRecord = record;
        }
      }
    });

    return Array.from(pondMap.values()).map((pond) => {
      const record = pond.latestRecord;
      const issues = [];
      if ((record.do || 0) < 6) issues.push('Low DO');
      if (record.turbidity > 20) issues.push('High Turbidity');
      if (record.ammonia >= 0.05) issues.push('High Ammonia');
      if (record.temperature < 26 || record.temperature > 30) issues.push('Temp Issue');
      if (record.ph < 6.8 || record.ph > 7.5) issues.push('pH Issue');

      let status = 'Active';
      if (record.prediction === 'Warning' || issues.length > 0) status = 'Warning';
      if (record.prediction === 'Fair') status = 'Fair';
      if (record.prediction === 'Excellent') status = 'Excellent';

      return {
        ...pond,
        status,
        problem: issues.length > 0 ? issues.join(', ') : 'None',
      };
    });
  }, [sortedRecords]);

  const filteredPonds = useMemo(
    () =>
      ponds.filter((pond) => {
        const matchesSearch =
          pond.pondName.toLowerCase().includes(searchTerm.toLowerCase()) ||
          pond.owner.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesSearch;
      }),
    [ponds, searchTerm]
  );

  const totalPages = useMemo(
    () => Math.max(1, Math.ceil(filteredPonds.length / PONDS_PER_PAGE)),
    [filteredPonds.length]
  );

  const paginatedPonds = useMemo(() => {
    const startIndex = (currentPage - 1) * PONDS_PER_PAGE;
    return filteredPonds.slice(startIndex, startIndex + PONDS_PER_PAGE);
  }, [filteredPonds, currentPage]);

  const visiblePageNumbers = useMemo(() => {
    const pages: number[] = [];
    const halfWindow = Math.floor(MAX_PAGE_BUTTONS / 2);
    let start = Math.max(1, currentPage - halfWindow);
    let end = Math.min(totalPages, start + MAX_PAGE_BUTTONS - 1);
    start = Math.max(1, end - MAX_PAGE_BUTTONS + 1);

    for (let page = start; page <= end; page += 1) {
      pages.push(page);
    }
    return pages;
  }, [currentPage, totalPages]);

  const showingFrom = filteredPonds.length === 0 ? 0 : (currentPage - 1) * PONDS_PER_PAGE + 1;
  const showingTo = Math.min(currentPage * PONDS_PER_PAGE, filteredPonds.length);

  const goToPage = (page: number) => {
    const nextPage = Math.min(totalPages, Math.max(1, page));
    setCurrentPage(nextPage);
  };

  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  useEffect(() => {
    setCurrentPage((previousPage) => Math.min(previousPage, totalPages));
  }, [totalPages]);

  const modalPondRecords = useMemo(() => {
    if (!modalRecord) return [];
    return sortedRecords.filter((record) => record.pondId === modalRecord.pondId);
  }, [sortedRecords, modalRecord]);

  const visibleModalRecords = useMemo(
    () => modalPondRecords.slice(0, MAX_MODAL_ROWS),
    [modalPondRecords]
  );

  const getAverage = (values: number[]) => {
    if (values.length === 0) return 0;
    return values.reduce((sum, value) => sum + value, 0) / values.length;
  };

  const handleViewRecord = (record: DataRecord) => {
    setModalRecord(record);
    setActiveTab('logs');
    setVisibleSeries({ ...DEFAULT_VISIBLE_SERIES });
  };

  const closeModal = () => {
    setModalRecord(null);
  };

  const pondStats = [
    {
      icon: <MdOutlineWater size={28} />, // Pond icon
      iconClass: 'stat-icon-ponds',
      value: ponds.length.toString(),
      label: 'Total Ponds',
    },
    {
      icon: <MdOutlineStorage size={28} />, // Data icon
      iconClass: 'stat-icon-data',
      value: records.length.toString(),
      label: 'Total Data',
    },
    {
      icon: <MdOutlineCheckCircle size={28} />, // Active icon
      iconClass: 'stat-icon-active',
      value: ponds.filter(p => p.status === 'Active' || p.status === 'Excellent').length.toString(),
      label: 'Active Ponds',
    },
  ];

  return (
    <div className="data-records-container">
      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            placeholder="Search by pond name or owner..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <button className="apply-filter-button">Apply Filters</button>
      </div>

      {/* Summary Stats */}
      <div className="stats-grid">
        {pondStats.map((metric) => (
          <div key={metric.label} className="stat-card">
            <div className={`stat-icon ${metric.iconClass}`}>{metric.icon}</div>
            <div>
              <p className="stat-value">{metric.value}</p>
              <p className="stat-label">{metric.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Data Table */}
      <div className="data-card">
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr className="table-header-row">
                <th className="table-header center-text">Pond name</th>
                <th className="table-header center-text">Owner</th>
                <th className="table-header center-text">row count</th>
                <th className="table-header center-text">export</th>
                <th className="table-header center-text">Action</th>
              </tr>
            </thead>
            <tbody>
              {paginatedPonds.map((pond, index) => (
                <tr key={pond.pondId} className={index % 2 === 0 ? 'table-row-even' : 'table-row-odd'}>
                  <td className="table-cell center-text">{pond.pondName}</td>
                  <td className="table-cell center-text">{pond.owner}</td>
                  <td className="table-cell center-text">{
                    sortedRecords.filter(r => r.pondId === pond.pondId).length
                  }</td>
                  <td className="table-cell center-text">
                    <button className="export-action-button" title="Export CSV for this pond">Export</button>
                  </td>
                  <td className="table-cell center-text">
                    <button className="view-action-button" onClick={() => handleViewRecord(pond.latestRecord)}>
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="pagination">
          <p className="pagination-text">
            Showing {showingFrom}-{showingTo} of {filteredPonds.length} matching ponds
          </p>
          <div className="pagination-buttons">
            <button className="page-button" onClick={() => goToPage(currentPage - 1)} disabled={currentPage === 1}>
              Previous
            </button>
            {visiblePageNumbers.map((page) => (
              <button
                key={page}
                className={`page-button ${page === currentPage ? 'active' : ''}`}
                onClick={() => goToPage(page)}
              >
                {page}
              </button>
            ))}
            <button
              className="page-button"
              onClick={() => goToPage(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Modal */}
      {modalRecord && (
        <div className="modal-backdrop" onClick={closeModal}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close-button" onClick={closeModal}>
              ✕
            </button>

            <div className="modal-header">
              <h2>Water Quality Details - {modalRecord.pondName}</h2>
                <p className="modal-subtitle">
                  <span style={{ fontWeight: 'bold' }}>Pond Name: {modalRecord.pondName}</span> • Showing latest {visibleModalRecords.length} records for this pond
                </p>
            </div>
            
            {/* Tab Navigation */}
            <div className="modal-tabs">
              <button
                className={`tab-button ${activeTab === 'logs' ? 'active' : ''}`}
                onClick={() => setActiveTab('logs')}
              >
                Logs
              </button>
              <button
                className={`tab-button ${activeTab === 'doPrediction' ? 'active' : ''}`}
                onClick={() => setActiveTab('doPrediction')}
              >
                DO Prediction
              </button>
              <button
                className={`tab-button ${activeTab === 'devicePrediction' ? 'active' : ''}`}
                onClick={() => setActiveTab('devicePrediction')}
              >
                Device Prediction
              </button>
              <button
                className={`tab-button ${activeTab === 'statistics' ? 'active' : ''}`}
                onClick={() => setActiveTab('statistics')}
              >
                Statistics
              </button>
            </div>

            <div className="modal-tab-wrapper">
              {activeTab === 'logs' && (
                <ModalComponentLogs records={visibleModalRecords} />
              )}
              {activeTab === 'doPrediction' && (
                <ModalComponentDoPrediction
                  visibleModalRecords={visibleModalRecords}
                  getStatus={(record) => {
                    const doValue = record.predicted_dissolved_oxygen ?? record.do ?? 0;
                    if (doValue >= 7) return 'Excellent';
                    if (doValue >= 5) return 'Good';
                    return 'Poor';
                  }}
                />
              )}
              {activeTab === 'devicePrediction' && (
                <ModalComponentDevicePrediction
                  visibleModalRecords={visibleModalRecords}
                  getDeviceProblem={(record) => {
                    const issues: string[] = [];
                    if ((record.do || 0) < 6) issues.push('Low DO');
                    if (record.turbidity > 20) issues.push('High Turbidity');
                    if (record.ammonia >= 0.05) issues.push('High Ammonia');
                    return issues.length ? issues.join(', ') : 'Normal';
                  }}
                  getDeviceSummary={(record) => {
                    if (record.final_devices) {
                      return `Heater: ${record.final_devices.heater ? 'ON' : 'OFF'} | Pump: ${record.final_devices.water_pump ? 'ON' : 'OFF'} | Danger: ${record.final_devices.danger ? 'YES' : 'NO'}`;
                    }
                    const aeratorOn = (record.do || 0) < 6;
                    const pumpOn = record.turbidity > 20;
                    const heaterOn = record.temperature < 26;
                    return `Heater: ${heaterOn ? 'ON' : 'OFF'} | Pump: ${pumpOn ? 'ON' : 'OFF'} | Aerator: ${aeratorOn ? 'ON' : 'OFF'}`;
                  }}
                />
              )}
              {activeTab === 'statistics' && (
                <ModalComponentStatistics
                  records={visibleModalRecords}
                  visibleSeries={visibleSeries}
                  getAverage={getAverage}
                />
              )}
              
            </div>
          </div>
        </div>
      )}
    </div>
  );
}