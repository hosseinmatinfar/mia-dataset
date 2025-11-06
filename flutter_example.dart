// نمونه کد Flutter برای استفاده از Mia RAG API
// این رو توی پروژه Flutter خودت استفاده کن

import 'dart:convert';
import 'package:http/http.dart' as http;

class MiaRagService {
  // آدرس API Server
  // اگه روی localhost اجرا می‌کنی، از این استفاده کن:
  // iOS Simulator: http://localhost:5000
  // Android Emulator: http://10.0.2.2:5000
  // Real Device: http://YOUR_COMPUTER_IP:5000
  final String baseUrl = 'http://localhost:5000';

  /// سوال پرسیدن از Mia
  Future<MiaResponse> askQuestion({
    required String question,
    String language = 'en', // 'en' or 'fa'
    int topK = 5,
    List<Map<String, String>>? conversationHistory,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/query'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'question': question,
          'language': language,
          'top_k': topK,
          'conversation_history': conversationHistory ?? [],
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return MiaResponse.fromJson(data);
      } else {
        throw Exception('Failed to get response: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error asking Mia: $e');
    }
  }

  /// جستجو در اسناد (بدون استفاده از OpenAI)
  Future<SearchResults> searchDocuments({
    required String query,
    int topK = 5,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/search'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'query': query,
          'top_k': topK,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return SearchResults.fromJson(data);
      } else {
        throw Exception('Failed to search: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error searching: $e');
    }
  }

  /// بررسی سلامت API
  Future<bool> checkHealth() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}

// Model برای پاسخ Mia
class MiaResponse {
  final bool success;
  final String answer;
  final List<DocumentSource> sources;
  final String question;
  final String language;

  MiaResponse({
    required this.success,
    required this.answer,
    required this.sources,
    required this.question,
    required this.language,
  });

  factory MiaResponse.fromJson(Map<String, dynamic> json) {
    return MiaResponse(
      success: json['success'] ?? false,
      answer: json['answer'] ?? '',
      sources: (json['sources'] as List?)
              ?.map((s) => DocumentSource.fromJson(s))
              .toList() ??
          [],
      question: json['question'] ?? '',
      language: json['language'] ?? 'en',
    );
  }
}

class DocumentSource {
  final String file;
  final int? page;

  DocumentSource({required this.file, this.page});

  factory DocumentSource.fromJson(Map<String, dynamic> json) {
    return DocumentSource(
      file: json['file'] ?? 'Unknown',
      page: json['page'],
    );
  }
}

class SearchResults {
  final bool success;
  final List<SearchResult> results;
  final String query;
  final int count;

  SearchResults({
    required this.success,
    required this.results,
    required this.query,
    required this.count,
  });

  factory SearchResults.fromJson(Map<String, dynamic> json) {
    return SearchResults(
      success: json['success'] ?? false,
      results: (json['results'] as List?)
              ?.map((r) => SearchResult.fromJson(r))
              .toList() ??
          [],
      query: json['query'] ?? '',
      count: json['count'] ?? 0,
    );
  }
}

class SearchResult {
  final String content;
  final String source;
  final int? page;

  SearchResult({
    required this.content,
    required this.source,
    this.page,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) {
    return SearchResult(
      content: json['content'] ?? '',
      source: json['source'] ?? 'Unknown',
      page: json['page'],
    );
  }
}

// ============================================
// نمونه استفاده در Widget
// ============================================

/*
import 'package:flutter/material.dart';

class MiaChatScreen extends StatefulWidget {
  @override
  _MiaChatScreenState createState() => _MiaChatScreenState();
}

class _MiaChatScreenState extends State<MiaChatScreen> {
  final MiaRagService _miaService = MiaRagService();
  final TextEditingController _controller = TextEditingController();
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    // اضافه کردن پیام کاربر
    setState(() {
      _messages.add(ChatMessage(text: text, isUser: true));
      _isLoading = true;
    });

    _controller.clear();

    try {
      // ارسال به Mia
      final response = await _miaService.askQuestion(
        question: text,
        language: 'en', // یا 'fa' برای فارسی
      );

      // اضافه کردن پاسخ Mia
      setState(() {
        _messages.add(ChatMessage(
          text: response.answer,
          isUser: false,
          sources: response.sources,
        ));
      });
    } catch (e) {
      // نمایش خطا
      setState(() {
        _messages.add(ChatMessage(
          text: 'Error: $e',
          isUser: false,
        ));
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Mia - Medical Assistant'),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              reverse: true,
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[_messages.length - 1 - index];
                return ChatBubble(message: message);
              },
            ),
          ),
          if (_isLoading)
            Padding(
              padding: EdgeInsets.all(8),
              child: CircularProgressIndicator(),
            ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: EdgeInsets.all(8),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              decoration: InputDecoration(
                hintText: 'Ask Mia a question...',
                border: OutlineInputBorder(),
              ),
              onSubmitted: _sendMessage,
            ),
          ),
          SizedBox(width: 8),
          IconButton(
            icon: Icon(Icons.send),
            onPressed: () => _sendMessage(_controller.text),
          ),
        ],
      ),
    );
  }
}

class ChatMessage {
  final String text;
  final bool isUser;
  final List<DocumentSource>? sources;

  ChatMessage({
    required this.text,
    required this.isUser,
    this.sources,
  });
}

class ChatBubble extends StatelessWidget {
  final ChatMessage message;

  const ChatBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: message.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.all(8),
        padding: EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: message.isUser ? Colors.blue[100] : Colors.grey[200],
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(message.text),
            if (message.sources != null && message.sources!.isNotEmpty)
              Padding(
                padding: EdgeInsets.only(top: 8),
                child: Text(
                  'Sources: ${message.sources!.map((s) => s.file).join(", ")}',
                  style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
*/
