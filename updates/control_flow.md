Perfect ? this is the best of both worlds. You're defining a **clear default behavior per mode**, and using CLI flags as **optional modifiers** (mutators) rather than requirements. Let?s formalize that in both **controller logic** and **CLI behavior**.

---

## ?? CLI Flags (keep them, but make them optional)

```python
group.add_argument(
    "--text",
    type=str,
    help="(Optional) Text to synthesize in audio-out mode. Defaults to previous transcription or preset sample."
)

group.add_argument(
    "--output",
    type=str,
    help="(Optional) Path to save synthesized audio. Defaults to system temp file."
)

group.add_argument(
    "--play",
    action="store_true",
    help="(Optional) Play the audio after generation. Defaults to True for audio-out."
)
```

---

## ? Default Behavior by Mode

### ? `audio-in`:
| Step       | Default Behavior                             |
|------------|----------------------------------------------|
| Capture    | Record audio from mic                        |
| Process    | STT ? return transcription                   |
| Output     | Print to terminal                            |
| Storage    | (optional) Save audio or transcription to temp/log |

### ?? `audio-out`:
| Step       | Default Behavior                             |
|------------|----------------------------------------------|
| Text Input | Use `--text` OR fallback to last transcription OR default string like `"Hello, world!"` |
| Process    | TTS ? synthesize speech                      |
| Output     | Save to temp WAV file                        |
| Playback   | Autoplay enabled unless `--no-play` or test mode |

---

## ? Pseudocode: `AudioPipelineController.handle_audio_out()`

```plaintext
def handle_audio_out():
    # Step 1: Get the text
    text = config.get("text") or get_latest_transcription() or "Hello, world!"

    # Step 2: Synthesize speech
    audio_data = TextToSpeechService.synthesize(text)

    # Step 3: Save audio (if requested or default)
    output_path = config.get("output_path") or generate_temp_output_path()
    FileService.save(audio_data, output_path)

    # Step 4: Play audio (default=True)
    if config.get("play_audio", True):
        AudioPlaybackService.play(audio_data)
```

---

## ? `config` Object Example from CLI

```python
config = {
    "text": args.text,  # may be None
    "output_path": args.output,
    "play_audio": args.play if args.play is not None else True
}
```

---
