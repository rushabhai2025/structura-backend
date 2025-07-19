# 🚀 PF1 Comprehensive Extractor - ALL PDFs
# Creates 3 specialized Excel files: Technical, Commercial, and Basic Details

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

# Define Technical Specifications (for Engineers)
TECHNICAL_COLUMNS = {
    # Machine Identification
    'machine_model': 'Machine Model',
    'machine_type': 'Machine Type',
    'machine_series': 'Machine Series',
    
    # Core Technical Specifications
    'forming_area': 'Forming Area (mm)',
    'forming_depth': 'Forming Depth (mm)',
    'sheet_size': 'Max Sheet Size (mm)',
    'sheet_thickness': 'Sheet Thickness Range (mm)',
    'vacuum_pressure': 'Vacuum Pressure (bar)',
    'air_pressure': 'Air Pressure (bar)',
    'heating_power': 'Heating Power (kW)',
    'cooling_power': 'Cooling Power (kW)',
    'cycle_time': 'Cycle Time (seconds)',
    'production_capacity': 'Production Capacity (parts/hour)',
    
    # Mechanical Specifications
    'machine_weight': 'Machine Weight (kg)',
    'machine_dimensions': 'Machine Dimensions (LxWxH mm)',
    'machine_footprint': 'Machine Footprint (m²)',
    'power_consumption': 'Power Consumption (kW)',
    'air_consumption': 'Air Consumption (L/min)',
    'water_consumption': 'Water Consumption (L/min)',
    
    # Automation & Control
    'automation_level': 'Automation Level',
    'control_system': 'Control System',
    'hmi_type': 'HMI Type',
    'programming_method': 'Programming Method',
    'safety_features': 'Safety Features',
    'emergency_stop': 'Emergency Stop System',
    
    # Heating System
    'heater_type': 'Heater Type',
    'heater_configuration': 'Heater Configuration',
    'heater_zones': 'Number of Heater Zones',
    'temperature_range': 'Temperature Range (°C)',
    'temperature_control': 'Temperature Control Method',
    'heater_material': 'Heater Material',
    
    # Vacuum System
    'vacuum_pump_type': 'Vacuum Pump Type',
    'vacuum_pump_capacity': 'Vacuum Pump Capacity (m³/h)',
    'vacuum_ports': 'Number of Vacuum Ports',
    'vacuum_distribution': 'Vacuum Distribution System',
    
    # Cooling System
    'cooling_method': 'Cooling Method',
    'cooling_medium': 'Cooling Medium',
    'cooling_capacity': 'Cooling Capacity',
    'cooling_time': 'Cooling Time (seconds)',
    
    # Material Handling
    'sheet_feeding': 'Sheet Feeding Method',
    'part_ejection': 'Part Ejection Method',
    'trimming_system': 'Trimming System',
    'material_handling': 'Material Handling System',
    
    # Quality & Precision
    'repeatability': 'Repeatability (mm)',
    'accuracy': 'Accuracy (mm)',
    'surface_finish': 'Surface Finish Quality',
    'part_tolerance': 'Part Tolerance (mm)',
    
    # Maintenance & Service
    'maintenance_schedule': 'Maintenance Schedule',
    'service_requirements': 'Service Requirements',
    'spare_parts': 'Critical Spare Parts',
    'lubrication_points': 'Lubrication Points',
    
    # Environmental
    'noise_level': 'Noise Level (dB)',
    'emissions': 'Emissions Standards',
    'energy_efficiency': 'Energy Efficiency Rating',
    'environmental_compliance': 'Environmental Compliance'
}

