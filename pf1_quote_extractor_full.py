# 📤 PF1 Quote Column Extractor - FULL VERSION (All PDFs)
# Complete script for processing all PDFs and merging with existing data

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

# Load existing CSV data if available
def load_existing_csv_data():
    """Load existing CSV data to merge with new findings"""
    existing_data = defaultdict(set)
    
    # Try to load from main CSV first
    if os.path.exists("column_suggestions.csv"):
        with open("column_suggestions.csv", 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                column_name = row['Column Name']
                values_str = row['All Values Found']
                if values_str:
                    values = values_str.split(" | ")
                    existing_data[column_name].update(values)
        print(f"📂 Loaded existing data from column_suggestions.csv")
    
    # Also try to load from test CSV
    if os.path.exists("column_suggestions_test.csv"):
        with open("column_suggestions_test.csv", 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                column_name = row['Column Name']
                values_str = row['All Values Found']
                if values_str:
                    values = values_str.split(" | ")
                    existing_data[column_name].update(values)
        print(f"📂 Loaded existing data from column_suggestions_test.csv")
    
    return existing_data

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

# STEP 3: Process all remaining PDFs in PF1 folder
def process_all_pdfs():
    """Process all PDF files in PF1 directory and merge with existing data"""
    # Load existing data
    field_values = load_existing_csv_data()
    processed_files = 0
    skipped_files = 0
    
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
    print(f"🔍 Found {total_files} PDF files in PF1 folder...")
    print(f"📊 Starting with {len(field_values)} existing columns...")
    
    for filepath in pdf_files:
        processed_files += 1
        print(f"📄 Processing {processed_files}/{total_files}: {os.path.basename(filepath)}...")
        
        # Extract text from PDF
        text = extract_text_pdfco(filepath)
        if not text:
            print(f"⚠️ No text extracted from {os.path.basename(filepath)}")
            skipped_files += 1
            continue
        
        # Rate limiting
        sleep(2)
        
        # Extract fields using GPT
        extracted = extract_fields_from_text(text, filepath)
        
        # Store new fields
        new_fields_count = 0
        for key, val in extracted.items():
            if key not in known_fields:
                field_values[key.strip()].add(str(val).strip())
                new_fields_count += 1
        
        print(f"✅ Extracted {len(extracted)} fields ({new_fields_count} new) from {os.path.basename(filepath)}")
    
    print(f"\n📈 Processing Summary:")
    print(f"   • Total files processed: {processed_files}")
    print(f"   • Files skipped: {skipped_files}")
    print(f"   • Total columns after processing: {len(field_values)}")
    
    return field_values

# STEP 4: Generate comprehensive output
def generate_full_output(field_values):
    """Generate comprehensive CSV and console output"""
    print(f"\n🆕 COMPLETE DATASET: Found {len(field_values)} total Airtable columns:")
    print("=" * 80)
    
    # Console output (show top 20 most common)
    sorted_fields = sorted(field_values.items(), key=lambda x: len(x[1]), reverse=True)
    print("🏆 Top 20 most common fields:")
    for i, (field, values) in enumerate(sorted_fields[:20], 1):
        sample_values = sorted(list(values))[:3]  # Show first 3 values
        print(f"   {i:2d}. {field}: {len(values)} values - {sample_values}")
    
    # CSV output with all values
    csv_filename = "column_suggestions_complete.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Column Name', 'All Values Found', 'Value Count', 'Sample Values'])
        
        for field, values in sorted_fields:
            # Show all values found, separated by pipes
            all_values = " | ".join(sorted(list(values)))
            sample_values = " | ".join(sorted(list(values))[:5])  # First 5 as samples
            writer.writerow([field, all_values, len(values), sample_values])
    
    print(f"\n💾 Complete results saved to: {csv_filename}")
    
    # Summary stats
    total_values = sum(len(values) for values in field_values.values())
    print(f"\n📊 Complete Dataset Summary:")
    print(f"   • Total columns found: {len(field_values)}")
    print(f"   • Total values extracted: {total_values}")
    print(f"   • Average values per column: {total_values/len(field_values):.1f}" if field_values else "0")
    
    # Show value distribution
    if field_values:
        value_counts = [len(values) for values in field_values.values()]
        print(f"   • Columns with 1 value: {sum(1 for c in value_counts if c == 1)}")
        print(f"   • Columns with 2-5 values: {sum(1 for c in value_counts if 2 <= c <= 5)}")
        print(f"   • Columns with 6+ values: {sum(1 for c in value_counts if c >= 6)}")

# Main execution
if __name__ == "__main__":
    print("🚀 PF1 Quote Column Extractor - FULL DATASET MODE")
    print("=" * 60)
    print("Processing all PDFs and merging with existing data...")
    
    # Process all PDFs
    field_values = process_all_pdfs()
    
    # Generate comprehensive output
    if field_values:
        generate_full_output(field_values)
    else:
        print("❌ No fields found in processing")
    
    print("\n✅ Complete extraction finished!")
    print("📊 Check column_suggestions_complete.csv for full dataset") 