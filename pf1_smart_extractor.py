# 🧠 PF1 Smart Extractor - Intelligent Column Deduplication
# Creates 3 specialized Excel files with smart filtering and column consolidation

import os
import requests
import json
import pandas as pd
from openai import OpenAI
from collections import defaultdict
from time import sleep
from dotenv import load_dotenv
import re
from difflib import SequenceMatcher
import numpy as np

# Load environment variables
load_dotenv()

# 🔐 Keys
PDFCO_API_KEY = os.getenv("PDFCO_API_KEY", "rushabh@machinecraft.org_BsvgOq6OwyqWriVHJCxSxko7ZVnte3ELH5oU4zlu4U1Ge4fEj4dBG4nVGw5M1kUv")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
openai = OpenAI(api_key=OPENAI_API_KEY)

# Smart Column Definitions with Synonyms
TECHNICAL_COLUMNS_SMART = {
    # Machine Identification
    'machine_model': 'Machine Model',
    'machine_type': 'Machine Type',
    'machine_series': 'Machine Series',
    
    # Core Technical Specifications (Consolidated)
    'forming_area': 'Forming Area (mm)',  # Combines: forming area, working area, sheet area
    'forming_depth': 'Forming Depth (mm)',  # Combines: forming depth, draw depth, mold depth
    'sheet_size': 'Max Sheet Size (mm)',  # Combines: sheet size, material size, plate size
    'sheet_thickness': 'Sheet Thickness Range (mm)',  # Combines: thickness, material thickness
    'vacuum_pressure': 'Vacuum Pressure (bar)',  # Combines: vacuum, vacuum level, suction
    'air_pressure': 'Air Pressure (bar)',  # Combines: air pressure, compressed air, pneumatic
    'heating_power': 'Heating Power (kW)',  # Combines: heating power, heater power, heating load, total load
    'cooling_power': 'Cooling Power (kW)',  # Combines: cooling power, cooling capacity, chiller power
    'cycle_time': 'Cycle Time (seconds)',  # Combines: cycle time, production time, forming time
    'production_capacity': 'Production Capacity (parts/hour)',  # Combines: capacity, output, production rate
    
    # Mechanical Specifications (Consolidated)
    'machine_weight': 'Machine Weight (kg)',  # Combines: weight, total weight, machine mass
    'machine_dimensions': 'Machine Dimensions (LxWxH mm)',  # Combines: dimensions, size, footprint
    'machine_footprint': 'Machine Footprint (m²)',  # Combines: footprint, floor space, area required
    'power_consumption': 'Power Consumption (kW)',  # Combines: power consumption, electrical load, energy usage
    'air_consumption': 'Air Consumption (L/min)',  # Combines: air consumption, compressed air usage
    'water_consumption': 'Water Consumption (L/min)',  # Combines: water consumption, cooling water
    
    # Automation & Control (Consolidated)
    'automation_level': 'Automation Level',  # Combines: automation, automation level, automation type
    'control_system': 'Control System',  # Combines: control, controller, control panel
    'hmi_type': 'HMI Type',  # Combines: HMI, interface, touch screen, display
    'programming_method': 'Programming Method',  # Combines: programming, setup, configuration
    'safety_features': 'Safety Features',  # Combines: safety, safety system, protection
    'emergency_stop': 'Emergency Stop System',  # Combines: emergency stop, E-stop, safety stop
    
    # Heating System (Consolidated)
    'heater_type': 'Heater Type',  # Combines: heater type, heating element, heating method
    'heater_configuration': 'Heater Configuration',  # Combines: heater layout, heating zones, configuration
    'heater_zones': 'Number of Heater Zones',  # Combines: zones, heating zones, zone count
    'temperature_range': 'Temperature Range (°C)',  # Combines: temperature, temp range, heating temp
    'temperature_control': 'Temperature Control Method',  # Combines: temp control, control method, regulation
    'heater_material': 'Heater Material',  # Combines: heater material, element material
    
    # Vacuum System (Consolidated)
    'vacuum_pump_type': 'Vacuum Pump Type',  # Combines: vacuum pump, pump type, suction pump
    'vacuum_pump_capacity': 'Vacuum Pump Capacity (m³/h)',  # Combines: pump capacity, vacuum capacity, flow rate
    'vacuum_ports': 'Number of Vacuum Ports',  # Combines: vacuum ports, suction ports, ports
    'vacuum_distribution': 'Vacuum Distribution System',  # Combines: vacuum distribution, suction system
    
    # Cooling System (Consolidated)
    'cooling_method': 'Cooling Method',  # Combines: cooling method, cooling type, cooling system
    'cooling_medium': 'Cooling Medium',  # Combines: cooling medium, coolant, cooling fluid
    'cooling_capacity': 'Cooling Capacity',  # Combines: cooling capacity, cooling power, chiller capacity
    'cooling_time': 'Cooling Time (seconds)',  # Combines: cooling time, cool down time
    
    # Material Handling (Consolidated)
    'sheet_feeding': 'Sheet Feeding Method',  # Combines: sheet feeding, material feeding, feeding system
    'part_ejection': 'Part Ejection Method',  # Combines: part ejection, ejection system, removal method
    'trimming_system': 'Trimming System',  # Combines: trimming, cutting, edge trimming
    'material_handling': 'Material Handling System',  # Combines: material handling, handling system
    
    # Quality & Precision (Consolidated)
    'repeatability': 'Repeatability (mm)',  # Combines: repeatability, precision, accuracy
    'accuracy': 'Accuracy (mm)',  # Combines: accuracy, precision, tolerance
    'surface_finish': 'Surface Finish Quality',  # Combines: surface finish, finish quality, surface quality
    'part_tolerance': 'Part Tolerance (mm)',  # Combines: tolerance, part tolerance, dimensional tolerance
    
    # Maintenance & Service (Consolidated)
    'maintenance_schedule': 'Maintenance Schedule',  # Combines: maintenance, service schedule, upkeep
    'service_requirements': 'Service Requirements',  # Combines: service, maintenance requirements
    'spare_parts': 'Critical Spare Parts',  # Combines: spare parts, parts, consumables
    'lubrication_points': 'Lubrication Points',  # Combines: lubrication, grease points, oil points
    
    # Environmental (Consolidated)
    'noise_level': 'Noise Level (dB)',  # Combines: noise, noise level, sound level
    'emissions': 'Emissions Standards',  # Combines: emissions, environmental compliance
    'energy_efficiency': 'Energy Efficiency Rating',  # Combines: efficiency, energy efficiency, power efficiency
    'environmental_compliance': 'Environmental Compliance'  # Combines: compliance, environmental standards
}