# Define Commercial Specifications (for Commercial Managers)
COMMERCIAL_COLUMNS = {
    # Project & Quote Information
    'project_number': 'Project Number',
    'quote_number': 'Quote Number',
    'quote_date': 'Quote Date',
    'valid_until': 'Quote Valid Until',
    'customer_name': 'Customer Name',
    'customer_company': 'Customer Company',
    'project_name': 'Project Name',
    'sales_contact': 'Sales Contact',
    
    # Pricing Information
    'base_price': 'Base Machine Price',
    'total_price': 'Total Quote Price',
    'currency': 'Price Currency',
    'price_validity': 'Price Validity Period',
    'price_terms': 'Price Terms',
    'discount_offered': 'Discount Offered',
    
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
    'delivery_location': 'Delivery Location',
    
    # What's Included/Excluded
    'included_items': 'What is Included',
    'excluded_items': 'What is Excluded',
    'scope_of_supply': 'Scope of Supply',
    'additional_services': 'Additional Services',
    
    # Installation & Service
    'installation_terms': 'Installation Terms',
    'installation_cost': 'Installation Cost',
    'commissioning_terms': 'Commissioning Terms',
    'training_terms': 'Training Terms',
    'service_terms': 'Service Terms',
    'warranty_period': 'Warranty Period',
    'warranty_terms': 'Warranty Terms',
    
    # Logistics
    'packaging_terms': 'Packaging Terms',
    'shipping_terms': 'Shipping Terms',
    'crating_requirements': 'Crating Requirements',
    'customs_requirements': 'Customs Requirements',
    
    # Additional Commercial Info
    'special_terms': 'Special Terms',
    'maintenance_contract': 'Maintenance Contract',
    'spare_parts_terms': 'Spare Parts Terms',
    'technical_support': 'Technical Support Terms',
    'after_sales_service': 'After Sales Service'
}

