import 'package:flutter/material.dart';
import '../../utils/api_service.dart';

class DashboardPondStatusWidget extends StatelessWidget {
  const DashboardPondStatusWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final String? pondId = ApiService.pondId;

    final pondName = 'Pond Alpha';
    final status = 'Safe';
    final updated = 'Just now';
    final statusColor = Colors.green;
    final progress = 0.9;

    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [

            /// HEADER
            const Text(
              'Pond Status',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),

            Text(
              pondId != null ? 'Monitoring 1 pond' : 'No pond selected',
              style: const TextStyle(
                fontSize: 14,
                color: Colors.grey,
              ),
            ),

            const SizedBox(height: 16),

            if (pondId != null)
              _pondItem(
                pondName: pondName,
                status: status,
                updated: updated,
                statusColor: statusColor,
                progress: progress,
              ),
          ],
        ),
      ),
    );
  }

  Widget _pondItem({
    required String pondName,
    required String status,
    required String updated,
    required Color statusColor,
    required double progress,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: statusColor, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [

          /// POND NAME + STATUS
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                pondName,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                ),
              ),

              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  status, // SAFE
                  style: TextStyle(
                    fontSize: 12,
                    color: statusColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          /// CENTER MESSAGE
          Center(
            child: Text(
              'No problem occurred yet',
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),

          const SizedBox(height: 12),

          /// UPDATED TEXT
          Text(
            'Updated $updated',
            style: const TextStyle(
              fontSize: 11,
              color: Colors.grey,
            ),
          ),
        ],
      ),
    );
  }
}
