import 'package:flutter/material.dart';

class PondParameters extends StatelessWidget {
  final double temperature;
  final double ph;
  final double dissolvedO2;
  final double ammonia;
  final double turbidity;

  const PondParameters({
    super.key,
    required this.temperature,
    required this.ph,
    required this.dissolvedO2,
    required this.ammonia,
    required this.turbidity,
  });

  Color getBorderColor(String param, double value) {
    switch (param) {
      case 'temp':
        if (value < 20 || value > 30) return Colors.red;
        if (value < 25 || value > 27) return Colors.orange;
        return Colors.green;
      case 'ph':
        if (value < 6.5 || value > 9) return Colors.red;
        if (value < 7 || value > 8.5) return Colors.orange;
        return Colors.green;
      case 'do':
        if (value < 3) return Colors.red;
        if (value < 5) return Colors.orange;
        return Colors.blue; // blue for DO
      case 'ammonia':
        if (value > 2) return Colors.red;
        if (value > 1) return Colors.orange;
        return Colors.yellow;
      case 'turbidity':
        if (value > 10) return Colors.red;
        if (value > 5) return Colors.orange;
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  Widget parameterCard(IconData icon, String name, double value, String key) {
    final borderColor = getBorderColor(key, value);

    return Expanded(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 4),
        padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 4),
        decoration: BoxDecoration(
          color: Colors.white, // no background color
          border: Border.all(color: borderColor, width: 1.5),
          borderRadius: BorderRadius.circular(10),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 6,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: borderColor, size: 22), // icon reflects status
            const SizedBox(height: 2),
            FittedBox(
              fit: BoxFit.scaleDown,
              child: Text(
                name,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: Colors.black, // label stays black
                ),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(height: 2),
            FittedBox(
              fit: BoxFit.scaleDown,
              child: Text(
                value.toStringAsFixed(1),
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                  color: borderColor, // value reflects status
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          parameterCard(Icons.thermostat_rounded, 'Temperature', temperature, 'temp'),
          parameterCard(Icons.bubble_chart_rounded, 'pH Level', ph, 'ph'),
          parameterCard(Icons.water_drop_rounded, 'Dissolved O₂', dissolvedO2, 'do'),
          parameterCard(Icons.science_rounded, 'Ammonia', ammonia, 'ammonia'),
          parameterCard(Icons.grain_rounded, 'Turbidity', turbidity, 'turbidity'),
        ],
      ),
    );
  }
}
