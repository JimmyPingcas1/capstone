import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';
import 'api_auth.dart';
import 'dart:async';

class ApiService {
  static const String baseUrl = 'http://10.166.95.24:5000';
  static const String wsBaseUrl = 'ws://10.166.95.24:5000';
  
  // User/Pond context for API calls
  static String? userId;
  static String? pondId;
  
  // WebSocket connection
  static WebSocketChannel? _wsChannel;
  static StreamSubscription? _wsSubscription;
  
  // Store pending query responses
  static final Map<String, Completer<dynamic>> _pendingQueries = {};
  static int _requestId = 0;

  // Sensor Data WebSocket
  static WebSocketChannel? _sensorDataChannel;
  static StreamSubscription? _sensorDataSubscription;

  /// Set user and pond context
  static void setUserPondContext(String uid, String pid) {
    userId = uid;
    pondId = pid;
  }

  /// Get auth headers with token
  static Future<Map<String, String>> _getHeaders() async {
    final headers = <String, String>{'Content-Type': 'application/json'};
    final token = await AuthService.getToken();
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  /// Connect to WebSocket
  static Future<void> connectWebSocket({
    required Function(dynamic message) onMessage,
    required Function(dynamic error) onError,
    required Function() onDone,
  }) async {
    if (userId == null || pondId == null) {
      final error = 'User and pond context not set (userId=$userId, pondId=$pondId)';
      print('❌ $error');
      throw Exception(error);
    }

    try {
      if (_wsChannel != null) {
        print('ℹ️  WebSocket already connected');
        return;
      }

      final wsUrl = '$wsBaseUrl/ws/ai-control/$userId/$pondId';
      print('\n🔌 Connecting WebSocket to: $wsUrl');
      _wsChannel = WebSocketChannel.connect(Uri.parse(wsUrl));

      // Listen for incoming messages
      _wsSubscription = _wsChannel!.stream.listen(
        (message) {
          print('📥 WebSocket message received: $message');
          final data = json.decode(message);
          
          // Check if this is a response to a pending query
          if (data['type'] == 'state_response' && data.containsKey('requestId')) {
            final requestId = data['requestId'].toString();
            if (_pendingQueries.containsKey(requestId)) {
              _pendingQueries[requestId]!.complete(data);
              _pendingQueries.remove(requestId);
            }
          }
          
          onMessage(data);
        },
        onError: (error) {
          print('❌ WebSocket error: $error');
          onError(error);
        },
        onDone: () {
          print('🔌 WebSocket disconnected');
          _wsChannel = null;
          _wsSubscription = null;
          onDone();
        },
      );

      print('✅ WebSocket connected successfully');
    } catch (e) {
      print('❌ Failed to connect WebSocket: $e');
      _wsChannel = null;
      _wsSubscription = null;
      onError(e);
    }
  }

  /// Disconnect WebSocket
  static Future<void> disconnectWebSocket() async {
    await _wsSubscription?.cancel();
    _wsSubscription = null;
    await _wsChannel?.sink.close();
    _wsChannel = null;
    print('WebSocket disconnected');
  }

  static bool get isWebSocketConnected => _wsChannel != null;

  static Future<void> ensureWebSocketConnected({
    required Function(dynamic message) onMessage,
    required Function(dynamic error) onError,
    required Function() onDone,
  }) async {
    if (isWebSocketConnected) return;
    await connectWebSocket(
      onMessage: onMessage,
      onError: onError,
      onDone: onDone,
    );
  }

  /// Query state via WebSocket
  static Future<Map<String, dynamic>> _queryState() async {
    if (_wsChannel == null) {
      throw Exception('WebSocket not connected');
    }

    final requestId = (++_requestId).toString();
    final completer = Completer<Map<String, dynamic>>();
    _pendingQueries[requestId] = completer;

    final message = {
      'type': 'query',
      'query': 'state',
      'requestId': requestId,
    };

    _wsChannel!.sink.add(json.encode(message));
    
    // Add timeout using the timeout method
    return completer.future.timeout(
      Duration(seconds: 5),
      onTimeout: () {
        if (_pendingQueries.containsKey(requestId)) {
          _pendingQueries.remove(requestId);
        }
        throw Exception('State query timeout');
      },
    );
  }

  /// Send device control command via WebSocket
  static Future<void> controlDeviceWebSocket(String device, bool state) async {
    if (_wsChannel == null) {
      throw Exception('WebSocket not connected');
    }

    final message = {
      'device': device,
      'action': state ? 'ON' : 'OFF',
    };

    _wsChannel!.sink.add(json.encode(message));
    print('Device control sent: $device -> ${state ? 'ON' : 'OFF'}');
  }

  /// Send AI mode toggle via WebSocket
  static Future<void> toggleAiModeWebSocket(bool enabled) async {
    if (_wsChannel == null) {
      throw Exception('WebSocket not connected');
    }

    final message = {'aiMode': enabled};
    final jsonMessage = json.encode(message);
    print('📤 Sending AI mode via WebSocket: $jsonMessage');
    _wsChannel!.sink.add(jsonMessage);
    print('✅ AI mode message sent to WebSocket: aiMode=$enabled');
  }

  /// Manual device control via HTTP (primary method) with WebSocket fallback
  static Future<Map<String, dynamic>> controlDevice(String device, bool state) async {
    if (userId == null || pondId == null) {
      throw Exception('User and pond context not set');
    }

    final action = state ? 'ON' : 'OFF';
    
    // Primary: Use HTTP for reliable device control with confirmation
    try {
      final uri = Uri.parse(
        '$baseUrl/api/v1/ManualDeviceControl?user_id=$userId&pond_id=$pondId&device=$device&action=$action'
      );
      
      print('📡 Device control via HTTP: $device → $action');
      final response = await http.post(
        uri,
        headers: await _getHeaders(),
      );

      if (response.statusCode == 200) {
        print('✅ HTTP device control succeeded');
        return json.decode(response.body);
      } else {
        print('❌ HTTP device control failed: ${response.statusCode}');
        throw Exception('HTTP failed: ${response.body}');
      }
    } catch (httpError) {
      print('⚠️  HTTP device control error: $httpError');
      
      // Fallback: Try WebSocket if HTTP fails
      if (_wsChannel != null) {
        try {
          print('🔄 Falling back to WebSocket...');
          await controlDeviceWebSocket(device, state);
          return {
            'status': 'queued_ws',
            'device': device,
            'action': action,
            'method': 'websocket_fallback'
          };
        } catch (wsError) {
          print('❌ WebSocket fallback also failed: $wsError');
          throw Exception('Both HTTP and WebSocket failed: $httpError | $wsError');
        }
      }
      
      rethrow;
    }
  }

  /// Toggle AI mode via WebSocket (preferred method)
  static Future<Map<String, dynamic>> toggleAiMode(bool enabled) async {
    print('\n🎯 toggleAiMode called with: $enabled');
    print('   WebSocket connected: ${_wsChannel != null}');
    print('   User: $userId | Pond: $pondId');
    
    if (_wsChannel != null) {
      // Use WebSocket if available
      try {
        print('   Using WebSocket...');
        await toggleAiModeWebSocket(enabled);
        return {
          'status': 'queued',
          'aiMode': enabled,
          'method': 'websocket'
        };
      } catch (e) {
        print('❌ WebSocket error, falling back to HTTP: $e');
      }
    }

    // Fallback to HTTP only if WebSocket not connected
    if (userId == null || pondId == null) {
      throw Exception('User and pond context not set');
    }

    print('   Using HTTP fallback...');
    final uri = Uri.parse('$baseUrl/api/v1/AIControl?user_id=$userId&pond_id=$pondId');
    print('   POST: $uri');
    print('   Body: {"aiMode": $enabled}');
    
    final response = await http.post(
      uri,
      headers: await _getHeaders(),
      body: json.encode({'aiMode': enabled}),
    );

    print('   Response status: ${response.statusCode}');
    print('   Response body: ${response.body}');
    
    if (response.statusCode == 200) {
      final result = json.decode(response.body);
      result['method'] = 'http';
      return result;
    } else {
      throw Exception('Failed to update AI mode: ${response.body}');
    }
  }

  /// Fetch AI mode via WebSocket (preferred method)
  static Future<Map<String, dynamic>> getAiMode() async {
    if (_wsChannel != null) {
      // Use WebSocket if available
      try {
        final response = await _queryState();
        return {
          'aiMode': response['aiMode'] ?? false,
          'devices': response['devices'] ?? {'aerator': false, 'waterpump': false, 'heater': false},
        };
      } catch (e) {
        print('WebSocket error, falling back to HTTP: $e');
      }
    }

    // Fallback to HTTP only if WebSocket not connected
    if (userId == null || pondId == null) {
      throw Exception('User and pond context not set');
    }

    final response = await http.get(
      Uri.parse('$baseUrl/api/v1/AIControl?user_id=$userId&pond_id=$pondId'),
      headers: await _getHeaders(),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return {
        'aiMode': data['aiMode'] ?? false,
        'devices': data['devices'] ?? {'aerator': false, 'waterpump': false, 'heater': false},
      };
    } else {
      throw Exception('Failed to fetch AI mode');
    }
  }

  /// Get device states via WebSocket (preferred method)
  static Future<Map<String, bool>> getDeviceStates() async {
    if (_wsChannel != null) {
      // Use WebSocket if available
      try {
        final response = await _queryState();
        final devices = response['devices'] ?? {'aerator': false, 'waterpump': false, 'heater': false};
        return {
          "aerator": devices['aerator'] ?? false,
          "waterpump": devices['waterpump'] ?? false,
          "heater": devices['heater'] ?? false,
        };
      } catch (e) {
        print('WebSocket error, falling back to HTTP: $e');
      }
    }

    // Fallback to HTTP only if WebSocket not connected
    if (userId == null || pondId == null) {
      throw Exception('User and pond context not set');
    }

    final response = await http.get(
      Uri.parse('$baseUrl/api/v1/devices?user_id=$userId&pond_id=$pondId'),
      headers: await _getHeaders(),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return {
        "aerator": data['aerator'] ?? false,
        "waterpump": data['waterpump'] ?? false,
        "heater": data['heater'] ?? false,
      };
    } else {
      throw Exception('Failed to fetch device states');
    }
  }

  // =============================
  // Sensor Data WebSocket
  // =============================
  static Future<void> connectSensorDataWebSocket({
    required String pondId,
    required Function(dynamic data) onData,
    required Function(dynamic error) onError,
    required Function() onDone,
  }) async {
    if (_sensorDataChannel != null) {
      // If the channel exists but is closed, clean up and allow reconnect
      try {
        if (_sensorDataSubscription != null) {
          await _sensorDataSubscription!.cancel();
          _sensorDataSubscription = null;
        }
        await _sensorDataChannel?.sink.close();
      } catch (_) {}
      _sensorDataChannel = null;
    }
    final token = await AuthService.getToken();
    if (token == null) {
      print('❌ No JWT token found. User not authenticated.');
      onError('No JWT token found. Please log in.');
      return;
    }
    final wsUrl = '$wsBaseUrl/ws/sensor-data/$pondId?token=$token';
    print('\n🔌 Connecting Sensor Data WebSocket to: $wsUrl');
    _sensorDataChannel = WebSocketChannel.connect(Uri.parse(wsUrl));
    _sensorDataSubscription = _sensorDataChannel!.stream.listen(
      (message) {
        print('📥 Sensor Data WS message: $message');
        try {
          final data = json.decode(message);
          onData(data);
        } catch (e) {
          print('❌ Failed to decode sensor data WS message: $e');
        }
      },
      onError: (error) async {
        print('❌ Sensor Data WS error: $error');
        await _sensorDataSubscription?.cancel();
        _sensorDataSubscription = null;
        await _sensorDataChannel?.sink.close();
        _sensorDataChannel = null;
        onError(error);
      },
      onDone: () async {
        print('🔌 Sensor Data WS disconnected');
        await _sensorDataSubscription?.cancel();
        _sensorDataSubscription = null;
        await _sensorDataChannel?.sink.close();
        _sensorDataChannel = null;
        onDone();
      },
      cancelOnError: true,
    );
    print('✅ Sensor Data WebSocket connected');
  }

  static Future<void> disconnectSensorDataWebSocket() async {
    try {
      await _sensorDataSubscription?.cancel();
    } catch (_) {}
    _sensorDataSubscription = null;
    try {
      await _sensorDataChannel?.sink.close();
    } catch (_) {}
    _sensorDataChannel = null;
    print('Sensor Data WebSocket disconnected');
  }

  static bool get isSensorDataWebSocketConnected => _sensorDataChannel != null;

  static Future<void> ensureSensorDataWebSocketConnected({
    required String pondId,
    required Function(dynamic data) onData,
    required Function(dynamic error) onError,
    required Function() onDone,
  }) async {
    if (isSensorDataWebSocketConnected) return;
    await connectSensorDataWebSocket(
      pondId: pondId,
      onData: onData,
      onError: onError,
      onDone: onDone,
    );
  }
}

