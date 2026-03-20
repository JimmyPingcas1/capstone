import 'package:flutter/material.dart';
import 'pondControlComponents/pondAutomationStatus.dart';
import 'pondControlComponents/pondDevices.dart';
import 'package:fishpond/utils/api_service.dart';

class PondControl extends StatefulWidget {
  final int pondId;

  const PondControl({super.key, required this.pondId});

  @override
  State<PondControl> createState() => _PondControlState();
}

class _PondControlState extends State<PondControl> {
  bool aiEnabled = false;
  bool manualMode = true;
  Map<String, bool> deviceStates = {
    "aerator": false,
    "waterpump": false,
    "heater": false,
  };

  String get pondName {
    switch (widget.pondId) {
      case 1:
        return 'Pond Alpha';
      default:
        return 'Unknown Pond';
    }
  }

  @override
  void initState() {
    super.initState();
    print('\n🔵 PondControl initialized for Pond ID: ${widget.pondId}');
    print('   ApiService.userId: ${ApiService.userId}');
    print('   ApiService.pondId: ${ApiService.pondId}');
    _loadInitialState();
  }

  @override
  void dispose() {
    super.dispose();
  }

  /// Load AI mode & device states
  Future<void> _loadInitialState() async {
    print('📥 Loading initial state...');
    try {
      final devices = await ApiService.getDeviceStates();
      final aiData = await ApiService.getAiMode();

      print('   Devices loaded: $devices');
      print('   AI data loaded: $aiData');

      if (!mounted) return;
      setState(() {
        deviceStates = devices;
        aiEnabled = aiData['aiMode'] ?? false;
        manualMode = aiData['manualMode'] ?? true;
      });
      print('✅ Initial state loaded: aiEnabled=$aiEnabled, manualMode=$manualMode\n');
    } catch (e) {
      print('❌ Failed to load initial state: $e\n');
    }
  }

  /// Toggle AI mode via WebSocket
  Future<void> _toggleAiMode(bool value) async {
    print('\n🔄 TOGGLE AI MODE REQUESTED: $value');
    print('   Current aiEnabled state: $aiEnabled');
    print('   User ID: ${ApiService.userId}');
    print('   Pond ID: ${ApiService.pondId}');
    
    try {
      await ApiService.ensureWebSocketConnected(
        onMessage: (message) {
          if (message is Map<String, dynamic>) {
            final type = message['type'];
            if (type == 'ai_mode') {
              print('✅ AI mode response received: ${message['aiMode']}');
            }
          }
        },
        onError: (error) {
          print('❌ WebSocket error: $error');
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Connection error: $error')),
          );
        },
        onDone: () {
          print('🔌 WebSocket connection closed');
        },
      );

      print('📤 Sending toggleAiMode request...');
      final response = await ApiService.toggleAiMode(value);
      print('📥 Toggle response: $response');

      if (!mounted) return;
      setState(() {
        aiEnabled = value;
        manualMode = !value;
      });
      print('✅ UI state updated: aiEnabled=$aiEnabled, manualMode=$manualMode\n');
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('AI ${value ? 'enabled' : 'disabled'} successfully'),
        ),
      );
    } catch (e) {
      print('❌ Failed to toggle AI mode: $e\n');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to update AI control: $e'),
        ),
      );
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
                        onChanged: _toggleAiMode,
                        thumbColor: MaterialStateProperty.resolveWith<Color>((states) {
                          if (states.contains(MaterialState.selected)) return Colors.white;
                          return Colors.blue;
                        }),
                        trackColor: MaterialStateProperty.resolveWith<Color>((states) {
                          if (states.contains(MaterialState.selected))
                            return Colors.blue.withOpacity(0.8);
                          return Colors.transparent;
                        }),
                        trackOutlineColor: MaterialStateProperty.all(Colors.blue),
                        trackOutlineWidth: MaterialStateProperty.all(2),
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 15),

            /// POND ALERTS
            const PondAutomationStatusContent(),
            const SizedBox(height: 30),

            /// POND DEVICES
            PondDevices(
              aiEnabled: aiEnabled,
              manualMode: manualMode,
              initialDevices: deviceStates,
            ),
          ],
        ),
      ),
    );
  }
}
