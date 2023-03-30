import 'package:chat_gpt_sdk/chat_gpt_sdk.dart';
import 'package:flutter/services.dart';

class GlobalData {
  static var server = _Server();
}

class _Server {
  Stream<String>? _textEnglishStream;
  Stream<String>? _textASLStream;

  OpenAI? chatGPT;

  Future<void> init() async {
    if(chatGPT != null) return;
    final token = await rootBundle.loadString('assets/chatgpt_token.txt');
    chatGPT = OpenAI.instance.build(
      token: token,
    );
  }

  Future<String> _translateTextToASL(String englishText) async {
    const prompt = "Act as an english to ASL grammar translation machine. Don't speak anything but the translation. Don't say „Gesture“ and just convert english grammar to ASL grammar. The sign to be translated starts with a < and ends with >";

    print('Me:\n$englishText\n---');
    final request = CompleteText(
      model: kTextDavinci3,
      prompt: "$prompt <$englishText>",
      maxTokens: 1024,
      temperature: 0.5,
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
