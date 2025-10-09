# XML and JSON Processing
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
from xml.sax import ContentHandler, make_parser
import xmltodict
from lxml import etree, html
import yaml

def json_operations():
    """JSON processing operations"""
    # Create sample data
    data = {
        "users": [
            {"id": 1, "name": "John", "email": "john@example.com"},
            {"id": 2, "name": "Jane", "email": "jane@example.com"}
        ],
        "metadata": {
            "version": "1.0",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    }
    
    # JSON serialization
    json_string = json.dumps(data, indent=2)
    
    # JSON deserialization
    parsed_data = json.loads(json_string)
    
    # Pretty printing
    pretty_json = json.dumps(data, indent=4, sort_keys=True)
    
    return {
        'user_count': len(parsed_data['users']),
        'json_length': len(json_string),
        'pretty_length': len(pretty_json)
    }

def xml_etree_operations():
    """XML processing with ElementTree"""
    # Create XML structure
    root = ET.Element("library")
    
    # Add books
    for i in range(3):
        book = ET.SubElement(root, "book", id=str(i+1))
        title = ET.SubElement(book, "title")
        title.text = f"Book Title {i+1}"
        author = ET.SubElement(book, "author")
        author.text = f"Author {i+1}"
        year = ET.SubElement(book, "year")
        year.text = str(2020 + i)
    
    # Convert to string
    xml_string = ET.tostring(root, encoding='unicode')
    
    # Parse XML string
    parsed_root = ET.fromstring(xml_string)
    books = parsed_root.findall('book')
    
    # Extract data
    book_data = []
    for book in books:
        book_info = {
            'id': book.get('id'),
            'title': book.find('title').text,
            'author': book.find('author').text,
            'year': book.find('year').text
        }
        book_data.append(book_info)
    
    return {
        'xml_length': len(xml_string),
        'book_count': len(book_data),
        'first_book': book_data[0] if book_data else None
    }

def xml_dom_operations():
    """XML processing with DOM"""
    # Create DOM document
    doc = xml.dom.minidom.Document()
    
    # Create root element
    catalog = doc.createElement("catalog")
    doc.appendChild(catalog)
    
    # Add products
    for i in range(2):
        product = doc.createElement("product")
        product.setAttribute("id", str(i+1))
        
        name = doc.createElement("name")
        name.appendChild(doc.createTextNode(f"Product {i+1}"))
        product.appendChild(name)
        
        price = doc.createElement("price")
        price.appendChild(doc.createTextNode(f"{(i+1)*10}.99"))
        product.appendChild(price)
        
        catalog.appendChild(product)
    
    # Convert to pretty XML
    pretty_xml = doc.toprettyxml(indent="  ")
    
    return {
        'dom_xml_length': len(pretty_xml),
        'product_count': len(doc.getElementsByTagName('product'))
    }

class XMLSAXHandler(ContentHandler):
    """SAX handler for XML parsing"""
    
    def __init__(self):
        self.current_element = None
        self.items = []
        self.current_item = {}
    
    def startElement(self, name, attrs):
        self.current_element = name
        if name == "item":
            self.current_item = {}
            if "id" in attrs:
                self.current_item["id"] = attrs["id"]
    
    def characters(self, content):
        if self.current_element in ["name", "description", "price"]:
            self.current_item[self.current_element] = content.strip()
    
    def endElement(self, name):
        if name == "item" and self.current_item:
            self.items.append(self.current_item)
        self.current_element = None

def xml_sax_operations():
    """XML processing with SAX"""
    xml_data = """<?xml version="1.0"?>
    <inventory>
        <item id="1">
            <name>Widget</name>
            <description>A useful widget</description>
            <price>19.99</price>
        </item>
        <item id="2">
            <name>Gadget</name>
            <description>An amazing gadget</description>
            <price>29.99</price>
        </item>
    </inventory>"""
    
    # Create parser and handler
    parser = make_parser()
    handler = XMLSAXHandler()
    parser.setContentHandler(handler)
    
    # Parse XML
    from io import StringIO
    parser.parse(StringIO(xml_data))
    
    return {
        'sax_items': len(handler.items),
        'first_item': handler.items[0] if handler.items else None
    }

def lxml_operations():
    """XML processing with lxml"""
    # Create XML with lxml
    root = etree.Element("company")
    
    # Add departments
    for dept_name in ["Engineering", "Sales", "Marketing"]:
        dept = etree.SubElement(root, "department", name=dept_name)
        
        # Add employees
        for i in range(2):
            employee = etree.SubElement(dept, "employee", id=str(i+1))
            name = etree.SubElement(employee, "name")
            name.text = f"{dept_name} Employee {i+1}"
            salary = etree.SubElement(employee, "salary")
            salary.text = str(50000 + i * 10000)
    
    # Convert to string
    xml_string = etree.tostring(root, pretty_print=True, encoding='unicode')
    
    # XPath queries
    all_employees = root.xpath("//employee")
    engineering_employees = root.xpath("//department[@name='Engineering']//employee")
    
    # Parse HTML (lxml can handle both XML and HTML)
    html_content = "<html><body><h1>Title</h1><p>Paragraph</p></body></html>"
    html_doc = html.fromstring(html_content)
    title = html_doc.xpath("//h1/text()")[0]
    
    return {
        'xml_length': len(xml_string),
        'total_employees': len(all_employees),
        'engineering_employees': len(engineering_employees),
        'html_title': title
    }

def yaml_operations():
    """YAML processing"""
    # Create YAML data
    yaml_data = {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'credentials': {
                'username': 'admin',
                'password': 'secret'
            }
        },
        'features': ['feature1', 'feature2', 'feature3'],
        'debug': True,
        'timeout': 30
    }
    
    # Convert to YAML string
    yaml_string = yaml.dump(yaml_data, default_flow_style=False)
    
    # Parse YAML string
    parsed_yaml = yaml.safe_load(yaml_string)
    
    return {
        'yaml_length': len(yaml_string),
        'feature_count': len(parsed_yaml['features']),
        'database_port': parsed_yaml['database']['port']
    }

if __name__ == "__main__":
    print("XML and JSON processing operations...")
    
    json_result = json_operations()
    print(f"JSON: {json_result['user_count']} users processed")
    
    etree_result = xml_etree_operations()
    print(f"ElementTree: {etree_result['book_count']} books processed")
    
    dom_result = xml_dom_operations()
    print(f"DOM: {dom_result['product_count']} products processed")
    
    sax_result = xml_sax_operations()
    print(f"SAX: {sax_result['sax_items']} items processed")
    
    lxml_result = lxml_operations()
    print(f"lxml: {lxml_result['total_employees']} employees processed")
    
    yaml_result = yaml_operations()
    print(f"YAML: {yaml_result['feature_count']} features configured")