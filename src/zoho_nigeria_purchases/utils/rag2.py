import os
import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector # Import register_vector for handling vector types
from psycopg2 import sql
import requests
import json # Import json for parsing Ollama responses

# from src.config import DBHOST, DBPORT, DBNAME, DBUSER, DBPASSWORD # Original import
from src.config import DBHOST, DBPORT, DBNAME, DBUSER, DBPASSWORD # Assuming these are still in src.config

# --- Ollama Configuration ---
OLLAMA_API_URL = "http://localhost:11434" # Base URL for Ollama API
OLLAMA_GENERATE_ENDPOINT = f"{OLLAMA_API_URL}/api/generate"
OLLAMA_EMBEDDING_ENDPOINT = f"{OLLAMA_API_URL}/api/embeddings"
OLLAMA_MODEL_NAME = "llama3.2:3b" # Your downloaded Ollama model for text generation
OLLAMA_EMBEDDING_MODEL_NAME = "nomic-embed-text" # A good general-purpose embedding model from Ollama
                                                # You might need to `ollama pull nomic-embed-text`

# --- Database Connection Helper ---
def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=DBUSER, password=DBPASSWORD, host=DBHOST, port=DBPORT)
        conn.autocommit = True # Ensure changes are committed immediately
        register_vector(conn) # Register the vector type for psycopg2
        return conn
    except (Exception, psycopg2.Error) as error:
        print(f"Error while connecting to PostgreSQL: {error}")
        return None

# --- Ollama Embedding Generation ---
def get_embedding_from_ollama(text: str, model_name: str = OLLAMA_EMBEDDING_MODEL_NAME):
    """
    Generates a text embedding using the specified Ollama embedding model.
    """
    if not text or not text.strip():
        return None

    payload = {
        "model": model_name,
        "prompt": text
    }
    try:
        response = requests.post(OLLAMA_EMBEDDING_ENDPOINT, json=payload)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        result = response.json()
        if "embedding" in result:
            return np.array(result["embedding"]) # Return as a numpy array
        else:
            print(f"Error: No 'embedding' found in Ollama response for text: '{text[:50]}...'")
            return None
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to Ollama at {OLLAMA_EMBEDDING_ENDPOINT}. "
              f"Please ensure Ollama is running and the model '{model_name}' is downloaded.")
        return None
    except requests.exceptions.Timeout:
        print("Error: Ollama embedding request timed out.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error during Ollama embedding generation: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during embedding: {e}")
        return None

# --- Data Ingestion/Updating with Embeddings ---
def ingest_data_with_embeddings(table_name: str, text_columns: list, vector_column_name: str):
    """
    Fetches data from the specified table, generates embeddings for a combined
    text from `text_columns`, and updates the table with these embeddings.
    This function assumes your table has a primary key named 'id' or similar.
    Adjust 'id' column name if different.
    """
    conn = get_db_connection()
    if not conn:
        return

    cur = conn.cursor()
    try:
        # 1. Fetch existing data (e.g., 'id' and the text columns)
        select_query = sql.SQL("SELECT id, {} FROM {}").format(
            sql.SQL(', ').join(map(sql.Identifier, text_columns)),
            sql.Identifier(table_name)
        )
        cur.execute(select_query)
        records = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]

        print(f"Fetched {len(records)} records for embedding generation.")

        # 2. Process each record, generate embedding, and update
        for record in records:
            record_dict = dict(zip(column_names, record))
            record_id = record_dict['id'] # Assuming 'id' is the primary key

            # Combine text from specified columns
            text_to_embed = " ".join([str(record_dict[col]) for col in text_columns if record_dict[col] is not None])

            if text_to_embed.strip():
                embedding = get_embedding_from_ollama(text_to_embed)
                if embedding is not None:
                    # Update the record with the new embedding
                    update_query = sql.SQL("UPDATE {} SET {} = %s WHERE id = %s").format(
                        sql.Identifier(table_name),
                        sql.Identifier(vector_column_name)
                    )
                    cur.execute(update_query, (embedding, record_id))
                    # print(f"Updated record ID {record_id} with embedding.")
                else:
                    print(f"Could not generate embedding for record ID {record_id}. Skipping.")
            else:
                print(f"No text to embed for record ID {record_id}. Skipping.")

        conn.commit()
        print("Embedding generation and database update complete.")

    except (Exception, psycopg2.Error) as error:
        print(f"Error during data ingestion with embeddings: {error}")
    finally:
        if conn:
            cur.close()
            conn.close()

# --- Semantic Search Function ---
def semantic_search(query_text: str, table_name: str, vector_column_name: str, top_k: int = 5):
    """
    Performs a semantic search on the database using Ollama embeddings and pgvector.
    Returns the top_k most similar records.
    """
    query_embedding = get_embedding_from_ollama(query_text)
    if query_embedding is None:
        print("Failed to generate embedding for the query.")
        return None, None

    conn = get_db_connection()
    if not conn:
        return None, None

    cur = conn.cursor()
    try:
        # Use the '<=>' operator for cosine distance (lower is more similar)
        # We order by distance and limit to top_k
        search_query = sql.SQL("SELECT *, {} <=> %s AS distance FROM {} ORDER BY distance LIMIT %s").format(
            sql.Identifier(vector_column_name),
            sql.Identifier(table_name)
        )
        cur.execute(search_query, (query_embedding, top_k))
        colnames = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        print(f"Found {len(data)} semantically similar records.")
        return colnames, data
    except (Exception, psycopg2.Error) as error:
        print(f"Error during semantic search: {error}")
        return None, None
    finally:
        if conn:
            cur.close()
            conn.close()

