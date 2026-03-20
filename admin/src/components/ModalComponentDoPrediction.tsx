import React from 'react';

interface ModalComponentDoPredictionProps {
  visibleModalRecords: any[];
  getStatus: (record: any) => string;
}

const ModalComponentDoPrediction: React.FC<ModalComponentDoPredictionProps> = ({ visibleModalRecords, getStatus }) => (
  <div className="do-prediction-tab">
    <table className="do-prediction-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Predicted Do</th>
          <th>Aerator</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {visibleModalRecords.map((record: any) => {
          const aeratorOn = record.aerator === true || record.aerator === 1 || record.aeratorOn === true;
          return (
            <tr key={record.id}>
              <td>{record.date} {record.time}</td>
              <td>
                {typeof record.predicted_dissolved_oxygen === 'number' && !isNaN(record.predicted_dissolved_oxygen)
                  ? record.predicted_dissolved_oxygen.toFixed(2)
                  : 'N/A'}
              </td>
              <td>
                <span style={{ color: aeratorOn ? 'green' : 'red', fontWeight: 'bold' }}>
                  {aeratorOn ? 'ON' : 'OFF'}
                </span>
              </td>
              <td>{getStatus(record)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  </div>
);

export default ModalComponentDoPrediction;
