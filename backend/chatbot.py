import os
import json
from groq import Groq
from dotenv import load_dotenv
from .db import search_computer_in_mongo
from .translator import translate_text
import streamlit as st

load_dotenv()

def clean_json_response(response):
    """
    Esta función limpia y valida que la respuesta del modelo sea un JSON.
    Si la respuesta es válida, la devuelve como un objeto JSON, de lo contrario, devuelve un mensaje de error.
    """
    try:
        # Intentar cargar la respuesta como un JSON
        response_json = json.loads(response)
        return response_json

    except (json.JSONDecodeError, ValueError) as e:
        return {"error": "La respuesta del modelo no es un JSON válido o está incompleta.", "details": str(e)}

def format_query(user_message):

    client = Groq(
        api_key=st.secrets["GROQ_API_KEY"],  # Tu API Key
    )

    # Mensaje de sistema: El asistente debe procesar la consulta y devolver solo los campos existentes del producto en JSON
    system_message = (
        "You are a helpful assistant that processes user queries about computer components. "
        "Your response should contain a JSON object with the information found in the document, taking in count the following fields: "
        "\"nombre\", \"precio\", \"almacenamiento\", \"modelo_grafica\", \"procesador\", \"frecuencia_procesador\", "
        "\"color\", \"ram\", \"tamano_pantalla\", \"pantalla_tactil\", \"marca\", \"marca_grafica\", \"archivo\". "
        "The field of 'almacenamiento' must be a number in GB. Do not include the unities of the numeric information, only the number."
        "The field 'pantalla_tactil must be only the values 'si' or 'no' depending if the user say if he wants 'pantalla tactil' or not"
        "Only include fields that are present in the document. If a field is not available, simply omit it from the JSON response."
        "If there is a graphic in the text, you must make the diference between the brand and the model, for example in the text 'Nvidia RTX 3050', you must set 'Nvidia' to 'marca_grafica' and 'RTX 3050' to 'modelo_grafica'"
        "It is important that you skip the information that you dont know from the query"
    )

    # Realizar la solicitud a la API de Groq para obtener la respuesta
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": "I'm looking for a computer with 16GB of RAM and a GeForce RTX 4050, preferably with a 1TB storage."},
            {"role" : "assistant", "content": """{"ram": "16","modelo_grafica": "GeForce RTX 4050","almacenamiento": "1024"}"""},
            {"role": "user", "content": user_message},
        ],
        model="llama3-8b-8192",  # El modelo específico de Groq que se utilizará
    )

    # Obtener la respuesta del modelo
    model_response = chat_completion.choices[0].message.content

    # Limpiar y validar la respuesta para asegurarse de que es un JSON válido
    cleaned_response = clean_json_response(model_response)

    print(cleaned_response)
    return cleaned_response


def chatbot_response(user_query, language=None):
    query = format_query(user_query)
    response = search_query(query, language)
    return response

def search_query(query, language=None):
    scored_products = search_computer_in_mongo(query)

    if scored_products:
        top_product = scored_products[0]
        product_name = top_product[0].get("nombre", "Producto sin nombre")
        product_price = top_product[0].get("precio", "Precio no disponible")
        file = top_product[0].get("archivo", "")

        if language:
            product_link = f"https://hugomorenostorage.blob.core.windows.net/ordenadores-{language}/{file}"
        else:
            product_link = f"https://hugomorenostorage.blob.core.windows.net/ordenadores/{file}"

        # Usar HTML para formatear el mensaje
        response = f"<b>{product_name}</b><br><br>"
        response += "Según tus requisitos, el producto incluye los siguientes componentes: <ul>"
        for k in query:
            product_component = top_product[0].get(k)
            response += f"<li>{k}: {product_component}</li>"
        response += "</ul>"
        response += f"<a href='{product_link}' target='_blank'>Ficha producto</a><br>"
        response += f"💰{product_price} €"

        return response
    else:
        return "Lo siento, no encontré ningún producto que coincida con tu consulta."