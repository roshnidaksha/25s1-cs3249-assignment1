"""
I/O utilities for reading/writing test data.
This module is complete - students should NOT modify.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

import jsonschema

logger = logging.getLogger(__name__)


def read_jsonl(filepath: str) -> List[Dict]:
    """
    Read JSONL file and return list of dictionaries.
    
    Args:
        filepath: Path to JSONL file
        
    Returns:
        List of parsed JSON objects
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON at line {line_num}: {e}")
                raise
    
    logger.info(f"Read {len(records)} records from {filepath}")
    return records


def write_jsonl(records: List[Dict], filepath: str):
    """
    Write list of dictionaries to JSONL file.
    
    Args:
        records: List of dictionaries to write
        filepath: Output file path
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    logger.info(f"Wrote {len(records)} records to {filepath}")


def load_schema(schema_path: str) -> Dict:
    """
    Load JSON schema from file.
    
    Args:
        schema_path: Path to schema file
        
    Returns:
        Parsed schema dictionary
        
    Raises:
        FileNotFoundError: If schema file doesn't exist
    """
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    logger.info(f"Loaded schema from {schema_path}")
    return schema


def validate_record(record: Dict, schema: Dict) -> bool:
    """
    Validate a record against JSON schema.
    
    Args:
        record: Dictionary to validate
        schema: JSON schema
        
    Returns:
        True if valid, False otherwise
    """
    try:
        jsonschema.validate(instance=record, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Schema validation failed: {e.message}")
        return False
    except jsonschema.exceptions.SchemaError as e:
        logger.error(f"Schema is invalid: {e.message}")
        raise


def ensure_path(path: str) -> Path:
    """
    Ensure path exists and return Path object.
    
    Args:
        path: File or directory path
        
    Returns:
        Path object
    """
    path_obj = Path(path)
    if path_obj.is_file():
        path_obj.parent.mkdir(parents=True, exist_ok=True)
    else:
        path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def safe_json_loads(text: str, default: Any = None) -> Any:
    """
    Safely parse JSON with fallback to default.
    
    Args:
        text: JSON string
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def format_json(obj: Any, indent: int = 2) -> str:
    """
    Format object as pretty JSON string.
    
    Args:
        obj: Object to format
        indent: Indentation spaces
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(obj, indent=indent, ensure_ascii=False)