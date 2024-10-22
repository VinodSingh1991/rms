def convert_columns_to_modal(column_names):
    """
    Converts the column names to a modal format with key, type, and name.
    """
    return [
        {
            "key": column_name,
            "type": "string",  # Assumed all columns are strings, update if needed
            "name": column_name
        }
        for column_name in column_names
    ]
    
def create_list_modal(rows, column_names):
    mapped_rows = []
    
    column_keys = [column['key'] for column in convert_columns_to_modal(column_names)]
    
    for row in rows:
        # Create a dictionary by zipping column keys with row values
        mapped_row = dict(zip(column_keys, row))
        
        # Add the mapped row dictionary to the list
        mapped_rows.append(mapped_row)
    
    return mapped_rows
        


def convert_listing_info(data_config):
    rows = data_config["rows"]
    columns = data_config["columns"]
    """
    Converts the rows and column names to a structured modal format.
    """
    
    rows_length = len(rows)
    
    if(rows_length > 0):
        data = {
            "response_type": "TABLE",
            "message": "Here is The List of Complete Leads",
            "lead_count": len(rows),
            "rows": create_list_modal(rows, columns),  # Rows should remain as a list, not serialized to JSON yet
            "columns": convert_columns_to_modal(columns)  # Column names as list of dicts
        }
    else:
        data = {
            "response_type": "TABLE",
            "message": "There is no leads available.",
            "lead_count": len(rows),
            "rows": create_list_modal(rows, columns),  # Rows should remain as a list, not serialized to JSON yet
            "columns": convert_columns_to_modal(columns)  # Column names as list of dicts
        }
    
    
    return data  # Return as dict, no need to serialize to JSON here

def convert_response_to_modal(type, data_config):
    if(type == "table"):
        return convert_listing_info(data_config)
    
    
import json

def format_tool_result(tool_result):
    """
    Format the result from the lead details tool into a valid JSON structure.

    Args:
        tool_result (dict): The result from the lead details tool.

    Returns:
        dict: A structured JSON representation with 'key', 'rows', 'columns', and 'type'.
    """
    try:
        # Check if the result contains required keys
        if isinstance(tool_result, dict):
            # Extract relevant parts
            result_type = tool_result.get("type")
            total_no_of_leads = tool_result.get("total_no_of_leads", 0)
            columns = tool_result.get("columns", [])
            rows = tool_result.get("rows", [])

            # Validate the presence of necessary keys
            if result_type == "table" and columns and isinstance(rows, list):
                # Create the structured JSON response
                formatted_result = {
                    "type": result_type,
                    "total_no_of_leads": total_no_of_leads,
                    "columns": columns,
                    "grid": [{"key": col, "type": "string", "name": col} for col in columns],  # Assuming all types are string, adjust as necessary
                    "rows": rows
                }
                return formatted_result
            else:
                return {"error": "Invalid structure: Missing required keys."}

        return {"error": "Tool result is not a valid dictionary."}

    except Exception as e:
        return {"error": f"An error occurred during formatting: {str(e)}"}
