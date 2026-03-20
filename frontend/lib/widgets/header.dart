import 'package:flutter/material.dart';
import '../screens/notification_screen.dart';
import '../utils/api_auth.dart';
import '../screens/login_screen.dart';

class AppHeader extends StatefulWidget {
  const AppHeader({super.key});

  @override
  State<AppHeader> createState() => _AppHeaderState();
}

class _AppHeaderState extends State<AppHeader> {
  String _accountName = "Account Name";

  @override
  void initState() {
    super.initState();
    _loadUserName();
  }

  Future<void> _loadUserName() async {
    final user = await AuthService.getUserData();
    setState(() {
      _accountName = user != null && user['name'] != null && user['name'].toString().trim().isNotEmpty
          ? user['name']
          : (user != null && user['email'] != null ? user['email'] : "Account Name");
    });
  }

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
              _accountName,
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
                GestureDetector(
                  onTap: () {
                    showDialog(
                      context: context,
                      barrierColor: Colors.black.withOpacity(0.3),
                      builder: (context) {
                        return Dialog(
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(20),
                          ),
                          backgroundColor: Colors.white,
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              crossAxisAlignment: CrossAxisAlignment.center,
                              children: [
                                Text(
                                  'Logout',
                                  style: TextStyle(
                                    color: Colors.redAccent,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 18,
                                  ),
                                ),
                                const SizedBox(height: 12),
                                const Text(
                                  'Are you sure you want to logout?',
                                  style: TextStyle(fontSize: 15),
                                  textAlign: TextAlign.center,
                                ),
                                const SizedBox(height: 24),
                                Row(
                                  children: [
                                    Expanded(
                                      child: TextButton(
                                        style: TextButton.styleFrom(
                                          foregroundColor: Colors.grey.shade700,
                                          textStyle: const TextStyle(fontSize: 16),
                                        ),
                                        onPressed: () {
                                          Navigator.of(context).pop();
                                        },
                                        child: const Text('Cancel'),
                                      ),
                                    ),
                                    Expanded(
                                      child: TextButton(
                                        style: TextButton.styleFrom(
                                          foregroundColor: Colors.blue,
                                          textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                                        ),
                                        onPressed: () async {
                                          Navigator.of(context).pop();
                                          await AuthService.logout();
                                          if (mounted) {
                                              Navigator.of(context).pushAndRemoveUntil(
                                                MaterialPageRoute(builder: (context) => LoginScreen()),
                                              (route) => false,
                                            );
                                          }
                                        },
                                        child: const Text('Confirm'),
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    );
                  },
                  child: const CircleAvatar(
                    radius: 14,
                    backgroundColor: Color(0xFFE0F0FF), // slight backcolor
                    child: Icon(
                      Icons.person,
                      size: 16,
                      color: Colors.blue,
                    ),
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
