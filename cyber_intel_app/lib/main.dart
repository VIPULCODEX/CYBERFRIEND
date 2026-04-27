import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'api_service.dart';
import 'widgets/neural_background.dart';
import 'widgets/threat_monitor.dart';

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

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();

  void _sendMessage(BuildContext context) {
    if (_controller.text.trim().isEmpty) return;
    
    final api = Provider.of<ApiService>(context, listen: false);
    api.sendMessage(_controller.text.trim());
    _controller.clear();
    
    // Unfocus the keyboard
    FocusScope.of(context).unfocus();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('🛡 QUANTX AI', style: Theme.of(context).textTheme.displayLarge?.copyWith(fontSize: 18)),
        backgroundColor: const Color(0xFF0B0F14).withOpacity(0.9),
        elevation: 0,
        centerTitle: true,
        // The hamburger icon will automatically appear when we add a Drawer!
      ),
      drawer: Drawer(
        backgroundColor: const Color(0xFF0B0F14),
        child: Consumer<ApiService>(
          builder: (context, apiService, _) {
            return Column(
              children: [
                DrawerHeader(
                  decoration: const BoxDecoration(
                    border: Border(bottom: BorderSide(color: Color(0xFF4CAF50), width: 2)),
                  ),
                  child: SizedBox(
                    width: double.infinity,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('SYSTEM STATUS', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.white70)),
                        const SizedBox(height: 8),
                        Text('ONLINE', style: Theme.of(context).textTheme.displayLarge?.copyWith(fontSize: 24, color: const Color(0xFF4CAF50))),
                      ],
                    ),
                  ),
                ),
                const ListTile(
                  leading: Icon(Icons.psychology, color: Color(0xFF4CAF50)),
                  title: Text('Smart Intelligence: ACTIVE', style: TextStyle(color: Colors.white, fontSize: 13)),
                  subtitle: Text('Auto-switching RAG & LLM', style: TextStyle(color: Colors.white54, fontSize: 11)),
                ),
                ListTile(
                  leading: const Icon(Icons.history, color: Color(0xFFFFC857)),
                  title: const Text('Mission Log History', style: TextStyle(color: Colors.white)),
                  subtitle: const Text('Local Persistence: Enabled', style: TextStyle(color: Colors.white54, fontSize: 11)),
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Chat history is automatically saved to local storage.')),
                    );
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.delete_sweep, color: Color(0xFFFF5252)),
                  title: const Text('Clear Tactical Interface', style: TextStyle(color: Colors.white)),
                  onTap: () {
                    apiService.clearChat(context);
                    Navigator.pop(context);
                  },
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                  child: ThreatMonitor(threatLevel: apiService.threatLevel),
                ),
                ListTile(
                  leading: const Icon(Icons.cloud_done, color: Color(0xFF2196F3)),
                  title: const Text('Cloud: HF 16GB Deployed', style: TextStyle(color: Colors.white)),
                  onTap: () {},
                ),
                const Spacer(),
                const Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Text(
                    'v1.1.0 — OPTIMIZED ROUTING',
                    style: TextStyle(color: Colors.white38, fontSize: 12),
                  ),
                ),
              ],
            );
          }
        ),
      ),
      body: NeuralBackground(
        child: Consumer<ApiService>(
          builder: (context, apiService, _) {
            return Column(
              children: [
                Expanded(
                  child: apiService.messages.isEmpty
                      ? Center(
                          child: Text(
                            'Tactical Interface Ready\nAwaiting Command...',
                            textAlign: TextAlign.center,
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: const Color(0xFF4CAF50).withOpacity(0.8),
                              shadows: [
                                Shadow(color: const Color(0xFF4CAF50).withOpacity(0.6), blurRadius: 10),
                              ]
                            ),
                          ),
                        )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        reverse: false, // In a real app we might want to reverse or auto-scroll
                        itemCount: apiService.messages.length,
                        itemBuilder: (context, index) {
                          final msg = apiService.messages[index];
                          final isUser = msg.role == 'user';
                          
                          Color borderColor = isUser ? const Color(0xFF4CAF50) : const Color(0xFFFFC857);
                          if (msg.type == 'alert') borderColor = Colors.redAccent;
                          
                          return Align(
                            alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                            child: TweenAnimationBuilder<double>(
                              tween: Tween(begin: 0.0, end: 1.0),
                              duration: const Duration(milliseconds: 300),
                              curve: Curves.easeOutCubic,
                              builder: (context, value, child) {
                                return Transform.translate(
                                  offset: Offset(isUser ? 20 * (1 - value) : -20 * (1 - value), 0),
                                  child: Opacity(
                                    opacity: value,
                                    child: child,
                                  ),
                                );
                              },
                              child: Container(
                                margin: const EdgeInsets.only(bottom: 12),
                                padding: const EdgeInsets.all(12),
                                constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF161F28).withOpacity(0.85),
                                  border: Border.all(color: borderColor.withOpacity(0.4), width: 1),
                                  boxShadow: [
                                    BoxShadow(
                                      color: borderColor.withOpacity(0.15),
                                      blurRadius: 8,
                                      spreadRadius: 1,
                                    )
                                  ],
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  msg.content,
                                  style: const TextStyle(
                                    color: Colors.white70,
                                    fontSize: 14,
                                    height: 1.4,
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
              ),
              
              if (apiService.isLoading)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 8.0),
                  child: SpinKitThreeBounce(
                    color: Color(0xFFFFC857),
                    size: 20.0,
                  ),
                ),
                
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                color: const Color(0xFF161F28),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _controller,
                        style: const TextStyle(color: Colors.white),
                        decoration: InputDecoration(
                          hintText: 'Enter command parameters...',
                          hintStyle: TextStyle(color: Colors.grey.shade600),
                          filled: true,
                          fillColor: const Color(0xFF0B0F14),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(4),
                            borderSide: const BorderSide(color: Color(0xFF4CAF50)),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(4),
                            borderSide: BorderSide(color: Colors.grey.shade800),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(4),
                            borderSide: const BorderSide(color: Color(0xFF4CAF50)),
                          ),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        ),
                        onSubmitted: (_) => _sendMessage(context),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      decoration: BoxDecoration(
                        color: const Color(0xFF4CAF50),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: IconButton(
                        icon: const Icon(Icons.send_rounded, color: Colors.black),
                        onPressed: () => _sendMessage(context),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
