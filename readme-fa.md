# 🎬 Persian Subtitle Translator (مترجم زیرنویس فارسی)

یه ابزار خفن Python برای ترجمه فایل‌های زیرنویس انگلیسی SRT به فارسی با استفاده از AI، با این **تضمین که هیچ زیرنویسی کم و زیاد نشه** و **ترجمه با در نظر گرفتن context (متن)** انجام بشه.

## ✨ امکانات اصلی

- **🎯 مَپینگ ۱:۱ بی‌نقص**: همه‌ی زیرنویس‌ها سر جاشون هستن، هیچ کدوم حذف یا قاطی نمیشن.
- **🧠 ترجمه context-aware**: ترجمه فارسی طبیعی و با توجه به context (نه کلمه به کلمه).
- **✅ بررسی خودکار**: یه چک‌کننده داخلی داره که مطمئن میشه ترجمه کامله.
- **🔄 منطق Retry**: اگه یه درخواست ناموفق بود، به صورت خودکار دوباره تلاش می‌کنه (exponential backoff).
- **💾 لاگ‌گیری کامل**: لاگ‌های Debug و بکاپ ترجمه‌ها برای عیب‌یابی.
- **📦 چانکینگ هوشمند**: فایل‌های زیرنویس بزرگ رو به تیکه‌های کوچیک‌تر تقسیم می‌کنه و ترجمه می‌کنه.
- **⚙️ تنظیمات قابل انعطاف**: تنظیمات رو راحت میشه تو یه جا تغییر داد.

## 🌟 چرا از این ابزار استفاده کنیم؟

### ترجمه فارسی Context-Aware

برخلاف مترجم‌های ساده کلمه به کلمه، یا ترجمه هایی که با کانتکس اصلی همخوانی ندارن، این ابزار **ترجمه فارسی طبیعی** ارائه میده که:

- context کامل ویدیو و روند داستان رو میفهمه.
- از اصطلاحات و عبارات مناسب فارسی استفاده می‌کنه.
- لحن و سطح رسمی یا غیررسمی بودن رو حفظ می‌کنه.
- تفاوت‌های فرهنگی و معانی رو حفظ می‌کنه.

### مشکل رویکردهای سنتی

وقتی زیرنویس رو با AI ترجمه می‌کنیم، مشکلات رایج اینا هستن:

- ❌ حذف شدن زیرنویس‌ها (مثلاً ۲۰۰ تا ورودی، ۱۸۵ تا خروجی)
- ❌ قاطی شدن زیرنویس‌ها و از دست رفتن زمان‌بندی
- ❌ ترجمه‌های کلمه به کلمه یا جمله به جمله که غیرطبیعی به نظر میرسن
- ❌ کمبود context که باعث اشتباه ترجمه میشه

### راه حل ما: فرآیند ترجمه سه مرحله‌ای

#### **مرحله ۱: درک Context** 📖

```
Input: متن کامل زیرنویس به صورت یه داستان پیوسته
AI: کل داستان/دیالوگ رو میخونه و میفهمه
Output: AI یه context کامل میسازه
```

*چرا؟* چون AI قبل از ترجمه، روابط شخصیت‌ها، پیشرفت داستان و context رو یاد می‌گیره.

#### **مرحله ۲: ترجمه ساختاریافته** 🔢

```
Input: JSON شماره‌گذاری شده: {1: "text", 2: "text", ...}
AI: هر ورودی رو با استفاده از دانش کامل context ترجمه می‌کنه
Output: JSON شماره‌گذاری شده با ترجمه‌های فارسی
```

*چرا؟* چون فرمت ساختاریافته مانع از این میشه که AI ورودی‌ها رو ترکیب یا حذف کنه. هر زیرنویس شماره خودش رو حفظ می‌کنه.

#### **مرحله ۳: بررسی و بازسازی** ✅

```
Process:
1. بررسی اینکه همه شماره‌ها وجود دارن (از ۱ تا N)
2. ترکیب متن فارسی با زمان‌بندی اصلی
3. اجرای چک‌کننده
4. ساخت فایل SRT نهایی
```

*چرا؟* چون double-check میکنیم که تطابق کامل بین نسخه انگلیسی و فارسی وجود داشته باشه.

### ملاحظات فنی

- ✅ **شماره‌گذاری**: فرمت JSON مانع از ادغام ورودی‌ها میشه

- ✅ **بررسی تعداد**: به API دستور داده میشه که تعداد دقیق ورودی‌ها رو برگردونه

- ✅ **چک‌کننده خودکار**: `checker.py` کامل بودن ترجمه رو بررسی می‌کنه

- ✅ **مکانیسم Retry**: اگه بررسی ناموفق بود، به صورت خودکار دوباره تلاش می‌کنه (مثلا Rate limit یا Connection)

- ✅ **حفظ زیرنویس‌های خالی**: حتی ورودی‌های خالی هم حفظ میشن

