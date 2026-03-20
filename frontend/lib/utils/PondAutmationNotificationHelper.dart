class AutomationHelper {
  static List<Map<String, dynamic>> getTriggeredDevices(
      Map<String, double> sensorData) {
    List<Map<String, dynamic>> alerts = [];

    // LOW DO → Turn ON Aerator
    if ((sensorData['do'] ?? 0) < 5.0) {
      alerts.add({
        'problem': 'Low DO: ${sensorData['do']} mg/L (Critical)',
        'devices': 'Aerator',
        'status': false, // needs action
      });
    }

    // HIGH AMMONIA → Turn ON Pump & Filter
    if ((sensorData['ammonia'] ?? 0) > 2.0) {
      alerts.add({
        'problem':
            'High Ammonia: ${sensorData['ammonia']} mg/L (Warning)',
        'devices': 'Pump, Filter',
        'status': false,
      });
    }

    // LOW TEMPERATURE → Turn ON Heater
    if ((sensorData['temperature'] ?? 0) < 24.0) {
      alerts.add({
        'problem': 'Low Temperature: ${sensorData['temperature']}°C',
        'devices': 'Heater',
        'status': false,
      });
    }

    // HIGH TEMPERATURE → Turn ON Pump
    if ((sensorData['temperature'] ?? 0) > 32.0) {
      alerts.add({
        'problem': 'High Temperature: ${sensorData['temperature']}°C',
        'devices': 'Pump',
        'status': false,
      });
    }

    return alerts;
  }
}
