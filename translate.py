import re
import json
import os
import requests
import time
from typing import List, Dict
from pathlib import Path
from datetime import datetime

# =========================================================================
# CONFIGURATION SECTION - ADJUST THESE SETTINGS
# =========================================================================

# API Configuration
API_ENDPOINT = "https://api.avalai.ir/v1/chat/completions"  # OR your own provider
API_KEY = "YOUR_API_KEY"
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"  # I strongly suggest to use gemini-2.5-flash

# Translation Configuration
TARGET_LANGUAGE = "Persian"
SOURCE_LANGUAGE = "English"

# Processing Configuration - INCREASED FOR BETTER RESULTS
MAX_OUTPUT_TOKENS = 24576  # to handle larger responses, maybe you need to change it if the subtitle is longer.
TEMPERATURE = 0.1
TOP_P = 0.95

# Retry Configuration [rate limits, etc.]
MAX_RETRIES = 3
RETRY_DELAY = 5

# Chunking Configuration (for large files)
MAX_SUBTITLES_PER_CHUNK = 50  # Process in smaller chunks if needed
ENABLE_CHUNKING = True  # Set to False to disable chunking

# File Paths
LOG_DIR = "translation_logs"
TEMP_DIR = "temp_json"
DEBUG_DIR = "debug_logs"  # Detailed debug logs

# =========================================================================
# SRT TRANSLATOR CLASS
# =========================================================================

