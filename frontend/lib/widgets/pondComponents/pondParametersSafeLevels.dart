import 'package:flutter/material.dart';

class ParametersSafeLevel extends StatelessWidget {
  const ParametersSafeLevel({super.key});

  final List<Map<String, dynamic>> parameters = const [
    {
      'name': 'Temperature',
      'icon': Icons.thermostat_rounded,
      'iconColor': Colors.orange,
      'value': '26 – 30 °C',
    },
    {
      'name': 'Dissolved Oxygen',
      'icon': Icons.water_drop_rounded,
      'iconColor': Colors.blue,
      'value': '≥ 5 mg/L',
    },
    {
      'name': 'Ammonia',
      'icon': Icons.science_rounded,
      'iconColor': Colors.red,
      'value': '≤ 0.02 mg/L',
    },
    {
      'name': 'pH Level',
      'icon': Icons.bubble_chart_rounded,
      'iconColor': Colors.green,
      'value': '6.5 – 8.5',
    },
    {
      'name': 'Turbidity',
      'icon': Icons.grain_rounded,
      'iconColor': Colors.teal,
      'value': '≤ 25 NTU',
    },
  ];

  Widget buildParamRow(Map<String, dynamic> param) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          // ICON WITHOUT BACKGROUND
          Icon(
            param['icon'],
            color: param['iconColor'],
            size: 18,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              param['name'],
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: Colors.black,
              ),
            ),
          ),
          Text(
            param['value'],
            style: const TextStyle(
              fontSize: 12,
              color: Colors.black,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        /// HEADER
        Row(
          children: [
            const Icon(
              Icons.security_rounded,
              color: Colors.blue,
              size: 24,
            ),
            const SizedBox(width: 6),
            const Text(
              'Pond Safe Level',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.black,
              ),
            ),
            const Spacer(),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Text(
                'Edit Pond',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.blue,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        const Divider(),

        /// PARAMETERS LIST
        ...parameters.map(buildParamRow).toList(),
      ],
    );
  }
}
