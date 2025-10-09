# PDF Processing and Document Generation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
import pypdf as PyPDF2
# import fitz  # PyMuPDF - not available
from fpdf import FPDF

def create_pdf_with_reportlab():
    """Create PDF using ReportLab"""
    filename = '/tmp/reportlab_document.pdf'
    
    # Create document
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    
    # Title
    title = Paragraph("Sample PDF Document", styles['Title'])
    content.append(title)
    content.append(Spacer(1, 12))
    
    # Normal text
    text = """
    This is a sample PDF document created using ReportLab library.
    It demonstrates various PDF creation capabilities including:
    - Text formatting
    - Tables
    - Styling
    - Layout management
    """
    
    para = Paragraph(text, styles['Normal'])
    content.append(para)
    content.append(Spacer(1, 12))
    
    # Table
    data = [
        ['Product', 'Quantity', 'Price'],
        ['Item 1', '5', '$10.00'],
        ['Item 2', '3', '$15.00'],
        ['Item 3', '8', '$7.50'],
        ['Total', '16', '$32.50']
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(table)
    
    # Build PDF
    doc.build(content)
    
    return {
        'filename': filename,
        'pages': 1,
        'elements': len(content)
    }

def simple_pdf_with_canvas():
    """Create simple PDF with canvas"""
    filename = '/tmp/canvas_document.pdf'
    
    # Create canvas
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Add content
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, height - 100, "Canvas PDF Document")
    
    c.setFont("Helvetica", 12)
    y_position = height - 150
    
    lines = [
        "This PDF was created using ReportLab Canvas.",
        "Canvas provides low-level control over PDF creation.",
        "You can position text, draw shapes, and add images precisely.",
        "",
        "Features demonstrated:",
        "• Text positioning",
        "• Font control",
        "• Basic graphics"
    ]
    
    for line in lines:
        c.drawString(100, y_position, line)
        y_position -= 20
    
    # Add a rectangle
    c.setStrokeColor(colors.blue)
    c.setFillColor(colors.lightblue)
    c.rect(100, y_position - 50, 200, 40, fill=1)
    
    # Add text in rectangle
    c.setFillColor(colors.black)
    c.drawString(120, y_position - 35, "Rectangle with text")
    
    c.save()
    
    return {
        'filename': filename,
        'width': width,
        'height': height,
        'lines': len(lines)
    }

def fpdf_document():
    """Create PDF using FPDF"""
    filename = '/tmp/fpdf_document.pdf'
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    
    # Title
    pdf.cell(0, 10, 'FPDF Document Example', 0, 1, 'C')
    pdf.ln(10)
    
    # Content
    pdf.set_font('Arial', '', 12)
    content = [
        "This document demonstrates FPDF library capabilities.",
        "FPDF is a lightweight PDF generation library.",
        "",
        "Key features:",
        "- Simple API",
        "- Unicode support", 
        "- Image insertion",
        "- Page formatting"
    ]
    
    for line in content:
        if line:
            pdf.cell(0, 10, line, 0, 1)
        else:
            pdf.ln(5)
    
    # Add a colored cell
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 10, 'Colored background cell', 1, 1, 'C', 1)
    
    pdf.output(filename)
    
    return {
        'filename': filename,
        'content_lines': len(content)
    }

def read_pdf_with_pypdf2():
    """Read PDF using PyPDF2"""
    # First create a sample PDF to read
    sample_pdf = '/tmp/sample_to_read.pdf'
    
    # Create sample PDF
    c = canvas.Canvas(sample_pdf)
    c.drawString(100, 750, "Sample PDF for reading test")
    c.drawString(100, 730, "This PDF contains sample text.")
    c.drawString(100, 710, "Line 3 of the document.")
    c.showPage()
    c.drawString(100, 750, "Page 2 content")
    c.save()
    
    try:
        # Read PDF
        with open(sample_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Get metadata
            num_pages = len(pdf_reader.pages)
            
            # Extract text from all pages
            text_content = []
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                text_content.append(text)
            
            # Get document info
            metadata = pdf_reader.metadata
            
            return {
                'num_pages': num_pages,
                'text_extracted': len(''.join(text_content)),
                'has_metadata': metadata is not None,
                'pages_content': text_content
            }
    except Exception as e:
        return {'error': str(e)}

def pdf_manipulation():
    """PDF manipulation operations"""
    try:
        # Create source PDFs
        pdf1_path = '/tmp/pdf1.pdf'
        pdf2_path = '/tmp/pdf2.pdf'
        
        # Create first PDF
        c1 = canvas.Canvas(pdf1_path)
        c1.drawString(100, 750, "Document 1 - Page 1")
        c1.showPage()
        c1.drawString(100, 750, "Document 1 - Page 2")
        c1.save()
        
        # Create second PDF
        c2 = canvas.Canvas(pdf2_path)
        c2.drawString(100, 750, "Document 2 - Page 1")
        c2.save()
        
        # Merge PDFs
        merger = PyPDF2.PdfMerger()
        merger.append(pdf1_path)
        merger.append(pdf2_path)
        
        merged_path = '/tmp/merged.pdf'
        merger.write(merged_path)
        merger.close()
        
        # Split PDF (extract specific pages)
        with open(pdf1_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_writer = PyPDF2.PdfWriter()
            
            # Add first page only
            pdf_writer.add_page(pdf_reader.pages[0])
            
            split_path = '/tmp/split.pdf'
            with open(split_path, 'wb') as output_file:
                pdf_writer.write(output_file)
        
        return {
            'merge_successful': True,
            'split_successful': True,
            'merged_file': merged_path,
            'split_file': split_path
        }
        
    except Exception as e:
        return {'error': str(e)}

def pymupdf_operations():
    """PyMuPDF (fitz) operations - Simulated"""
    try:
        # Create sample PDF
        sample_path = '/tmp/pymupdf_sample.pdf'
        c = canvas.Canvas(sample_path)
        c.drawString(100, 750, "PyMuPDF Test Document")
        c.drawString(100, 730, "This document tests PyMuPDF capabilities.")
        c.save()
        
        # Simulate PyMuPDF operations (fitz not available)
        return {
            'pages': 1,
            'text_extracted': "PyMuPDF Test Document\\nThis document tests PyMuPDF capabilities.",
            'page_size': (612, 792),
            'simulation': True
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("PDF processing and document generation...")
    
    # ReportLab document
    reportlab_result = create_pdf_with_reportlab()
    print(f"ReportLab: Created {reportlab_result['filename']} with {reportlab_result['elements']} elements")
    
    # Canvas document
    canvas_result = simple_pdf_with_canvas()
    print(f"Canvas: Created {canvas_result['filename']} with {canvas_result['lines']} lines")
    
    # FPDF document
    fpdf_result = fpdf_document()
    print(f"FPDF: Created {fpdf_result['filename']} with {fpdf_result['content_lines']} content lines")
    
    # PyPDF2 reading
    read_result = read_pdf_with_pypdf2()
    if 'error' not in read_result:
        print(f"PyPDF2 read: {read_result['num_pages']} pages, {read_result['text_extracted']} characters")
    
    # PDF manipulation
    manip_result = pdf_manipulation()
    if 'error' not in manip_result:
        print(f"PDF manipulation: Merge and split successful")
    
    # PyMuPDF operations
    pymupdf_result = pymupdf_operations()
    if 'error' not in pymupdf_result:
        print(f"PyMuPDF: {pymupdf_result['pages']} pages (simulation mode)")