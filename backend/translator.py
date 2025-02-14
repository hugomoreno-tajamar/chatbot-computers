from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv
import os
import re

def translate_text(text, language):
    load_dotenv()
    key = os.getenv("AZURE_AI_KEY")
    endpoint = os.getenv("AZURE_AI_ENDPOINT")
    region = "eastus"
    credential = TranslatorCredential(key, region)
    text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)

    # Función para procesar el texto y evitar traducir lo que está dentro de etiquetas HTML
    def process_html(text):
        # Encontrar todas las partes del texto dentro de etiquetas HTML
        html_pattern = re.compile(r"<[^>]+>")
        matches = html_pattern.findall(text)  # Lista de todas las etiquetas encontradas
        placeholder_map = {}  # Diccionario para almacenar los marcadores temporales
        cleaned_text = text

        # Eliminar espacios dentro de las etiquetas HTML
        matches_no_spaces = [re.sub(r"\s+", "", match) for match in matches]

        # Reemplazar cada parte dentro de etiquetas con un marcador único
        for i, (match, match_no_spaces) in enumerate(zip(matches, matches_no_spaces)):
            # Crear un marcador sin espacios
            placeholder = f"{{no-translation-marker{i+1}}}"  # Ejemplo: {{no-translation-marker1}}, ...
            placeholder_map[placeholder] = match  # Guardar el marcador y su contenido original
            cleaned_text = cleaned_text.replace(match, placeholder)

        return cleaned_text, placeholder_map

    try:
        source_language = "es"
        target_language = [language]
        input_text_elements = []

        # Procesar el texto para evitar traducir etiquetas HTML
        cleaned_text, placeholder_map = process_html(text)
        input_text_elements.append(InputTextItem(text=cleaned_text))

        # Traducir el texto limpio
        response = text_translator.translate(
            content=input_text_elements,
            to=target_language,
            from_parameter=source_language
        )

        # Obtener la traducción principal
        translation = response[0] if response else None
        if translation:
            translated_text = translation.translations[0].text

            # Restaurar las partes originales dentro de las etiquetas
            for placeholder, original_content in placeholder_map.items():
                translated_text = translated_text.replace(placeholder, original_content)

            return translated_text

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")