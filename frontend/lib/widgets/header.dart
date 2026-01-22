import 'package:flutter/material.dart';
import '../screens/notification_screen.dart';

class AppHeader extends StatelessWidget {
  final String accountName;

  const AppHeader({super.key, this.accountName = "Account Name"});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      bottom: false, // Don't block bottom padding
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: const BoxDecoration(
          border: Border(
            bottom: BorderSide(color: Colors.grey, width: 0.3),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            // Account name
            Text(
              "Madam Aqua Flask",
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),

            // Right side icons
            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.notifications_none, size: 26),
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const NotificationScreen(),
                      ),
                    );
                  },
                ),
                const SizedBox(width: 16),
                const CircleAvatar(
                  radius: 14,
                  backgroundColor: Color(0xFFE0F0FF), // slight backcolor
                  child: Icon(
                    Icons.person,
                    size: 16,
                    color: Colors.blue,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
