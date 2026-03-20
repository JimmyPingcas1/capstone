import 'package:flutter/material.dart';
import '../widgets/loginCustomTextField.dart';
import '../utils/validators.dart';
import '../widgets/customButton.dart';
import 'forgot-password-screen.dart';
import '../layouts/main_layout.dart';
import '../utils/api_auth.dart';
import '../utils/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void dispose() {
    // Always dispose controllers
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final result = await AuthService.login(
        emailController.text.trim(),
        passwordController.text,
      );

      if (mounted) {
        if (result['success']) {
          // Set user and pond context for API calls
          final user = result['user'];
          final userId = user['id'] as String;
          
          // Using pond_id from database: Pond Beta
          ApiService.setUserPondContext(userId, "69a39f9cbb28dfc1b9a307fb");
          
          print('User context set: userId=$userId, pondId=69a39f9cbb28dfc1b9a307fb');
          
          // Navigate to dashboard on successful login
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => const MainLayout(),
            ),
          );
        } else {
          setState(() {
            _errorMessage = result['error'] ?? 'Login failed';
            _isLoading = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = 'An error occurred: $e';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                 // Logo takes 1/3 of the screen
                  Flexible(
                    flex: 1,
                    child: Center(
                      child: Image.asset(
                        'assets/images/fishpond-logo.png', // path to your logo
                        fit: BoxFit.contain,
                        height: 120, // adjust height as needed
                      ),
                    ),
                  ),

                // Login form takes 2/3 of the screen
                Flexible(
                  flex: 3,
                  child: SingleChildScrollView(
                    child: Padding(
                      padding: const EdgeInsets.only(top: 20.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Login to your Account",
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          SizedBox(height: 20),

                          // Error message display
                          if (_errorMessage != null)
                            Container(
                              padding: EdgeInsets.all(12),
                              margin: EdgeInsets.only(bottom: 16),
                              decoration: BoxDecoration(
                                color: Colors.red.shade50,
                                border: Border.all(color: Colors.red.shade300),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                _errorMessage!,
                                style: TextStyle(
                                  color: Colors.red.shade700,
                                  fontSize: 14,
                                ),
                              ),
                            ),

                          // Email field
                          CustomTextField(
                            label: "Email",
                            icon: Icons.email,
                            controller: emailController,
                            validator: Validators.email,
                          ),

                          SizedBox(height: 20),

                          // Password field
                          CustomTextField(
                            label: "Password",
                            icon: Icons.lock_outline,
                            controller: passwordController,
                            validator: Validators.password,
                            isPassword: true,
                          ),

                          // Forgot password button aligned to the right
                          Align(
                            alignment: Alignment.centerRight,
                            child: TextButton(
                              onPressed: _isLoading ? null : () {
                                // Navigate to forgot password screen
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => ForgotPasswordScreen(),
                                  ),
                                );
                              },
                              child: Text(
                                "Forgot Password?",
                                style: TextStyle(
                                  color: _isLoading ? Colors.grey : Colors.blue,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ),

                          SizedBox(height: 20),

                          // Login button
                          SizedBox(
                            width: double.infinity,
                            height: 50,
                            child: ElevatedButton(
                              onPressed: _isLoading ? null : _handleLogin,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: _isLoading ? Colors.grey : Colors.blue,
                                disabledBackgroundColor: Colors.grey,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(10),
                                ),
                              ),
                              child: _isLoading
                                  ? SizedBox(
                                      height: 24,
                                      width: 24,
                                      child: CircularProgressIndicator(
                                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                        strokeWidth: 2,
                                      ),
                                    )
                                  : Text(
                                      "Login",
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                            ),
                          ),

                          SizedBox(height: 25),
                          // "Don't have an account?" section
                          Center(
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              mainAxisSize: MainAxisSize.min, // Row shrinks to its content
                              children: [
                                const Text(
                                  "Don't have an account?",
                                  style: TextStyle(fontSize: 16),
                                ),
                                const SizedBox(width: 4), // small space
                                TextButton(
                                  onPressed: _isLoading ? null : () {
                                    // Navigate to your Register/Sign-up screen
                                  },
                                  style: TextButton.styleFrom(
                                    padding: EdgeInsets.zero, // remove extra padding
                                    minimumSize: Size(0, 0),
                                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                  ),
                                  child: const Text(
                                    "Create Account",
                                    style: TextStyle(
                                      color: Colors.blue,
                                      fontSize: 15,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          )
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
