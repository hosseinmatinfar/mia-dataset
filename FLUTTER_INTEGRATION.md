# Mia API Integration Guide for Flutter

## Overview
Mia (Medical Intelligence Assistant) is a RAG-based AI assistant for pharmaceutical and medical education. The API provides intelligent answers to medical/pharmaceutical questions using a vector database of 16 PDF textbooks (5,022 document chunks) combined with OpenAI GPT-4o-mini.

**Purpose**: Medical education and clinical support for students and healthcare professionals
**Languages**: Multilingual support for 12+ languages (Persian, English, Arabic, Spanish, French, German, Turkish, Urdu, Russian, Chinese, Japanese, Korean, and more)
**Data Sources**: Pharmaceutical textbooks including Rang & Dale's Pharmacology and pharmaceutical technology references

---

## API Base URL
```
https://web-production-b4577.up.railway.app
```

---

## Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running and ready.

**Response Example:**
```json
{
  "status": "healthy",
  "message": "Mia RAG API is running",
  "version": "6.3b",
  "database": "loaded",
  "openai": "ready",
  "cache_size": 0
}
```

---

### 2. Query (Main Endpoint)
**POST** `/query`

Ask Mia a question and get an AI-powered answer with sources.

**Request Body:**
```json
{
  "question": "What is aspirin?",
  "language": "en",
  "top_k": 5,
  "use_cache": true
}
```

**Parameters:**
- `question` (required, string): The medical/pharmaceutical question
- `language` (optional, string): Language code for response (default: "auto" - auto-detect from question)
  - `"auto"`: Auto-detect language from question (default)
  - Explicit codes: `fa` (Persian), `en` (English), `ar` (Arabic), `es` (Spanish), `fr` (French), `de` (German), `tr` (Turkish), `ur` (Urdu), `ru` (Russian), `zh` (Chinese), `ja` (Japanese), `ko` (Korean)
  - You can omit this parameter entirely and Mia will respond in the same language as your question
- `top_k` (optional, int): Number of relevant documents to retrieve (default: 5, range: 1-10)
- `use_cache` (optional, bool): Use cached responses for faster results (default: true)

**Response Example:**
```json
{
  "success": true,
  "answer": "Aspirin is a medication that affects platelet aggregation...",
  "sources": [
    {
      "file": "Rang_and_Dales_Pharmacology_Updated.Edit.pdf",
      "page": 160
    },
    {
      "file": "TECHNO1+2+3+4-merged.pdf",
      "page": 2402
    }
  ],
  "question": "What is aspirin?",
  "language": "en",
  "cached": false
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Service not fully initialized"
}
```

---

### 3. Search (Database Only)
**POST** `/search`

Search the vector database without AI generation (faster, no OpenAI cost).

**Request Body:**
```json
{
  "query": "aspirin",
  "top_k": 5
}
```

**Response Example:**
```json
{
  "success": true,
  "results": [
    {
      "content": "Changes in the degradation constant of aspirin...",
      "source": "TECHNO1+2+3+4-merged.pdf",
      "page": 2402
    }
  ],
  "query": "aspirin",
  "count": 3
}
```

---