# --- Data Formatting for LLM ---
def format_data_for_llm(column_names, data_rows):
    """
    Formats the database query results into a human-readable string
    suitable for an LLM. Excludes the 'embedding' and 'distance' columns.
    """
    if not data_rows:
        return ""
    formatted_texts = []
    # Filter out embedding and distance columns for LLM output
    display_column_names = [col for col in column_names if col not in ['embedding', 'distance']]
    display_indices = [column_names.index(col) for col in display_column_names]

    for row_idx, row in enumerate(data_rows):
        text_parts = []
        for display_col_idx, original_col_idx in enumerate(display_indices):
            col_name = display_column_names[display_col_idx]
            if row[original_col_idx] is not None:
                text_parts.append(f"{col_name}: {row[original_col_idx]}")
        if text_parts:
            formatted_texts.append(f"Record {row_idx + 1}: " + "; ".join(text_parts))
    return "\n\n".join(formatted_texts)

# --- Ollama Summarization (re-used from previous version) ---
def summarize_with_ollama(text_to_summarize: str, model_name: str = OLLAMA_MODEL_NAME):
    """
    Sends text to the local Ollama instance for summarization.
    """
    if not text_to_summarize or not text_to_summarize.strip():
        return "No text provided for summarization."

    try:
        prompt = f"""Is there a trend  following database records can we say at a particular time we have more customers?. Focus on key entities and relationships. If the records are about customers, summarize their details and any trends.

{text_to_summarize}

Summary:"""

        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(OLLAMA_GENERATE_ENDPOINT, json=payload)
        response.raise_for_status()
        result = response.json()

        if "response" in result:
            return result["response"].strip()
        else:
            print(f"Summarization failed: Unexpected response format from Ollama: {result}")
            return "Summarization failed: Unexpected response format from Ollama."

    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to Ollama at {OLLAMA_GENERATE_ENDPOINT}. " \
               f"Please ensure Ollama is running and the model '{model_name}' is downloaded."
    except requests.exceptions.Timeout:
        return "Error: Ollama request timed out."
    except requests.exceptions.RequestException as e:
        return f"Error during Ollama summarization: {e}"
    except Exception as e:
        return f"An unexpected error occurred during summarization: {e}"

# --- Main execution ---
if __name__ == "__main__":
    DB_TABLE_NAME = "zoho_nigeria_sales.customers" # Your table name
    VECTOR_COLUMN_NAME = "embedding" # Name of your new vector column
    # Columns to combine for generating the embedding for each record
    # Adjust these based on which columns contain meaningful text for your search
    TEXT_COLUMNS_FOR_EMBEDDING = ['customer_name', 'email', 'phone_number', 'address', 'city', 'state', 'country']

    print("--- RAG Application with Semantic Search ---")

    # --- Step 0: Ensure Embedding Model is Pulled ---
    print(f"\nStep 0: Please ensure you have the '{OLLAMA_EMBEDDING_MODEL_NAME}' model downloaded for Ollama.")
    print(f"You can pull it using: `ollama pull {OLLAMA_EMBEDDING_MODEL_NAME}` in your terminal.")
    print("Also ensure Ollama is running.")

    # --- Step 1: Ingest/Update Data with Embeddings (Run this once or when data changes) ---
    print("\nStep 1: Generating and ingesting embeddings for database records...")
    print(f"This might take a while depending on your data size and Ollama performance.")
    ingest_data_with_embeddings(DB_TABLE_NAME, TEXT_COLUMNS_FOR_EMBEDDING, VECTOR_COLUMN_NAME)
    print("Embedding ingestion process finished.")

    # --- Step 2: Get User's Natural Language Query ---
    user_question = input("\nStep 2: Enter your natural language question about the customers: ")
    if not user_question.strip():
        print("No question entered. Exiting.")
    else:
        # --- Step 3: Perform Semantic Search ---
        print(f"\nStep 3: Performing semantic search for: '{user_question}'...")
        col_names, db_data = semantic_search(user_question, DB_TABLE_NAME, VECTOR_COLUMN_NAME, top_k=5)

        if db_data:
            print(f"Successfully retrieved {len(db_data)} semantically relevant records.")
            print("\nStep 4: Formatting retrieved data for LLM...")
            llm_ready_text = format_data_for_llm(col_names, db_data)

            if llm_ready_text.strip():
                print(f"\nStep 5: Requesting summary from Ollama ({OLLAMA_MODEL_NAME})...")
                final_summary = summarize_with_ollama(llm_ready_text)
                print("\n--- Final Summary (from Ollama) ---")
                print(final_summary)
                print("------------------------------------")
            else:
                print("No relevant data formatted for LLM. Cannot summarize.")
        else:
            print("Failed to retrieve semantically relevant data from database.")

# Note: This code assumes you have a PostgreSQL database with the necessary tables and columns.
# Ensure you have the pgvector extension installed in your PostgreSQL database.