
# Skinally Speech-to-Text

A lightweight and customizable **speech-to-text transcription system** built with Python. Designed for real-time audio input from microphone or file, with support for voice activity detection (VAD) and offline transcription.

---

## 🔧 Features

- 🎙️ Real-time microphone transcription
- 🗃️ Support for audio file transcription
- 🧠 Custom ASR model integration
- ⚙️ Configurable VAD sensitivity
- 🖥️ Runs on CPU or GPU

---

## 📦 Installation

### Requirements

- Python 3.8 or later
- `pip` (or Conda)
- Compatible audio input (e.g. microphone)

### Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/lukaszbos/Skinally-speach-to-text.git
cd Skinally-speach-to-text
pip install -r requirements.txt
```

---

## 🚀 Usage

### Live Microphone Transcription

```bash
python main.py --model path/to/model --device cpu --threshold 0.5
```

### Audio File Transcription

```bash
python evaluate.py --model path/to/model --audio path/to/audio.wav
```

---

## 🧰 Parameters

| Parameter     | Description                            | Example       |
|---------------|----------------------------------------|---------------|
| `--model`     | Path to the ASR model                  | `./models/my-model` |
| `--device`    | Device to run model on (`cpu` or `cuda`)| `cpu`         |
| `--threshold` | VAD threshold (0–1 sensitivity)        | `0.5`         |
| `--audio`     | Path to audio file (for evaluate.py)   | `sample.wav`  |

---

## 🗂 Project Structure

```
Skinally-speach-to-text/
├── skinally/              # Core speech and VAD logic
│   ├── __init__.py
│   ├── stt.py
│   └── vad.py
├── main.py                # Main live transcription runner
├── evaluate.py            # Audio file transcriber
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## 🧪 Example

```bash
python evaluate.py --model models/base --audio tests/test.wav
```

Output:

```
[00:00 – 00:05] Hello, how can I help you?
```

---

## 👨‍💻 Author

**Lukaszbos**  
Feel free to contribute or open issues!

---

## 📄 License

This project is licensed under the MIT License.
