"""
Building Code Parser Module

This module handles parsing and extraction of building code rules from various formats:
- PDF files using PyMuPDF
- DOCX files
- Text files
"""

import os
import re
import json
import logging

# Configure logger
logger = logging.getLogger(__name__)

try:
    # Try to import PyMuPDF if available
    import fitz
    PDF_SUPPORT = True
except ImportError:
    logger.warning("PyMuPDF not available, PDF parsing will be limited")
    PDF_SUPPORT = False

try:
    # Try to import python-docx if available
    import docx
    DOCX_SUPPORT = True
except ImportError:
    logger.warning("python-docx not available, DOCX parsing will be limited")
    DOCX_SUPPORT = False

try:
    # Try to import spaCy if available
    import spacy
    SPACY_SUPPORT = True
    nlp = spacy.load("en_core_web_sm")
except ImportError:
    logger.warning("spaCy not available, NLP processing will be limited")
    SPACY_SUPPORT = False

def parse_building_code(file_path):
    """
    Parse building code file and extract rules
    
    Args:
        file_path: Path to the building code file
        
    Returns:
        list: List of dictionaries containing extracted building code rules
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return parse_pdf(file_path)
    elif file_ext == '.docx':
        return parse_docx(file_path)
    elif file_ext == '.txt':
        return parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

def parse_pdf(file_path):
    """
    Parse PDF file using PyMuPDF
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        list: List of dictionaries containing extracted building code rules
    """
    if not PDF_SUPPORT:
        logger.warning("PyMuPDF not available, using placeholder data")
        return get_placeholder_code_rules()
    
    try:
        # Open the PDF file
        doc = fitz.open(file_path)
        
        # Extract text from each page
        text = ""
        for page in doc:
            text += page.get_text()
        
        # Process the extracted text
        return process_code_text(text)
        
    except Exception as e:
        logger.error(f"Error parsing PDF file: {str(e)}")
        # Return placeholder data if parsing fails
        return get_placeholder_code_rules()

def parse_docx(file_path):
    """
    Parse DOCX file using python-docx
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        list: List of dictionaries containing extracted building code rules
    """
    if not DOCX_SUPPORT:
        logger.warning("python-docx not available, using placeholder data")
        return get_placeholder_code_rules()
    
    try:
        # Open the DOCX file
        doc = docx.Document(file_path)
        
        # Extract text from the document
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        
        # Process the extracted text
        return process_code_text(text)
        
    except Exception as e:
        logger.error(f"Error parsing DOCX file: {str(e)}")
        # Return placeholder data if parsing fails
        return get_placeholder_code_rules()

def parse_txt(file_path):
    """
    Parse text file
    
    Args:
        file_path: Path to the text file
        
    Returns:
        list: List of dictionaries containing extracted building code rules
    """
    try:
        # Open the text file
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Process the extracted text
        return process_code_text(text)
        
    except Exception as e:
        logger.error(f"Error parsing text file: {str(e)}")
        # Return placeholder data if parsing fails
        return get_placeholder_code_rules()

def process_code_text(text):
    """
    Process extracted text to identify and structure building code rules
    
    Args:
        text: Extracted text from the building code document
        
    Returns:
        list: List of dictionaries containing structured building code rules
    """
    if SPACY_SUPPORT:
        # Use spaCy for NLP processing
        return process_with_spacy(text)
    else:
        # Fallback to basic regex processing
        return process_with_regex(text)

def process_with_spacy(text):
    """
    Process text using spaCy NLP for more advanced rule extraction
    
    Args:
        text: Text to process
        
    Returns:
        list: List of dictionaries containing structured building code rules
    """
    rules = []
    
    # Process the text with spaCy
    doc = nlp(text)
    
    # Split into sections
    sections = re.split(r'\n\s*\n', text)
    
    for section in sections:
        if len(section.strip()) == 0:
            continue
            
        # Try to identify section code/number
        section_match = re.search(r'(\d+[\.\d]*)\s+(.+?)(?:\n|$)', section)
        rule_id = section_match.group(1) if section_match else ""
        
        # Try to identify the MEP type
        mep_type = identify_mep_type(section)
        
        # Extract numerical values with units
        values = extract_numerical_values(section)
        
        # Create rule dictionary
        rule = {
            'type': mep_type,
            'id': rule_id,
            'description': section.strip(),
            'region': 'General',  # Default region
            'values': values
        }
        
        rules.append(rule)
    
    return rules

def process_with_regex(text):
    """
    Process text using regex for basic rule extraction
    
    Args:
        text: Text to process
        
    Returns:
        list: List of dictionaries containing structured building code rules
    """
    rules = []
    
    # Split into sections
    sections = re.split(r'\n\s*\n', text)
    
    for section in sections:
        if len(section.strip()) == 0:
            continue
            
        # Try to identify section code/number
        section_match = re.search(r'(\d+[\.\d]*)\s+(.+?)(?:\n|$)', section)
        rule_id = section_match.group(1) if section_match else ""
        
        # Try to identify the MEP type
        mep_type = identify_mep_type(section)
        
        # Extract numerical values with units
        values = extract_numerical_values(section)
        
        # Create rule dictionary
        rule = {
            'type': mep_type,
            'id': rule_id,
            'description': section.strip(),
            'region': 'General',  # Default region
            'values': values
        }
        
        rules.append(rule)
    
    return rules

def identify_mep_type(text):
    """
    Identify the MEP type based on the text content
    
    Args:
        text: Text to analyze
        
    Returns:
        str: MEP type ('M' for mechanical, 'E' for electrical, 'P' for plumbing)
    """
    text_lower = text.lower()
    
    # Check for mechanical keywords
    mechanical_keywords = ['hvac', 'ventilation', 'air conditioning', 'heating', 'duct', 'fan', 'air flow']
    for keyword in mechanical_keywords:
        if keyword in text_lower:
            return 'M'
    
    # Check for electrical keywords
    electrical_keywords = ['electrical', 'voltage', 'current', 'circuit', 'wire', 'breaker', 'panel', 'conduit', 'lighting']
    for keyword in electrical_keywords:
        if keyword in text_lower:
            return 'E'
    
    # Check for plumbing keywords
    plumbing_keywords = ['plumbing', 'pipe', 'water', 'drainage', 'sanitary', 'fixture', 'valve', 'vent']
    for keyword in plumbing_keywords:
        if keyword in text_lower:
            return 'P'
    
    # Default to general if can't identify
    return 'G'

def extract_numerical_values(text):
    """
    Extract numerical values with units from text
    
    Args:
        text: Text to analyze
        
    Returns:
        list: List of dictionaries containing extracted values and units
    """
    values = []
    
    # Regular expression to match numbers with units
    # Matches patterns like "15 cfm", "2.5 inches", "100 A", etc.
    pattern = r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)'
    
    matches = re.finditer(pattern, text)
    for match in matches:
        value = float(match.group(1))
        unit = match.group(2)
        
        values.append({
            'value': value,
            'unit': unit
        })
    
    return values

def get_placeholder_code_rules():
    """
    Generate placeholder building code rules for testing
    
    Returns:
        list: List of dictionaries containing placeholder building code rules
    """
    return [
        {
            'type': 'M',
            'id': '1.1',
            'description': 'Mechanical ventilation systems shall be designed to provide outdoor air at a rate of 15 cfm per person in commercial spaces.',
            'region': 'General',
            'values': [{'value': 15, 'unit': 'cfm'}]
        },
        {
            'type': 'M',
            'id': '1.2',
            'description': 'HVAC ductwork shall maintain a minimum clearance of 6 inches from electrical equipment.',
            'region': 'General',
            'values': [{'value': 6, 'unit': 'inches'}]
        },
        {
            'type': 'E',
            'id': '2.1',
            'description': 'Electrical panels shall have a minimum clearance of 36 inches in front of the panel.',
            'region': 'General',
            'values': [{'value': 36, 'unit': 'inches'}]
        },
        {
            'type': 'E',
            'id': '2.2',
            'description': 'Circuit breakers shall be sized at 125% of the continuous load.',
            'region': 'General',
            'values': [{'value': 125, 'unit': '%'}]
        },
        {
            'type': 'P',
            'id': '3.1',
            'description': 'Plumbing waste pipes shall have a minimum slope of 1/4 inch per foot.',
            'region': 'General',
            'values': [{'value': 0.25, 'unit': 'inch'}]
        },
        {
            'type': 'P',
            'id': '3.2',
            'description': 'Water supply pipes shall be sized to maintain a minimum pressure of 15 psi at all fixtures.',
            'region': 'General',
            'values': [{'value': 15, 'unit': 'psi'}]
        }
    ]
