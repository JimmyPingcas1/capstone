import 'package:flutter/material.dart';
import '../screens/Dashboard_screen.dart';
import '../screens/Control_screen.dart';
import '../screens/Pond_screen.dart';
import '../screens/Account_screen.dart';
import '../widgets/header.dart';
import '../widgets/tabs.dart';

class MainLayout extends StatefulWidget {
  const MainLayout({super.key});

  @override
  State<MainLayout> createState() => _MainLayoutState();
}

class _MainLayoutState extends State<MainLayout> {
  int _currentIndex = 0;

  // List of screens for easy access
  final List<Widget> _screens = const [
    DashboardScreen(),
    ControlScreen(),
    PondScreen(),
    AccountScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          const AppHeader(), // Top header

          // Main content for the selected tab
          Expanded(
            child: _screens[_currentIndex],
          ),
        ],
      ),

      // Bottom navigation
      bottomNavigationBar: BottomTabs(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index; // Switch screen
          });
        },
      ),
    );
  }
}
