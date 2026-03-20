
import 'package:flutter/material.dart';
import '../utils/api_auth.dart';


class AccountScreen extends StatefulWidget {
  const AccountScreen({super.key});

  @override
  State<AccountScreen> createState() => _AccountScreenState();
}

class _AccountScreenState extends State<AccountScreen> {
  String? userName;

  @override
  void initState() {
    super.initState();
    _loadUserName();
  }

  Future<void> _loadUserName() async {
    final userData = await AuthService.getUserData();
    setState(() {
      userName = userData != null && userData['name'] != null ? userData['name'] as String : 'User';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Profile Icon
              CircleAvatar(
                radius: 48,
                backgroundColor: Colors.blue[200],
                child: Icon(Icons.person, size: 56, color: Colors.white),
              ),
              const SizedBox(height: 16),
              // Name
              Text(
                userName ?? '',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey[900],
                ),
              ),
              const SizedBox(height: 6),
              // Location
              Text(
                'Malaybalay City',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Password Update Form Widget
class _PasswordUpdateForm extends StatefulWidget {
  @override
  State<_PasswordUpdateForm> createState() => _PasswordUpdateFormState();
}

class _PasswordUpdateFormState extends State<_PasswordUpdateForm> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _oldPasswordController = TextEditingController();
  final TextEditingController _newPasswordController = TextEditingController();
  bool _isLoading = false;
  String? _errorMessage;
  String? _successMessage;

  @override
  void dispose() {
    _oldPasswordController.dispose();
    _newPasswordController.dispose();
    super.dispose();
  }

  void _submit() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _successMessage = null;
    });
    // Simulate password update delay
    await Future.delayed(const Duration(seconds: 2));
    // TODO: Replace with actual password update logic
    if (_oldPasswordController.text == "oldpassword" && _newPasswordController.text.length >= 6) {
      setState(() {
        _successMessage = "Password updated successfully!";
      });
    } else {
      setState(() {
        _errorMessage = "Incorrect old password or new password too short.";
      });
    }
    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextFormField(
            controller: _oldPasswordController,
            obscureText: true,
            decoration: InputDecoration(
              labelText: 'Old Password',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your old password';
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _newPasswordController,
            obscureText: true,
            decoration: InputDecoration(
              labelText: 'New Password',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter a new password';
              }
              if (value.length < 6) {
                return 'Password must be at least 6 characters';
              }
              return null;
            },
          ),
          const SizedBox(height: 20),
          if (_errorMessage != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 8.0),
              child: Text(
                _errorMessage!,
                style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
              ),
            ),
          if (_successMessage != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 8.0),
              child: Text(
                _successMessage!,
                style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold),
              ),
            ),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isLoading
                  ? null
                  : () {
                      if (_formKey.currentState!.validate()) {
                        _submit();
                      }
                    },
              style: ElevatedButton.styleFrom(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              child: _isLoading
                  ? SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : Text('Update Password', style: TextStyle(fontSize: 16)),
            ),
          ),
        ],
      ),
    );
  }
}

class PondCard extends StatelessWidget {
  final String pondName;
  final String location;
  final String status;

  const PondCard({
    super.key,
    required this.pondName,
    required this.location,
    required this.status,
  });

  Color getStatusColor() {
    switch (status) {
      case 'Healthy':
        return Colors.green[400]!;
      case 'Warning':
        return Colors.orange[400]!;
      case 'Danger':
        return Colors.red[400]!;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: getStatusColor(),
          child: Icon(Icons.water, color: Colors.white),
        ),
        title: Text(
          pondName,
          style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey[900]),
        ),
        subtitle: Text(location),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: getStatusColor().withOpacity(0.15),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            status,
            style: TextStyle(
              color: getStatusColor(),
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        onTap: () {},
      ),
    );
  }
}
