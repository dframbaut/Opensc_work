from file_reader import get_records_data, get_mismatch_files, get_valid_files, check_expected_files
from config_loader import load_config
from data_contract import load_table_definitions, extract_expected_columns
from file_reader import list_folders, select_folder
from html_report_generator import generate_html_report, send_email_with_html_report
import os

def main():
    # Load configurations from the config.json file
    config = load_config('config.json')
    
    # Retrieve paths and other parameters from the config file
    data_contract_path = config['data_contract_path']
    uploads_folder_path = config['uploads_folder_path']
    prefixes = config['prefixes']
    suffix_order = config['suffix_order']
    smtp_user = config['smtp_user']
    smtp_password = config['smtp_password']
    sender_email = config['sender_email']
    receiver_emails = config['receiver_emails']
    expected_files = config['expected_files']


    # Load and process the data contract
    json_data = load_table_definitions(data_contract_path)
    expected_columns = extract_expected_columns(json_data)
    
    # List folders and allow selection
    folders = list_folders(uploads_folder_path)
    
    if folders:
        selection = input(f"\nPlease enter the number or name of the folder to analyze (from the list above): ")
        selected_path = select_folder(uploads_folder_path, selection, folders)
        
        # Check for missing expected files
        missing_files = check_expected_files(selected_path, expected_files,prefixes)
            
        # Get the name of the selected folder
        selected_folder_name = os.path.basename(selected_path)

        records_data = get_records_data(selected_path, prefixes)
        
        # Get files with column mismatches
        mismatch_files = get_mismatch_files(selected_path, expected_columns, prefixes)
        
        # Get valid files
        valid_files = get_valid_files(selected_path, prefixes)

        # Debugging: Print results
        print("=== REPORT PREVIEW IN TERMINAL ===")
        
        if missing_files:
            print("Missing expected files:")
            for file in missing_files:
                print(f" - {file}")
        else:
            print("All expected files are present.")

        # Print Records Data
        print("\nRecords Data (Num records | File Name):")
        print(len(records_data))
        for row in records_data:
            print(f"Number of records: {row[0]} | File name: {row[1]}")
        
        # Print Mismatch Files
        print("\nMismatch Files (File Name | Expected Columns | Found Columns):")
        for row in mismatch_files:
            print(f"File name: {row[0]} | Expected columns: {row[1]} | Found columns: {row[2]}")
        
        # Print Valid Files
        print("\nValid Files and their DataFrames:")
        for file, df in valid_files:
            print(f"File: {file}")
            print(df.head())

        # Ask if the report should be sent via email
        send_email = input("\nDo you want to send the report by email? (yes/no): ").strip().lower()
        
        if send_email in ['yes', 'y']:
            # Generate the HTML report
            html_report = generate_html_report(
                                            missing_files,
                                            records_data, 
                                            mismatch_files, 
                                            valid_files)
            
            # Send the report via email
            email_subject = f"File analysis report - {selected_folder_name}"
            send_email_with_html_report(
                subject=email_subject,
                body_html=html_report,
                sender_email=sender_email,
                receiver_email=", ".join(receiver_emails),
                smtp_user=smtp_user,
                smtp_password=smtp_password
            )
            print(f"Report sent by email. Subject: {email_subject}")
        else:
            print("Report not sent.")
    
if __name__ == "__main__":
    main()