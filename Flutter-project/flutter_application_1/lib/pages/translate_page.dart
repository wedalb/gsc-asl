import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_speech/speech_client_authenticator.dart';

final serviceAccount = ServiceAccount.fromString(
        '${(await rootBundle.loadString('assets/hale-function-380900-db1efafd1ef2.json'))}');
class TranslatePage extends StatelessWidget {

  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Text('This is the Translate Page'),
      ),
    );
  }
}
