import 'package:flutter/material.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[300],
      body: SafeArea(
        child: Column(
          children: [
            // app bar
            Row(
              children: [Text("Hello")],
            )

            // search bar (search for a word or sentence to learn it)

            // horizontal list -> card view

            //
          ],
        ),
      ),
    );
  }
}
