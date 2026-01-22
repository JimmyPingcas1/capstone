import 'package:flutter/material.dart';
import '../widgets/dashboardComponents/dashboardPondStatistics.dart'; 
import '../widgets/dashboardComponents/dashboardAlert.dart';
import '../widgets/dashboardComponents/dashboardPondStatus.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA), // <-- same as ControlScreen
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start, // align text to left
          children: [
            const SizedBox(height: 10),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16), // adjust space
              child: Text(
                "Dashboard",
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue, // built-in blue color
                ),
              ),
            ),
            
            const WaterQualityTrendWidget(),
            const DashboardAlertWidget(),
            const DashboardPondStatusWidget(),
          ],
        ),
      ),
    );
  }
}
