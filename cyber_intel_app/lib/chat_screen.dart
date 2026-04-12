import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'api_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final api = context.watch<ApiService>();
    
    return Scaffold(
      backgroundColor: const Color(0xFF020202),
      appBar: AppBar(
        title: Text('🛡 QUANTX AI', style: Theme.of(context).textTheme.displayLarge?.copyWith(fontSize: 16)),
        backgroundColor: const Color(0xFF030d08),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_sweep, color: Color(0xFF8A9B8F)),
            onPressed: () => api.clearChat(),
          ),
        ],
      ),
      body: Column(
        children: [
          // ── TACTICAL PANEL (Threat Indicator) ──
          _buildThreatPanel(api.threatLevel),
          
          // ── CHAT AREA ──
          Expanded(
            child: api.messages.isEmpty
                ? _buildWelcomeCard()
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
                    itemCount: api.messages.length,
                    itemBuilder: (context, index) {
                      final msg = api.messages[index];
                      return _buildMessageBubble(msg);
                    },
                  ),
          ),
          
          if (api.isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: SpinKitThreeBounce(color: Color(0xFF00FF9F), size: 20),
            ),

          // ── INPUT AREA ──
          _buildInputArea(api),
        ],
      ),
    );
  }

  Widget _buildThreatPanel(double level) {
    Color color = level < 30 ? const Color(0xFF00FF9F) : level < 60 ? const Color(0xFFFFC857) : const Color(0xFFFF3D5A);
    String label = level < 30 ? "LOW" : level < 60 ? "ELEVATED" : "CRITICAL";

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF080C0A),
        border: Border(bottom: BorderSide(color: color.withOpacity(0.1), width: 1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text("THREAT LEVEL", style: GoogleFonts.rajdhani(color: Colors.white54, fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 2)),
              Text(label, style: GoogleFonts.orbitron(color: color, fontSize: 11, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(2),
            child: LinearProgressIndicator(
              value: level / 100,
              backgroundColor: Colors.white.withOpacity(0.05),
              valueColor: AlwaysStoppedAnimation<Color>(color),
              minHeight: 4,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWelcomeCard() {
    return Center(
      child: Container(
        margin: const EdgeInsets.all(30),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: const Color(0xFF080C0A),
          border: Border.all(color: const Color(0xFF00FF9F).withOpacity(0.1)),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.security, size: 40, color: Color(0xFF00FF9F)),
            const SizedBox(height: 16),
            Text("SYSTEM READY", style: GoogleFonts.orbitron(color: const Color(0xFF00FF9F), fontSize: 14, fontWeight: FontWeight.bold, letterSpacing: 2)),
            const SizedBox(height: 12),
            const Text(
              "I am your tactical intelligence assistant.\nEnter a query below to begin analysis.",
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white70, fontSize: 13, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageBubble(ApiMessage msg) {
    bool isUser = msg.role == 'user';
    Color themeColor = msg.type == 'alert' ? const Color(0xFFFF3D5A) : msg.type == 'news' ? const Color(0xFF00CFFF) : const Color(0xFF00FF9F);
    
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.85),
        decoration: BoxDecoration(
          color: isUser ? const Color(0xFF00CFFF).withOpacity(0.08) : const Color(0xFF00FF9F).withOpacity(0.05),
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(isUser ? 16 : 4),
            topRight: Radius.circular(isUser ? 4 : 16),
            bottomLeft: const Radius.circular(16),
            bottomRight: const Radius.circular(16),
          ),
          border: Border.all(color: isUser ? const Color(0xFF00CFFF).withOpacity(0.2) : themeColor.withOpacity(0.15)),
          borderSide: isUser ? null : BorderSide(color: themeColor, width: 2), // Left border for bot
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              isUser ? "OPERATOR" : "QUANTX CORE",
              style: GoogleFonts.rajdhani(color: isUser ? const Color(0xFF00CFFF) : themeColor, fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 2),
            ),
            const SizedBox(height: 6),
            Text(
              msg.content,
              style: GoogleFonts.inter(color: Colors.white, fontSize: 14, height: 1.6),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInputArea(ApiService api) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
      color: Colors.black,
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              style: const TextStyle(color: Color(0xFF00FF9F), fontSize: 14),
              decoration: InputDecoration(
                hintText: "// ENTER QUERY...",
                hintStyle: const TextStyle(color: Colors.white24, fontSize: 13),
                filled: true,
                fillColor: const Color(0xFF080C0A),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: Colors.white.withOpacity(0.05))),
                focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF00FF9F), width: 1)),
              ),
              onSubmitted: (val) => _handleSend(api),
            ),
          ),
          const SizedBox(width: 12),
          GestureDetector(
            onTap: () => _handleSend(api),
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF00FF9F),
                borderRadius: BorderRadius.circular(12),
                boxShadow: [BoxShadow(color: const Color(0xFF00FF9F).withOpacity(0.3), blurRadius: 10, spreadRadius: 1)],
              ),
              child: const Icon(Icons.send_rounded, color: Colors.black, size: 20),
            ),
          ),
        ],
      ),
    );
  }

  void _handleSend(ApiService api) {
    if (_controller.text.trim().isEmpty || api.isLoading) return;
    api.sendMessage(_controller.text);
    _controller.clear();
    _scrollToBottom();
  }
}