# Column Synonyms for Smart Matching
COLUMN_SYNONYMS = {
    # Technical Synonyms
    'heating_power': ['heating power', 'heater power', 'heating load', 'total load', 'heater capacity', 'heating capacity'],
    'forming_area': ['forming area', 'working area', 'sheet area', 'material area', 'plate area'],
    'forming_depth': ['forming depth', 'draw depth', 'mold depth', 'drawing depth', 'forming height'],
    'sheet_size': ['sheet size', 'material size', 'plate size', 'sheet dimensions', 'material dimensions'],
    'vacuum_pressure': ['vacuum pressure', 'vacuum', 'vacuum level', 'suction', 'vacuum force'],
    'air_pressure': ['air pressure', 'compressed air', 'pneumatic pressure', 'air force'],
    'cycle_time': ['cycle time', 'production time', 'forming time', 'cycle duration', 'processing time'],
    'production_capacity': ['production capacity', 'capacity', 'output', 'production rate', 'throughput'],
    'machine_weight': ['machine weight', 'weight', 'total weight', 'machine mass', 'equipment weight'],
    'machine_dimensions': ['machine dimensions', 'dimensions', 'size', 'machine size', 'equipment size'],
    'power_consumption': ['power consumption', 'electrical load', 'energy usage', 'power usage', 'electrical consumption'],
    'automation_level': ['automation level', 'automation', 'automation type', 'automation degree'],
    'control_system': ['control system', 'control', 'controller', 'control panel', 'control unit'],
    'temperature_range': ['temperature range', 'temperature', 'temp range', 'heating temperature', 'operating temperature'],
    'vacuum_pump_type': ['vacuum pump type', 'vacuum pump', 'pump type', 'suction pump', 'vacuum system'],
    'cooling_method': ['cooling method', 'cooling type', 'cooling system', 'cooling approach'],
    'sheet_feeding': ['sheet feeding', 'material feeding', 'feeding system', 'feed method', 'material feed'],
    'repeatability': ['repeatability', 'precision', 'accuracy', 'repeatable accuracy'],
    'maintenance_schedule': ['maintenance schedule', 'maintenance', 'service schedule', 'upkeep schedule'],
    
    # Commercial Synonyms
    'base_price': ['base price', 'machine price', 'unit price', 'basic price', 'core price'],
    'total_price': ['total price', 'total cost', 'final price', 'quote price', 'total amount'],
    'lead_time': ['lead time', 'delivery time', 'production time', 'manufacturing time', 'delivery period'],
    'payment_terms': ['payment terms', 'payment conditions', 'payment schedule', 'payment arrangement'],
    'warranty_period': ['warranty period', 'warranty', 'guarantee period', 'warranty duration'],
    'installation_terms': ['installation terms', 'installation', 'setup terms', 'installation conditions'],
    'packaging_terms': ['packaging terms', 'packaging', 'packing terms', 'packaging conditions'],
    
    # Basic Details Synonyms
    'machine_capacity': ['machine capacity', 'capacity', 'production capacity', 'output capacity'],
    'applications': ['applications', 'application areas', 'use cases', 'applicable industries'],
    'materials_processed': ['materials processed', 'materials', 'processed materials', 'material types'],
    'automation_features': ['automation features', 'automation', 'automated features', 'automation capabilities']
}

