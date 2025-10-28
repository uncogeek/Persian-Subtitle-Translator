# 🎬 Persian Subtitle Translator

A robust Python tool for translating English SRT subtitle files to Persian (Farsi) using AI, with **guaranteed 1:1 subtitle mapping** and **context-aware translation**.

## ✨ Key Features

- **🎯 Perfect 1:1 Mapping**: Every subtitle preserved - no dropped or merged entries
- **🧠 Context-Aware Translation**: Natural, contextual Persian translations (not word-by-word)
- **✅ Automatic Validation**: Built-in checker ensures translation completeness
- **🔄 Retry Logic**: Automatic retry with exponential backoff for failed requests
- **💾 Comprehensive Logging**: Debug logs and translation backups for troubleshooting
- **📦 Smart Chunking**: Handles large subtitle files by processing in chunks
- **⚙️ Flexible Configuration**: Easy-to-configure settings in one place

## 🌟 Why This Tool?

### Context-Aware Persian Translation

Unlike simple word-by-word translators, this tool delivers **natural Persian translations** that:
- Understand the full video context and narrative flow
- Use appropriate Persian expressions and idioms
- Maintain proper tone and formality levels
- Preserve cultural nuances and meaning

### The Problem with Traditional Approaches

When translating subtitles with AI, common issues include:
- ❌ Dropped subtitles (200 in → 185 out)
- ❌ Merged entries losing timing sync
- ❌ Word-by-word translations that sound unnatural
- ❌ Lack of context leading to mistranslations

### Our Solution: Three-Phase Translation Process

#### **Phase 1: Context Understanding** 📖
```
Input: ALL subtitle text as continuous narrative
AI: Reads and understands the full story/dialogue
Output: AI builds complete context
```
*Why?* The AI learns character relationships, plot progression, and context before translating anything.

#### **Phase 2: Structured Translation** 🔢
```
Input: Numbered JSON: {1: "text", 2: "text", ...}
AI: Translates each entry using full context knowledge
Output: Numbered JSON with Persian translations
```
*Why?* Structured format prevents the AI from combining or dropping entries. Each subtitle keeps its index.

#### **Phase 3: Validation & Reconstruction** ✅
```
Process: 
1. Verify all indices present (1 to N)
2. Merge Persian text with original timing
3. Run validation checker
4. Build final SRT file
```
*Why?* Double-checking ensures perfect alignment between English and Persian versions.

### Technical Safeguards

- ✅ **Numbered Indices**: JSON structure prevents entry merging
- ✅ **Explicit Count Validation**: API instructed to return exact number of entries
- ✅ **Automated Checker**: `checker.py` verifies translation completeness
- ✅ **Retry Mechanism**: Automatic retry if validation fails
- ✅ **Empty Subtitle Preservation**: Even blank entries are maintained
- ✅ **Timing Isolation**: Timing data never sent to AI (reduces confusion)

## 📋 Requirements

```bash
pip install requests pysrt
```

**Note**: `pysrt` is required for the validation checker (`checker.py`).

## 🚀 Quick Start

### 1. Configure API Settings

Edit the configuration section in `translate.py`:

```python
# API Configuration
API_ENDPOINT = "https://api.avalai.ir/v1/chat/completions"
API_KEY = "your-api-key-here"  # ⚠️ REQUIRED: Add your API key
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

# Translation Configuration
TARGET_LANGUAGE = "Persian"
SOURCE_LANGUAGE = "English"
```

### 2. Run Translation

```bash
python translate.py
```

By default, it looks for `input.srt` and creates `output_persian.srt`.

### 3. Validate Translation (Optional)

```bash
python checker.py
```

Verifies that all subtitles were translated correctly.

## ⚙️ Configuration Options

All settings are at the top of `translate.py`:

```python
# API Settings
API_ENDPOINT = "https://api.avalai.ir/v1/chat/completions"
API_KEY = "your-key"
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

# Translation Settings
TARGET_LANGUAGE = "Persian"  # Output language
SOURCE_LANGUAGE = "English"  # Input language

# Model Parameters
MAX_OUTPUT_TOKENS = 24576    # Maximum response length
TEMPERATURE = 0.1            # Lower = more consistent
TOP_P = 0.95                 # Sampling parameter

# Retry Settings
MAX_RETRIES = 3              # Retry failed requests
RETRY_DELAY = 5              # Seconds between retries

# Chunking Configuration
MAX_SUBTITLES_PER_CHUNK = 50 # Process large files in chunks
ENABLE_CHUNKING = True       # Enable/disable chunking

# Directories
LOG_DIR = "translation_logs" # Translation backups
TEMP_DIR = "temp_json"       # Temporary JSON files
DEBUG_DIR = "debug_logs"     # Detailed debug logs
```

## 📊 Output Files

For each translation session, you get:

1. **Translated SRT**: `output_persian.srt` - Final Persian subtitles
2. **JSON Backup**: `temp_json/input_with_timing.json` - Full data with timing
3. **Translation Log**: `translation_logs/input_translated_Persian.json` - Reusable translations
4. **Debug Logs**: `debug_logs/YYYYMMDD_HHMMSS/` - Complete session logs including:
   - Original SRT
   - Parsed structure
   - API requests/responses
   - Validation results
   - Final output

## 🎯 Example Usage

### Basic Translation

```python
from translate import SRTTranslator

translator = SRTTranslator()
translator.translate("movie.srt", "movie_fa.srt")
```

