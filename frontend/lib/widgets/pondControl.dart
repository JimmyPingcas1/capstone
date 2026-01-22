import 'package:flutter/material.dart';
import 'pondControlComponents/pondParameters.dart';
import 'pondControlComponents/pondAutomationStatus.dart';
import 'pondControlComponents/pondDevices.dart';

class PondControl extends StatefulWidget {
  final int pondId;

  const PondControl({super.key, required this.pondId});

  @override
  State<PondControl> createState() => _PondControlState();
}

class _PondControlState extends State<PondControl> {
  bool aiEnabled = false;

  String get pondName {
    switch (widget.pondId) {
      case 1:
        return 'Pond Alpha';
      case 2:
        return 'Pond Beta';
      default:
        return 'Unknown Pond';
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Container(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 28),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            /// HEADER
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  pondName,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Row(
                  children: [
                    const Icon(
                      Icons.smart_toy_outlined,
                      color: Colors.blue,
                      size: 22,
                    ),
                    const SizedBox(width: 6),
                    const Text(
                      'AI Control',
                      style: TextStyle(fontWeight: FontWeight.w500),
                    ),
                    const SizedBox(width: 10),
                    Transform.scale(
                      scale: 0.8,
                      child: Switch(
                        value: aiEnabled,
                        onChanged: (value) {
                          setState(() {
                            aiEnabled = value;
                          });
                        },
                        thumbColor:
                            MaterialStateProperty.resolveWith<Color>((states) {
                          if (states.contains(MaterialState.selected)) {
                            return Colors.white;
                          }
                          return Colors.blue;
                        }),
                        trackColor:
                            MaterialStateProperty.resolveWith<Color>((states) {
                          if (states.contains(MaterialState.selected)) {
                            return Colors.blue.withOpacity(0.8);
                          }
                          return Colors.transparent;
                        }),
                        trackOutlineColor:
                            MaterialStateProperty.all(Colors.blue),
                        trackOutlineWidth:
                            MaterialStateProperty.all(2),
                        materialTapTargetSize:
                            MaterialTapTargetSize.shrinkWrap,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 15),

            // /// POND PARAMETERS
            // PondParameters(
            //   temperature: 26.5,
            //   ph: 7.8,
            //   dissolvedO2: 4.2,
            //   ammonia: 0.8,
            //   turbidity: 6.5,
            // ),

            // const SizedBox(height: 30),

            /// POND ALERTS HEADER
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: const [
                Icon(
                  Icons.warning_amber_rounded,
                  size: 25,
                  color: Colors.orange,
                ),
                SizedBox(width: 4),
                Text(
                  'Pond Alerts',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),

            /// ALERT CARDS
            const PondAutomationStatusContent(),

            const SizedBox(height: 3),
            const Divider(thickness: 1, color: Colors.black12),
            const SizedBox(height: 30),

            /// POND DEVICES HEADER
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: const [
                Icon(
                  Icons.devices_rounded,
                  size: 25,
                  color: Colors.blue,
                ),
                SizedBox(width: 6),
                Text(
                  'Pond Control Devices',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),

            /// DEVICE CARDS
            PondDevices(aiEnabled: aiEnabled),
          ],
        ),
      ),
    );
  }
}
