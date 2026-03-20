import React from 'react';

interface ModalComponentStatisticsProps {
  records: any[];
  visibleSeries: Record<string, boolean>;
  getAverage: (values: number[]) => number;
}

const METRIC_LABELS: Record<string, string> = {
  temperature: 'Temperature (°C)',
  ph: 'pH',
  ammonia: 'Ammonia (ppm)',
  turbidity: 'Turbidity (NTU)',
  do: 'Predicted DO (mg/L)',
};

const ModalComponentStatistics: React.FC<ModalComponentStatisticsProps> = ({
  records,
  visibleSeries,
  getAverage,
}) => {





















  const statsFor = (key: string) => {
    const values = records
      .map((record) =>
        key === 'do'
          ? Number(record.predicted_dissolved_oxygen ?? record.do)
          : Number(record[key])
      )
      .filter((value) => !Number.isNaN(value));

    if (values.length === 0) {
      return { avg: '-', min: '-', max: '-' };
    }

    const avg = getAverage(values);
    const min = Math.min(...values);
    const max = Math.max(...values);

    return { avg: avg.toFixed(2), min: min.toFixed(2), max: max.toFixed(2) };
  };



  return (
    <div>
      <table className="statistics-table">
        <thead>
          <tr>
            <th>Metric</th>
            <th>Average</th>
            <th>Min</th>
            <th>Max</th>
          </tr>
        </thead>
        <tbody>
          {Object.keys(METRIC_LABELS)
            .filter((key) => visibleSeries[key])
            .map((key) => {
              const stats = statsFor(key);
              return (
                <tr key={key}>
                  <td>{METRIC_LABELS[key]}</td>
                  <td>{stats.avg}</td>
                  <td>{stats.min}</td>
                  <td>{stats.max}</td>
                </tr>
              );
            })}
        </tbody>
      </table>
    </div>
  );
};

export default ModalComponentStatistics;


