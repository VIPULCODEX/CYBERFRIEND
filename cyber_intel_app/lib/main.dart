import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'api_service.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ApiService()),
      ],
      child: const QuantXApp(),
    ),
  );
}

class QuantXApp extends StatelessWidget {
  const QuantXApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'QuantX AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0B0F14),
        primaryColor: const Color(0xFFFFC857),
        hintColor: const Color(0xFF4CAF50),
        
        // Define Cyberpunk Typography
        textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme).copyWith(
          displayLarge: GoogleFonts.orbitron(
            color: const Color(0xFFFFC857),
            fontWeight: FontWeight.bold,
            letterSpacing: 4,
          ),
          titleMedium: GoogleFonts.rajdhani(
            color: const Color(0xFF4CAF50),
            fontWeight: FontWeight.bold,
            letterSpacing: 2,
          ),
        ),
      ),
      home: const ChatScreen(),
    );
  }
}

// Placeholder for ChatScreen — will implement in next file
class ChatScreen extends StatelessWidget {
  const ChatScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('🛡 QUANTX AI', style: Theme.of(context).textTheme.displayLarge?.copyWith(fontSize: 18)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
      body: const Center(child: Text('Initializing tactical interface...')),
    );
  }
}