## Flutter Implementation Example

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class MiaAPIService {
  static const String baseUrl = 'https://web-production-b4577.up.railway.app';

  /// Query Mia with a medical/pharmaceutical question
  static Future<MiaResponse> query({
    required String question,
    String? language, // Null = auto-detect
    int topK = 5,
    bool useCache = true,
  }) async {
    try {
      // Build request body
      final Map<String, dynamic> requestBody = {
        'question': question,
        'top_k': topK,
        'use_cache': useCache,
      };

      // Only include language if explicitly specified
      if (language != null) {
        requestBody['language'] = language;
      }

      final response = await http.post(
        Uri.parse('$baseUrl/query'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode(requestBody),
      ).timeout(
        const Duration(seconds: 30),
        onTimeout: () => throw TimeoutException('Request timeout'),
      );

      if (response.statusCode == 200) {
        // Decode UTF-8 to handle Persian text correctly
        final Map<String, dynamic> data = jsonDecode(
          utf8.decode(response.bodyBytes)
        );
        return MiaResponse.fromJson(data);
      } else if (response.statusCode == 429) {
        throw RateLimitException('Too many requests. Please try again later.');
      } else if (response.statusCode == 503) {
        throw ServiceUnavailableException('Service temporarily unavailable');
      } else {
        throw APIException('API Error: ${response.statusCode}');
      }
    } on SocketException {
      throw NetworkException('No internet connection');
    } on TimeoutException {
      throw NetworkException('Request timeout');
    } catch (e) {
      throw APIException('Unexpected error: $e');
    }
  }

  /// Check API health status
  static Future<bool> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['status'] == 'healthy';
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}

// Data Models
class MiaResponse {
  final bool success;
  final String answer;
  final List<Source> sources;
  final String question;
  final String language;
  final bool cached;

  MiaResponse({
    required this.success,
    required this.answer,
    required this.sources,
    required this.question,
    required this.language,
    required this.cached,
  });

  factory MiaResponse.fromJson(Map<String, dynamic> json) {
    return MiaResponse(
      success: json['success'] ?? false,
      answer: json['answer'] ?? '',
      sources: (json['sources'] as List?)
          ?.map((s) => Source.fromJson(s))
          .toList() ?? [],
      question: json['question'] ?? '',
      language: json['language'] ?? 'en',
      cached: json['cached'] ?? false,
    );
  }
}

class Source {
  final String file;
  final int? page;

  Source({required this.file, this.page});

  factory Source.fromJson(Map<String, dynamic> json) {
    return Source(
      file: json['file'] ?? 'Unknown',
      page: json['page'],
    );
  }

  String get displayName {
    if (page != null) {
      return '$file (page $page)';
    }
    return file;
  }
}

// Custom Exceptions
class APIException implements Exception {
  final String message;
  APIException(this.message);
  @override
  String toString() => message;
}

class NetworkException implements Exception {
  final String message;
  NetworkException(this.message);
  @override
  String toString() => message;
}

class RateLimitException implements Exception {
  final String message;
  RateLimitException(this.message);
  @override
  String toString() => message;
}

class ServiceUnavailableException implements Exception {
  final String message;
  ServiceUnavailableException(this.message);
  @override
  String toString() => message;
}
```

---

## Usage Example in Flutter Widget

```dart
class MiaChat extends StatefulWidget {
  @override
  _MiaChatState createState() => _MiaChatState();
}

class _MiaChatState extends State<MiaChat> {
  final TextEditingController _controller = TextEditingController();
  bool _isLoading = false;
  MiaResponse? _response;
  String? _error;

  Future<void> _sendQuestion() async {
    if (_controller.text.trim().isEmpty) return;

    setState(() {
      _isLoading = true;
      _error = null;
      _response = null;
    });

    try {
      final response = await MiaAPIService.query(
        question: _controller.text,
        // language: 'fa', // Optional - omit for auto-detect
        topK: 5,
      );

      setState(() {
        _response = response;
        _isLoading = false;
      });
    } on RateLimitException catch (e) {
      setState(() {
        _error = 'محدودیت درخواست: لطفاً بعداً تلاش کنید';
        _isLoading = false;
      });
    } on NetworkException catch (e) {
      setState(() {
        _error = 'خطای اتصال: اینترنت خود را بررسی کنید';
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'خطا: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Mia Assistant')),
      body: Column(
        children: [
          // Question input
          Padding(
            padding: EdgeInsets.all(16),
            child: TextField(
              controller: _controller,
              decoration: InputDecoration(
                hintText: 'سوال خود را بپرسید...',
                suffixIcon: IconButton(
                  icon: Icon(Icons.send),
                  onPressed: _isLoading ? null : _sendQuestion,
                ),
              ),
            ),
          ),

          // Loading indicator
          if (_isLoading)
            CircularProgressIndicator(),

          // Error message
          if (_error != null)
            Padding(
              padding: EdgeInsets.all(16),
              child: Text(_error!, style: TextStyle(color: Colors.red)),
            ),

          // Response
          if (_response != null)
            Expanded(
              child: SingleChildScrollView(
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _response!.answer,
                      style: TextStyle(fontSize: 16),
                    ),
                    SizedBox(height: 16),
                    Text(
                      'منابع:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    ...(_response!.sources.map((s) =>
                      Text('• ${s.displayName}')
                    )),
                    if (_response!.cached)
                      Padding(
                        padding: EdgeInsets.only(top: 8),
                        child: Text(
                          '⚡ از حافظه موقت',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
```

---

## Auto-Detect Language Examples

The API automatically detects the language of your question and responds in the same language. You don't need to specify the language parameter unless you want to force a specific language.

```dart
// Auto-detect (recommended)
// Persian question → Persian answer
await MiaAPIService.query(question: "آسپرین چیست؟");

// Arabic question → Arabic answer
await MiaAPIService.query(question: "ما هو الأسبرين؟");

// English question → English answer
await MiaAPIService.query(question: "What is aspirin?");

// Spanish question → Spanish answer
await MiaAPIService.query(question: "¿Qué es la aspirina?");

// Force specific language (override auto-detect)
await MiaAPIService.query(
  question: "What is aspirin?",
  language: "fa", // Answer in Persian even though question is English
);
```

---

## Important Notes

### Rate Limiting
- **100 requests per hour** per IP address
- **30 requests per minute** for `/query` endpoint
- **60 requests per minute** for `/search` endpoint
- Error 429: Rate limit exceeded

### Response Time
- `/health`: ~0.5 seconds
- `/search`: ~1-2 seconds
- `/query`: ~10-15 seconds (includes OpenAI API call)

### Character Encoding
**IMPORTANT**: Always use `utf8.decode(response.bodyBytes)` instead of `response.body` to properly handle Persian text!

```dart
// ❌ Wrong - Persian text will be corrupted
final data = jsonDecode(response.body);

// ✅ Correct - Persian text decoded properly
final data = jsonDecode(utf8.decode(response.bodyBytes));
```

### Error Handling
Always handle these error cases:
- Network errors (no internet)
- Timeouts (slow connection)
- Rate limiting (429)
- Service unavailable (503)
- Invalid requests (400)

### Best Practices
1. **Show loading indicators** - Queries can take 10-15 seconds
2. **Cache responses locally** - Reduce API calls
3. **Implement retry logic** - For network failures
4. **Add timeout handling** - Don't let requests hang forever
5. **Validate input** - Don't send empty questions
6. **Handle Persian text properly** - Use UTF-8 decoding

### Testing
Test these scenarios:
- English questions
- Persian/Farsi questions
- Long questions (500+ characters)
- Medical terminology
- Drug names
- Connection errors
- Rate limit exceeded

---

## Support & Troubleshooting

### Common Issues

**Issue**: Persian text shows as `????` or garbled characters
**Solution**: Use `utf8.decode(response.bodyBytes)` instead of `response.body`

**Issue**: Timeout errors
**Solution**: Increase timeout to 30-60 seconds, queries are slow

**Issue**: 429 Rate Limit
**Solution**: Implement local caching, respect rate limits

**Issue**: 503 Service Unavailable
**Solution**: Database or OpenAI not ready, retry after a few seconds

---

## API Status & Monitoring

Check API status: `GET /health`

Expected healthy response:
```json
{
  "status": "healthy",
  "database": "loaded",
  "openai": "ready"
}
```

If `database` or `openai` is not ready, wait and retry.

---

## Data Sources
The API uses these pharmaceutical textbooks:
- Rang & Dale's Pharmacology (Updated Edition)
- Pharmaceutical Technology textbooks (merged)
- Additional pharmaceutical reference materials

Total: 5,022 document chunks from 16 PDF files

---

## Security & Privacy
- All requests are over HTTPS
- No API key required from client
- Rate limiting protects against abuse
- No user data is stored
- Responses are cached temporarily for performance

---

## Contact & Deployment
- **Deployment**: Railway.app
- **Repository**: Private GitHub repository
- **Version**: 6.3b
- **Model**: OpenAI GPT-4o-mini
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2

---

Generated: November 2025