- ✅ **جداسازی زمان‌بندی**: داده‌های زمان‌بندی به AI ارسال نمیشه (باعث میشه گیج نشه)

  > بعد از کلی آزمون و خطا، به یک پروسه مطمئن نیاز داشتم تا ویدئو هایی که زیرنویس براشون وجود نداره رو ترجمه کنم، و این ساده ترین و مطمئن ترین راه برای ترجمه زیرنویس ها هست.

## 📋 نیازمندی‌ها

```bash
pip install requests pysrt
```

**نکته**: `pysrt` برای چک‌کننده (`checker.py`) لازمه.

## 🚀 شروع

### ۱. تنظیم API

قسمت تنظیمات رو تو `translate.py` ادیت کن:

```python
# API Configuration
API_ENDPOINT = "https://api.avalai.ir/v1/chat/completions"
API_KEY = "your-api-key-here"  # ⚠️ REQUIRED: Add your API key
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

# Translation Configuration
TARGET_LANGUAGE = "Persian"
SOURCE_LANGUAGE = "English"
```

### ۲. اجرای ترجمه

```bash
python translate.py
```

به صورت پیش‌فرض، دنبال `input.srt` میگرده و `output_persian.srt` رو میسازه.

### ۳. بررسی ترجمه (اختیاری)

```bash
python checker.py
```

بررسی می‌کنه که همه زیرنویس‌ها درست ترجمه شده باشن.

## ⚙️ تنظیمات

همه تنظیمات بالای `translate.py` هستن:

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

## 📊 فایل‌های خروجی

برای هر session ترجمه، اینا رو میگیری:

1. **SRT ترجمه شده**: `output_persian.srt` - زیرنویس‌های فارسی نهایی
2. **بکاپ JSON**: `temp_json/input_with_timing.json` - داده کامل با زمان‌بندی
3. **لاگ ترجمه**: `translation_logs/input_translated_Persian.json` - ترجمه‌های قابل استفاده مجدد
4. **لاگ‌های Debug**: `debug_logs/YYYYMMDD_HHMMSS/` - لاگ‌های کامل session شامل:
   - SRT اصلی
   - ساختار parsed شده
   - درخواست‌ها/پاسخ‌های API
   - نتایج بررسی
   - خروجی نهایی

## 🎯 مثال

### ترجمه

```python
from translate import SRTTranslator

translator = SRTTranslator()
translator.translate("movie.srt", "movie_fa.srt")
```

### ترجمه چند فایل

```python
from pathlib import Path
from translate import SRTTranslator

translator = SRTTranslator()

for srt_file in Path(".").glob("*.srt"):
    output = f"{srt_file.stem}_persian.srt"
    print(f"Translating {srt_file}...")
    translator.translate(str(srt_file), output)
```

### بررسی بعد از ترجمه

```python
from checker import compare_srt_files

missing_subs, status = compare_srt_files("input.srt", "output_persian.srt")

if not missing_subs:
    print("✅ Perfect translation - all subtitles present!")
else:
    print(f"⚠️ Missing subtitles: {missing_subs}")
```

## 📈 فرآیند ترجمه

```
📂 input.srt (200 subtitles)
    ↓
📊 Parse SRT → استخراج شماره + زمان‌بندی + متن
    ↓
💾 ذخیره: {1: {time: "...", text: "..."}, 2: {...}, ...}
    ↓
📖 مرحله ۱: ساخت متن context برای درک AI
    ↓
🔢 مرحله ۲: ساخت JSON ترجمه {1: "text", 2: "text", ...}
    ↓
📤 ارسال به AI: "Translate with context, return EXACTLY 200 entries"
    ↓
🤖 AI با استفاده از دانش کامل context ترجمه می‌کنه
    ↓
📥 دریافت JSON فارسی: {1: "translated", 2: "translated", ...}
    ↓
✅ مرحله ۳: بررسی تعداد = 200 ✓
    ↓
⏰ ادغام داده‌های زمان‌بندی به ترجمه‌ها
    ↓
📋 اجرای checker.py
    ↓
💾 ذخیره output_persian.srt (200 subtitles) ✅
```

## 🛠 عیب‌یابی

### "API call failed"

- ✅ چک کن API key تو `translate.py` درست باشه
- ✅ اینترنتت وصل باشه (و برای ما در ایران، موضوع پراکسی چک بشه حتما(مشکل از داخل + مسدود سازی پراکسی از بیرون)، و بلاک از بیرون :| => یک وی‌پی‌ان مطمئن)
- ✅ API endpoint در دسترس باشه
- ✅ اعتبار یا لیمیت API رو چک کن

### "Validation failed - COUNT MISMATCH"

