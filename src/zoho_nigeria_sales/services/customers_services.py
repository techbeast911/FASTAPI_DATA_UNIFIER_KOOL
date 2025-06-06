import httpx
from sqlalchemy import select
from src.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ORG_ID
from src.zoho_nigeria_inventory.db.database import async_session
from src.zoho_nigeria_sales.models.models_customers import Customer
from sqlalchemy import String, Integer, Float, Boolean, DateTime
import traceback
import asyncio
from dateutil.parser import parse
import json
from datetime import datetime


async def get_access_token():
    url = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params)
        response.raise_for_status()
        return response.json()["access_token"]



async def fetch_customers():
    try:
        token = await get_access_token()
        if not token:
            raise ValueError("Failed to get access token")
            
        page = 1
        per_page = 200  # Start with smaller page size
        all_customers = []
        max_pages = 1000  # Safety limit
        data_center = "com"  # Change to "eu" or "in" if needed

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            while page <= max_pages:
                url = f"https://inventory.zoho.{data_center}/api/v1/contacts"
                headers = {
                    "Authorization": f"Zoho-oauthtoken {token}",
                    "X-com-zoho-inventory-organizationid": str(ORG_ID),
                    "Content-Type": "application/json"
                }
                params = {
                    "organization_id": ORG_ID,
                    "page": page,
                    "per_page": per_page
                }

                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 400:
                    error_data = response.json()
                    print(f"Zoho API Error: {error_data}")
                    if 'message' in error_data:
                        raise ValueError(f"Zoho API: {error_data['message']}")
                    break
                
                response.raise_for_status()
                data = response.json()
                
                customers = data.get("contacts", [])
                if not customers:
                    break

                all_customers.extend(customers)
                
                if len(customers) < per_page:
                    break
                    
                page += 1
                await asyncio.sleep(1)  # More conservative rate limiting

        return all_customers
        
    except Exception as e:
        print(f"Failed to fetch customers: {str(e)}")
        traceback.print_exc()
        return []

# async def insert_customers_to_db(customers):
#     print("Inserting customers into database...")
#     async with async_session() as db:
#         try:
#             for customer in customers:
#                 cust_data = {}
#                 for key, value in customer.items():
#                     if not hasattr(Customer, key):
#                         continue
                    
#                     # Handle empty strings for numeric fields
#                     column_type = getattr(Customer, key).type
#                     if isinstance(value, str) and value.strip() == "":
#                         try:
#                             if issubclass(column_type.python_type, (int, float)):
#                                 value = None
#                         except NotImplementedError:
#                             pass
                    
#                     # Handle JSON fields
#                     if key in ['custom_fields', 'custom_field_hash', 'tags', 'non_default_currency_values']:
#                         if isinstance(value, str):
#                             try:
#                                 value = json.loads(value)
#                             except (json.JSONDecodeError, TypeError):
#                                 value = None
                    
#                     cust_data[key] = value

#                 # Check if customer exists
#                 result = await db.execute(
#                     select(Customer).filter_by(contact_id=cust_data["contact_id"])
#                 )
#                 db_customer = result.scalars().first()

#                 if db_customer:
#                     # Update existing customer
#                     for key, value in cust_data.items():
#                         setattr(db_customer, key, value)
#                 else:
#                     # Create new customer
#                     db_customer = Customer(**cust_data)
#                     db.add(db_customer)

#             await db.commit()
#             print(f"Successfully inserted/updated {len(customers)} customers")
#         except Exception as e:
#             await db.rollback()
#             print(f"Error while inserting customers into database: {e}")
#             traceback.print_exc() 

async def insert_customers_to_db(customers):
    print("Inserting customers into database...")
    async with async_session() as db:
        try:
            for customer in customers:
                cust_data = {}
                for key, value in customer.items():
                    if not hasattr(Customer, key):
                        continue
                    
                    column_type = getattr(Customer, key).type
                    
                    # Handle datetime conversion
                    if key in ['created_time', 'last_modified_time']:
                        if value:
                            try:
                                # Convert string to datetime and remove timezone
                                dt = parse(value)
                                if dt.tzinfo is not None:
                                    dt = dt.replace(tzinfo=None)  # Make timezone-naive
                                value = dt
                            except (ValueError, TypeError):
                                value = None
                        else:
                            value = None
                    
                    # Handle empty/None values
                    elif value is None or value == "":
                        if isinstance(column_type, (String, DateTime)):
                            value = None
                        elif isinstance(column_type, (Integer, Float)):
                            value = 0
                        elif isinstance(column_type, Boolean):
                            value = False
                    
                    # Convert numeric values to strings for string columns
                    elif isinstance(column_type, String) and isinstance(value, (int, float)):
                        value = str(value)
                    
                    # Handle JSON fields
                    elif key in ['custom_fields', 'custom_field_hash', 'tags', 'non_default_currency_values']:
                        if isinstance(value, str):
                            try:
                                value = json.loads(value)
                            except (json.JSONDecodeError, TypeError):
                                value = {}
                        elif value is None:
                            value = {}
                    
                    cust_data[key] = value

                # Check if customer exists
                result = await db.execute(
                    select(Customer).filter_by(contact_id=cust_data["contact_id"])
                )
                db_customer = result.scalars().first()

                if db_customer:
                    # Update existing customer
                    for key, value in cust_data.items():
                        setattr(db_customer, key, value)
                else:
                    # Create new customer
                    db_customer = Customer(**cust_data)
                    db.add(db_customer)

            await db.commit()
            print(f"Successfully inserted/updated {len(customers)} customers")
        except Exception as e:
            await db.rollback()
            print(f"Error while inserting customers into database: {e}")
            traceback.print_exc()