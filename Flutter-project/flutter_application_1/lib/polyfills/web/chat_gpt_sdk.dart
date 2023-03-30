// This is a polyfill for the ChatGPT SDK, which depends on dart:ffi and is not
// available on browsers.
// For now, it is a simple mock-up that contains only the classes required by
// our code, and can translate only one sentence

class OpenAI {
  String token;

  OpenAI({ required this.token });

  static final instance = OpenAI(token: '');

  OpenAI build({ required String token }){
    return OpenAI(token: token);
  }

  Future<CTResponse?> onCompletion({ required CompleteText request }) async {
    if(request.prompt == "Translate the following text to ASL gloss: I like anything that has chocolate in it."){
      return CTResponse(choices: [
        Choices(
          text: "I LIKE ANYTHING HAVE CHOCOLATE INSIDE.",
        )
      ]);
    } else {
      throw UnimplementedError("Sorry, this is just a mockup of the real ChatGPT");
    }
  }
}

class Choices {
  String text;
  Choices({ required this.text });
}

class CTResponse {
  List<Choices> choices;
  CTResponse({ required this.choices });
}

const String kTextDavinci3 = 'text-davinci-003';

class CompleteText {
  String prompt;

  CompleteText({
    required this.prompt,
    required String model,
    int maxTokens = 100,
    double temperature = 0.3,
  });
}
