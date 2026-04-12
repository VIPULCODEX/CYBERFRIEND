import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class ApiMessage {
  final String role;
  final String content;
  final String type; // 'user', 'rag', 'news', 'alert'

  ApiMessage({required this.role, required this.content, this.type = 'rag'});
}

class ApiService with ChangeNotifier {
  // Update this URL once you deploy to Render/Railway
  String _baseUrl = "http://10.0.2.2:8000"; // Default for Android Emulator to host
  
  final List<ApiMessage> _messages = [];
  bool _isLoading = false;
  int _queryCount = 0;
  double _threatLevel = 15.0;

  List<ApiMessage> get messages => _messages;
  bool get isLoading => _isLoading;
  int get queryCount => _queryCount;
  double get threatLevel => _threatLevel;

  void setBaseUrl(String url) {
    _baseUrl = url;
    notifyListeners();
  }

  Future<void> sendMessage(String query) async {
    if (query.trim().isEmpty) return;

    // Add user message to UI
    _messages.add(ApiMessage(role: 'user', content: query, type: 'user'));
    _isLoading = true;
    notifyListeners();

    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'query': query,
          'user_id': 'mobile_user_1', // Can be dynamic
        }),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        String botResponse = data['response'];
        bool isCached = data['cached'] ?? false;
        
        // Simple logic to detect message type from response content (similar to app.py)
        String type = _detectMessageType(query, botResponse);
        
        _messages.add(ApiMessage(
          role: 'assistant', 
          content: botResponse, 
          type: type
        ));
        
        _queryCount++;
        _updateThreatLevel(query);
      } else {
        String errorMsg = "Error: ${response.statusCode}";
        if (response.statusCode == 429) errorMsg = "Rate limit exceeded. Try again later.";
        _messages.add(ApiMessage(role: 'assistant', content: errorMsg, type: 'alert'));
      }
    } catch (e) {
      _messages.add(ApiMessage(
        role: 'assistant', 
        content: "Connection failed. Please ensure the backend server is running at $_baseUrl.", 
        type: 'alert'
      ));
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  String _detectMessageType(String query, String response) {
    final q = query.toLowerCase();
    final r = response.toLowerCase();
    
    if (q.contains('news') || q.contains('latest') || q.contains('incident')) return 'news';
    if (r.contains('attack type:') || r.contains('critical') || r.contains('vulnerability')) return 'alert';
    return 'rag';
  }

  void _updateThreatLevel(String query) {
    // Mimic the logic in streamlit app
    if (query.toLowerCase().contains('attack') || query.toLowerCase().contains('hack')) {
      _threatLevel = (_threatLevel + 15).clamp(0, 100);
    } else {
      _threatLevel = (_threatLevel + 2).clamp(0, 95);
    }
  }

  void clearChat() {
    _messages.clear();
    _queryCount = 0;
    notifyListeners();
  }
}
