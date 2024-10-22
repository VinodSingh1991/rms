import sqlite3
from langchain_core.tools import tool

import logging

# Initialize logging (this can be configured more globally)
logging.basicConfig(level=logging.INFO)

@tool
def get_all_lead_details_tool(ss: str):
    db_file = 'databse-sqllite/Lead.sqlite'
    """
    Fetch all lead details from the Leads table in the database.
    This function retrieves all the leads available in the database.
    Args:
        db_file (str): The path to the SQLite database file.
    Returns:
        List[Dict]: A list of dictionaries representing all leads,
        where each dictionary contains column names as keys.
    """
    conn = None
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        logging.info("Connected to database")

        # Execute query to fetch all rows from Leads table
        query = 'SELECT LeadId, Name, Email, Phone FROM Leads'
        logging.info("Executing query: %s", query)
        cursor.execute(query)
        
        # Fetch all rows and extract column names
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]
        
        logging.info("Query executed successfully, fetched %d rows", len(rows))
        
        return results
    
    except sqlite3.Error as e:
        logging.error("SQLite error: %s", e)
        return []

    finally:
        if conn:
            cursor.close()
            conn.close()
            logging.info("Database connection closed")

    