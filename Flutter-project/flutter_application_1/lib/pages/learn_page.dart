import 'dart:io';

import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

Stream<String> getTextStream() async* {
  // TODO
  for(int i = 1; i<10; i++) {
    yield "World";
    yield "Hello";
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

  Future<void> textToVideo(Stream<String> text) async {
    await for(String gloss in text){
      print('Loading file assets/videos/signs/$gloss.mp4');
      print(File('assets/videos/signs/$gloss.mp4').hashCode);
      _controller = VideoPlayerController.asset('assets/videos/signs/$gloss.mp4');
      _initializeVideoPlayerFuture = _controller!.initialize();
      await _initializeVideoPlayerFuture;
      await _controller!.play();
      print('Video finished');
    }
  }

  @override
  void dispose(){
    _controller?.dispose(); // Make sure to dispose the Controller to free up resources
    super.dispose();
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
      body: SingleChildScrollView(
        child: Container(
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
                  height: 200,
                  width: 300,
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.black),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  padding: const EdgeInsets.all(5.0),
                  child: _controller == null
                    ? const Text(
                      'No video loaded',
                      style: TextStyle(color: Colors.grey),
                    )
                    : AspectRatio(
                      aspectRatio: _controller!.value.aspectRatio,
                      child: VideoPlayer(_controller!),
                    ),
                ),
                const SizedBox(
                  height: 10,
                ),
                if(_controller == null) ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    elevation: 10,
                    backgroundColor: Colors.purple[300],
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(15),
                    ),
                  ),
                  onPressed: () => textToVideo(getTextStream()),
                  child: const Text(
                    'Text to video',
                    style: TextStyle(fontSize: 20),
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
