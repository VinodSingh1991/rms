import sqlite3
import os
import logging
import json

# Initialize logging
logging.basicConfig(level=logging.INFO)

from response_helper import convert_response_to_modal

def get_all_lead_details():
    """
    Fetch all lead details from the Leads table in the SQLite database.
    Returns the result in a JSON-compatible format.
    """
    db_file = 'databse-sqllite/Lead.sqlite'  # Make sure this path is correct

    conn = None
    try:
        # Check if the database file exists
        if not os.path.exists(db_file):
            logging.error(f"Database file not found: {db_file}")
            return json.dumps({"error": "Database file not found"})
        
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        logging.info("Connected to database")

        # Execute query to fetch all rows from the Leads table
        query = "SELECT LeadID, FirstName, LastName, Email, Phone, CreatedOn from Leads"
        logging.info("Executing query: %s", query)
        cursor.execute(query)
        
        # Fetch all rows and extract column names
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        
        # Convert the result to modal format
        results = convert_response_to_modal("table", {"rows": rows, "columns": column_names})
        
        output = {
            "type": "table",
            "total_no_of_leads": len(rows),
            "columns": column_names,
            "grid": [{"key": "LeadID", "type": "int", "name": "Lead ID"}],  # Customize grid with other columns if needed
            "rows": results
        }
        
        logging.info("Query executed successfully, fetched %d rows", len(rows))
        
        # Return the final JSON response
        return output  # Serialize here at the very end
    
    except sqlite3.Error as e:
        logging.error("SQLite error: %s", e)
        return json.dumps({"error": str(e)})

    finally:
        if conn:
            cursor.close()
            conn.close()
            logging.info("Database connection closed")

# Call the function and print the result
all_leads = get_all_lead_details()

print(all_leads)
