import 'package:flutter/material.dart';
import 'pondComponents/pondParametersStatus.dart';
import 'pondComponents/pondParametersSafeLevels.dart';
import 'pondComponents/pondStatistics.dart'; // optional
import 'pondComponents/pondStatistics.dart'; // <-- WaterQualityTrendWidget

class Ponds extends StatelessWidget {
  const Ponds({super.key});

  final List<Map<String, dynamic>> pondList = const [
    {
      'name': 'Pond Alpha',
      'status': 'Healthy',
      'statusColor': Colors.green,
      'fishType': 'Tilapia',
    },
    {
      'name': 'Pond Beta',
      'status': 'Warning',
      'statusColor': Colors.orange,
      'fishType': 'Catfish',
    },
    {
      'name': 'Pond Gamma',
      'status': 'Critical',
      'statusColor': Colors.red,
      'fishType': 'Bangus',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        children: pondList.map((pond) {
          return Container(
            margin: const EdgeInsets.only(bottom: 24),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 8,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Pond Name and Status
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          pond['name'],
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        RichText(
                          text: TextSpan(
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.grey[700],
                              fontWeight: FontWeight.w500,
                            ),
                            children: [
                              const TextSpan(text: 'Fish Type: '),
                              TextSpan(
                                text: pond['fishType'],
                                style: const TextStyle(
                                  color: Colors.black,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: pond['statusColor'],
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        pond['status'],
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                // Safe Levels
                const ParametersSafeLevel(),

                const Divider(),
                const SizedBox(height: 16),

                // Pond Parameters
                const PondParametersStatus(),
                const SizedBox(height: 8),

                const Divider(),
                const SizedBox(height: 24),
                
                // Water Quality Trend Chart (function call)
                const PondStatistics(),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
}

