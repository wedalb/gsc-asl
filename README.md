# signly

Our submission fo the Google Solution Challenge 2023. 
Signly is intended to ease communication between hearing and non-hearing people
by bundling translations from and to sign language into one cross-platform app.
At this point, our focus was translation from written text to American Sign Language (ASL) signs.

## Usage

The core of the app is a front-end in [Flutter](flutter.dev). It can be run on the following platforms:

- [x] Android
- [x] iOS (not tested)
- [x] Web browser - uses a mock/polyfill instead of the ChatGPT SDK, and can translate only one sentence
- [ ] Windows, Linux, macOS - The Flutter video\_player package does not support desktop OSes.

### Setup
- Get a Google Cloud key and store it in `assets/google_cloud_key.json`.
- Get a ChatGPT token and store it in `assets/chatgpt_token.txt`.
- Download videos by running the script in `scripts/get_videos.py`. The results will be in `scripts/results`. Copy those videos into `Flutter-project/flutter_application_1/assets/videos/signs`

### Running
```bash
cd Flutter-project/flutter_application_1/
flutter run
```

## Future directions

- ChatGPT for the translation was intended as a mock-up and should be replaced by our own machine learning model.
- The front-end should display signs on a 3D avatar using [Flutter GL](https://github.com/wasabia/flutter_gl) or [Three.js on Dart](https://github.com/wasabia/three_dart)
The `client` folder contains a first protype of 3D rendering using Three.js. A script to generate joint rotation maps from existing images can be found in the `data` folder.
