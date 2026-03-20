import 'package:flutter/material.dart';
import '../widgets/ponds.dart'; // Make sure this path is correct

class PondScreen extends StatelessWidget {
  const PondScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [

            // HEADER TEXT + BUTTON ROW (same horizontal padding as ControlScreen)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Ponds',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 8), // Spacing below header

            // PONDS LIST
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Ponds(),
            ),

            const SizedBox(height: 15), // Bottom spacing
          ],
        ),
      ),
    );
  }
}
