# Network Programming and HTTP Clients
import socket
import urllib.request
import urllib.parse
import http.client
import ftplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

def socket_programming():
    """Basic socket operations"""
    try:
        # Create socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        
        # Connect to a server
        client_socket.connect(('httpbin.org', 80))
        
        # Send HTTP request
        request = b"GET /json HTTP/1.1\r\nHost: httpbin.org\r\n\r\n"
        client_socket.send(request)
        
        # Receive response
        response = client_socket.recv(4096)
        
        client_socket.close()
        
        return {'response_length': len(response), 'success': True}
    except Exception as e:
        return {'error': str(e), 'success': False}

def urllib_operations():
    """URL operations with urllib"""
    try:
        # Simple GET request
        url = 'https://httpbin.org/json'
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read()
            json_data = json.loads(data.decode('utf-8'))
        
        # POST request
        post_data = urllib.parse.urlencode({'key': 'value', 'name': 'test'})
        post_data = post_data.encode('utf-8')
        
        post_url = 'https://httpbin.org/post'
        request = urllib.request.Request(post_url, data=post_data)
        
        with urllib.request.urlopen(request, timeout=10) as response:
            post_response = response.read()
        
        return {
            'get_data': len(str(json_data)),
            'post_response_length': len(post_response),
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}

def http_client_operations():
    """HTTP client operations"""
    try:
        # HTTP connection
        conn = http.client.HTTPSConnection('httpbin.org', timeout=10)
        
        # GET request
        conn.request('GET', '/json')
        response = conn.getresponse()
        data = response.read()
        
        # POST request
        headers = {'Content-Type': 'application/json'}
        post_data = json.dumps({'test': 'data'})
        conn.request('POST', '/post', post_data, headers)
        post_response = conn.getresponse()
        post_data_response = post_response.read()
        
        conn.close()
        
        return {
            'get_status': response.status,
            'post_status': post_response.status,
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}

def ftp_operations():
    """FTP operations (demonstration only)"""
    # Note: This is a demonstration of FTP imports and basic structure
    try:
        ftp_config = {
            'server': 'ftp.example.com',
            'username': 'anonymous',
            'password': 'guest@example.com'
        }
        
        # FTP connection would go here in a real scenario
        # ftp = ftplib.FTP(ftp_config['server'])
        # ftp.login(ftp_config['username'], ftp_config['password'])
        # files = ftp.nlst()
        # ftp.quit()
        
        return {'simulated': True, 'files_would_list': 0}
    except Exception as e:
        return {'error': str(e), 'success': False}

def email_operations():
    """Email operations (demonstration only)"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = 'sender@example.com'
        msg['To'] = 'recipient@example.com'
        msg['Subject'] = 'Test Email'
        
        body = 'This is a test email sent from Python.'
        msg.attach(MIMEText(body, 'plain'))
        
        # SMTP configuration (not actually sending)
        smtp_config = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': 'your_username',
            'password': 'your_password'
        }
        
        # Email would be sent here in a real scenario
        # server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        # server.starttls()
        # server.login(smtp_config['username'], smtp_config['password'])
        # server.send_message(msg)
        # server.quit()
        
        return {'message_created': True, 'attachments': len(msg.get_payload())}
    except Exception as e:
        return {'error': str(e), 'success': False}

if __name__ == "__main__":
    print("Network programming operations...")
    
    socket_result = socket_programming()
    print(f"Socket operations: {socket_result}")
    
    urllib_result = urllib_operations()
    print(f"urllib operations: {urllib_result}")
    
    http_result = http_client_operations()
    print(f"HTTP client operations: {http_result}")
    
    ftp_result = ftp_operations()
    print(f"FTP operations: {ftp_result}")
    
    email_result = email_operations()
    print(f"Email operations: {email_result}")
