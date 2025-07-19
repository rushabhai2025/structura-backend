# 📊 PF1 Excel Generator - Machine Models vs Fields Matrix
# Creates Excel file with machine models as rows and extracted fields as columns

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

# Define the standardized columns based on your categorization
STANDARD_COLUMNS = {
    # Technical Specifications
    'max_forming_area': 'Machine Capacity',
    'heater_type': 'Heating Technology',
    'total_heater_load': 'Power Consumption',
    'heater_control_system': 'Control Mechanism',
    
    # Machine Movements
    'bottom_table_movement': 'Bottom Table Movement',
    'top_table_movement': 'Top Table Movement',
    'sheet_clamping': 'Sheet Clamp Movement',
    'heater_movement_type': 'Heater Movement',
    
    # Machine Features
    'sag_control_system': 'Sheet Control',
    'sheet_loading': 'Loading Method',
    'vacuum_pump_capacity': 'Vacuum Performance',
    'max_tool_depth': 'Tool Specifications',
    
    # Contact Information
    'contact_name': 'Primary Contact',
    'contact_email': 'Email Address',
    'contact_mobile': 'Mobile Number',
    'contact_position': 'Job Title',
    'client_name': 'Customer Contact',
    'company_name': 'Customer Company',
    
    # Document Management
    'quote_number': 'Quote Identifier',
    'date': 'Quote Date',
    'quote_date': 'Additional Date',
    
    # Power & Energy
    'total_connected_load': 'Total Power',
    'total_heating_load': 'Heating Power',
    'total_other_load': 'Other Power Consumption',
    'energy_efficiency': 'Efficiency Features',
    
    # Automation & Features
    'automatic_sheet_loading': 'Sheet Automation',
    'automatic_part_unloading': 'Unloading Automation',
    'quick_tool_loading': 'Tool Loading Speed',
    'universal_sheet_size_setting': 'Universal Aperture Automation',
    
    # Dimensions & Measurements
    'heater_size': 'Heater Dimensions',
    'clamping_edge_size': 'Clamping Specifications',
    'floor_plan': 'Machine Footprint',
    'max_stroke_z': 'Z-axis Movement',
    'max_plug_assist_height': 'Plug Assist Range',
    'max_tool_height': 'Tool Height Limit',
    'min_forming_area': 'Minimum Capacity',
    
    # Time & Performance
    'adjustment_time': 'Setup Time',
    'loading_unloading_time': 'Cycle Time',
    'tool_clamp_time_bolts': 'Bolt Clamping Time',
    'tool_clamp_time_pneumatic': 'Pneumatic Clamping Time',
    'preblow_bubble_height_adjustment': 'Bubble Control',
    
    # Equipment & Components
    'heater_make': 'Heater Manufacturer',
    'heater_movement_make': 'Movement System Brand',
    'tool_loading_method': 'Tool Loading Approach',
    'cooling_system_type': 'Cooling System',
    'sheet_temperature_sensing': 'Temperature Monitoring'
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

# STEP 3: Use GPT to extract field names and values
def extract_fields_from_text(text, filename=""):
    """Extract structured fields from quote text using GPT-4"""
    prompt = f"""
You are an intelligent spec extractor for industrial PF1 thermoforming machine quotes.

From the quote text below, extract **all field names and values** relevant to the PF1 machine. 
Focus on technical specifications, commercial terms, and machine features.

Return ONLY a valid JSON object with:
- keys as standardized column names (use consistent naming)
- values as the actual values mentioned in the quote

Use these exact field names:
{list(STANDARD_COLUMNS.keys())}

Extract the actual values mentioned in the quote for each field.

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

# STEP 4: Process up to 50 PDFs and create Excel
def process_pdfs_and_create_excel():
    """Process up to 50 PDFs and create Excel file with machine models vs fields"""
    machine_data = {}
    processed_files = 0
    max_files = 50  # Process up to 50 files
    
    # Find all PDF files in PF1 folder
    pf1_dir = "./PF1"
    if not os.path.exists(pf1_dir):
        print(f"❌ PF1 directory not found: {pf1_dir}")
        return
    
    pdf_files = []
    for file in os.listdir(pf1_dir):
        if file.lower().endswith(".pdf"):
            pdf_files.append(os.path.join(pf1_dir, file))
    
    total_files = len(pdf_files)
    print(f"🔍 Found {total_files} PDF files in PF1 folder...")
    print(f"🚀 SERIAL MODE: Processing up to {max_files} files...")
    
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
        
        # Extract fields using GPT
        extracted = extract_fields_from_text(text, filename)
        
        # Store data for this machine
        machine_data[machine_model] = extracted
        
        print(f"✅ Extracted {len(extracted)} fields from {filename}")
        
        # Stop after max_files
        if processed_files >= max_files:
            print(f"🛑 Serial processing completed: Processed {max_files} files")
            break
    
    return machine_data

# STEP 5: Create Excel file
def create_excel_file(machine_data):
    """Create Excel file with machine models as rows and fields as columns"""
    
    # Create DataFrame
    rows = []
    for machine_model, fields in machine_data.items():
        row = {'Machine Model': machine_model}
        
        # Add all standard columns
        for field_name, field_description in STANDARD_COLUMNS.items():
            value = fields.get(field_name, '')
            row[field_description] = value
        
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Reorder columns to put Machine Model first
    cols = ['Machine Model'] + list(STANDARD_COLUMNS.values())
    df = df[cols]
    
    # Save to Excel
    excel_filename = "PF1_Machine_Specifications.xlsx"
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Machine Specs', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Machine Specs']
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
    
    print(f"\n💾 Excel file created: {excel_filename}")
    print(f"📊 Data summary:")
    print(f"   • Machine models: {len(machine_data)}")
    print(f"   • Total columns: {len(STANDARD_COLUMNS) + 1}")
    print(f"   • Data points: {len(machine_data) * len(STANDARD_COLUMNS)}")
    
    return excel_filename

# Main execution
if __name__ == "__main__":
    print("📊 PF1 Excel Generator - Machine Models vs Fields Matrix")
    print("=" * 60)
    print("Processing up to 50 PDFs to create comprehensive Excel file...")
    
    # Process PDFs and extract data
    machine_data = process_pdfs_and_create_excel()
    
    if machine_data:
        # Create Excel file
        excel_file = create_excel_file(machine_data)
        
        print(f"\n✅ Excel generation complete!")
        print(f"📁 File: {excel_file}")
        print(f"🎯 Ready for review and expansion!")
    else:
        print("❌ No data extracted from PDFs") 