class SRTTranslator:
    def __init__(self):
        """Initialize the SRT Translator with configuration from above"""
        self.api_endpoint = API_ENDPOINT
        self.api_key = API_KEY
        self.model_name = MODEL_NAME
        self.target_language = TARGET_LANGUAGE
        self.source_language = SOURCE_LANGUAGE
        self.max_output_tokens = MAX_OUTPUT_TOKENS
        self.temperature = TEMPERATURE
        self.top_p = TOP_P
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY
        self.enable_chunking = ENABLE_CHUNKING
        self.max_chunk_size = MAX_SUBTITLES_PER_CHUNK
        
        # Create directories
        self.log_dir = Path(LOG_DIR)
        self.temp_dir = Path(TEMP_DIR)
        self.debug_dir = Path(DEBUG_DIR)
        self.log_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        self.debug_dir.mkdir(exist_ok=True)
        
        # Create session-specific debug directory
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.debug_dir / self.session_id
        self.session_dir.mkdir(exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"🎬 SRT SUBTITLE TRANSLATOR v2.0 (WITH FULL LOGGING)")
        print(f"{'='*70}")
        print(f"📡 API: {self.api_endpoint}")
        print(f"🤖 Model: {self.model_name}")
        print(f"🌍 Translation: {self.source_language} → {self.target_language}")
        print(f"🔢 Max Output Tokens: {self.max_output_tokens}")
        print(f"📦 Chunking: {'Enabled' if self.enable_chunking else 'Disabled'}")
        if self.enable_chunking:
            print(f"📏 Chunk Size: {self.max_chunk_size} subtitles")
        print(f"📁 Debug Session: {self.session_id}")
        print(f"{'='*70}\n")
    
    def log_to_file(self, filename: str, content: str, mode: str = 'w'):
        """Save content to a log file in the session directory"""
        filepath = self.session_dir / filename
        try:
            with open(filepath, mode, encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"⚠️ Warning: Could not save log file {filename}: {e}")
            return False
    
    def parse_srt(self, srt_file: str) -> List[Dict]:
        """Parse SRT file into structured data with timing and text"""
        print(f"📂 Reading SRT file: {srt_file}")
        
        try:
            with open(srt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Save original SRT for debugging
            self.log_to_file("00_original_srt.txt", content)
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return []
        
        # Split by double newlines to get subtitle blocks
        blocks = re.split(r'\n\s*\n', content.strip())
        subtitles = []
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                index = lines[0].strip()
                timing = lines[1].strip()
                text = '\n'.join(lines[2:])
                
                subtitles.append({
                    'index': index,
                    'time': timing,
                    'text': text
                })
        
        print(f"✅ Parsed {len(subtitles)} subtitle entries\n")
        
        # Save parsed structure
        self.log_to_file("01_parsed_structure.json", 
                        json.dumps(subtitles, ensure_ascii=False, indent=2))
        
        return subtitles
    
    def save_json_with_timing(self, subtitles: List[Dict], output_file: str) -> Dict:
        """Save full JSON with timing information"""
        json_data = {}
        for sub in subtitles:
            json_data[sub['index']] = {
                'time': sub['time'],
                'text': sub['text']
            }
        
        filepath = self.temp_dir / output_file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"💾 Saved full JSON with timing: {filepath}")
            
            # Also save to debug
            self.log_to_file("02_json_with_timing.json",
                           json.dumps(json_data, ensure_ascii=False, indent=2))
            
            return json_data
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")
            return {}
    
    def create_context_text(self, subtitles: List[Dict]) -> str:
        """Create context text for AI to understand full content"""
        context = '\n'.join([sub['text'] for sub in subtitles])
        print(f"📝 Created context text: {len(context)} characters")
        
        # Save context
        self.log_to_file("03_context_text.txt", context)
        
        return context
    
    def create_translation_json(self, subtitles: List[Dict]) -> Dict:
        """Create JSON without timing for translation"""
        json_data = {}
        for sub in subtitles:
            json_data[sub['index']] = {
                'text': sub['text']
            }
        return json_data
    
    def build_translation_prompt(self, context: str, json_data: Dict, count: int) -> str:
        """Build the exact prompt for AI API"""
        json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        
        prompt = f"""You are a professional subtitle translator specializing in {self.source_language} to {self.target_language} translation.

CONTEXT - Full subtitle content for understanding the complete narrative:
{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ CRITICAL REQUIREMENTS ⚠️

1. YOU MUST RETURN EXACTLY {count} JSON OBJECTS
2. EVERY INDEX from 1 to {count} MUST BE PRESENT
3. DO NOT skip, combine, or delete ANY entries
4. If text is empty, keep it empty - DO NOT delete the entry
5. Return COMPLETE JSON - do not truncate or cut off the response
6. Ensure the JSON is VALID and COMPLETE with closing braces

Translation Guidelines:
- Translate naturally using the full context above
- Maintain subtitle timing-appropriate length
- Keep tone and style consistent
- Preserve line breaks within subtitles
- Use commonly accepted {self.target_language} equivalents for technical terms

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

JSON TO TRANSLATE ({count} entries):

{json_str}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESPONSE FORMAT:
- Return ONLY the translated JSON
- Do NOT include explanations, comments, or markdown
- Do NOT wrap in code blocks
- Return pure JSON starting with {{ and ending with }}
- Ensure COMPLETE response - all {count} entries must be present

FINAL CHECK:
✓ Does response have exactly {count} entries?
✓ Are all indices from 1 to {count} present?
✓ Is the JSON valid and COMPLETE?
✓ Does it end with proper closing braces?"""
        
        return prompt
    
    def call_ai_api(self, prompt: str, chunk_info: str = "", retry_count: int = 0) -> str:
        """Call the Avalai.ir API with the given prompt"""
        
        # Save prompt for debugging
        prompt_filename = f"04_prompt_{chunk_info}attempt{retry_count+1}.txt"
        self.log_to_file(prompt_filename, prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_output_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p
        }
        
        # Save request payload
        request_filename = f"05_request_{chunk_info}attempt{retry_count+1}.json"
        self.log_to_file(request_filename,
                        json.dumps(payload, ensure_ascii=False, indent=2))
        
        try:
            print(f"🚀 Calling API{chunk_info}... (Attempt {retry_count + 1}/{self.max_retries + 1})")
            
            response = requests.post(
                self.api_endpoint, 
                headers=headers, 
                json=payload, 
                timeout=300  # Increased timeout
            )
            
            # Save full response for debugging
            response_filename = f"06_response_{chunk_info}attempt{retry_count+1}.txt"
            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text
            }
            self.log_to_file(response_filename,
                           json.dumps(response_data, ensure_ascii=False, indent=2))
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Save just the content for easy review
                content_filename = f"07_api_content_{chunk_info}attempt{retry_count+1}.txt"
                self.log_to_file(content_filename, content)
                
                print(f"✅ API response received ({len(content)} characters)")
                
                # Check if response looks truncated
                if not content.rstrip().endswith('}'):
                    print(f"⚠️ Warning: Response may be truncated (doesn't end with }}")
                    self.log_to_file("warning_truncated.txt", 
                                   f"Response appears truncated:\n{content[-200:]}")
                
                return content
            else:
                print(f"❌ API Error: Status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
                # Save error
                self.log_to_file(f"error_{chunk_info}attempt{retry_count+1}.txt",
                               f"Status: {response.status_code}\n{response.text}")
                
                if retry_count < self.max_retries:
                    print(f"⏳ Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    return self.call_ai_api(prompt, chunk_info, retry_count + 1)
                return ""
                    
        except Exception as e:
            print(f"❌ Error in API call: {str(e)}")
            
            # Save exception
            self.log_to_file(f"exception_{chunk_info}attempt{retry_count+1}.txt",
                           f"Exception: {str(e)}\n{type(e)}")
            
            if retry_count < self.max_retries:
                print(f"⏳ Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                return self.call_ai_api(prompt, chunk_info, retry_count + 1)
            return ""
    
    def extract_json_from_response(self, response: str, chunk_info: str = "") -> Dict:
        """Extract JSON from AI response (handles markdown code blocks)"""
        
        # Save original response
        self.log_to_file(f"08_raw_response_{chunk_info}.txt", response)
        
        # Remove markdown code blocks if present
        response = response.strip()
        if '```' in response:
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if match:
                response = match.group(1)
            else:
                response = re.sub(r'^```(?:json)?\s*', '', response)
                response = re.sub(r'\s*```$', '', response)
        
        # Save cleaned response
        self.log_to_file(f"09_cleaned_response_{chunk_info}.txt", response)
        
        try:
            parsed = json.loads(response)
            self.log_to_file(f"10_parsed_json_{chunk_info}.json",
                           json.dumps(parsed, ensure_ascii=False, indent=2))
            return parsed
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"   Response length: {len(response)} characters")
            print(f"   Response preview: {response[:300]}...")
            print(f"   Response ending: ...{response[-300:]}")
            
            # Save detailed error info
            error_info = f"""JSON Parse Error Details:
Error: {e}
Position: {e.pos if hasattr(e, 'pos') else 'unknown'}
Line: {e.lineno if hasattr(e, 'lineno') else 'unknown'}
Column: {e.colno if hasattr(e, 'colno') else 'unknown'}

Full Response Length: {len(response)}
Response Start: {response[:500]}
...
Response End: {response[-500:]}
"""
            self.log_to_file(f"error_json_parse_{chunk_info}.txt", error_info)
            
            # Try to find JSON object in response
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                try:
                    extracted = json.loads(match.group(0))
                    print(f"✓ Recovered partial JSON with {len(extracted)} entries")
                    return extracted
                except:
                    pass
            
            return {}
    
    def validate_translation(self, original: Dict, translated: Dict, chunk_info: str = "") -> bool:
        """Validate that translation has exact same structure"""
        print(f"\n🔍 Validating translation{chunk_info}...")
        
        validation_log = []
        validation_log.append(f"Original count: {len(original)}")
        validation_log.append(f"Translated count: {len(translated)}")
        
        if len(original) != len(translated):
            print(f"❌ COUNT MISMATCH!")
            print(f"   Expected: {len(original)} entries")
            print(f"   Received: {len(translated)} entries")
            
            original_keys = set(original.keys())
            translated_keys = set(translated.keys())
            missing = original_keys - translated_keys
            extra = translated_keys - original_keys
            
            if missing:
                missing_sorted = sorted(missing, key=lambda x: int(x))
                print(f"   Missing indices: {missing_sorted[:20]}...")
                validation_log.append(f"Missing: {missing_sorted}")
            
            if extra:
                extra_sorted = sorted(extra, key=lambda x: int(x))
                print(f"   Extra indices: {extra_sorted[:20]}...")
                validation_log.append(f"Extra: {extra_sorted}")
            
            # Save validation failure details
            self.log_to_file(f"validation_failed_{chunk_info}.txt",
                           "\n".join(validation_log))
            
            return False
        
        missing_keys = []
        for key in original.keys():
            if key not in translated:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"❌ MISSING KEYS: {missing_keys[:10]}...")
            validation_log.append(f"Missing keys: {missing_keys}")
            self.log_to_file(f"validation_failed_{chunk_info}.txt",
                           "\n".join(validation_log))
            return False
        
        print(f"✅ Validation passed: {len(translated)} entries matched perfectly")
        validation_log.append("✅ VALIDATION PASSED")
        self.log_to_file(f"validation_success_{chunk_info}.txt",
                       "\n".join(validation_log))
        return True
    
    def translate_chunk(self, subtitles: List[Dict], chunk_num: int = 0, total_chunks: int = 1) -> Dict:
        """Translate a single chunk of subtitles"""
        
        chunk_info = f"_chunk{chunk_num+1}of{total_chunks}_" if total_chunks > 1 else ""
        
        print(f"\n{'─'*70}")
        if total_chunks > 1:
            print(f"📦 PROCESSING CHUNK {chunk_num+1}/{total_chunks} ({len(subtitles)} subtitles)")
        print(f"{'─'*70}")
        
        # Create context text
        context = self.create_context_text(subtitles)
        
        # Create translation JSON
        translation_json = self.create_translation_json(subtitles)
        print(f"📊 Created translation JSON: {len(translation_json)} entries")
        
        # Build prompt
        prompt = self.build_translation_prompt(context, translation_json, len(subtitles))
        print(f"✅ Prompt ready: {len(prompt)} characters")
        
        # Call API
        response = self.call_ai_api(prompt, chunk_info)
        
        if not response:
            print(f"❌ Translation failed - no response from API")
            return {}
        
        # Extract JSON
        translated_json = self.extract_json_from_response(response, chunk_info)
        
        if not translated_json:
            print(f"❌ Failed to extract valid JSON from response")
            return {}
        
        print(f"✅ Extracted {len(translated_json)} translated entries")
        
        # Validate
        if not self.validate_translation(translation_json, translated_json, chunk_info):
            print(f"❌ Validation failed - translation incomplete")
            return {}
        
        return translated_json
    
    def merge_timing(self, original_with_timing: Dict, translated: Dict) -> List[Dict]:
        """Merge timing information back into translated subtitles"""
        print(f"🔗 Merging timing information...")
        merged = []
        for index in sorted(original_with_timing.keys(), key=lambda x: int(x)):
            merged.append({
                'index': index,
                'time': original_with_timing[index]['time'],
                'text': translated[index]['text']
            })
        print(f"✅ Merged {len(merged)} subtitle entries")
        
        # Save merged result
        self.log_to_file("11_merged_final.json",
                        json.dumps(merged, ensure_ascii=False, indent=2))
        
        return merged
    
    def save_srt(self, subtitles: List[Dict], output_file: str):
        """Save subtitles back to SRT format"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, sub in enumerate(subtitles):
                    f.write(f"{sub['index']}\n")
                    f.write(f"{sub['time']}\n")
                    f.write(f"{sub['text']}\n")
                    if i < len(subtitles) - 1:
                        f.write("\n")
            
            print(f"💾 Saved translated SRT: {output_file}")
            
            # Also save to debug folder
            self.log_to_file("12_final_output.srt",
                           open(output_file, 'r', encoding='utf-8').read())
            
            return True
        except Exception as e:
            print(f"❌ Error saving SRT: {e}")
            self.log_to_file("error_save_srt.txt", str(e))
            return False
    
    def save_translation_log(self, original_file: str, translated: Dict):
        """Save translation log for reuse"""
        log_file = self.log_dir / f"{Path(original_file).stem}_translated_{self.target_language}.json"
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(translated, f, ensure_ascii=False, indent=2)
            print(f"📋 Saved translation log: {log_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving log: {e}")
            return False
    
    def translate(self, srt_file: str, output_srt: str = None) -> bool:
        """
        Main translation workflow
        
        Args:
            srt_file: Input SRT file path
            output_srt: Output SRT file path (optional)
        
        Returns:
            bool: True if translation successful, False otherwise
        """
        if output_srt is None:
            output_srt = str(Path(srt_file).stem) + f"_{self.target_language.lower()}.srt"
        
        print(f"\n{'='*70}")
        print(f"🎯 STARTING TRANSLATION PROCESS")
        print(f"{'='*70}")
        print(f"📥 Input:  {srt_file}")
        print(f"📤 Output: {output_srt}")
        print(f"📁 Debug:  {self.session_dir}")
        print(f"{'='*70}\n")
        
        # Parse SRT
        print(f"{'─'*70}")
        print(f"STEP 1: PARSING SRT FILE")
        print(f"{'─'*70}")
        subtitles = self.parse_srt(srt_file)
        if not subtitles:
            print("❌ Failed to parse SRT file")
            return False
        
        # Save full JSON with timing
        print(f"\n{'─'*70}")
        print(f"STEP 2: SAVING JSON WITH TIMING")
        print(f"{'─'*70}")
        json_with_timing_file = f"{Path(srt_file).stem}_with_timing.json"
        original_with_timing = self.save_json_with_timing(subtitles, json_with_timing_file)
        if not original_with_timing:
            print("❌ Failed to save JSON with timing")
            return False
        
        # Decide whether to chunk
        total_subtitles = len(subtitles)
        should_chunk = self.enable_chunking and total_subtitles > self.max_chunk_size
        
        if should_chunk:
            print(f"\n{'─'*70}")
            print(f"📦 CHUNKING ENABLED: {total_subtitles} subtitles > {self.max_chunk_size} limit")
            print(f"{'─'*70}")
            
            chunks = []
            for i in range(0, total_subtitles, self.max_chunk_size):
                chunks.append(subtitles[i:i + self.max_chunk_size])
            
            print(f"📦 Created {len(chunks)} chunks")
            
            # Translate each chunk
            all_translated = {}
            for i, chunk in enumerate(chunks):
                translated_chunk = self.translate_chunk(chunk, i, len(chunks))
                if not translated_chunk:
                    print(f"❌ Chunk {i+1} translation failed")
                    return False
                all_translated.update(translated_chunk)
                print(f"✅ Chunk {i+1}/{len(chunks)} complete")
            
            translated_json = all_translated
            
        else:
            print(f"\n{'─'*70}")
            print(f"STEP 3: TRANSLATING (SINGLE PASS)")
            print(f"{'─'*70}")
            translated_json = self.translate_chunk(subtitles)
            if not translated_json:
                return False
        
        # Merge timing back
        print(f"\n{'─'*70}")
        print(f"FINAL STEP: MERGING AND SAVING")
        print(f"{'─'*70}")
        final_subtitles = self.merge_timing(original_with_timing, translated_json)
        
        # Save translated SRT
        if not self.save_srt(final_subtitles, output_srt):
            print("❌ Failed to save translated SRT")
            return False
        
        # Save translation log
        self.save_translation_log(srt_file, translated_json)
        
        print(f"\n{'='*70}")
        print(f"🎉 TRANSLATION COMPLETE!")
        print(f"{'='*70}")
        print(f"✅ Translated {len(final_subtitles)} subtitle entries")
        print(f"✅ Output saved: {output_srt}")
        print(f"📁 Debug logs: {self.session_dir}")
        print(f"{'='*70}\n")
        
        # Create summary file
        summary = f"""Translation Summary
==================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Input: {srt_file}
Output: {output_srt}
Total Subtitles: {len(final_subtitles)}
Source Language: {self.source_language}
Target Language: {self.target_language}
Model: {self.model_name}
Chunking: {'Yes' if should_chunk else 'No'}
Status: SUCCESS ✅
"""
        self.log_to_file("SUMMARY.txt", summary)
        
        return True


# =========================================================================
# MAIN ENTRY POINT
# =========================================================================

def main():
    """Main function to run the translator"""
    
    # Check API key
    if API_KEY == "your-api-key-here":
        print("\n" + "!"*70)
        print("⚠️  WARNING: Please set your API_KEY in the configuration section!")
        print("!"*70 + "\n")
        return
    
    # Create translator instance
    translator = SRTTranslator()
    
    # Example usage
    input_file = "input.srt"
    output_file = "output_persian.srt"
    
    if not Path(input_file).exists():
        print(f"❌ Input file not found: {input_file}")
        print(f"💡 Please place your SRT file in the same directory as this script")
        return
    
    # Perform translation
    success = translator.translate(input_file, output_file)
    
    if success:
        print("✅ All done! Check your output file.")
        print(f"📁 Debug logs saved to: debug_logs/{translator.session_id}/")
    else:
        print("❌ Translation failed. Check the debug logs for details.")
        print(f"📁 Debug logs: debug_logs/{translator.session_id}/")


if __name__ == "__main__":

    main()
