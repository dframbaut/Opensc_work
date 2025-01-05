#html_report_generator.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Main function that generates the complete HTML report
def generate_html_report(missing_files,records_data, mismatch_files, valid_files):
    html_report = []
    # Start HTML
    html_report.append("<html><body style='font-family: Arial, sans-serif;'>")
    html_report.append("<h2 style='color: #4CAF50;'>File Analysis Report</h2>")
    
    # Generate different sections of the report
    html_report.append(generate_missing_files_section(missing_files))
    html_report.append(generate_table_of_records(records_data))
    html_report.append(generate_mismatch_section(mismatch_files))
    html_report.append(generate_null_count_section(valid_files))
    
    # Close HTML
    html_report.append("</body></html>")
    return "\n".join(html_report)

# Function to generate the section for missing files
def generate_missing_files_section(missing_files):
    html_missing = []
    
    # If there are missing files, display them
    if missing_files:
        html_missing.append("<h3 style='color: #f44336;'>Missing Expected Files:</h3>")
        html_missing.append('<ul>')
        for file in missing_files:
            html_missing.append(f"<li style='color: red;'>{file}</li>")
        html_missing.append('</ul>')
    else:
        # If no files are missing, show a success message
        html_missing.append("<h3 style='color: #4CAF50;'>All expected files have been received.</h3>")
    
    return "\n".join(html_missing)

# Function to generate the records table with color based on file status
def generate_table_of_records(records_data):
    html_table = []
    html_table.append("<h3 style='color: #2196F3;'>Records Table:</h3>")
    html_table.append('<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">')
    html_table.append("<tr style='background-color: #f2f2f2;'><th>Records</th><th>File Name</th></tr>")
    
    for row in records_data:
        if len(row) == 2:  # Ensure there are exactly two columns per row (records and file name)
            num_records = row[0]
            file_name = row[1]

            # If the file is empty, show it in red
            if num_records == 'empty file':
                html_table.append(f"<tr><td>{num_records}</td><td style='color: red;'>{file_name}</td></tr>")
            # If there are records, show it in green
            else:
                html_table.append(f"<tr><td>{num_records}</td><td style='color: green;'>{file_name}</td></tr>")
        else:
            # Row with missing data
            html_table.append("<tr><td colspan='2' style='color: red;'>Data missing</td></tr>")
    
    html_table.append("</table><br>")
    return "\n".join(html_table)

# Function to generate the section for files with column mismatches
def generate_mismatch_section(mismatch_files):
    if not mismatch_files:
        return ""  # If there are no mismatched files, do not generate this section
    
    html_mismatch = []
    html_mismatch.append("<h3 style='color: #f44336;'>Files with Column Mismatches:</h3>")
    html_mismatch.append('<ul>')
    
    for mismatch in mismatch_files:
        # Access list elements using indices
        file_name = mismatch[0]
        expected_columns = mismatch[1]
        found_columns = mismatch[2]

        html_mismatch.append(f"<li><strong>File:</strong> {file_name}</li>")
        html_mismatch.append(f"<li><strong>Expected Columns:</strong> {expected_columns}</li>")
        html_mismatch.append(f"<li><strong>Found Columns:</strong> {found_columns}</li>")
        html_mismatch.append("<br>")
    
    html_mismatch.append('</ul>')
    return "\n".join(html_mismatch)

# Function to generate the section for valid files and the null count per column
def generate_null_count_section(valid_files):
    if not valid_files:
        return ""  # If there are no valid files, do not generate this section
    
    html_nulls = []
    html_nulls.append("<h3 style='color: #FF9800;'>Valid Files (Null Count by Column):</h3>")
    
    for file, df in valid_files:
        null_counts = df.isnull().sum()
        
        # Filter only the columns that have null values
        null_columns = null_counts[null_counts > 0]
        
        if not null_columns.empty:  # If there are columns with null values
            html_nulls.append(f"<h4>File: {file}</h4>")
            html_nulls.append('<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">')
            html_nulls.append("<tr style='background-color: #f2f2f2;'><th>Column</th><th>Null Count</th></tr>")
            
            for col, null_count in null_columns.items():
                html_nulls.append(f"<tr><td>{col}</td><td>{null_count}</td></tr>")
            
            html_nulls.append("</table><br>")
    
    return "\n".join(html_nulls)

# Function to send an email with an HTML report
def send_email_with_html_report(subject, body_html, sender_email, receiver_email, smtp_user, smtp_password):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Create the HTML content
    html_part = MIMEText(body_html, 'html')

    # Attach the HTML content to the message
    msg.attach(html_part)

    # Send email
    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(smtp_user, smtp_password)
        smtp_server.sendmail(msg["From"], msg["To"].split(','), msg.as_string())
        print(f"Email sent successfully to {receiver_email}.")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        smtp_server.quit()