# Function to calculate similarity between two strings
def string_similarity(a, b):
    """Calculate similarity between two strings using SequenceMatcher"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# Function to find similar columns and consolidate them
def consolidate_similar_columns(df, column_synonyms, similarity_threshold=0.8):
    """Consolidate similar columns based on synonyms and similarity"""
    print("🧠 Smart column consolidation in progress...")
    
    # Create a copy of the dataframe
    df_consolidated = df.copy()
    columns_to_drop = []
    columns_consolidated = {}
    
    # Process each column group
    for primary_column, synonyms in column_synonyms.items():
        if primary_column in df_consolidated.columns:
            primary_col_name = df_consolidated.columns[df_consolidated.columns.get_loc(primary_column)]
            
            # Find similar columns
            similar_columns = []
            for col in df_consolidated.columns:
                if col != primary_col_name:
                    # Check exact match with synonyms
                    if any(synonym in col.lower() for synonym in synonyms):
                        similar_columns.append(col)
                    # Check similarity
                    elif string_similarity(col.lower(), primary_col_name.lower()) > similarity_threshold:
                        similar_columns.append(col)
            
            if similar_columns:
                print(f"   🔄 Consolidating {primary_col_name} with: {similar_columns}")
                
                # Merge data from similar columns
                for similar_col in similar_columns:
                    # Fill empty values in primary column with values from similar column
                    mask = df_consolidated[primary_col_name].isna() | (df_consolidated[primary_col_name] == '')
                    df_consolidated.loc[mask, primary_col_name] = df_consolidated.loc[mask, similar_col]
                    
                    # Mark for deletion
                    columns_to_drop.append(similar_col)
                    columns_consolidated[similar_col] = primary_col_name
    
    # Drop consolidated columns
    df_consolidated = df_consolidated.drop(columns=columns_to_drop)
    
    print(f"   ✅ Consolidated {len(columns_consolidated)} similar columns")
    return df_consolidated, columns_consolidated

# Function to remove empty or near-empty columns
def remove_empty_columns(df, min_fill_percentage=0.1):
    """Remove columns that are mostly empty"""
    print("🧹 Cleaning empty columns...")
    
    total_rows = len(df)
    columns_to_drop = []
    
    for col in df.columns:
        # Count non-empty values
        non_empty_count = df[col].notna().sum() + (df[col] == '').sum()
        fill_percentage = non_empty_count / total_rows
        
        if fill_percentage < min_fill_percentage:
            columns_to_drop.append(col)
            print(f"   🗑️  Removing empty column: {col} (fill rate: {fill_percentage:.1%})")
    
    df_cleaned = df.drop(columns=columns_to_drop)
    print(f"   ✅ Removed {len(columns_to_drop)} empty columns")
    return df_cleaned

# Function to standardize column names
def standardize_column_names(df):
    """Standardize column names for consistency"""
    print("📝 Standardizing column names...")
    
    # Create mapping for standardization
    column_mapping = {}
    for col in df.columns:
        # Remove extra spaces and standardize
        new_name = col.strip()
        new_name = re.sub(r'\s+', ' ', new_name)  # Replace multiple spaces with single space
        new_name = new_name.replace('(', ' (').replace(')', ') ')  # Standardize parentheses spacing
        new_name = re.sub(r'\s+', ' ', new_name).strip()  # Clean up again
        
        if new_name != col:
            column_mapping[col] = new_name
    
    if column_mapping:
        df_standardized = df.rename(columns=column_mapping)
        print(f"   ✅ Standardized {len(column_mapping)} column names")
        return df_standardized
    
    return df

# Enhanced extraction functions with smart filtering
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

def extract_smart_fields_from_text(text, filename="", field_type="technical"):
    """Extract fields with smart filtering using GPT-4"""
    
    if field_type == "technical":
        columns = TECHNICAL_COLUMNS_SMART
        role = "mechanical engineer specializing in thermoforming machines"
        focus = "technical specifications and engineering details"
    elif field_type == "commercial":
        columns = COMMERCIAL_COLUMNS
        role = "commercial manager specializing in industrial machine quotes"
        focus = "commercial and business-related information"
    else:  # basic
        columns = BASIC_COLUMNS
        role = "business consultant helping owners understand thermoforming machines"
        focus = "basic machine information and business-relevant details"
    
    prompt = f"""