# Define Basic Machine Details (for Owners)
BASIC_COLUMNS = {
    # Machine Overview
    'machine_model': 'Machine Model',
    'machine_name': 'Machine Name',
    'machine_category': 'Machine Category',
    'machine_description': 'Machine Description',
    
    # Basic Specifications
    'basic_specs': 'Basic Specifications',
    'key_features': 'Key Features',
    'machine_capacity': 'Machine Capacity',
    'suitable_materials': 'Suitable Materials',
    'material_types': 'Material Types',
    
    # Applications
    'applications': 'Applications',
    'industries_served': 'Industries Served',
    'end_products': 'End Products',
    'sample_applications': 'Sample Applications',
    
    # Performance
    'cycle_time_info': 'Cycle Time Information',
    'production_rate': 'Production Rate',
    'efficiency_rating': 'Efficiency Rating',
    'quality_output': 'Quality Output',
    
    # Automation Features
    'automation_features': 'Automation Features',
    'automation_level': 'Automation Level',
    'ease_of_operation': 'Ease of Operation',
    'operator_requirements': 'Operator Requirements',
    
    # Materials Processing
    'materials_processed': 'Materials It Processes',
    'material_thickness': 'Material Thickness Range',
    'material_formats': 'Material Formats',
    'material_handling': 'Material Handling',
    
    # Business Benefits
    'business_benefits': 'Business Benefits',
    'roi_considerations': 'ROI Considerations',
    'cost_savings': 'Cost Savings',
    'competitive_advantages': 'Competitive Advantages',
    
    # Operational Info
    'operational_requirements': 'Operational Requirements',
    'space_requirements': 'Space Requirements',
    'utility_requirements': 'Utility Requirements',
    'maintenance_needs': 'Maintenance Needs',
    
    # Market Position
    'market_position': 'Market Position',
    'target_customers': 'Target Customers',
    'competitive_positioning': 'Competitive Positioning',
    'unique_selling_points': 'Unique Selling Points'
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

# STEP 3: Use GPT to extract technical fields
def extract_technical_fields_from_text(text, filename=""):
    """Extract technical specifications from quote text using GPT-4"""
    prompt = f"""
You are a mechanical engineer specializing in thermoforming machines. Extract ALL technical specifications and engineering details from this PF1 thermoforming machine quote.

Focus on:
- Machine dimensions, capacities, and performance specs
- Heating, vacuum, and cooling system details
- Automation and control specifications
- Material handling and processing capabilities
- Quality, precision, and repeatability metrics
- Maintenance and service requirements
- Environmental and safety specifications

Return ONLY a valid JSON object with these exact field names:
{list(TECHNICAL_COLUMNS.keys())}

Extract the actual technical values mentioned in the quote. If a field is not mentioned, leave it empty.

QUOTE TEXT:
{text[:8000]}

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
        return {}
    except Exception as e:
        print(f"❌ OpenAI API error for {filename}: {e}")
        return {}

# STEP 4: Use GPT to extract commercial fields
def extract_commercial_fields_from_text(text, filename=""):
    """Extract commercial specifications from quote text using GPT-4"""
    prompt = f"""
You are a commercial manager specializing in industrial machine quotes. Extract ALL commercial and business-related information from this PF1 thermoforming machine quote.

Focus on:
- Project and quote identification
- Pricing and payment terms
- Delivery and lead time information
- What's included vs excluded in the quote
- Installation and service terms
- Warranty and support information
- Logistics and packaging details

Return ONLY a valid JSON object with these exact field names:
{list(COMMERCIAL_COLUMNS.keys())}

Extract the actual values mentioned in the quote. If a field is not mentioned, leave it empty.

QUOTE TEXT:
{text[:8000]}

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
        return {}
    except Exception as e:
        print(f"❌ OpenAI API error for {filename}: {e}")
        return {}

# STEP 5: Use GPT to extract basic machine details
def extract_basic_fields_from_text(text, filename=""):
    """Extract basic machine details for owners from quote text using GPT-4"""
    prompt = f"""
You are a business consultant helping owners understand thermoforming machines. Extract basic machine information and business-relevant details from this PF1 thermoforming machine quote.

Focus on:
- Machine overview and basic specifications
- Applications and industries served
- Materials it can process
- Automation features and ease of operation
- Business benefits and ROI considerations
- Operational requirements
- Market positioning and competitive advantages

Return ONLY a valid JSON object with these exact field names:
{list(BASIC_COLUMNS.keys())}

Extract the actual values mentioned in the quote. If a field is not mentioned, leave it empty.

QUOTE TEXT:
{text[:8000]}

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
        return {}
    except Exception as e:
        print(f"❌ OpenAI API error for {filename}: {e}")
        return {}

# STEP 6: Process all PDFs and extract all three types of data
def process_all_pdfs():
    """Process all PDFs and extract technical, commercial, and basic details"""
    technical_data = {}
    commercial_data = {}
    basic_data = {}
    processed_files = 0
    
    # Find all PDF files in PF1 folder
    pf1_dir = "./PF1"
    if not os.path.exists(pf1_dir):
        print(f"❌ PF1 directory not found: {pf1_dir}")
        return technical_data, commercial_data, basic_data
    
    pdf_files = []
    for file in os.listdir(pf1_dir):
        if file.lower().endswith(".pdf"):
            pdf_files.append(os.path.join(pf1_dir, file))
    
    total_files = len(pdf_files)
    print(f"🔍 Found {total_files} PDF files in PF1 folder...")
    print(f"🚀 COMPREHENSIVE MODE: Processing ALL files for 3 specialized databases...")
    
    for filepath in pdf_files:
        processed_files += 1
        filename = os.path.basename(filepath)
        print(f"📄 Processing {processed_files}/{total_files}: {filename}...")
        
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
        
        # Extract all three types of data using GPT
        technical_extracted = extract_technical_fields_from_text(text, filename)
        commercial_extracted = extract_commercial_fields_from_text(text, filename)
        basic_extracted = extract_basic_fields_from_text(text, filename)
        
        # Store data for this machine
        technical_data[machine_model] = technical_extracted
        commercial_data[machine_model] = commercial_extracted
        basic_data[machine_model] = basic_extracted
        
        print(f"✅ Extracted data for {filename}:")
        print(f"   • Technical fields: {len(technical_extracted)}")
        print(f"   • Commercial fields: {len(commercial_extracted)}")
        print(f"   • Basic fields: {len(basic_extracted)}")
    
    return technical_data, commercial_data, basic_data

# STEP 7: Create three specialized Excel files
def create_specialized_excel_files(technical_data, commercial_data, basic_data):
    """Create three specialized Excel files for different stakeholders"""
    
    # 1. Technical Specifications Excel (for Engineers)
    technical_rows = []
    for machine_model, fields in technical_data.items():
        row = {'Machine Model': machine_model}
        for field_name, field_description in TECHNICAL_COLUMNS.items():
            value = fields.get(field_name, '')
            row[field_description] = value
        technical_rows.append(row)
    
    technical_df = pd.DataFrame(technical_rows)
    technical_cols = ['Machine Model'] + list(TECHNICAL_COLUMNS.values())
    technical_df = technical_df[technical_cols]
    
    # 2. Commercial Specifications Excel (for Commercial Managers)
    commercial_rows = []
    for machine_model, fields in commercial_data.items():
        row = {'Machine Model': machine_model}
        for field_name, field_description in COMMERCIAL_COLUMNS.items():
            value = fields.get(field_name, '')
            row[field_description] = value
        commercial_rows.append(row)
    
    commercial_df = pd.DataFrame(commercial_rows)
    commercial_cols = ['Machine Model'] + list(COMMERCIAL_COLUMNS.values())
    commercial_df = commercial_df[commercial_cols]
    
    # 3. Basic Machine Details Excel (for Owners)
    basic_rows = []
    for machine_model, fields in basic_data.items():
        row = {'Machine Model': machine_model}
        for field_name, field_description in BASIC_COLUMNS.items():
            value = fields.get(field_name, '')
            row[field_description] = value
        basic_rows.append(row)
    
    basic_df = pd.DataFrame(basic_rows)
    basic_cols = ['Machine Model'] + list(BASIC_COLUMNS.values())
    basic_df = basic_df[basic_cols]
    
    # Save all three Excel files
    excel_files = []
    
    # Technical Excel
    technical_filename = "PF1_Technical_Specifications_Complete.xlsx"
    with pd.ExcelWriter(technical_filename, engine='openpyxl') as writer:
        technical_df.to_excel(writer, sheet_name='Technical Specs', index=False)
        worksheet = writer.sheets['Technical Specs']
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
    excel_files.append(technical_filename)
    
    # Commercial Excel
    commercial_filename = "PF1_Commercial_Specifications_Complete.xlsx"
    with pd.ExcelWriter(commercial_filename, engine='openpyxl') as writer:
        commercial_df.to_excel(writer, sheet_name='Commercial Specs', index=False)
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
    excel_files.append(commercial_filename)
    
    # Basic Details Excel
    basic_filename = "PF1_Basic_Machine_Details_Complete.xlsx"
    with pd.ExcelWriter(basic_filename, engine='openpyxl') as writer:
        basic_df.to_excel(writer, sheet_name='Basic Details', index=False)
        worksheet = writer.sheets['Basic Details']
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
    excel_files.append(basic_filename)
    
    # Print summary
    print(f"\n💾 Three specialized Excel files created:")
    print(f"📊 Data summary:")
    print(f"   • Machine models processed: {len(technical_data)}")
    print(f"   • Technical columns: {len(TECHNICAL_COLUMNS) + 1}")
    print(f"   • Commercial columns: {len(COMMERCIAL_COLUMNS) + 1}")
    print(f"   • Basic detail columns: {len(BASIC_COLUMNS) + 1}")
    print(f"   • Total data points: {len(technical_data) * (len(TECHNICAL_COLUMNS) + len(COMMERCIAL_COLUMNS) + len(BASIC_COLUMNS) + 3)}")
    
    for filename in excel_files:
        print(f"   📁 {filename}")
    
    return excel_files

# Main execution
if __name__ == "__main__":
    print("🚀 PF1 Comprehensive Extractor - ALL PDFs")
    print("=" * 70)
    print("Creating 3 specialized databases:")
    print("🔧 Technical Specs (for Engineers)")
    print("💰 Commercial Specs (for Commercial Managers)")
    print("👑 Basic Details (for Owners)")
    print("=" * 70)
    
    # Process all PDFs and extract all three types of data
    technical_data, commercial_data, basic_data = process_all_pdfs()
    
    if technical_data or commercial_data or basic_data:
        # Create three specialized Excel files
        excel_files = create_specialized_excel_files(technical_data, commercial_data, basic_data)
        
        print(f"\n✅ Comprehensive extraction complete!")
        print(f"🎯 Three specialized databases ready for different stakeholders!")
        print(f"🔧 Engineers: Technical specifications and engineering details")
        print(f"💰 Managers: Commercial terms, pricing, and project information")
        print(f"👑 Owners: Basic machine details, applications, and business benefits")
    else:
        print("❌ No data extracted from PDFs") 