### Translate Multiple Files

```python
from pathlib import Path
from translate import SRTTranslator

translator = SRTTranslator()

for srt_file in Path(".").glob("*.srt"):
    output = f"{srt_file.stem}_persian.srt"
    print(f"Translating {srt_file}...")
    translator.translate(str(srt_file), output)
```

### Validate After Translation

```python
from checker import compare_srt_files

missing_subs, status = compare_srt_files("input.srt", "output_persian.srt")

if not missing_subs:
    print("✅ Perfect translation - all subtitles present!")
else:
    print(f"⚠️ Missing subtitles: {missing_subs}")
```

## 📈 Translation Flow

```
📂 input.srt (200 subtitles)
    ↓
📊 Parse SRT → Extract indices + timing + text
    ↓
💾 Save: {1: {time: "...", text: "..."}, 2: {...}, ...}
    ↓
📖 Phase 1: Create context text for AI understanding
    ↓
🔢 Phase 2: Create translation JSON {1: "text", 2: "text", ...}
    ↓
📤 Send to AI: "Translate with context, return EXACTLY 200 entries"
    ↓
🤖 AI translates using full context knowledge
    ↓
📥 Receive Persian JSON: {1: "translated", 2: "translated", ...}
    ↓
✅ Phase 3: Validate count = 200 ✓
    ↓
⏰ Merge timing data back into translations
    ↓
📋 Run checker.py validation
    ↓
💾 Save output_persian.srt (200 subtitles) ✅
```

## 🛠 Troubleshooting

### "API call failed"
- ✅ Check your API key is correct in `translate.py`
- ✅ Verify internet connection
- ✅ Confirm API endpoint is accessible
- ✅ Check API credits/quota

### "Validation failed - COUNT MISMATCH"
- ✅ Tool automatically retries (up to 3 times)
- ✅ Check `debug_logs/` for detailed API responses
- ✅ Try reducing `MAX_OUTPUT_TOKENS` if response is truncated
- ✅ Enable chunking for very large files

### "Failed to parse JSON"
- ✅ Check `debug_logs/` for raw API response
- ✅ Tool automatically strips markdown code blocks
- ✅ Verify API returned complete response

### Empty Output File
- ✅ Verify input SRT file is valid
- ✅ Check API has sufficient credits
- ✅ Review error messages in console
- ✅ Check `debug_logs/` for detailed error info

### Persian Text Issues
- ✅ Ensure your text editor supports UTF-8 and RTL (Right-to-Left)
- ✅ Use media players that support Persian subtitles (VLC, MPC-HC)
- ✅ Check font supports Persian characters

## 📈 Performance Tips

1. **For Long Videos**: ~30-60 seconds per 200 subtitles
2. **Cost Optimization**: Sending only text (no timing) saves ~50% tokens
3. **Best Model**: Gemini Flash provides fast, accurate Persian translations
4. **Large Files**: Enable chunking for files with 500+ subtitles
5. **Rate Limits**: Built-in retry with exponential backoff handles API limits

## 🔒 Security Notes

- ⚠️ **Never commit your API key** to version control
- ✅ Add `translate.py` to `.gitignore` or use environment variables:
  ```python
  import os
  API_KEY = os.getenv("AVALAI_API_KEY", "your-fallback-key")
  ```
- ✅ Keep your API key private and secure

## 📝 SRT Format Support

Supports standard SRT format:
```
1
00:00:00,080 --> 00:00:01,920
First subtitle text

2
00:00:01,920 --> 00:00:04,080
Second subtitle text
```

✅ Multi-line subtitles supported  
✅ Empty subtitles preserved  
✅ All timing formats supported  
✅ Special characters and Persian text handled  
✅ UTF-8 encoding with BOM support

## 📁 Project Structure

```
persian-subtitle-translator/
├── translate.py          # Main translation script
├── checker.py            # Validation checker
├── README.md            # This file
├── input.srt            # Your input file (example)
├── output_persian.srt   # Generated output
├── translation_logs/    # Translation backups
├── temp_json/          # Temporary JSON files
└── debug_logs/         # Detailed debug logs
    └── YYYYMMDD_HHMMSS/  # Session-specific logs
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Report issues
2. Suggest features
3. Submit pull requests
4. Improve documentation

## 📄 License

Free to use and modify for personal and commercial projects.

## 🙏 Credits

Built with ❤️ for the Persian-speaking community using:
- **Avalai.ir API** - AI translation service (my favorite provider❤️)
- **Google Gemini** - Powerful language model with excellent Persian support
- **Python** - Simple and powerful

## 💡 Why Context Matters

Traditional subtitle translation treats each line independently, resulting in awkward Persian that sounds robotic. Our approach:

1. **Understands the Scene**: Characters, emotions, setting
2. **Maintains Tone**: Formal/informal, serious/comedic
3. **Uses Natural Expressions**: Persian idioms instead of literal translations
4. **Preserves Cultural Nuances**: Appropriate for Persian-speaking audiences

**Example:**
- ❌ Word-by-word: "من دارم می‌روم به فروشگاه" (literal)
- ✅ Contextual: "دارم برای خرید میرم" (natural Persian)

---

**⭐ If this tool helps you create better Persian subtitles, please star this repository!**

**🐛 Found a bug?** Open an issue with your debug logs from `debug_logs/`

**💬 Questions?** Check existing issues or create a new one
