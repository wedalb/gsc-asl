import 'package:flutter/services.dart';
import 'package:chat_gpt_sdk/chat_gpt_sdk.dart'
  if(dart.library.html) 'package:flutter_application_1/polyfills/web/chat_gpt_sdk.dart'
  as openai;

class GlobalData {
  static var server = _Server();
}

class _Server {
  Stream<String>? _textEnglishStream;
  Stream<String>? _textASLStream;

  openai.OpenAI? chatGPT;

  Future<void> init() async {
    if(chatGPT != null) return;
    final token = await rootBundle.loadString('assets/chatgpt_token.txt');
    chatGPT = openai.OpenAI.instance.build(
      token: token,
    );
  }

  Future<String> _translateTextToASL(String englishText) async {
    const prompt = "Translate the following text to ASL gloss:";

    print('Me:\n$englishText\n---');
    final request = openai.CompleteText(
      model: openai.kTextDavinci3,
      prompt: "$prompt $englishText",
      maxTokens: 1024,
      temperature: 0,
    );
    final response = await chatGPT!.onCompletion(request: request);
    final result = response!.choices[0].text;
    print("GPT:\n$result\n---");
    return result;
  }

  Stream<String> _streamTranslateTextToASL(Stream<String> englishText) async* {
    String buffer = '';
    await init();
    await for(String chunk in englishText){
      final sentenceEnd = chunk.indexOf(RegExp('[.;!?:]'));
      if(sentenceEnd != -1){
        buffer += chunk.substring(0, sentenceEnd+1); // end is exclusive, but we want to keep the end character
        yield await _translateTextToASL(buffer);
        buffer = chunk.substring(sentenceEnd+1);
      } else {
        buffer += chunk;
      }
    }
    if(buffer != '') yield await _translateTextToASL(buffer);
  }

  Future<Stream<String>?> getASLTextStream() async {
    if(_textASLStream == null){
      if(_textEnglishStream == null) return null;
      _textASLStream = _streamTranslateTextToASL(_textEnglishStream!);
    }
    return _textASLStream;
  }

  void setEnglishTextStream(Stream<String> englishText){
    _textEnglishStream = englishText;
  }
}