You are a {role}. Extract {focus} from this PF1 thermoforming machine quote.

IMPORTANT: Use smart filtering to avoid duplicate or similar fields. If you find multiple fields that mean the same thing, consolidate them into the most appropriate single field.

Return ONLY a valid JSON object with these exact field names:
{list(columns.keys())}

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

def process_pdfs_with_smart_filtering(max_files=20):
    """Process PDFs with smart filtering and column consolidation"""
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
    print(f"🧠 SMART MODE: Processing up to {max_files} files with intelligent filtering...")
    
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
        
        # Extract all three types of data with smart filtering
        technical_extracted = extract_smart_fields_from_text(text, filename, "technical")
        commercial_extracted = extract_smart_fields_from_text(text, filename, "commercial")
        basic_extracted = extract_smart_fields_from_text(text, filename, "basic")
        
        # Store data for this machine
        technical_data[machine_model] = technical_extracted
        commercial_data[machine_model] = commercial_extracted
        basic_data[machine_model] = basic_extracted
        
        print(f"✅ Smart extraction for {filename}:")
        print(f"   • Technical fields: {len(technical_extracted)}")
        print(f"   • Commercial fields: {len(commercial_extracted)}")
        print(f"   • Basic fields: {len(basic_extracted)}")
        
        # Stop after max_files
        if processed_files >= max_files:
            print(f"🛑 Smart processing completed: Processed {max_files} files")
            break
    
    return technical_data, commercial_data, basic_data

