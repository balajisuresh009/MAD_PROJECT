import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'YouTube Transcriber',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: TranscriptionScreen(),
    );
  }
}

class TranscriptionScreen extends StatefulWidget {
  @override
  _TranscriptionScreenState createState() => _TranscriptionScreenState();
}

class _TranscriptionScreenState extends State<TranscriptionScreen> {
  String _transcript = "";

  Future<void> _transcribe(String url) async {
    try {
      final response = await http.post(
        Uri.parse('http://172.16.45.138:5000/transcribe'),  // Use your server IP here
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'url': url}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _transcript = data['transcript'];
        });
      } else {
        setState(() {
          _transcript = 'Error: ${response.reasonPhrase}';
        });
      }
    } catch (e) {
      setState(() {
        _transcript = 'Error: ${e.toString()}';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    TextEditingController urlController = TextEditingController();

    return Scaffold(
      appBar: AppBar(title: Text("YouTube Transcriber")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: urlController,
              decoration: InputDecoration(labelText: "Enter YouTube URL"),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                _transcribe(urlController.text);
              },
              child: Text("Transcribe"),
            ),
            SizedBox(height: 20),
            Text("Transcript:"),
            SizedBox(height: 10),
            Expanded(
              child: SingleChildScrollView(
                child: Text(_transcript),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
