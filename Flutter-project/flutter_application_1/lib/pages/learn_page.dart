import 'package:flutter/services.dart';
import 'package:flutter_application_1/server.dart';
import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'dart:io';

Stream<String> getTextStream() async* {
  //TODO
  const text = """
To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take Arms against a Sea of troubles,
And by opposing end them: to die, to sleep
No more; and by a sleep, to say we end
The heart-ache, and the thousand natural shocks
That Flesh is heir to? 'Tis a consummation
Devoutly to be wished.
  """;

  for(String line in text.split("\n")) {
    yield line;
  }
}

class LearnPage extends StatefulWidget {
  const LearnPage({Key? key}) : super(key: key);

  final String title = 'Sign Videos';

  @override
  State<LearnPage> createState() => _PageState();
}

class _PageState extends State<LearnPage> {
  VideoPlayerController? _controller;
  Future<void>? _initializeVideoPlayerFuture;

  @override
  void initState() {
    super.initState();
  }

  Future<void> playOneVideo(gloss) async {
    _controller = VideoPlayerController.asset('assets/videos/signs/$gloss.mp4');
    _initializeVideoPlayerFuture = _controller!.initialize();
    await _initializeVideoPlayerFuture;
  }

  Future<void> streamTextToVideo(Stream<String> text) async {
    await for(String chunk in text){
      for(String gloss in chunk.split(' ')) {
        gloss = gloss.replaceAll('.', '').toLowerCase();

        try {
          await playOneVideo(gloss);
        } on PlatformException catch(_) { // this is thrown when the video does not exist
          for(String char in gloss.split('')){
            await playOneVideo(char);
          }
        }

        setState(() {}); // Reload UI
        await _controller!.play(); // The video has started playing (not yet finished)
        await Future.delayed(_controller!.value.duration);
      }
    }
  }

  @override
  void dispose(){
    _controller?.dispose(); // Make sure to dispose the Controller to free up resources
    super.dispose();
  }

  void toggleTextToVideo() async {
    Stream<String>? aslStream = await GlobalData.server.getASLTextStream();
    if(aslStream != null) {
      streamTextToVideo( aslStream );
    }
  }

  void textToVideo(String text) async {
    GlobalData.server.setEnglishTextStream(() async* { yield text; }());
    toggleTextToVideo();
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
        title: const Text('Text to signs'),
      ),
      body: Container(
        height: MediaQuery.of(context).size.height,
        width: MediaQuery.of(context).size.width,
        decoration: const BoxDecoration(
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
              const SizedBox(
                height: 70,
              ),
              Container(
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.black),
                  borderRadius: BorderRadius.circular(20),
                ),
                padding: const EdgeInsets.all(5.0),
                child: LayoutBuilder(builder: (context, constraints){
                  return SizedBox(
                    width: 800,
                    height: 400,
                    child: _controller == null
                    ? const Text(
                      'No video loaded',
                      style: TextStyle(color: Colors.grey),
                    ) : AspectRatio(
                      aspectRatio: _controller!.value.aspectRatio,
                      child: VideoPlayer(_controller!),
                    )
                  );
                }),
              ),
              const SizedBox(
                height: 10,
              ),
              TextField(
                onSubmitted: textToVideo,
                style: const TextStyle(color: Colors.grey),
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  labelText: 'Enter text...',
                ),
              ),
              if(_controller == null) ElevatedButton(
                style: ElevatedButton.styleFrom(
                  elevation: 10,
                  backgroundColor: Colors.purple[300],
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                ),
                onPressed: toggleTextToVideo,
                child: const Text(
                  'Text to video',
                  style: TextStyle(fontSize: 20),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
