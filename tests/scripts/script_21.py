# Email and Communication
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import poplib
import ssl
from email.header import decode_header

def smtp_email_sending():
    """SMTP email sending demonstration"""
    # Email configuration (demonstration only)
    smtp_config = {
        'server': 'smtp.gmail.com',
        'port': 587,
        'username': 'your_email@gmail.com',
        'password': 'your_app_password'
    }
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_config['username']
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Test Email from Python'
    
    # Email body
    body = '''
    Hello,
    
    This is a test email sent from a Python application.
    It demonstrates SMTP email functionality.
    
    Best regards,
    Python Script
    '''
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Simulate sending (without actual SMTP connection)
    try:
        # In real scenario:
        # server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        # server.starttls()
        # server.login(smtp_config['username'], smtp_config['password'])
        # text = msg.as_string()
        # server.sendmail(smtp_config['username'], 'recipient@example.com', text)
        # server.quit()
        
        return {
            'status': 'simulated',
            'message_size': len(msg.as_string()),
            'recipients': 1
        }
    except Exception as e:
        return {'error': str(e)}

def html_email_with_attachments():
    """HTML email with attachments"""
    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'HTML Email with Attachment'
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient@example.com'
    
    # Create HTML content
    html = '''
    <html>
      <head></head>
      <body>
        <h2>Welcome to our Newsletter!</h2>
        <p>This is an <b>HTML email</b> with formatting.</p>
        <ul>
          <li>Feature 1</li>
          <li>Feature 2</li>
          <li>Feature 3</li>
        </ul>
        <p>Visit our <a href="https://example.com">website</a> for more info.</p>
      </body>
    </html>
    '''
    
    # Create plain text version
    text = '''
    Welcome to our Newsletter!
    
    This is a plain text email version.
    
    Features:
    - Feature 1
    - Feature 2
    - Feature 3
    
    Visit our website: https://example.com
    '''
    
    # Convert to MIMEText objects
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    
    # Add parts to message
    msg.attach(part1)
    msg.attach(part2)
    
    # Simulate attachment (create dummy file content)
    attachment_content = b"This is a dummy attachment content for demonstration."
    
    # Create attachment
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(attachment_content)
    encoders.encode_base64(attachment)
    attachment.add_header(
        'Content-Disposition',
        'attachment; filename="report.txt"'
    )
    msg.attach(attachment)
    
    return {
        'html_length': len(html),
        'text_length': len(text),
        'attachment_size': len(attachment_content),
        'total_message_size': len(msg.as_string())
    }

def imap_email_reading():
    """IMAP email reading demonstration"""
    # IMAP configuration (demonstration only)
    imap_config = {
        'server': 'imap.gmail.com',
        'port': 993,
        'username': 'your_email@gmail.com',
        'password': 'your_app_password'
    }
    
    try:
        # Simulate IMAP operations
        # In real scenario:
        # mail = imaplib.IMAP4_SSL(imap_config['server'], imap_config['port'])
        # mail.login(imap_config['username'], imap_config['password'])
        # mail.select('inbox')
        
        # Simulate email data
        simulated_emails = [
            {
                'from': 'sender1@example.com',
                'subject': 'Meeting Reminder',
                'date': '2024-01-01',
                'body': 'Don\'t forget about our meeting tomorrow.'
            },
            {
                'from': 'sender2@example.com',
                'subject': 'Project Update',
                'date': '2024-01-02',
                'body': 'The project is progressing well.'
            }
        ]
        
        # Process emails
        processed_emails = []
        for email_data in simulated_emails:
            processed_emails.append({
                'from': email_data['from'],
                'subject': email_data['subject'],
                'word_count': len(email_data['body'].split()),
                'date': email_data['date']
            })
        
        return {
            'total_emails': len(processed_emails),
            'processed_emails': processed_emails
        }
        
    except Exception as e:
        return {'error': str(e)}

