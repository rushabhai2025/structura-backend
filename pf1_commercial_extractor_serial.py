# 💰 PF1 Commercial Extractor - SERIAL VERSION (50 PDFs)
# Extracts commercial specifications from PF1 quotes (pricing, terms, options, etc.)

import os
import requests
import json
import pandas as pd
from openai import OpenAI
from collections import defaultdict
from time import sleep
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# 🔐 Keys
PDFCO_API_KEY = os.getenv("PDFCO_API_KEY", "rushabh@machinecraft.org_BsvgOq6OwyqWriVHJCxSxko7ZVnte3ELH5oU4zlu4U1Ge4fEj4dBG4nVGw5M1kUv")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
openai = OpenAI(api_key=OPENAI_API_KEY)

# Define commercial-focused columns
COMMERCIAL_COLUMNS = {
    # Machine Identification
    'machine_model': 'Machine Model Name',
    'machine_series': 'Machine Series',
    'machine_type': 'Machine Type',
    
    # Pricing Information
    'base_price': 'Base Machine Price',
    'total_price': 'Total Quote Price',
    'currency': 'Price Currency',
    'price_validity': 'Price Validity Period',
    'price_terms': 'Price Terms',
    
    # Options & Add-ons
    'options_list': 'Available Options',
    'option_prices': 'Individual Option Prices',
    'total_options_cost': 'Total Options Cost',
    'optional_features': 'Optional Features',
    
    # Commercial Terms
    'lead_time': 'Delivery Lead Time',
    'payment_terms': 'Payment Terms',
    'payment_schedule': 'Payment Schedule',
    'delivery_terms': 'Delivery Terms',
    'warranty_period': 'Warranty Period',
    'warranty_terms': 'Warranty Terms',
    
    # Installation & Service
    'installation_terms': 'Installation Terms',
    'installation_cost': 'Installation Cost',
    'commissioning_terms': 'Commissioning Terms',
    'training_terms': 'Training Terms',
    'service_terms': 'Service Terms',
    
    # Logistics
    'packaging_terms': 'Packaging Terms',
    'shipping_terms': 'Shipping Terms',
    'machine_weight': 'Machine Weight',
    'machine_dimensions': 'Machine Dimensions',
    'machine_footprint': 'Machine Footprint',
    'crating_requirements': 'Crating Requirements',
    
    # Component Brands
    'heater_brand': 'Heater Brand/Make',
    'motor_brand': 'Motor Brand/Make',
    'pump_brand': 'Vacuum Pump Brand',
    'controller_brand': 'Controller Brand',
    'sensor_brand': 'Sensor Brand',
    'valve_brand': 'Valve Brand',
    'component_brands': 'Other Component Brands',
    
    # Commercial Details
    'quote_number': 'Quote Number',
    'quote_date': 'Quote Date',
    'valid_until': 'Quote Valid Until',
    'sales_contact': 'Sales Contact',
    'customer_name': 'Customer Name',
    'customer_company': 'Customer Company',
    'project_name': 'Project Name',
    
    # Additional Commercial Info
    'discount_offered': 'Discount Offered',
    'special_terms': 'Special Terms',
    'maintenance_contract': 'Maintenance Contract',
    'spare_parts_terms': 'Spare Parts Terms',
    'technical_support': 'Technical Support Terms'
}

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

# STEP 2: Extract machine model from filename
def extract_machine_model(filename):
    """Extract machine model from filename using regex patterns"""
    filename_lower = filename.lower()
    
    # Common PF1 patterns
    patterns = [
        r'pf1[-\s]?(\w+)[-\s]?(\d+)',  # PF1-C-3020, PF1 C 3020
        r'pf1[-\s]?(\d+)',  # PF1 3020
        r'(\d+)[-\s]?pf1',  # 3020 PF1
        r'pf1[-\s]?(\w+)',  # PF1-C
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename_lower)
        if match:
            if len(match.groups()) == 2:
                return f"PF1-{match.group(1).upper()}-{match.group(2)}"
            elif len(match.groups()) == 1:
                return f"PF1-{match.group(1).upper()}"
    
    # If no pattern found, use a simplified version
    return filename.replace('.pdf', '').replace('_', '-').upper()