def create_smart_excel_files(technical_data, commercial_data, basic_data):
    """Create three specialized Excel files with smart filtering and consolidation"""
    
    print("\n🧠 Creating smart Excel files with intelligent filtering...")
    
    # 1. Technical Specifications Excel (for Engineers)
    technical_rows = []
    for machine_model, fields in technical_data.items():
        row = {'Machine Model': machine_model}
        for field_name, field_description in TECHNICAL_COLUMNS_SMART.items():
            value = fields.get(field_name, '')
            row[field_description] = value
        technical_rows.append(row)
    
    technical_df = pd.DataFrame(technical_rows)
    technical_cols = ['Machine Model'] + list(TECHNICAL_COLUMNS_SMART.values())
    technical_df = technical_df[technical_cols]
    
    # Apply smart filtering to technical data
    technical_df = standardize_column_names(technical_df)
    technical_df, tech_consolidated = consolidate_similar_columns(technical_df, COLUMN_SYNONYMS)
    technical_df = remove_empty_columns(technical_df, min_fill_percentage=0.15)
    
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
    
    # Apply smart filtering to commercial data
    commercial_df = standardize_column_names(commercial_df)
    commercial_df, comm_consolidated = consolidate_similar_columns(commercial_df, COLUMN_SYNONYMS)
    commercial_df = remove_empty_columns(commercial_df, min_fill_percentage=0.15)
    
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
    
    # Apply smart filtering to basic data
    basic_df = standardize_column_names(basic_df)
    basic_df, basic_consolidated = consolidate_similar_columns(basic_df, COLUMN_SYNONYMS)
    basic_df = remove_empty_columns(basic_df, min_fill_percentage=0.15)
    
    # Save all three Excel files
    excel_files = []
    
    # Technical Excel
    technical_filename = "PF1_Technical_Specifications_Smart.xlsx"
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
    commercial_filename = "PF1_Commercial_Specifications_Smart.xlsx"
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
    basic_filename = "PF1_Basic_Machine_Details_Smart.xlsx"
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
    print(f"\n💾 Three smart Excel files created:")
    print(f"📊 Smart data summary:")
    print(f"   • Machine models processed: {len(technical_data)}")
    print(f"   • Technical columns (after smart filtering): {len(technical_df.columns)}")
    print(f"   • Commercial columns (after smart filtering): {len(commercial_df.columns)}")
    print(f"   • Basic detail columns (after smart filtering): {len(basic_df.columns)}")
    print(f"   • Total data points: {len(technical_data) * (len(technical_df.columns) + len(commercial_df.columns) + len(basic_df.columns) - 3)}")
    
    for filename in excel_files:
        print(f"   📁 {filename}")
    
    return excel_files

# Main execution
if __name__ == "__main__":
    print("🧠 PF1 Smart Extractor - Intelligent Column Deduplication")
    print("=" * 70)
    print("Creating 3 specialized databases with smart filtering:")
    print("🔧 Technical Specs (for Engineers) - Smart consolidated")
    print("💰 Commercial Specs (for Commercial Managers) - Smart filtered")
    print("👑 Basic Details (for Owners) - Smart cleaned")
    print("=" * 70)
    
    # Process PDFs with smart filtering
    technical_data, commercial_data, basic_data = process_pdfs_with_smart_filtering(max_files=20)
    
    if technical_data or commercial_data or basic_data:
        # Create three specialized Excel files with smart filtering
        excel_files = create_smart_excel_files(technical_data, commercial_data, basic_data)
        
        print(f"\n✅ Smart extraction complete!")
        print(f"🎯 Three intelligent databases ready with consolidated columns!")
        print(f"🧠 Smart features applied:")
        print(f"   • Column similarity detection and consolidation")
        print(f"   • Empty column removal")
        print(f"   • Column name standardization")
        print(f"   • Synonym-based field matching")
    else:
        print("❌ No data extracted from PDFs") 