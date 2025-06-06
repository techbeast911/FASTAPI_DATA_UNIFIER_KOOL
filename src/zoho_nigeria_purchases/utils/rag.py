import os
import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2 import sql
import requests # Import the requests library for making HTTP calls
# from src.config import DBHOST, DBPORT, DBNAME, DBUSER, DBPASSWORD, GOOGLE_API_KEY # GOOGLE_API_KEY is no longer needed
from src.config import DBHOST, DBPORT, DBNAME, DBUSER, DBPASSWORD # Updated import

# Define Ollama API endpoint and model name
OLLAMA_API_URL = "http://localhost:11434/api/generate" # Default Ollama API URL
OLLAMA_MODEL_NAME = "llama3.2:3b" # Your downloaded Ollama model

def get_data_from_db(query):
    """
    Connects to the PostgreSQL database, executes the given query,
    and returns column names and fetched data.
    """
    conn = None
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=DBUSER, password=DBPASSWORD, host=DBHOST, port=DBPORT)
        cur = conn.cursor()
        cur.execute(query)
        colnames = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        cur.close()
        return colnames, data
    except (Exception, psycopg2.Error) as error:
        print(f"Error while connecting to PostgreSQL or fetching data: {error}")
        return None, None
    finally:
        if conn:
            conn.close()

def format_data_for_llm(column_names, data_rows):
    """
    Formats the database query results into a human-readable string
    suitable for an LLM.
    """
    if not data_rows:
        return ""
    formatted_texts = []
    for row_idx, row in enumerate(data_rows):
        text_parts = []
        for col_idx, col_name in enumerate(column_names):
            if row[col_idx] is not None:
                text_parts.append(f"{col_name}: {row[col_idx]}")
        if text_parts:
            formatted_texts.append(f"Record {row_idx + 1}: " + "; ".join(text_parts))
    return "\n\n".join(formatted_texts)

def summarize_with_ollama(text_to_summarize, model_name=OLLAMA_MODEL_NAME):
    """
    Sends text to the local Ollama instance for summarization.
    """
    if not text_to_summarize or not text_to_summarize.strip():
        return "No text provided for summarization."

    try:
        # Construct the prompt for Ollama
        prompt = f"""Please Is there a trend in the  information from the following database records? Can we say at a particular season we have more customers?:

{text_to_summarize}

Summary:"""

        # Prepare the payload for Ollama API
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False # We want the full response at once
        }

        # Make the POST request to Ollama API
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        # Parse the JSON response
        result = response.json()

        # Extract the generated text
        if "response" in result:
            return result["response"].strip()
        else:
            return f"Summarization failed: Unexpected response format from Ollama: {result}"

    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to Ollama at {OLLAMA_API_URL}. Please ensure Ollama is running and the model '{model_name}' is downloaded."
    except requests.exceptions.Timeout:
        return "Error: Ollama request timed out."
    except requests.exceptions.RequestException as e:
        return f"Error during Ollama summarization: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Main execution ---
if __name__ == "__main__":
    # Define your SQL query
    sql_query = "SELECT * FROM zoho_nigeria_sales.customers ;" # Example from your code, added LIMIT for testing

    print("Step 1: Fetching data from database...")
    col_names, db_data = get_data_from_db(sql_query)

    if db_data:
        print(f"Successfully retrieved {len(db_data)} records.")
        print("\nStep 2: Formatting data for LLM...")
        llm_ready_text = format_data_for_llm(col_names, db_data)

        if llm_ready_text.strip():
            print(f"\nStep 3: Requesting summary from Ollama ({OLLAMA_MODEL_NAME})...")
            # Use the new function name
            final_summary = summarize_with_ollama(llm_ready_text)
            print("\n--- Final Summary (from Ollama) ---")
            print(final_summary)
            print("------------------------------------")
        else:
            print("No data formatted for LLM. Cannot summarize.")
    else:
        print("Failed to retrieve data from database.")