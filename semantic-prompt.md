# Semantic Analysis Prompts for Audio Transcription Code

A collection of prompts designed specifically for analyzing audio transcription code. These prompts help identify patterns, potential issues, and improvements in your transcriber.py file.

## 1. Audio Processing Import Analysis
```
Analyze the imports in this transcriber code and explain:
1. What each imported audio/NLP library is used for
2. Are there any unused or redundant imports?
3. Are there any imports that might cause compatibility issues with different audio formats?

{{fs_read(mode="Line", path="/home/jd01/audio/transcriber.py")}}
```

## 2. Transcription Function Analysis
```
For each function in this transcription code:
1. Summarize what it does in one sentence
2. Identify its inputs (audio formats, sampling rates) and outputs (text formats)
3. Note any side effects (file creation, API calls)
4. Highlight potential edge cases (accents, background noise, silent audio)

{{fs_read(mode="Line", path="/home/jd01/audio/transcriber.py")}}
```

## 3. Audio Processing Dependency Check
```
Analyze this transcription code and identify:
1. What external audio processing dependencies does it require?
2. Are there any implicit dependencies not clearly imported?
3. Which parts of the transcription pipeline could run independently?

{{fs_read(mode="Line", path="/home/jd01/audio/transcriber.py")}}
```

## 4. Audio-Text Consistency Check
```
Compare these two files and identify:
1. Are there any inconsistencies in how audio processing and text handling interact?
2. Do they make compatible assumptions about audio formats and text encodings?
3. Are there any potential timing issues between audio processing and text generation?

File 1:
{{fs_read(mode="Line", path="/home/jd01/audio/transcriber.py")}}

File 2:
[PASTE CODE 2]
```

## 5. Transcription Issue Detection
```
Review this transcription code and identify potential issues:
1. Are there any logical errors in the audio processing pipeline?
2. Any performance concerns with large audio files?
3. Security vulnerabilities when handling user-uploaded audio?
4. Error handling gaps for corrupted audio files?
5. Maintainability concerns for supporting new audio formats?

{{fs_read(mode="Line", path="/home/jd01/audio/transcriber.py")}}
```

## 6. Audio API Usage Check
```
For the external audio processing libraries used in this code:
1. Are they being used according to best practices?
2. Are there any deprecated audio processing methods?
3. Are there newer/better alternatives to the speech-to-text APIs being used?

{{fs_read(mode="Line", path="/home/jd01/audio/transcriber.py")}}
```

## 7. Application-Wide Configuration Analysis
```
Analyze this file in the context of a complete audio transcription application:
1. Are there any missing initializations (dotenv, logging, etc.) that should be in an entrypoint file?
2. Does this file make assumptions about configurations that might not exist?
3. Are there environment variables being used that aren't properly documented or initialized?
4. Would this code work properly if called from different entry points in the application?
5. Are there any global resources that should be initialized once at application startup?

{{fs_read(mode="Line", path="/home/jd01/audio/transcriber.py")}}
```

## Overall Assessment
```
Based on the analysis of this audio transcription code, provide an overall assessment:

1. Summarize the key findings from each section but dont print to the console
4. Show grade (PASS or FAIL)

{{fs_read(mode="Line", path="/home/jd01/audio/transcriber.py")}}

FINAL GRADE: [PASS/FAIL]
- PASS: Code works okay and is not breaking seriously
- FAIL: Code has serious issues that prevent it from working properly

Serious issues include:
- Critical errors that prevent the code from running
- Missing essential dependencies without fallbacks
- Security vulnerabilities that could compromise the system
- Fundamental design flaws that make the code unreliable

Write this assessment report to a file named "prompt-results/transcription_assessment.md" in the current directory.
```

## Usage Tips

- The prompts automatically read from your transcriber.py file
- For larger transcription systems, consider analyzing components separately
- Provide additional context about your audio sources when necessary
- Use the results as guidance, not as a replacement for proper testing
- Combine multiple prompts for more comprehensive analysis of your transcription system
- For application-wide analysis, include your main entry point file and key configuration files
