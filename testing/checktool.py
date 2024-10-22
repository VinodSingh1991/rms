import sqlite3
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

def get_all_lead_details():
    db_file = 'databse-sqllite/Lead.sqlite'  # Make sure this path is correct
    
    """
    Fetch all lead details from the Leads table in the database.

    This function retrieves all the leads available in the database.

    Returns:
        List[Dict]: A list of dictionaries representing all leads,
        where each dictionary contains column names as keys.
    """
    conn = None
    try:
        # Check if the database file exists
        if not os.path.exists(db_file):
            logging.error(f"Database file not found: {db_file}")
            return []
        
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        logging.info("Connected to database")

        # Execute query to fetch all rows from the correct table
        query = "SELECT * from Leads"  # Replace 'Leads' with your actual table name
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

# Call the function and print the result
sql = get_all_lead_details()
print(sql)