# STEP 3: Use GPT to extract commercial fields
def extract_commercial_fields_from_text(text, filename=""):
    """Extract commercial specifications from quote text using GPT-4"""
    prompt = f"""
You are a commercial analyst specializing in industrial machine quotes. Extract ALL commercial and business-related information from this PF1 thermoforming machine quote.

Focus on:
- Machine model identification
- Pricing (base price, total price, currency, validity)
- Options and their individual prices
- Commercial terms (lead time, payment terms, delivery terms)
- Installation and service terms
- Logistics (packaging, shipping, weight, dimensions)
- Component brands and makes
- Warranty and support terms

Return ONLY a valid JSON object with these exact field names:
{list(COMMERCIAL_COLUMNS.keys())}

Extract the actual values mentioned in the quote. If a field is not mentioned, leave it empty.

QUOTE TEXT:
{text[:8000]}  # Limit text length for API efficiency

FILENAME: {filename}
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=3000
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

# STEP 4: Process up to 50 PDFs for comprehensive commercial data
def process_serial_pdfs():
    """Process up to 50 PDFs and extract commercial specifications"""
    commercial_data = {}
    processed_files = 0
    max_files = 50  # Process up to 50 files
    
    # Find all PDF files in PF1 folder
    pf1_dir = "./PF1"
    if not os.path.exists(pf1_dir):
        print(f"❌ PF1 directory not found: {pf1_dir}")
        return commercial_data
    
    pdf_files = []
    for file in os.listdir(pf1_dir):
        if file.lower().endswith(".pdf"):
            pdf_files.append(os.path.join(pf1_dir, file))
    
    total_files = len(pdf_files)
    print(f"🔍 Found {total_files} PDF files in PF1 folder...")
    print(f"🚀 COMMERCIAL SERIAL MODE: Processing up to {max_files} files...")
    
    for filepath in pdf_files:
        processed_files += 1
        filename = os.path.basename(filepath)
        print(f"📄 Processing {processed_files}/{min(max_files, total_files)}: {filename}...")
        
        # Extract machine model from filename
        machine_model = extract_machine_model(filename)
        print(f"   🏷️  Machine Model: {machine_model}")
        
        # Extract text from PDF
        text = extract_text_pdfco(filepath)
        if not text:
            print(f"⚠️ No text extracted from {filename}")
            continue
        
        # Rate limiting
        sleep(2)
        
        # Extract commercial fields using GPT
        extracted = extract_commercial_fields_from_text(text, filename)
        
        # Store data for this machine
        commercial_data[machine_model] = extracted
        
        print(f"✅ Extracted {len(extracted)} commercial fields from {filename}")
        
        # Stop after max_files
        if processed_files >= max_files:
            print(f"🛑 Commercial serial processing completed: Processed {max_files} files")
            break
    
    return commercial_data

# STEP 5: Create comprehensive Excel file with commercial data
def create_commercial_excel(commercial_data):
    """Create comprehensive Excel file with commercial specifications"""
    
    # Create DataFrame
    rows = []
    for machine_model, fields in commercial_data.items():
        row = {'Machine Model': machine_model}
        
        # Add all commercial columns
        for field_name, field_description in COMMERCIAL_COLUMNS.items():
            value = fields.get(field_name, '')
            row[field_description] = value
        
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Reorder columns to put Machine Model first
    cols = ['Machine Model'] + list(COMMERCIAL_COLUMNS.values())
    df = df[cols]
    
    # Save to Excel
    excel_filename = "PF1_Commercial_Specifications_Complete.xlsx"
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Commercial Specs', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Commercial Specs']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"\n💾 Comprehensive commercial Excel file created: {excel_filename}")
    print(f"📊 Commercial data summary:")
    print(f"   • Machine models: {len(commercial_data)}")
    print(f"   • Total commercial columns: {len(COMMERCIAL_COLUMNS) + 1}")
    print(f"   • Data points: {len(commercial_data) * len(COMMERCIAL_COLUMNS)}")
    
    # Show pricing statistics
    pricing_fields = ['base_price', 'total_price', 'currency']
    pricing_data = []
    for machine_model, fields in commercial_data.items():
        for field in pricing_fields:
            if fields.get(field):
                pricing_data.append(fields[field])
    
    if pricing_data:
        print(f"   • Pricing information found: {len(pricing_data)} data points")
    
    return excel_filename

# Main execution
if __name__ == "__main__":
    print("💰 PF1 Commercial Extractor - SERIAL MODE")
    print("=" * 60)
    print("Extracting commercial specifications from up to 50 PDFs...")
    
    # Process PDFs and extract commercial data
    commercial_data = process_serial_pdfs()
    
    if commercial_data:
        # Create Excel file
        excel_file = create_commercial_excel(commercial_data)
        
        print(f"\n✅ Comprehensive commercial extraction complete!")
        print(f"📁 File: {excel_file}")
        print(f"🎯 Ready for commercial analysis and decision making!")
    else:
        print("❌ No commercial data extracted from PDFs") 