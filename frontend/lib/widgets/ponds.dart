
import 'package:flutter/material.dart';
import '../utils/api_service.dart';
import 'pondComponents/pondParametersStatus.dart';
import 'pondComponents/pondStatistics.dart';

class Ponds extends StatefulWidget {
  const Ponds({super.key});
  @override
  State<Ponds> createState() => _PondsState();
}

class _PondsState extends State<Ponds> {
  String status = 'Healthy';
  Color statusColor = Colors.green;

  @override
  Widget build(BuildContext context) {
    final String? pondId = ApiService.pondId;
    final String pondName = 'Pond Alpha';
    final String fishType = 'Hito';

    if (pondId == null) {
      return const Center(child: Text('No pond selected for this user.'));
    }

    return SingleChildScrollView(
      child: Container(
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
                      pondName,
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
                          color: Colors.grey,
                          fontWeight: FontWeight.w500,
                        ),
                        children: [
                          const TextSpan(text: 'Fish Type: '),
                          TextSpan(
                            text: fishType,
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
                    color: statusColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    status,
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

            const Divider(),
            const SizedBox(height: 16),

            // Pond Parameters
            PondParametersStatus(
              pondId: pondId,
              onStatusChanged: (newStatus, newColor) {
                if (newStatus != status || newColor != statusColor) {
                  setState(() {
                    status = newStatus;
                    statusColor = newColor;
                  });
                }
              },
            ),
            const SizedBox(height: 8),

            const Divider(),
            const SizedBox(height: 24),
            // Water Quality Trend Chart (function call)
            const PondStatistics(),
          ],
        ),
      ),
    );
  }
}

