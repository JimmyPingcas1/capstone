import React from 'react';

interface ModalComponentLogsProps {
  records: any[];
}

const ModalComponentLogs: React.FC<ModalComponentLogsProps> = ({ records }) => (
  <div className="logs-tab">
    <table className="logs-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Temperature</th>
          <th>pH</th>
          <th>Ammonia</th>
          <th>Turbidity</th>
          <th>Predicted Do</th>
          <th>Warnings</th>
        </tr>
      </thead>
      <tbody>
        {records.map((r) => (
          <tr key={r.id}>
            <td>{r.date} {r.time}</td>
            <td>{r.temperature}</td>
            <td>{r.ph}</td>
            <td>{r.ammonia}</td>
            <td>{r.turbidity}</td>
            <td>
              {typeof r.predicted_dissolved_oxygen === 'number' && !isNaN(r.predicted_dissolved_oxygen)
                ? r.predicted_dissolved_oxygen.toFixed(2)
                : 'N/A'}
            </td>
            <td>{(r.validation_warnings && r.validation_warnings.length > 0) ? r.validation_warnings.join(', ') : 'None'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default ModalComponentLogs;
