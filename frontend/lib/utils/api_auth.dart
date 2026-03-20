import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  static const String baseUrl = 'http://10.166.95.24:5000';
  
  // In-memory storage (session-based)
  static String? _token;
  static Map<String, dynamic>? _userData;

  /// Login with email and password
  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final token = data['token'];
        final user = data['user'];

        // Store in memory
        _token = token;
        _userData = user;

        return {'success': true, 'token': token, 'user': user};
      } else {
        final error = json.decode(response.body);
        return {
          'success': false,
          'error': error['detail'] ?? 'Login failed'
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Connection error: $e'
      };
    }
  }

  /// Register new account
  static Future<Map<String, dynamic>> register(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final token = data['token'];
        final user = data['user'];

        // Store in memory
        _token = token;
        _userData = user;

        return {'success': true, 'token': token, 'user': user};
      } else {
        final error = json.decode(response.body);
        return {
          'success': false,
          'error': error['detail'] ?? 'Registration failed'
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Connection error: $e'
      };
    }
  }

  /// Get stored auth token
  static Future<String?> getToken() async {
    return _token;
  }

  /// Get stored user data
  static Future<Map<String, dynamic>?> getUserData() async {
    return _userData;
  }

  /// Check if user is logged in
  static Future<bool> isLoggedIn() async {
    return _token != null;
  }

  /// Logout - clear stored data
  static Future<void> logout() async {
    _token = null;
    _userData = null;
  }
}

