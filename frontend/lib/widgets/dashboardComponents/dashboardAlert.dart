import 'package:flutter/material.dart';

// Alerts data
final List<AlertItem> alerts = [
  AlertItem(
    type: AlertType.ph,
    message: 'pH level slightly elevated',
    pond: 'Pond Alpha',
    timeAgo: '5 min ago',
  ),
  AlertItem(
    type: AlertType.maintenance,
    message: 'Scheduled maintenance reminder',
    pond: 'Pond Beta',
    timeAgo: '1 hour ago',
  ),
  AlertItem(
    type: AlertType.oxygen,
    message: 'Oxygen level below threshold',
    pond: 'Pond Delta',
    timeAgo: '2 hours ago',
  ),
];

class DashboardAlertWidget extends StatelessWidget {
  const DashboardAlertWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
       padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14), // match PondControl
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08), // subtle shadow like PondControl
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Recent Alerts',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                TextButton(
                  onPressed: () {},
                  child: const Text(
                    'View all',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.blue,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
            Text('${alerts.length} active notifications',
                style: const TextStyle(fontSize: 14, color: Colors.grey)),
            const SizedBox(height: 10),
            // Alert cards
            Column(
              children: alerts.map((alert) => AlertCard(alert: alert)).toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class AlertCard extends StatelessWidget {
  final AlertItem alert;
  const AlertCard({super.key, required this.alert});

  @override
  Widget build(BuildContext context) {
    Color bgColor;
    Color iconColor;
    Color borderColor;
    Widget iconWidget;

    switch (alert.type) {
      case AlertType.ph:
        bgColor = Colors.orange.withOpacity(0.15);
        iconColor = Colors.orange.shade800;
        borderColor = Colors.orange.shade200;
        iconWidget = Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            color: Colors.orange.shade100,
            shape: BoxShape.circle,
            border: Border.all(color: iconColor, width: 2),
          ),
          child: Center(
            child: Text(
              '!',
              style: TextStyle(color: iconColor, fontWeight: FontWeight.bold),
            ),
          ),
        );
        break;
      case AlertType.oxygen:
        bgColor = Colors.red.withOpacity(0.15);
        iconColor = Colors.red.shade800;
        borderColor = Colors.red.shade200;
        iconWidget = Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            color: Colors.red.shade100,
            shape: BoxShape.circle,
            border: Border.all(color: iconColor, width: 2),
          ),
          child: Icon(Icons.warning_amber, color: iconColor, size: 16),
        );
        break;
      case AlertType.maintenance:
        bgColor = Colors.blue.withOpacity(0.15);
        iconColor = Colors.blue.shade800;
        borderColor = Colors.blue.shade200;
        iconWidget = Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            color: Colors.blue.shade100,
            shape: BoxShape.circle,
            border: Border.all(color: iconColor, width: 2),
          ),
          child: Icon(Icons.info, color: iconColor, size: 16),
        );
        break;
      default:
        bgColor = Colors.grey.withOpacity(0.2);
        iconColor = Colors.grey.shade700;
        borderColor = Colors.grey.shade400;
        iconWidget = Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            color: Colors.grey.shade200,
            shape: BoxShape.circle,
            border: Border.all(color: iconColor, width: 2),
          ),
          child: Icon(Icons.notifications, color: iconColor, size: 16),
        );
    }

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 6),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(14), // match PondControl
        border: Border.all(color: borderColor, width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08), // subtle shadow like PondControl
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          iconWidget,
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  alert.message,
                  style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: iconColor),
                ),
                const SizedBox(height: 4),
                Text(
                  '${alert.pond} • ${alert.timeAgo}',
                  style: const TextStyle(fontSize: 11, color: Colors.grey),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class AlertItem {
  final AlertType type;
  final String message;
  final String pond;
  final String timeAgo;

  const AlertItem(
      {required this.type,
      required this.message,
      required this.pond,
      required this.timeAgo});
}

enum AlertType { ph, oxygen, maintenance, other }
