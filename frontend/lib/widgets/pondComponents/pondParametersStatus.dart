import 'package:flutter/material.dart';
import '../../utils/api_service.dart';


typedef StatusChangedCallback = void Function(String status, Color color);

class PondParametersStatus extends StatefulWidget {
  final String pondId;
  final StatusChangedCallback? onStatusChanged;

  const PondParametersStatus({super.key, required this.pondId, this.onStatusChanged});

  @override
  State<PondParametersStatus> createState() => _PondParametersStatusState();
}

class _PondParametersStatusState extends State<PondParametersStatus> {
  Map<String, dynamic>? sensorData;
  bool _wsConnected = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _connectWebSocket();
  }

  @override
  void dispose() {
    ApiService.disconnectSensorDataWebSocket();
    super.dispose();
  }

  void _connectWebSocket() async {
    final String pondId = widget.pondId;

    await ApiService.connectSensorDataWebSocket(
      pondId: pondId,
      onData: (data) {
        setState(() {
          sensorData = data;
          _wsConnected = true;
          _error = null;
        });
      },
      onError: (err) {
        setState(() {
          _wsConnected = false;
          _error = err.toString();
        });
      },
      onDone: () {
        setState(() {
          _wsConnected = false;
        });
      },
    );
  }

  Color getStatusColor(String status) {
    switch (status) {
      case 'Healthy':
        return Colors.green;
      case 'Warning':
        return Colors.orange;
      case 'Critical':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String getStatus(String param, num value) {
    switch (param) {
      case 'ph':
        if (value < 6.5 || value > 8.5) return 'Critical';
        return 'Healthy';

      case 'ammonia':
        if (value > 0.5) return 'Critical';
        if (value > 0.1) return 'Warning';
        return 'Healthy';

      case 'turbidity':
        if (value > 50) return 'Critical';
        if (value > 20) return 'Warning';
        return 'Healthy';

      case 'temperature':
        if (value < 20 || value > 32) return 'Critical';
        if (value < 22 || value > 30) return 'Warning';
        return 'Healthy';

      case 'do':
        if (value < 3) return 'Critical';
        if (value < 5) return 'Warning';
        return 'Healthy';

      default:
        return 'Healthy';
    }
  }

  Widget buildParamBox({
    required String name,
    required String value,
    required String unit,
    required String status,
    required IconData icon,
  }) {

    final Color borderColor = getStatusColor(status);

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        border: Border.all(color: borderColor, width: 2),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [

          Icon(icon, color: borderColor, size: 18),

          const SizedBox(height: 6),

          Text(
            name,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w800,
            ),
            textAlign: TextAlign.center,
          ),

          const SizedBox(height: 4),

          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [

              Text(
                value,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: borderColor,
                ),
              ),

              if (unit.isNotEmpty) ...[
                const SizedBox(width: 4),
                Text(unit, style: TextStyle(fontSize: 12, color: Colors.grey[700]))
              ]
            ],
          )
        ],
      ),
    );
  }

  String getOverallStatus(Map<String, dynamic> data) {
    // Compute the most severe status among all parameters
    final statuses = [
      getStatus('ph', data['ph']),
      getStatus('ammonia', data['ammonia']),
      getStatus('turbidity', data['turbidity']),
      getStatus('temperature', data['temperature']),
      getStatus('do', data['predicted_dissolved_oxygen']),
    ];
    if (statuses.contains('Critical')) return 'Danger';
    if (statuses.contains('Warning')) return 'Warning';
    return 'Healthy';
  }

  Color getOverallColor(String status) {
    switch (status) {
      case 'Danger':
        return Colors.red;
      case 'Warning':
        return Colors.orange;
      default:
        return Colors.green;
    }
  }

  @override
  Widget build(BuildContext context) {

    if (_error != null) {
      return Center(child: Text("WebSocket error: $_error"));
    }

    if (!_wsConnected || sensorData == null) {
      return const Center(child: CircularProgressIndicator());
    }

    // Calculate last update string (e.g., '2 min ago')
    String? lastUpdateStr;
    if (sensorData!.containsKey('timestamp')) {
      try {
        DateTime dt = DateTime.parse(sensorData!['timestamp']).toLocal();
        final now = DateTime.now();
        final diff = now.difference(dt);
        if (diff.inSeconds < 60) {
          lastUpdateStr = '${diff.inSeconds} sec ago';
        } else if (diff.inMinutes < 60) {
          lastUpdateStr = '${diff.inMinutes} min ago';
        } else if (diff.inHours < 24) {
          lastUpdateStr = '${diff.inHours} hr ago';
        } else {
          lastUpdateStr = '${diff.inDays} day${diff.inDays > 1 ? 's' : ''} ago';
        }
      } catch (_) {
        lastUpdateStr = null;
      }
    }

    Widget statusCircle(Color color) => Container(
      width: 10,
      height: 10,
      margin: const EdgeInsets.only(right: 3),
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
      ),
    );

    // Row with status circles and labels, and last update
    Widget statusRow = Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            statusCircle(Colors.green),
            Text('Safe', style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 13)),
            const SizedBox(width: 14),
            statusCircle(Colors.orange),
            Text('Warning', style: TextStyle(color: Colors.orange, fontWeight: FontWeight.bold, fontSize: 13)),
            const SizedBox(width: 14),
            statusCircle(Colors.red),
            Text('Danger', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 13)),
          ],
        ),
        Expanded(
          child: Align(
            alignment: Alignment.centerRight,
            child: lastUpdateStr != null
                ? Text('Last update $lastUpdateStr', style: const TextStyle(fontSize: 10, color: Colors.grey))
                : const SizedBox.shrink(),
          ),
        ),
      ],
    );

    // Notify parent of status change
    if (sensorData != null && widget.onStatusChanged != null) {
      final overallStatus = getOverallStatus(sensorData!);
      final color = getOverallColor(overallStatus);
      WidgetsBinding.instance.addPostFrameCallback((_) {
        widget.onStatusChanged!(overallStatus, color);
      });
    }

    // Layout: status row above, then 3 above, 2 below
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 10.0),
          child: statusRow,
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            Expanded(
              child: buildParamBox(
                name: "pH Level",
                value: sensorData!["ph"].toString(),
                unit: "",
                status: getStatus("ph", sensorData!["ph"]),
                icon: Icons.bubble_chart,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: buildParamBox(
                name: "Ammonia",
                value: sensorData!["ammonia"].toString(),
                unit: "",
                status: getStatus("ammonia", sensorData!["ammonia"]),
                icon: Icons.science,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: buildParamBox(
                name: "Turbidity",
                value: sensorData!["turbidity"].toString(),
                unit: "",
                status: getStatus("turbidity", sensorData!["turbidity"]),
                icon: Icons.grain,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            Expanded(
              child: buildParamBox(
                name: "Temperature",
                value: sensorData!["temperature"].toString(),
                unit: "°C",
                status: getStatus("temperature", sensorData!["temperature"]),
                icon: Icons.thermostat,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: buildParamBox(
                name: "Dissolved Oxygen",
                value: sensorData!["predicted_dissolved_oxygen"].toString(),
                unit: "mg/L",
                status: getStatus("do", sensorData!["predicted_dissolved_oxygen"]),
                icon: Icons.water_drop,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