def pop3_email_retrieval():
    """POP3 email retrieval demonstration"""
    pop3_config = {
        'server': 'pop.gmail.com',
        'port': 995,
        'username': 'your_email@gmail.com',
        'password': 'your_app_password'
    }
    
    try:
        # Simulate POP3 operations
        # In real scenario:
        # mail = poplib.POP3_SSL(pop3_config['server'], pop3_config['port'])
        # mail.user(pop3_config['username'])
        # mail.pass_(pop3_config['password'])
        
        # Simulate email statistics
        email_stats = {
            'message_count': 15,
            'mailbox_size': 2048576,  # bytes
            'oldest_message_date': '2024-01-01',
            'newest_message_date': '2024-01-15'
        }
        
        # mail.quit()
        
        return email_stats
        
    except Exception as e:
        return {'error': str(e)}

def email_parsing_example():
    """Email parsing and header analysis"""
    # Sample email content
    raw_email = '''From: sender@example.com
To: recipient@example.com
Subject: =?utf-8?B?VGVzdCBTdWJqZWN0IMWGxJE=?=
Date: Mon, 01 Jan 2024 10:00:00 +0000
Content-Type: multipart/alternative; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset=utf-8

This is the plain text version of the email.
It contains important information.

--boundary123
Content-Type: text/html; charset=utf-8

<html>
<body>
<h1>This is the HTML version</h1>
<p>It contains <b>formatted</b> text.</p>
</body>
</html>

--boundary123--
'''
    
    # Parse email
    msg = email.message_from_string(raw_email)
    
    # Extract headers
    headers = {
        'from': msg['From'],
        'to': msg['To'],
        'subject': msg['Subject'],
        'date': msg['Date'],
        'content_type': msg['Content-Type']
    }
    
    # Decode subject if encoded
    decoded_subject = decode_header(headers['subject'])
    if decoded_subject[0][1]:
        headers['decoded_subject'] = decoded_subject[0][0].decode(decoded_subject[0][1])
    else:
        headers['decoded_subject'] = decoded_subject[0][0]
    
    # Extract body parts
    parts = []
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ['text/plain', 'text/html']:
                parts.append({
                    'type': content_type,
                    'content': part.get_payload(decode=True).decode('utf-8', errors='ignore'),
                    'charset': part.get_content_charset()
                })
    
    return {
        'headers': headers,
        'parts_count': len(parts),
        'has_html': any(part['type'] == 'text/html' for part in parts),
        'has_plain': any(part['type'] == 'text/plain' for part in parts)
    }

def email_validation():
    """Email address validation"""
    import re
    
    def validate_email(email_address):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email_address) is not None
    
    # Test email addresses
    test_emails = [
        'valid@example.com',
        'user.name+tag@example.co.uk',
        'invalid.email',
        '@invalid.com',
        'valid@sub.domain.com',
        'invalid@.com',
        'test@localhost'
    ]
    
    validation_results = []
    for email_addr in test_emails:
        is_valid = validate_email(email_addr)
        validation_results.append({
            'email': email_addr,
            'valid': is_valid
        })
    
    valid_count = sum(1 for result in validation_results if result['valid'])
    
    return {
        'total_tested': len(validation_results),
        'valid_count': valid_count,
        'invalid_count': len(validation_results) - valid_count,
        'results': validation_results
    }

if __name__ == "__main__":
    print("Email and communication operations...")
    
    # SMTP email sending
    smtp_result = smtp_email_sending()
    print(f"SMTP email: {smtp_result}")
    
    # HTML email with attachments
    html_result = html_email_with_attachments()
    print(f"HTML email created: {html_result['total_message_size']} bytes")
    
    # IMAP email reading
    imap_result = imap_email_reading()
    if 'error' not in imap_result:
        print(f"IMAP: {imap_result['total_emails']} emails processed")
    
    # POP3 email retrieval
    pop3_result = pop3_email_retrieval()
    if 'error' not in pop3_result:
        print(f"POP3: {pop3_result['message_count']} messages in mailbox")
    
    # Email parsing
    parsing_result = email_parsing_example()
    print(f"Email parsing: {parsing_result['parts_count']} parts found")
    
    # Email validation
    validation_result = email_validation()
    print(f"Email validation: {validation_result['valid_count']}/{validation_result['total_tested']} valid")