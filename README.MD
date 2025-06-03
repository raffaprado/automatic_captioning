# 🎥 Auto Subtitles Generator with Gemini AI and MoviePy

This project automates the subtitle creation process for videos using **Google Gemini AI** for transcription, **Google Translate** for translation, and **MoviePy** to burn subtitles directly into the video.

---

## ⚙️ Features

* ✅ Extract audio from a video file (.mp4)
* ✅ Automatic transcription with Gemini AI
* ✅ Generate `.srt` subtitle files
* ✅ Translate subtitles into other languages using Google Translate
* ✅ Burn subtitles into the video (multiple languages supported)

---

## 🧰 Requirements

* Python 3.8+
* A Google Gemini API key
* Install the required libraries:

```bash
pip install moviepy pysrt google-generativeai googletrans==4.0.0-rc1
```

> ⚠️ `googletrans` might fail for large texts or rate-limited by Google. For production, consider using Google Cloud Translate API.

---

## 🚀 How to Use

1. **Set your input video path:**

```python
video_input_path = "PATH TO YOUR VIDEO"
```

2. **Add your Gemini API key:**

```python
genai.configure(api_key="YOUR_API_KEY_HERE")
```

3. **Run the main script:**

```bash
python your_script.py
```

4. The script will:

   * Extract the audio from the video
   * Transcribe the audio to text
   * Create an `.srt` subtitle file
   * Optionally translate the subtitles
   * Add subtitles to the video

---

## 📌 Notes

* Gemini AI transcription is limited by token size. Long videos might get truncated.
* Subtitle timing is based on average words per second.
* `TextClip` rendering may fail if the font isn't installed on your system.

---

## 🧠 Credits

* [MoviePy](https://zulko.github.io/moviepy/)
* [Google Generative AI](https://ai.google.dev/)
* [Googletrans](https://github.com/ssut/py-googletrans)
* [pysrt](https://github.com/byroot/pysrt)

---

## 📄 License

This project is free to use for educational and prototyping purposes. For commercial use, review the terms of service of the respective APIs and libraries.
