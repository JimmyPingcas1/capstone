import 'package:flutter/material.dart';
import 'package:fishpond/utils/api_service.dart';

class PondDevices extends StatefulWidget {
  final bool aiEnabled;
  final bool manualMode;
  final Map<String, bool> initialDevices; // ✅ added parameter

  const PondDevices({
    super.key,
    this.aiEnabled = false,
    this.manualMode = true,
    this.initialDevices = const {
      "aerator": false,
      "waterpump": false,
      "heater": false,
    },
  });

  @override
  State<PondDevices> createState() => _PondDevicesState();
}

class _PondDevicesState extends State<PondDevices> {
  // Spam protection: track toggle history and lock state
  Map<String, List<DateTime>> _toggleHistory = {};
  Map<String, DateTime?> _toggleLockUntil = {};
  late bool aeratorOn;
  late bool waterPumpOn;
  late bool heaterOn;
  bool _wsConnected = false;

  // ...existing code...

  final Map<String, List<String>> deviceParameters = {
    'Aerator': ['DO', 'Temperature'],
    'Water Pump': ['Ammonia'],
    'Heater': ['Temperature', 'pH'],
  };

  @override
  void initState() {
    super.initState();

    // Set initial device states from parent widget
    aeratorOn = widget.initialDevices['aerator'] ?? false;
    waterPumpOn = widget.initialDevices['waterpump'] ?? false;
    heaterOn = widget.initialDevices['heater'] ?? false;

    // Initialize toggle history and lock maps
    _toggleHistory = {
      'aerator': [],
      'waterpump': [],
      'heater': [],
    };
    _toggleLockUntil = {
      'aerator': null,
      'waterpump': null,
      'heater': null,
    };

    // Fetch device states from backend in case initialDevices is outdated
    _loadDeviceStates();
    // Connect to WebSocket
    _connectWebSocket();
  }

  @override
  void dispose() {
    ApiService.disconnectWebSocket();
    super.dispose();
  }

