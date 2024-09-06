import streamlit as st
import time
import os
import msal
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener las variables de entorno
CLIENT_ID = os.getenv("CLIENT_ID")
AUTHORITY = os.getenv("AUTHORITY")
CLIENT_CREDENTIAL = os.getenv("CLIENT_CREDENTIAL")
USER_PRINCIPAL_NAME = os.getenv("USER_PRINCIPAL_NAME")
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"

# Función para obtener el token de acceso usando MSAL
def get_access_token():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_CREDENTIAL
    )

    token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    if 'access_token' in token_response:
        return token_response['access_token']
    else:
        st.write(f"Error obteniendo token de acceso: {token_response.get('error_description')}")
        return None

# Función para enviar el correo usando Microsoft Graph API
def send_email(recipient_email, access_token):
    url = f"{GRAPH_API_ENDPOINT}/users/{USER_PRINCIPAL_NAME}/sendMail"

    email_message = {
        "message": {
            "subject": "Contador completado",
            "body": {
                "contentType": "Text",
                "content": "El contador ha llegado a 30."
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient_email
                    }
                }
            ]
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=email_message, headers=headers)

    if response.status_code == 202:
        st.write(f"Correo enviado a {recipient_email}")
    else:
        st.write(f"Error enviando correo: {response.status_code}, {response.text}")

# Interfaz de Streamlit
st.title("Contador hasta 30 con notificación por correo")

# Campo para ingresar el correo de notificación
recipient_email = st.text_input("Correo electrónico para la notificación:")

# Inicialización del contador
if "count" not in st.session_state:
    st.session_state.count = 0

# Botón para iniciar el contador
if st.button("Iniciar contador"):
    if recipient_email:
        # Obtener el token de acceso antes de iniciar el contador
        access_token = get_access_token()

        if access_token:
            # Bucle que incrementa el contador hasta 30
            for i in range(st.session_state.count, 31):
                st.session_state.count = i
                st.write(f"Contador: {i}")
                time.sleep(1)  # Espera 1 segundo en cada iteración

                # Cuando llega a 30, enviar el correo
                if i == 30:
                    send_email(recipient_email, access_token)
                    break
    else:
        st.write("Por favor, ingresa una dirección de correo válida.")
