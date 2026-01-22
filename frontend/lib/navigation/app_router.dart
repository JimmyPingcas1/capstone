import 'package:flutter/material.dart';
import '../screens/dashboard_screen.dart';
import '../screens/control_screen.dart';
import '../screens/pond_screen.dart';
import '../screens/account_screen.dart';

class AppRouter {
  static Widget getScreen(int index) {
    switch (index) {
      case 0:
        return const DashboardScreen();
      case 1:
        return const ControlScreen();
      case 2:
        return const PondScreen();
      case 3:
        return const AccountScreen();
      default:
        return const DashboardScreen();
    }
  }
}
