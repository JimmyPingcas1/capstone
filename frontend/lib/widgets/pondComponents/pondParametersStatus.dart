import 'package:flutter/material.dart';

class PondParametersStatus extends StatelessWidget {
  const PondParametersStatus({super.key});

  final List<Map<String, dynamic>> parameters = const [
    {
      'name': 'pH Level',
      'value': '7.2',
      'unit': '',
      'status': 'Healthy',
      'icon': Icons.bubble_chart_rounded,
    },
    {
      'name': 'Ammonia',
      'value': '0.02',
      'unit': '',
      'status': 'Warning',
      'icon': Icons.science_rounded,
    },
    {
      'name': 'Turbidity',
      'value': '12',
      'unit': '',
      'status': 'Healthy',
      'icon': Icons.grain_rounded,
    },
    {
      'name': 'Temperature',
      'value': '26.5',
      'unit': '°C',
      'status': 'Critical',
      'icon': Icons.thermostat_rounded,
    },
    {
      'name': 'Dissolved Oxygen',
      'value': '8.5',
      'unit': 'mg/L',
      'status': 'Critical',
      'icon': Icons.water_drop_rounded,
    },
  ];

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

  Widget buildParamBox(Map<String, dynamic> param) {
    final Color borderColor = getStatusColor(param['status']);

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        border: Border.all(color: borderColor, width: 2),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Icon(
            param['icon'],
            color: borderColor,
            size: 18,
          ),
          const SizedBox(height: 6),
          Text(
            param['name'],
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
                param['value'],
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: borderColor,
                ),
              ),
              if (param['unit'].isNotEmpty) ...[
                const SizedBox(width: 4),
                Text(
                  param['unit'],
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[700],
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }

  Widget buildStatusLabel(String status, Color color) {
    return Row(
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(
          status,
          style: TextStyle(fontSize: 12, color: color, fontWeight: FontWeight.w600),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final topRow = parameters.sublist(0, 3);
    final bottomRow = parameters.sublist(3);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // HEADER
        Row(
          children: const [
            Icon(Icons.show_chart_rounded, color: Colors.blue),
            SizedBox(width: 6),
            Text(
              'Water Status',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),

        // STATUS LABELS BELOW HEADER
        Row(
          children: [
            buildStatusLabel('Healthy', Colors.green),
            const SizedBox(width: 12),
            buildStatusLabel('Warning', Colors.orange),
            const SizedBox(width: 12),
            buildStatusLabel('Critical', Colors.red),
          ],
        ),
        const SizedBox(height: 12),

        // TOP ROW (3 ITEMS)
        Row(
          children: topRow
              .map(
                (param) => Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: buildParamBox(param),
                  ),
                ),
              )
              .toList(),
        ),
        const SizedBox(height: 12),

        // BOTTOM ROW (2 ITEMS)
        Row(
          children: bottomRow
              .map(
                (param) => Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: buildParamBox(param),
                  ),
                ),
              )
              .toList(),
        ),
      ],
    );
  }
}
