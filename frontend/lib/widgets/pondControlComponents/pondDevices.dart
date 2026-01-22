import 'package:flutter/material.dart';

class PondDevices extends StatefulWidget {
  final bool aiEnabled;

  const PondDevices({super.key, required this.aiEnabled});

  @override
  State<PondDevices> createState() => _PondDevicesState();
}

class _PondDevicesState extends State<PondDevices> {
  bool aeratorOn = true;
  bool waterPumpOn = false;
  bool heaterOn = true;

  final Map<String, List<String>> deviceParameters = {
    'Aerator': ['DO', 'Temperature'],
    'Water Pump': ['Ammonia'],
    'Heater': ['Temperature', 'pH'],
  };

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        buildDeviceCard(
          icon: Icons.air,
          name: 'Aerator',
          isOn: aeratorOn,
          onChanged: (v) => setState(() => aeratorOn = v),
          workingOn: deviceParameters['Aerator']!,
        ),
        const SizedBox(height: 12),
        buildDeviceCard(
          icon: Icons.water,
          name: 'Water Pump',
          isOn: waterPumpOn,
          onChanged: (v) => setState(() => waterPumpOn = v),
          workingOn: deviceParameters['Water Pump']!,
        ),
        const SizedBox(height: 12),
        buildDeviceCard(
          icon: Icons.local_fire_department,
          name: 'Heater',
          isOn: heaterOn,
          onChanged: (v) => setState(() => heaterOn = v),
          workingOn: deviceParameters['Heater']!,
        ),
      ],
    );
  }

  Widget buildDeviceCard({
    required IconData icon,
    required String name,
    required bool isOn,
    required ValueChanged<bool> onChanged,
    required List<String> workingOn,
  }) {
    return Container(
      padding: const EdgeInsets.fromLTRB(12, 4, 8, 10),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: Colors.grey.shade300),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(icon, size: 28, color: Colors.blue),
                  const SizedBox(width: 12),
                  Text(
                    name,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              Transform.scale(
                scale: 0.8,
                child: Switch(
                  value: isOn,
                  onChanged: widget.aiEnabled ? null : onChanged, // disables interaction
                  thumbColor: MaterialStateProperty.resolveWith<Color>((states) {
                    Color baseColor = states.contains(MaterialState.selected) ? Colors.white : Colors.blue;
                    return widget.aiEnabled ? baseColor.withOpacity(0.5) : baseColor; // transparent effect
                  }),
                  trackColor: MaterialStateProperty.resolveWith<Color>((states) {
                    Color baseColor = states.contains(MaterialState.selected)
                        ? Colors.blue.withOpacity(0.8)
                        : Colors.white;
                    return widget.aiEnabled ? baseColor.withOpacity(0.5) : baseColor; // transparent effect
                  }),
                  trackOutlineColor: MaterialStateProperty.all(widget.aiEnabled ? Colors.blue.withOpacity(0.5) : Colors.blue),
                  trackOutlineWidth: MaterialStateProperty.all(2),
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
              ),
            ],
          ),

          const SizedBox(height: 4),

          // Current Status
          Text.rich(
            TextSpan(
              text: 'Current Status: ',
              children: [
                TextSpan(
                  text: isOn ? 'ON' : 'OFF',
                  style: TextStyle(
                    color: isOn ? Colors.green : Colors.red,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 2),

          // Working on
          Text(
            'Working on: ${workingOn.join(', ')}',
            style: const TextStyle(
              color: Colors.grey,
              fontSize: 12,
            ),
          ),

          // AI Control Active (only if AI is enabled)
          if (widget.aiEnabled)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Text(
                'AI Control Active',
                style: const TextStyle(
                  color: Colors.blue,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
