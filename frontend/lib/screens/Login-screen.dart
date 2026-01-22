import 'package:flutter/material.dart';
import '../widgets/loginCustomTextField.dart';
import '../utils/validators.dart';
import '../widgets/customButton.dart';
import 'forgot-password-screen.dart';
import '../layouts/main_layout.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  @override
  void dispose() {
    // Always dispose controllers
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
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
                              onPressed: () {
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
                                  color: Colors.blue, // match your theme
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
                            child: CustomButton(
                              text: "Login",
                              onPressed: () {
                                // Temporary navigation to Dashboard
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => const  MainLayout(),
                                  ),
                                );

                                // If you want to keep validation later, you can still wrap it
                                // if (_formKey.currentState!.validate()) {
                                //   Navigator.push(
                                //     context,
                                //     MaterialPageRoute(
                                //       builder: (context) => const DashboardScreen(),
                                //     ),
                                //   );
                                // }
                              },
                            ),
                          ),


                          SizedBox(height: 20),

                          // Divider with "or"
                          Row(
                            children: [
                              Expanded(child: Divider(thickness: 1)),
                              Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 8.0),
                                child: Text("or", style: TextStyle(color: Colors.grey)),
                              ),
                              Expanded(child: Divider(thickness: 1)),
                            ],
                          ),

                          SizedBox(height: 20),

                          // Login with Google button
                        SizedBox(
                          width: double.infinity,
                          height: 50,
                          child: ElevatedButton.icon(
                            icon: Image.asset(
                              'assets/icons/google-icon.png',
                              height: 24,
                              width: 24,
                            ),
                            label: const Text(
                              "Login with Google",
                              style: TextStyle(color: Colors.black),
                            ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.white,
                              elevation: 0, 
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10),
                              ),
                              side: BorderSide(color: Colors.grey.shade300),
                            ),
                            onPressed: () {
                              // Perform Google login action
                            },
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
                                  onPressed: () {
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