- ✅ ابزار به صورت خودکار دوباره تلاش می‌کنه (تا ۳ بار)
- ✅ `debug_logs/` رو برای پاسخ‌های API چک کن
- ✅ اگه پاسخ ناقصه، `MAX_OUTPUT_TOKENS` رو کم کن
- ✅ برای فایل‌های خیلی بزرگ chunking رو فعال کن

### "Failed to parse JSON"

- ✅ `debug_logs/` رو برای پاسخ خام API چک کن
- ✅ ابزار به صورت خودکار بلاک‌های کد markdown رو حذف می‌کنه
- ✅ مطمئن شو API پاسخ کامل برگردونده

### فایل خروجی خالی

- ✅ مطمئن شو فایل SRT ورودی معتبره
- ✅ چک کن API اعتبار کافی داشته باشه
- ✅ پیام‌های خطا تو کنسول رو بررسی کن
- ✅ `debug_logs/` رو برای اطلاعات بیشتر چک کن

### مشکلات متن فارسی

- ✅ مطمئن شو ادیتور متن از UTF-8 و RTL (راست به چپ) پشتیبانی می‌کنه
- ✅ از media playerهایی استفاده کن که زیرنویس فارسی رو پشتیبانی می‌کنن (**Pot Player**, VLC, MPC-HC)
- ✅ پیشنهاد من Pot Player هست، و میتونید با کلیک راست روی ویدئو هنگام پخش و گزینه Subtitles > Add/Select Subtitles زیرنویس های اضافه شده رو ببینید (یا همزمان هر دوتاش رو در بالا و پایین ویدئو اضافه کنید که برای ویدئو های آموزشی خیلی مناسبه و مورد علاقه من هست)
- ✅ چک کن فونت از کاراکترهای فارسی پشتیبانی کنه (پیشنهاد من فونت Vazir یادگار صابر راستی کردار عزیز )

## 📈 نکته

1. **برای ویدیوهای طولانی**: حدود ۳۰-۶۰ ثانیه برای هر ۲۰۰ زیرنویس
2. **بهینه‌سازی هزینه**: ارسال فقط متن (بدون زمان‌بندی) حدود ۵۰٪ توکن‌ها رو ذخیره می‌کنه
3. **بهترین مدل**: Gemini Flash ترجمه‌های فارسی سریع و دقیقی ارائه میده (پیشنهاد من برای ترجمه و تصحیح ساختار متن مدل های Gemini هست)
4. **فایل‌های بزرگ**: برای فایل‌هایی با ۵۰۰+ زیرنویس chunking رو فعال کن
5. **Rate Limits**: Retry با exponential backoff از API محافظت میکنه

## 📝 پشتیبانی از فرمت SRT

پشتیبانی از فرمت استاندارد SRT:

```
1
00:00:00,080 --> 00:00:01,920
First subtitle text

2
00:00:01,920 --> 00:00:04,080
Second subtitle text
```

✅ زیرنویس‌های چند خطی پشتیبانی میشن  
✅ زیرنویس‌های خالی حفظ میشن  
✅ همه فرمت‌های زمان‌بندی پشتیبانی میشن  
✅ کاراکترهای خاص و متن فارسی پشتیبانی میشن  
✅ UTF-8 با BOM پشتیبانی میشه

## 📁 ساختار

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

1. 

## 📄 لایسنس

آزاد برای استفاده و ویرایش برای پروژه‌های شخصی و تجاری.

## 🙏 تشکر

ساخته شده با ❤️ برای فارسی‌زبانان با استفاده از:

- **Avalai.ir API** - سرویس ارائه دهنده (مورد علاقه من ❤️)
- **Google Gemini** - مدل زبانی قدرتمند با پشتیبانی عالی از فارسی ❤️
- **Python** - ساده و قدرتمند ❤️

## 💡نکته: چرا Context مهمه

ترجمه زیرنویس سنتی هر خط رو جدا ترجمه می‌کنه، که باعث میشه فارسی عجیب و غریبی تولید بشه. رویکرد ما:

1. **درک صحنه**: شخصیت‌ها، احساسات، setting
2. **حفظ لحن**: رسمی/غیررسمی، جدی/کمدی
3. **استفاده از عبارات طبیعی**: اصطلاحات فارسی به جای ترجمه‌های کلمه به کلمه
4. **حفظ تفاوت‌های فرهنگی**: مناسب برای مخاطبان فارسی‌زبان

**مثال:**

- ❌ کلمه به کلمه: "من دارم می‌روم به فروشگاه" (literal)
- ✅ Contextual: "دارم برای خرید میرم" (natural Persian)

---

**⭐ اگه این ابزار بهت کمک می‌کنه زیرنویس‌های فارسی بهتری بسازی، یه ستاره به این repository بده!**

**🐛 باگ پیدا کردی؟** یه issue باز کن و لاگ‌های debug رو از `debug_logs/` ضمیمه کن

**💬 سوال داری؟** issueهای موجود رو چک کن یا یه issue جدید باز کن

و در پایان امیدوارم لذت ببرید.