  /// Connect to WebSocket
  Future<void> _connectWebSocket() async {
    try {
      await ApiService.ensureWebSocketConnected(
        onMessage: (message) {
          _handleWebSocketMessage(message);
        },
        onError: (error) {
          print('WebSocket error: $error');
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Connection error: $error')),
          );
        },
        onDone: () {
          setState(() => _wsConnected = false);
        },
      );
      
      if (!mounted) return;
      setState(() => _wsConnected = ApiService.isWebSocketConnected);
    } catch (e) {
      print('Failed to connect WebSocket: $e');
    }
  }

  /// Handle WebSocket messages
  void _handleWebSocketMessage(dynamic message) {
    if (!mounted) return;
    
    if (message is Map<String, dynamic>) {
      final type = message['type'];
      
      if (type == 'device_control') {
        // Device control response
        final device = message['device'];
        final action = message['action'];
        print('Device control response: $device -> $action');
      } else if (type == 'ai_mode') {
        // AI mode response
        final aiMode = message['aiMode'];
        print('AI mode response: $aiMode');
      }
    }
  }

  /// Fetch device state from API
  Future<void> _loadDeviceStates() async {
    try {
      final devices = await ApiService.getDeviceStates();
      if (!mounted) return;
      setState(() {
        aeratorOn = devices['aerator'] ?? false;
        waterPumpOn = devices['waterpump'] ?? false;
        heaterOn = devices['heater'] ?? false;
      });

      // 🔹 Print initial fetched device states
      print('Initial device states loaded: aerator=${aeratorOn ? 'ON' : 'OFF'}, '
          'waterpump=${waterPumpOn ? 'ON' : 'OFF'}, heater=${heaterOn ? 'ON' : 'OFF'}');
    } catch (e) {
      print('Failed to fetch device states: $e');
    }
  }

  /// Toggle a device via HTTP (with WebSocket fallback)
  void toggleDevice(String device, bool state) {
    final now = DateTime.now();

    // Only allow known devices
    final allowedDevices = ["aerator", "waterpump", "heater"];
    if (!allowedDevices.contains(device)) {
      print("Unknown device key: $device");
      return;
    }

    // Ensure the device exists in history and lock maps
    _toggleHistory[device] ??= [];
    _toggleLockUntil[device] ??= null;

    // --- SPAM PROTECTION: Check if device is locked ---
    final lockUntil = _toggleLockUntil[device];
    if (lockUntil != null && now.isBefore(lockUntil)) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Too many toggles! $device locked for ${lockUntil.difference(now).inSeconds} seconds.'),
          duration: const Duration(seconds: 2),
        ),
      );
      return;
    }

    // --- Record toggle timestamp ---
    _toggleHistory[device]!.add(now);

    // Keep only last 2 seconds
    _toggleHistory[device] = _toggleHistory[device]!
        .where((t) => now.difference(t).inMilliseconds < 2000)
        .toList();

    // --- Lock device if toggled >4 times in 2 seconds ---
    if (_toggleHistory[device]!.length > 3) {
      _toggleLockUntil[device] = now.add(const Duration(seconds: 5));
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Too many toggles! Device locked for 5 seconds.'),
          duration: Duration(seconds: 2),
        ),
      );
      return;
    }

    // --- Update UI ---
    setState(() {
      if (device == "aerator") aeratorOn = state;
      if (device == "waterpump") waterPumpOn = state;
      if (device == "heater") heaterOn = state;
    });

    // --- Send command ---
    ApiService.controlDevice(device, state).then((response) {
      print('✅ Device $device turned ${state ? 'ON' : 'OFF'}: $response');
      Future.delayed(const Duration(milliseconds: 300), _refreshDeviceStates);
    }).catchError((error) {
      print('❌ Failed to control device $device: $error');
      setState(() {
        if (device == "aerator") aeratorOn = !state;
        if (device == "waterpump") waterPumpOn = !state;
        if (device == "heater") heaterOn = !state;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to control $device: $error'),
          duration: const Duration(seconds: 3),
        ),
      );
    });
  }
  
  /// Refresh device states from database
  Future<void> _refreshDeviceStates() async {
    try {
      print('🔄 Refreshing device states from database...');
      final devices = await ApiService.getDeviceStates();
      if (!mounted) return;
      
      setState(() {
        aeratorOn = devices['aerator'] ?? false;
        waterPumpOn = devices['waterpump'] ?? false;
        heaterOn = devices['heater'] ?? false;
      });
      print('✅ Device states refreshed: aerator=$aeratorOn, waterpump=$waterPumpOn, heater=$heaterOn');
    } catch (e) {
      print('⚠️  Failed to refresh device states: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    // Aerator is always manual (AI never controls it)
    final aeratorEnabled = true;
    
    // Heater & Waterpump are only manual when AI is OFF
    final aiDevicesEnabled = widget.manualMode && !widget.aiEnabled;

    return Column(
      children: [
        buildDeviceCard(
          icon: Icons.air,
          name: 'Aerator',
          isOn: aeratorOn,
          onChanged: (v) => toggleDevice("aerator", v),
          workingOn: deviceParameters['Aerator']!,
          enabled: aeratorEnabled,
          isAiControlled: false, // Always manual
        ),
        const SizedBox(height: 12),
        buildDeviceCard(
          icon: Icons.water,
          name: 'Water Pump',
          isOn: waterPumpOn,
          onChanged: (v) => toggleDevice("waterpump", v),
          workingOn: deviceParameters['Water Pump']!,
          enabled: aiDevicesEnabled,
          isAiControlled: widget.aiEnabled, // AI controls when enabled
        ),
        const SizedBox(height: 12),
        buildDeviceCard(
          icon: Icons.local_fire_department,
          name: 'Heater',
          isOn: heaterOn,
          onChanged: (v) => toggleDevice("heater", v),
          workingOn: deviceParameters['Heater']!,
          enabled: aiDevicesEnabled,
          isAiControlled: widget.aiEnabled, // AI controls when enabled
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
    required bool enabled,
    required bool isAiControlled,
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
          Row(
            children: [
              Icon(icon, size: 28, color: Colors.blue),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
              Transform.scale(
                scale: 0.8,
                child: Switch(
                  value: isOn,
                  onChanged: enabled ? onChanged : null,
                  thumbColor: MaterialStateProperty.resolveWith<Color>(
                    (states) {
                      final base = states.contains(MaterialState.selected) ? Colors.white : Colors.blue;
                      return enabled ? base : base.withOpacity(0.5);
                    },
                  ),
                  trackColor: MaterialStateProperty.resolveWith<Color>(
                    (states) {
                      final base = states.contains(MaterialState.selected) ? Colors.blue.withOpacity(0.8) : Colors.white;
                      return enabled ? base : base.withOpacity(0.5);
                    },
                  ),
                  trackOutlineColor: MaterialStateProperty.all(enabled ? Colors.blue : Colors.blue.withOpacity(0.5)),
                  trackOutlineWidth: MaterialStateProperty.all(2),
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          isAiControlled
              ? const Text.rich(
                  TextSpan(
                    text: 'Current Status: ',
                    style: TextStyle(fontWeight: FontWeight.normal),
                    children: [
                      TextSpan(
                        text: 'AI CONTROLLED',
                        style: TextStyle(
                          color: Colors.blue,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                )
              : Text.rich(
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
          Text(
            'Working on: ${workingOn.join(', ')}',
            style: const TextStyle(color: Colors.grey, fontSize: 12),
          ),
        ],
      ),
    );
  }
}
