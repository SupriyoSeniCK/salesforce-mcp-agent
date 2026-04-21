# tools.py

from simple_salesforce import Salesforce
from dotenv import load_dotenv
import os
from typing import Any, Dict, Optional

load_dotenv()

_sf_client: Optional[Salesforce] = None


def get_sf() -> Salesforce:
    """Create the Salesforce client lazily so MCP server startup does not require a live connection."""
    global _sf_client
    if _sf_client is None:
        _sf_client = Salesforce(
            username=os.getenv("SF_USERNAME"),
            password=os.getenv("SF_PASSWORD"),
            security_token=os.getenv("SF_SECURITY_TOKEN"),
            domain="login"
        )
    return _sf_client


def get_record_tool(object_type: str, record_id: str, fields: Optional[list] = None) -> Dict[str, Any]:
    """
    Retrieve a Salesforce record by ID with automatic summarization.
    
    Args:
        object_type: Salesforce object type (Account, Contact, Opportunity, etc)
        record_id: The record ID to retrieve
        fields: Optional list of specific fields to retrieve
    
    Returns:
        Dict containing the record data, summary, and metadata
    """
    try:
        sf = get_sf()
        sf_object = getattr(sf, object_type)
        
        if fields:
            field_str = ", ".join(fields)
            query = f"SELECT {field_str} FROM {object_type} WHERE Id='{record_id}'"
            result = sf.query(query)
            record = result.get('records', [{}])[0] if result.get('records') else None
        else:
            record = sf_object.get(record_id)
        
        if not record:
            return {"error": "Record not found"}
        
        # Automatically call summarize_record_tool to include summary
        summary = summarize_record_tool(object_type, record_id)
        
        return {
            "status": "success",
            "full_record": record,
            "summary": summary,
            "object_type": object_type,
            "record_id": record_id
        }
    except Exception as e:
        return {"error": f"Failed to get record: {str(e)}"}


def update_record_tool(object_type: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a Salesforce record with new field values.
    
    Args:
        object_type: Salesforce object type
        record_id: The record ID to update
        fields: Dictionary of fields and values to update
    
    Returns:
        Dict with status confirmation or error
    """
    try:
        sf = get_sf()
        sf_object = getattr(sf, object_type)
        sf_object.update(record_id, fields)
        return {
            "status": "success",
            "message": f"Record {record_id} updated successfully",
            "record_id": record_id
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to update record: {str(e)}"}


def summarize_record_tool(object_type: str, record_id: str) -> Dict[str, Any]:
    """
    Retrieve and summarize a Salesforce record's key information.
    
    Args:
        object_type: Salesforce object type
        record_id: The record ID to summarize
    
    Returns:
        Dict containing summarized record data
    """
    try:
        sf = get_sf()
        sf_object = getattr(sf, object_type)
        record = sf_object.get(record_id)
        
        # Extract key fields based on object type
        summary = {
            "id": record.get("Id"),
            "type": object_type,
            "name": record.get("Name") or record.get("Subject"),
            "created_date": record.get("CreatedDate"),
            "last_modified": record.get("LastModifiedDate"),
        }
        
        return summary
    except Exception as e:
        return {"error": f"Failed to summarize record: {str(e)}"}


def validate_update_tool(object_type: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that a proposed update is safe before applying it.
    
    Args:
        object_type: Salesforce object type
        record_id: The record ID to validate
        fields: Dictionary of fields proposed for update
    
    Returns:
        Dict with validation result and any warnings
    """
    try:
        sf = get_sf()
        warnings = []
        
        # Check if record exists
        sf_object = getattr(sf, object_type)
        record = sf_object.get(record_id)
        
        if not record:
            return {"valid": False, "error": "Record not found"}
        
        # Validate field names (basic check)
        for field_key in fields.keys():
            if field_key.startswith("_"):
                warnings.append(f"Field '{field_key}' is a system field - be careful updating it")
        
        # Check for large text updates
        for field_key, field_value in fields.items():
            if isinstance(field_value, str) and len(field_value) > 4000:
                warnings.append(f"Field '{field_key}' exceeds recommended length")
        
        return {
            "valid": True,
            "record_id": record_id,
            "fields_to_update": len(fields),
            "warnings": warnings if warnings else []
        }
    except Exception as e:
        return {"valid": False, "error": f"Validation failed: {str(e)}"}


def salesforce_tool(params: dict):
    """
    Legacy tool for backward compatibility.
    Dispatches to specific tool handlers based on action.
    """
    action = params.get("action")
    obj = params.get("object")

    try:
        sf = get_sf()
        sf_object = getattr(sf, obj)
    except:
        return {"error": f"Invalid object {obj}"}

    if action == "GET":
        if params.get("record_id"):
            return get_record_tool(obj, params["record_id"])

        elif params.get("filters"):
            filters = " AND ".join(
                [f"{k}='{v}'" for k, v in params["filters"].items()]
            )
            query = f"SELECT Id, Name FROM {obj} WHERE {filters} LIMIT 1"
            return sf.query(query)

    elif action == "UPDATE":
        return update_record_tool(obj, params["record_id"], params["fields"])

    elif action == "CREATE":
        try:
            result = sf_object.create(params["fields"])
            return {"status": "success", "record_id": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return {"error": "Unsupported action"}


# Tool registry for MCP
TOOLS = {
    "get_record": get_record_tool,
    "update_record": update_record_tool,
    "summarize_record": summarize_record_tool,
    "validate_update": validate_update_tool,
}
