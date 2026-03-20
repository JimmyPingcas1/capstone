import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'screens/Login_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Empty App',
      debugShowCheckedModeBanner: false,

      theme: ThemeData(
        useMaterial3: true,

        // ✅ WHITE BACKGROUND EVERYWHERE
        scaffoldBackgroundColor: Colors.white,

        // ✅ LIGHT STATUS BAR (time & battery visible)
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          elevation: 0,
          iconTheme: IconThemeData(color: Colors.black),
          titleTextStyle: TextStyle(
            color: Colors.black,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),

        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          background: Colors.white,
        ),
      ),

      home: const LoginScreen(),
    );
  }
}

class EmptyPage extends StatelessWidget {
  const EmptyPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: SafeArea(
        child: Center(
          child: Text("Empty Page"),
        ),
      ),
    );
  }
}
