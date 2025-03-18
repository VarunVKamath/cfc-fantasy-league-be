import gspread
import pandas as pd
import time

# Authenticate using your service account JSON file
gc = gspread.service_account(filename="reliable-proton-449504-g2-d77e329f347c.json")

spreadsheet_name = "CFC Fantasy League"
try:
    spreadsheet = gc.open(spreadsheet_name)  # Try to open existing spreadsheet
except gspread.exceptions.SpreadsheetNotFound:
    spreadsheet = gc.create(spreadsheet_name)  # Create new spreadsheet if not found

# Load Excel file and its sheets
excel_file = "CFC Fantasy League.xlsx"
sheets = pd.ExcelFile(excel_file).sheet_names  # Get all sheet names

# Get existing sheet names in Google Sheets
existing_sheets = {ws.title: ws for ws in spreadsheet.worksheets()}

for sheet_name in sheets:
    # Read each sheet into a DataFrame (ignore index column to fix "Unnamed: 0" issue)
    df_excel = pd.read_excel(excel_file, sheet_name=sheet_name, index_col=None)
    df_excel.columns = [" " if col.startswith("Unnamed") else col for col in df_excel.columns]  # Rename Unnamed columns to blank
    data_excel = df_excel.astype(str).values.tolist()  # Convert to list of strings for accurate comparison
    data_excel.insert(0, df_excel.columns.tolist())  # Add headers

    if sheet_name in existing_sheets:
        # Fetch existing data from Google Sheets
        worksheet = existing_sheets[sheet_name]
        data_gsheet = worksheet.get_all_values()

        # Compare the existing data with the new data
        if data_gsheet == data_excel:
            print(f"⏩ Skipping unchanged sheet: {sheet_name}")
            continue  # Skip updating this sheet

        print(f"🔄 Updating modified sheet: {sheet_name}")
        worksheet.clear()  # Clear existing data before updating
    else:
        print(f"🆕 Creating new sheet: {sheet_name}")
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    # Batch update in **one API request** to avoid rate limits
    try:
        worksheet.update(range_name="A1", values=data_excel)
        print(f"✅ Updated sheet: {sheet_name}")
    except gspread.exceptions.APIError:
        print(f"⏳ Rate limit exceeded. Retrying {sheet_name} in 20 seconds...")
        time.sleep(10)  # Wait and retry once
        worksheet.update(range_name="A1", values=data_excel)
        print(f"✅ Updated sheet: {sheet_name} (after retry)")

    # Delay to prevent hitting API rate limits
    time.sleep(2)

print("🎉 All sheets successfully processed!")
