# Intent Extractor Dashboard

A lightweight Python desktop application that parses JSON-based intent data and converts it into clean, structured Markdown for easier analysis, documentation, and review.

---

## Overview

Working with intent data (e.g., Dialogflow or similar structured JSON formats) can be messy and time-consuming, especially when reviewing large numbers of training phrases.

This tool simplifies that process by:

- Extracting training phrases from JSON
- Normalizing different schema formats
- Converting them into readable Markdown
- Providing a simple UI for filtering, exporting, and analysis

---

## Features

- Supports Dialogflow-style JSON (`trainingPhrases`)  
- Handles generic intent schemas (`intents`, `examples`)  
- Filter intents by name  
- Copy results to clipboard  
- Export output as `.md` files  
- Recent files tracking  
- Clean, easy-to-use desktop UI (Tkinter)  
- No external dependencies required  

---

## Demo

### Input (JSON)
```json
{
  "trainingPhrases": [
    {
      "parts": [
        {"text": "How do I receive my complimentary binge account?"}
      ]
    }
  ]
}
```

## How to install:
No Python environment setup needed! easy to run and use.

- Go to 'Releases'
- download .exe file

# Rebuilding For new release
- clean old build files: 
```bash
rmdir /s /q build
rmdir /s /q dist
del *.spec
```

- rebuild app:
```bash
python -m PyInstaller --onefile --windowed intentExtractor.py
```

- rebuild with clean flag:
```bash
python -m PyInstaller --onefile --windowed --clean intent_dashboard.py
```