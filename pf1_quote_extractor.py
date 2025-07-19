# 📤 PF1 Quote Column Extractor (PDF.co + OpenAI)
# Scans all PDF quotes in folder using PDF.co for OCR + GPT for field extraction.
# Returns suggested new Airtable columns with sample values.

import os
import requests
import json
import csv
from openai import OpenAI
from collections import defaultdict
from time import sleep
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 🔐 Keys
PDFCO_API_KEY = os.getenv("PDFCO_API_KEY", "rushabh@machinecraft.org_BsvgOq6OwyqWriVHJCxSxko7ZVnte3ELH5oU4zlu4U1Ge4fEj4dBG4nVGw5M1kUv")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
openai = OpenAI(api_key=OPENAI_API_KEY)

# Known fields to exclude (from specs.json if available)
known_fields = set()
if os.path.exists("specs.json"):
    with open("specs.json") as f:
        specs = json.load(f)
        known_fields = set(specs.keys())
    print(f"📋 Loaded {len(known_fields)} known fields from specs.json")

# STEP 1: Extract text from PDF using PDF.co API
def extract_text_pdfco(file_path):
    """Extract text from PDF using PDF.co API with OCR capabilities"""
    
    try:
        # Step 1: Upload file to PDF.co
        upload_url = "https://api.pdf.co/v1/file/upload"
        
        with open(file_path, "rb") as f:
            upload_response = requests.post(
                upload_url,
                headers={"x-api-key": PDFCO_API_KEY},
                files={"file": f}
            )
        
        if not upload_response.ok:
            print(f"⚠️ PDF.co Upload Error on {file_path}: {upload_response.status_code} - {upload_response.text}")
            return ""
        
        upload_data = upload_response.json()
        uploaded_file_url = upload_data["url"]
        
        # Step 2: Convert PDF to text
        convert_url = "https://api.pdf.co/v1/pdf/convert/to/text"
        convert_response = requests.post(
            convert_url,
            headers={"x-api-key": PDFCO_API_KEY},
            json={
                "url": uploaded_file_url,
                "inline": True,
                "pages": "0-",
                "ocr": True
            }
        )
        
        if convert_response.ok:
            return convert_response.text
        else:
            print(f"⚠️ PDF.co Convert Error on {file_path}: {convert_response.status_code} - {convert_response.text}")
            return ""
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return ""

# STEP 2: Use GPT to extract field names and values
def extract_fields_from_text(text, filename=""):
    """Extract structured fields from quote text using GPT-4"""
    prompt = f"""
You are an intelligent spec extractor for industrial PF1 thermoforming machine quotes.

From the quote text below, extract **all field names and values** relevant to the PF1 machine. 
Focus on technical specifications, commercial terms, and machine features.

Return ONLY a valid JSON object with:
- keys as standardized column names (use consistent naming)
- values as the actual values mentioned in the quote

Extract fields like: forming area, heater type, plug assist, CE compliance, warranty, price, power consumption, autoloader, vacuum pump, etc.

QUOTE TEXT:
{text[:8000]}  # Limit text length for API efficiency

FILENAME: {filename}
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up the response to ensure it's valid JSON
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        return json.loads(content)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error for {filename}: {e}")
        print(f"Raw response: {content[:200]}...")
        return {}
    except Exception as e:
        print(f"❌ OpenAI API error for {filename}: {e}")
        return {}

# STEP 3: Process all PDFs in PF1 folder
def process_all_pdfs():
    """Process all PDF files in PF1 directory"""
    field_values = defaultdict(set)
    processed_files = 0
    max_files = 10  # Stop after 10 files
    
    # Find all PDF files in PF1 folder
    pf1_dir = "./PF1"
    if not os.path.exists(pf1_dir):
        print(f"❌ PF1 directory not found: {pf1_dir}")
        return field_values
    
    pdf_files = []
    for file in os.listdir(pf1_dir):
        if file.lower().endswith(".pdf"):
            pdf_files.append(os.path.join(pf1_dir, file))
    
    total_files = len(pdf_files)
    print(f"🔍 Found {total_files} PDF files in PF1 folder to process...")
    print(f"🛑 Will process only first {max_files} files for demo...")
    
    for filepath in pdf_files:
        processed_files += 1
        print(f"📄 Processing {processed_files}/{min(max_files, total_files)}: {filepath}...")
        
        # Extract text from PDF
        text = extract_text_pdfco(filepath)
        if not text:
            print(f"⚠️ No text extracted from {filepath}")
            continue
        
        # Rate limiting
        sleep(2)
        
        # Extract fields using GPT
        extracted = extract_fields_from_text(text, filepath)
        
        # Store new fields
        for key, val in extracted.items():
            if key not in known_fields:
                field_values[key.strip()].add(str(val).strip())
        
        print(f"✅ Extracted {len(extracted)} fields from {filepath}")
        
        # Stop after max_files
        if processed_files >= max_files:
            print(f"🛑 Stopped after processing {max_files} files as requested")
            break
    
    return field_values

# STEP 4: Generate output
def generate_output(field_values):
    """Generate CSV and console output"""
    print(f"\n🆕 Found {len(field_values)} new potential Airtable columns:")
    print("=" * 60)
    
    # Console output
    for field, values in sorted(field_values.items()):
        sample_values = sorted(list(values))[:5]  # Show first 5 values
        print(f"• {field}: {sample_values}")
    
    # CSV output with detailed values
    csv_filename = "column_suggestions.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Column Name', 'All Values Found', 'Value Count'])
        
        for field, values in sorted(field_values.items()):
            # Show all values found, separated by pipes
            all_values = " | ".join(sorted(list(values)))
            writer.writerow([field, all_values, len(values)])
    
    print(f"\n💾 Detailed results saved to: {csv_filename}")
    
    # Summary stats
    total_values = sum(len(values) for values in field_values.values())
    print(f"\n📊 Summary:")
    print(f"   • New columns found: {len(field_values)}")
    print(f"   • Total values extracted: {total_values}")
    print(f"   • Average values per column: {total_values/len(field_values):.1f}" if field_values else "0")
    
    # Show top 5 most common fields
    if field_values:
        print(f"\n🏆 Top 5 most common fields:")
        sorted_fields = sorted(field_values.items(), key=lambda x: len(x[1]), reverse=True)
        for i, (field, values) in enumerate(sorted_fields[:5], 1):
            print(f"   {i}. {field}: {len(values)} values")

# Main execution
if __name__ == "__main__":
    print("🚀 PF1 Quote Column Extractor Starting...")
    print("=" * 50)
    
    # Process all PDFs
    field_values = process_all_pdfs()
    
    # Generate output
    if field_values:
        generate_output(field_values)
    else:
        print("❌ No new fields found or no PDFs processed successfully")
    
    print("\n✅ Extraction complete!") 