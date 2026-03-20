import { useEffect, useState } from 'react';
import '../styles/dashboard.css';
import { AdminApiService } from '../services/adminApiService';

const DEFAULT_VISIBLE_SERIES = {
  temperature: true,
  ph: true,
  ammonia: true,
  turbidity: true,
  do: true,
};

export default function Dashboard() {
  const [tooltipData, setTooltipData] = useState<{ x: number; record: any } | null>(null);
  const [visibleSeries, setVisibleSeries] = useState({ ...DEFAULT_VISIBLE_SERIES });
  const [loadError, setLoadError] = useState('');

  // Generate fallback 24 hours of data when API is unavailable.
  const fallbackReadings = Array.from({ length: 24 }, (_, i) => {
    const hour = i + 1; // 1-24
    let displayHour = hour;
    let period = 'am';
    
    if (hour === 12) {
      displayHour = 12;
      period = 'pm';
    } else if (hour > 12 && hour < 24) {
      displayHour = hour - 12;
      period = 'pm';
    } else if (hour === 24) {
      displayHour = 12;
      period = 'am';
    }
    
    const timeStr = `${displayHour}${period}`;
    
    return {
      time: timeStr,
      temp: 27 + Math.random() * 3 + Math.sin(i / 3) * 1.5,
      ph: 7.0 + Math.random() * 0.4 - 0.2,
      ammonia: 0.025 + Math.random() * 0.02,
      turbidity: 15 + Math.random() * 10,
      do: 6.0 + Math.random() * 1.5 + Math.cos(i / 4) * 0.5,
    };
  });

  const [overviewStats, setOverviewStats] = useState([
    { title: 'Total Ponds', value: '0', icon: '🐟', tone: 'ponds' },
    { title: 'Total Users', value: '0', icon: '👥', tone: 'users' },
    { title: 'Active Pond Today', value: '0', icon: '✅', tone: 'activepond' },
  ]);
  const [recentReadings, setRecentReadings] = useState(fallbackReadings);

  useEffect(() => {
    let isMounted = true;

    const loadDashboard = async () => {
      try {
        const data = await AdminApiService.getDashboard();
        if (!isMounted) return;

        setOverviewStats([
          { title: 'Total Ponds', value: String(data.totalPonds ?? 0), icon: '🐟', tone: 'ponds' },
          { title: 'Total Users', value: String(data.totalUsers ?? 0), icon: '👥', tone: 'users' },
          {
            title: 'Active Pond Today',
            value: String(data.activePondToday ?? 0),
            icon: '✅',
            tone: 'activepond',
          },
        ]);

        if (Array.isArray(data.recentReadings) && data.recentReadings.length > 0) {
          setRecentReadings(data.recentReadings);
        }
      } catch {
        if (!isMounted) return;
        setLoadError('Unable to load live dashboard data. Showing fallback values.');
      }
    };

    loadDashboard();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="dashboard-container">
      {/* Overview Stats */}
      <div className="dashboard-stats-grid">
        {overviewStats.map((stat, index) => (
          <div key={index} className="dashboard-stat-card">
            <div className={`dashboard-stat-icon dashboard-stat-icon-${stat.tone}`}>{stat.icon}</div>
            <div className="dashboard-stat-content">
              <p className="dashboard-stat-value">{stat.value}</p>
              <p className="dashboard-stat-title">{stat.title}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Error message if loadError is set */}
      {loadError && (
        <div className="dashboard-error-message" style={{ color: '#e53935', margin: '12px 0', textAlign: 'center' }}>
          {loadError}
        </div>
      )}

      {/* Trend Chart */}
      <div className="dashboard-card">
        <h2 className="dashboard-card-title">Water Quality Trends (Last 24 Hours)</h2>
        <div className="dashboard-chart-container">
          {(() => {
            const chartWidth = 1100;
            const chartHeight = 340;
            const chartPadding = { top: 20, right: 20, bottom: 38, left: 42 };
            const innerWidth = chartWidth - chartPadding.left - chartPadding.right;
            const innerHeight = chartHeight - chartPadding.top - chartPadding.bottom;

            const trendSeries = [
              {
                key: 'temperature',
                label: 'Temperature',
                color: '#0ea5e9',
                getValue: (record: (typeof recentReadings)[number]) => record.temp,
                format: (value: number) => `${value.toFixed(1)}°C`,
              },
              {
                key: 'ph',
                label: 'pH Level',
                color: '#22c55e',
                getValue: (record: (typeof recentReadings)[number]) => record.ph,
                format: (value: number) => value.toFixed(2),
              },
              {
                key: 'ammonia',
                label: 'Ammonia',
                color: '#f97316',
                getValue: (record: (typeof recentReadings)[number]) => record.ammonia,
                format: (value: number) => `${value.toFixed(3)} ppm`,
              },
              {
                key: 'turbidity',
                label: 'Turbidity',
                color: '#8b5cf6',
                getValue: (record: (typeof recentReadings)[number]) => record.turbidity,
                format: (value: number) => `${value.toFixed(1)} NTU`,
              },
              {
                key: 'do',
                label: 'Dissolved Oxygen',
                color: '#14b8a6',
                getValue: (record: (typeof recentReadings)[number]) => record.do,
                format: (value: number) => `${value.toFixed(1)} mg/L`,
              },
            ] as const;

            const getAverage = (values: number[]) => {
              if (values.length === 0) return 0;
              return values.reduce((sum, value) => sum + value, 0) / values.length;
            };

            const allValues = trendSeries.flatMap((series) =>
              recentReadings.map((record) => series.getValue(record))
            );
            const rawMin = allValues.length > 0 ? Math.min(...allValues) : 0;
            const rawMax = allValues.length > 0 ? Math.max(...allValues) : 1;
            const axisPadding = Math.max((rawMax - rawMin) * 0.08, 0.5);
            const yMin = Math.max(0, rawMin - axisPadding);
            const yMax = rawMax + axisPadding;
            const yRange = yMax - yMin || 1;

            const trendData = trendSeries.map((series) => {
              const values = recentReadings.map((record) => series.getValue(record));

              const points = values.map((value, index) => {
                const x =
                  chartPadding.left +
                  (values.length === 1 ? innerWidth / 2 : (index / (values.length - 1)) * innerWidth);
                const y = chartPadding.top + innerHeight - ((value - yMin) / yRange) * innerHeight;
                return { x, y };
              });

              const path = points
                .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
                .join(' ');

              return {
                ...series,
                points,
                path,
                average: getAverage(values),
              };
            });

            const yTicks = Array.from({ length: 5 }, (_, index) => yMin + (index / 4) * yRange);
            const xTicks = recentReadings
              .filter((_, index) => index % 3 === 0) // Show every 3rd hour
              .map((record) => {
                const recordIndex = recentReadings.indexOf(record);
                return {
                  label: record.time,
                  x:
                    chartPadding.left +
                    (recentReadings.length === 1
                      ? innerWidth / 2
                      : (recordIndex / (recentReadings.length - 1)) * innerWidth),
                };
              });

            const visibleTrendData = trendData.filter((series) => visibleSeries[series.key]);
            const tooltipWidth = 220;
            const tooltipLineHeight = 20;
            const tooltipHeight = 44 + visibleTrendData.length * tooltipLineHeight;
            const minTooltipX = chartPadding.left + 6;
            const maxTooltipX = chartPadding.left + innerWidth - tooltipWidth - 6;

            return (
              <>
                <div className="dashboard-stats-averages">
                  {trendData.map((series) => (
                    <button
                      key={series.key}
                      type="button"
                      className={`dashboard-avg-stat-card ${visibleSeries[series.key] ? 'active' : 'inactive'}`}
                      style={{ borderColor: visibleSeries[series.key] ? series.color : '#e2e8f0' }}
                      onClick={() =>
                        setVisibleSeries((previous) => ({
                          ...previous,
                          [series.key]: !previous[series.key],
                        }))
                      }
                    >
                      <span className="dashboard-avg-label-row">
                        <span className="dashboard-avg-color-dot" style={{ backgroundColor: series.color }} />
                        <span className="dashboard-avg-label">{series.label}</span>
                      </span>
                      <span className="dashboard-avg-value">{series.format(series.average)}</span>
                      <span className="dashboard-avg-toggle-text">
                        {visibleSeries[series.key] ? 'Visible - click to hide' : 'Hidden - click to show'}
                      </span>
                    </button>
                  ))}
                </div>

                <div className="dashboard-trend-chart-card">
                  <svg
                    className="dashboard-trend-chart-svg"
                    viewBox={`0 0 ${chartWidth} ${chartHeight}`}
                    onMouseLeave={() => setTooltipData(null)}
                  >
                    <defs>
                      {trendData.map((series) => (
                        <linearGradient
                          key={`gradient-${series.key}`}
                          id={`dash-gradient-${series.key}`}
                          x1="0%"
                          y1="0%"
                          x2="0%"
                          y2="100%"
                        >
                          <stop offset="0%" stopColor={series.color} stopOpacity="0.25" />
                          <stop offset="100%" stopColor={series.color} stopOpacity="0.05" />
                        </linearGradient>
                      ))}
                    </defs>

                    {yTicks.map((tick) => {
                      const y = chartPadding.top + innerHeight - ((tick - yMin) / yRange) * innerHeight;
                      const tickLabel = tick >= 10 ? tick.toFixed(1) : tick >= 1 ? tick.toFixed(2) : tick.toFixed(3);

                      return (
                        <g key={tick}>
                          <line
                            className="dashboard-trend-grid-line"
                            x1={chartPadding.left}
                            y1={y}
                            x2={chartPadding.left + innerWidth}
                            y2={y}
                          />
                          <text className="dashboard-trend-axis-label" x={chartPadding.left - 10} y={y + 4} textAnchor="end">
                            {tickLabel}
                          </text>
                        </g>
                      );
                    })}

                    {xTicks.map((tick) => (
                      <text
                        key={tick.label + tick.x}
                        className="dashboard-trend-axis-label"
                        x={tick.x}
                        y={chartPadding.top + innerHeight + 18}
                        textAnchor="middle"
                      >
                        {tick.label}
                      </text>
                    ))}

                    {visibleTrendData.map((series) => (
                      <g key={series.key}>
                        <path
                          className="dashboard-trend-area-fill"
                          d={`${series.path} L ${series.points[series.points.length - 1].x} ${chartPadding.top + innerHeight} L ${series.points[0].x} ${chartPadding.top + innerHeight} Z`}
                          style={{ fill: `url(#dash-gradient-${series.key})` }}
                        />
                        <path className="dashboard-trend-line-path" d={series.path} style={{ stroke: series.color }} />
                      </g>
                    ))}

                    {recentReadings.map((record, index) => {
                      const x =
                        chartPadding.left +
                        (recentReadings.length === 1 ? innerWidth / 2 : (index / (recentReadings.length - 1)) * innerWidth);
                      const segmentWidth = recentReadings.length > 1 ? innerWidth / (recentReadings.length - 1) : innerWidth;
                      const startX = index === 0 ? chartPadding.left : x - segmentWidth / 2;
                      const endX =
                        index === recentReadings.length - 1 ? chartPadding.left + innerWidth : x + segmentWidth / 2;

                      return (
                        <rect
                          key={`hover-area-${index}`}
                          x={startX}
                          y={chartPadding.top}
                          width={endX - startX}
                          height={innerHeight}
                          fill="transparent"
                          style={{ cursor: 'pointer' }}
                          onMouseEnter={() => {
                            setTooltipData({
                              x: x,
                              record,
                            });
                          }}
                        />
                      );
                    })}

                    {tooltipData &&
                      visibleTrendData.length > 0 &&
                      (() => {
                        const preferredRightX = tooltipData.x + 12;
                        const preferredLeftX = tooltipData.x - tooltipWidth - 12;
                        const tooltipX =
                          preferredRightX <= maxTooltipX ? preferredRightX : Math.max(minTooltipX, preferredLeftX);

                        return (
                          <g className="dashboard-trend-tooltip">
                            <line
                              className="dashboard-trend-crosshair"
                              x1={tooltipData.x}
                              y1={chartPadding.top}
                              x2={tooltipData.x}
                              y2={chartPadding.top + innerHeight}
                            />
                            <rect
                              className="dashboard-trend-tooltip-bg"
                              x={tooltipX}
                              y={chartPadding.top + 10}
                              width={tooltipWidth}
                              height={tooltipHeight}
                              rx="8"
                            />
                            <text
                              className="dashboard-trend-tooltip-time"
                              x={tooltipX + tooltipWidth / 2}
                              y={chartPadding.top + 30}
                              textAnchor="middle"
                            >
                              {tooltipData.record.time}
                            </text>
                            {visibleTrendData.map((series, idx) => (
                              <text
                                key={series.key}
                                className="dashboard-trend-tooltip-value"
                                x={tooltipX + 14}
                                y={chartPadding.top + 52 + idx * tooltipLineHeight}
                                style={{ fill: series.color }}
                              >
                                {series.label}: {series.format(series.getValue(tooltipData.record))}
                              </text>
                            ))}
                          </g>
                        );
                      })()}

                    {visibleTrendData.length === 0 && (
                      <text
                        className="dashboard-trend-empty-state"
                        x={chartPadding.left + innerWidth / 2}
                        y={chartPadding.top + innerHeight / 2}
                        textAnchor="middle"
                      >
                        Click a parameter card to show trend data.
                      </text>
                    )}
                  </svg>
                </div>
              </>
            );
          })()}
        </div>
      </div>
    </div>
  );
}