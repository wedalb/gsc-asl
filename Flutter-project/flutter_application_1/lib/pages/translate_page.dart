import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_speech/speech_client_authenticator.dart';
import 'package:google_speech/google_speech.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:loading_indicator/loading_indicator.dart';
import 'dart:io';
import 'dart:async';

class TranslatePage extends StatefulWidget {
  TranslatePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<TranslatePage> createState() => _TranslatePageState();
}

class _TranslatePageState extends State<TranslatePage> {
  bool is_Transcribing = false;
  String content = '';

  void transcribe() async {
    setState(() {
      is_Transcribing = true;
    });
    final serviceAccount = ServiceAccount.fromString(
        await rootBundle.loadString('assets/google_cloud_key.json'));
    final speechToText = SpeechToText.viaServiceAccount(serviceAccount);

    final config = RecognitionConfig(
        encoding: AudioEncoding.LINEAR16,
        model: RecognitionModel.basic,
        enableAutomaticPunctuation: true,
        sampleRateHertz: 16000,
        languageCode: 'en-US');

    final audio = await _getAudioContent('test.wav');
    await speechToText.recognize(config, audio).then((value) {
      setState(() {
        content = value.results
            .map((e) => e.alternatives.first.transcript)
            .join('\n');
      });
    }).whenComplete(() {
      setState(() {
        is_Transcribing = false;
      });
    });
  }

  Future<List<int>> _getAudioContent(String name) async {
    //final directory = await getApplicationDocumentsDirectory();
    //final path = directory.path + '/$name';
    final path = '/sdcard/Download/temp.wav';
    return File(path).readAsBytesSync().toList();
  }

  @override
  void initState() {
    setPermissions();
    super.initState();
  }

  void setPermissions() async {
    // The Permission API is only available on some platforms
    if(!kIsWeb && (Platform.isAndroid || Platform.isIOS || Platform.isWindows)) {
      await Permission.manageExternalStorage.request();
      await Permission.storage.request();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.purple[300],
      appBar: AppBar(
        toolbarHeight: 80,
        backgroundColor: Colors.purple[300],
        elevation: 0,
        centerTitle: true,
        title: Text('Transcribe Your Audio'),
      ),
      body: SingleChildScrollView(
        child: Container(
          height: MediaQuery.of(context).size.height,
          width: MediaQuery.of(context).size.width,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.only(
              topRight: Radius.circular(50),
              topLeft: Radius.circular(50),
            ),
          ),
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.start,
              children: <Widget>[
                SizedBox(
                  height: 70,
                ),
                Container(
                  height: 200,
                  width: 300,
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.black),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  padding: EdgeInsets.all(5.0),
                  child: content == ''
                      ? Text(
                          'Your text will appear here',
                          style: TextStyle(color: Colors.grey),
                        )
                      : Text(
                          content,
                          style: TextStyle(fontSize: 20),
                        ),
                ),
                SizedBox(
                  height: 10,
                ),
                Container(
                  child: is_Transcribing
                      ? Expanded(
                          child: LoadingIndicator(
                            indicatorType: Indicator.ballPulse,
                            colors: [Colors.red, Colors.green, Colors.blue],
                          ),
                        )
                      : ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            elevation: 10,
                            primary: Colors.purple[300],
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(15),
                            ),
                          ),
                          onPressed: is_Transcribing ? () {} : transcribe,
                          child: is_Transcribing
                              ? CircularProgressIndicator()
                              : Text(
                                  'Transcribe',
                                  style: TextStyle(fontSize: 20),
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
