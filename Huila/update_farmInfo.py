import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Leer el archivo CSV
excel_file_path = 'data/Codigos AAA.xlsx'  # Reemplaza con la ruta real del archivo CSV
csv_data = pd.read_excel(excel_file_path)

# Endpoint y credenciales
auth_url = 'https://api.opensc.engineering/auth/token'
search_url = 'https://api.opensc.engineering/product-events/search'
update_url = 'https://api.opensc.engineering/products/commissioned/corrected'

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def get_access_token():
    try:
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "audience": "https://api.opensc.engineering"
        }
        headers = {
            "User-Agent": "HuilaAgent",
            "Content-type": "application/json",
            "Accept": "application/vnd.opensc.api.1+json"
        }
        response = requests.post(auth_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

def search_product_events(access_token, product_id):
    try:
        payload = {
            "productIds": [product_id],
            "supplyChainIds": ["ffa1e7b3-ed6c-42b1-89c4-e58bfc62dbec"],
            "eventsPerProduct": "ALL",
            "eventTypes": ["COMMISSIONED"],
            "nonDecommissionedProducts": True
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "HuilaAgent",
            "Content-type": "application/json",
            "Accept": "application/vnd.opensc.api.1+json"
        }
        response = requests.post(search_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while searching product events: {http_err}")
    except Exception as err:
        print(f"An error occurred while searching product events: {err}")

def update_product(access_token, product_id, commissioned_datetime, location_id, process, farm_code):
    try:
        payload = {
            "id": product_id,
            "commissionedDatetime": commissioned_datetime,
            "locationId": location_id,
            "process": process,
            "attributes": [
                {
                    "type": "FARM_CODE",
                    "value": farm_code
                }
            ]
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "HuilaAgent",
            "Content-type": "application/json",
            "Accept": "application/vnd.opensc.api.1+json"
        }
        response = requests.put(update_url, json=payload, headers=headers)
        if response.status_code == 409:
            print("Error 409: Conflicto. Verifica que el producto ya no esté actualizado correctamente.")
            return response.json()
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while updating product: {http_err}")
    except Exception as err:
        print(f"An error occurred while updating product: {err}")

if __name__ == "__main__":
    # Obtener token de acceso
    token = get_access_token()

    # Procesar cada fila del CSV
    for index, row in csv_data.iterrows():
        product_id = row['SKU']
        farm_code = row['Codigo AAA Finca']

        # Buscar eventos del producto
        events_response = search_product_events(token, product_id)
        
        if events_response['content']:
            event = events_response['content'][0]
            commissioned_datetime = event['eventDatetime']
            location_id = event['location']['id']
            process = event['process']

            # Actualizar producto
            update_response = update_product(token, event['product']['id'], commissioned_datetime, location_id, process, farm_code)
            print(f"Producto actualizado: {update_response}")
        else:
            print(f"No se encontraron eventos para el producto {product_id}")
