import 'package:flutter/material.dart';

class NotificationScreen extends StatelessWidget {
  const NotificationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white, // Use white (no color)
        elevation: 1,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () {
            Navigator.pop(context); // Go back to previous screen
          },
        ),
        title: const Text(
          "Notifications",
          style: TextStyle(
            color: Colors.black, // Title in black
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
        actions: const [], // No bell icon
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          ListTile(
            leading: Icon(Icons.notifications, color: Colors.blue),
            title: Text("Your order has been shipped"),
            subtitle: Text("2 hours ago"),
          ),
          Divider(),
          ListTile(
            leading: Icon(Icons.notifications, color: Colors.blue),
            title: Text("New message from Aqua Support"),
            subtitle: Text("5 hours ago"),
          ),
          Divider(),
          ListTile(
            leading: Icon(Icons.notifications, color: Colors.blue),
            title: Text("Reminder: Weekly pond check"),
            subtitle: Text("Yesterday"),
          ),
          Divider(),
          // Add more notifications as needed
        ],
      ),
    );
  }
}
