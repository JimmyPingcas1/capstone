import 'package:flutter/material.dart';

// Compact Pond Automation Status for farmers
class PondAutomationStatusContent extends StatelessWidget {
  const PondAutomationStatusContent({super.key});

  @override
  Widget build(BuildContext context) {
    final List<Map<String, dynamic>> problems = [
      {
        'problem': 'Low DO: 10 mg/L (Critical)',
        'devices': 'Aerator',
        'status': false, // not fixing
      },
      {
        'problem': 'High Ammonia: 5 mg/L (Warning)',
        'devices': 'Pump, Filter',
        'status': true, // fixing
      },
      {
        'problem': 'Temperature Normal',
        'devices': 'Heater, Sensor',
        'status': true,
      },
    ];

    return Column(
      children: problems
          .map(
            (problem) => CompactStatusCard(
              problemText: problem['problem'],
              devices: problem['devices'],
              isFixing: problem['status'],
            ),
          )
          .toList(),
    );
  }
}

class CompactStatusCard extends StatelessWidget {
  final String problemText;
  final String devices;
  final bool isFixing;

  const CompactStatusCard({
    super.key,
    required this.problemText,
    required this.devices,
    required this.isFixing,
  });

  Color getStatusColor() => isFixing ? Colors.green : Colors.red;

  String getStatusText() => isFixing ? 'Fixing' : 'Not Fixing';

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.symmetric(vertical: 6),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: getStatusColor(),
          width: 1.2, // 0.5 border as requested
        ),
        boxShadow: const [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 4,
            offset: Offset(2, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Status row
          Row(
            children: [
              const Text(
                'Status: ',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: getStatusColor(),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  getStatusText(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 9,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.3,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 6),

          // Problem text
          Text(
            'Problem: $problemText',
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),

          const SizedBox(height: 2),

          // Devices needed
          RichText(
            text: TextSpan(
              children: [
                const TextSpan(
                  text: 'Device Needed: ',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey,
                    fontWeight: FontWeight.w400,
                  ),
                ),
                TextSpan(
                  text: devices,
                  style: const TextStyle(
                    fontSize: 12,
                    color: Colors.black,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
