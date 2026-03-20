import React from 'react';

interface ModalComponentDevicePredictionProps {
  visibleModalRecords: any[];
  getDeviceProblem: (record: any) => string;
  getDeviceSummary: (record: any) => string;
}

const ModalComponentDevicePrediction: React.FC<ModalComponentDevicePredictionProps> = ({
  visibleModalRecords,
  getDeviceProblem,
}) => (
  <div className="device-prediction-tab">
    <table className="device-prediction-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Detected Issue</th>
          <th>Device Prediction</th>
        </tr>
      </thead>
      <tbody>
        {visibleModalRecords.map((record: any) => (
          <tr key={record.id}>
            <td>{record.date} {record.time}</td>
            <td>{getDeviceProblem(record)}</td>
            <td>
              Pump: <span style={{ color: (record.waterPumpOn === true || (record.final_devices && record.final_devices.water_pump)) ? 'green' : 'red', fontWeight: 'bold' }}>
                {record.waterPumpOn === true || (record.final_devices && record.final_devices.water_pump) ? 'ON' : 'OFF'}
              </span>
              {' | '}Heater: <span style={{ color: (record.heaterOn === true || (record.final_devices && record.final_devices.heater)) ? 'green' : 'red', fontWeight: 'bold' }}>
                {record.heaterOn === true || (record.final_devices && record.final_devices.heater) ? 'ON' : 'OFF'}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default ModalComponentDevicePrediction;
