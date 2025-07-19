# 🧠 PF1 Quote Column Extractor

Extract structured data from PF1 thermoforming machine quote PDFs using PDF.co API for text extraction and OpenAI GPT-4 for intelligent field parsing.

## 🚀 Features

- **PDF.co API Integration**: High-quality OCR and text extraction from complex PDFs
- **GPT-4 Field Extraction**: Intelligent parsing of technical specifications and commercial terms
- **Deduplication**: Identifies new fields not in your existing `specs.json`
- **CSV Output**: Generates `column_suggestions.csv` with sample values
- **Progress Tracking**: Real-time processing status and error handling

## 📋 Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Keys**:
   Create a `.env` file in the same directory:
   ```bash
   PDFCO_API_KEY=your_pdfco_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Place Script in Quotes Folder**:
   Copy `pf1_quote_extractor.py` to your PF1 quotes directory (where the PDFs are located).

## 🎯 Usage

```bash
python pf1_quote_extractor.py
```

The script will:
1. Scan all `.pdf` files in the current directory
2. Extract text using PDF.co API
3. Parse fields using GPT-4
4. Generate `column_suggestions.csv` with new field suggestions
5. Display summary in console

## 📊 Output

### Console Output
```
🆕 Found 15 new potential Airtable columns:
• Heater Type: ['Halogen Top', 'Quartz IR']
• CE Certification: ['Yes', 'Included']
• Warranty Duration: ['12 months', '18 months']
• Max Sheet Thickness: ['6 mm', '8 mm']
```

### CSV Output (`column_suggestions.csv`)
| Column Name | Sample Values | Value Count |
|-------------|---------------|-------------|
| Heater Type | Halogen Top \| Quartz IR | 2 |
| CE Certification | Yes \| Included | 2 |

## 🔧 Configuration

- **Text Length Limit**: Set to 8000 characters per PDF for API efficiency
- **Rate Limiting**: 2-second delay between API calls
- **Known Fields**: Automatically loads from `specs.json` if present
- **Error Handling**: Continues processing even if individual files fail

## 🛠 Troubleshooting

- **PDF.co API Errors**: Check your API key and credits
- **OpenAI API Errors**: Verify your API key and billing status
- **JSON Parsing Errors**: The script will skip problematic files and continue
- **No Text Extracted**: Some PDFs may be image-only or corrupted

## 📈 Next Steps

After running the extractor:
1. Review `column_suggestions.csv` for new fields
2. Add relevant fields to your Airtable database
3. Update `specs.json` with new field definitions
4. Re-run to find additional fields

## 💡 Tips

- Run on a subset of PDFs first to test
- Check the console output for processing status
- Use the CSV output to prioritize which fields to add to your database
- Consider running periodically as new quotes are added 