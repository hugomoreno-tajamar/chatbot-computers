import streamlit as st
from backend.chatbot import chatbot_response
from backend.document_intelligence import recognize_entities
import docx

def convert_file_to_text(file):
    file_type = file.type.split("/")[1]  # Obtener el tipo de archivo (sin el MIME type)
    
    if file_type == "docx":
        # Procesar archivos Word (.docx)
        try:
            doc = docx.Document(file)  # Cargar el documento Word
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])  # Extraer texto
            return text
        except Exception as e:
            return f"Error al procesar el archivo Word: {e}"
    
    elif file_type == "txt" or file_type == "plain":
        # Procesar archivos de texto (.txt)
        try:
            text = file.read().decode("utf-8")  # Leer y decodificar el archivo
            return text
        except Exception as e:
            return f"Error al procesar el archivo TXT: {e}"
    
    else:
        # Para otros tipos de archivo, devolvemos un mensaje simulado
        return f"Texto extraído de {file.name} (tipo no soportado)"

def chat_ui():
    # Configurar la página con tema oscuro y título
    st.set_page_config(page_title="Chatbot", layout="centered")
    
    # Aplicar estilos mejorados con CSS
    st.markdown(
        """
        <style>
            body {
                background-color: #121212;
                color: white;
                font-family: 'Arial', sans-serif;
            }
            .stTextArea, .stTextInput, .stButton>button {
                background-color: #333;
                color: white;
                border-radius: 10px;
                border: 1px solid #555;
                padding: 10px;
            }
            .stButton>button:hover {
                background-color: #555;
            }
            .chat-box {
                max-height: 400px;
                overflow-y: auto;
                padding: 10px;
                border: 1px solid #555;
                border-radius: 10px;
                background-color: #1e1e1e;
            }
            .stChatMessage {
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 5px;
            }
            .user-message {
                background-color: #1e88e5;
                color: white;
                text-align: right;
            }
            .assistant-message {
                background-color: #2e2e2e;
                color: white;
                text-align: left;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Inicializar la sesión para guardar el historial del chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Variables para evitar re-ejecuciones innecesarias
    if "file_uploaded" not in st.session_state:
        st.session_state.file_uploaded = False

    st.title("Hugo Componentes 💻")
    st.write("Dinos cuáles son tus preferencias de componentes y buscaremos el mejor modelo para ti 😁")
    
    # Checkbox para activar traducción
    translate = st.checkbox("Traducir respuesta")
    language = None
    
    if translate:
        language_options = {
            "Inglés": ["english", "en"],
            "Francés": ["french", "fr"],
            "Chino": ["chineese", "zh"], 
            "Ruso": ["russian", "ru"]
        }
        selected_language = st.selectbox("Selecciona un idioma:", list(language_options.keys()))
        language, lang = language_options[selected_language] 
    
    # Mostrar historial de la sesión en una caja scrollable
    chat_box = st.empty()
    with chat_box.container():
        for message in st.session_state.messages:
            role_class = "user-message" if message["role"] == "user" else "assistant-message"
            st.markdown(f'<div class="stChatMessage {role_class}">{message["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    def handle_send(message, lang=None):
        if message:
            st.session_state.messages.append({"role": "user", "text": message})
            if lang:
                bot_reply = chatbot_response(message, lang)
            else:
                bot_reply = chatbot_response(message)
            st.session_state.messages.append({"role": "assistant", "text": bot_reply})

    # Entrada del usuario
    user_input = st.text_input("Escribe tu mensaje:", "", key="user_input")

    # Botón para enviar mensaje al presionar Enter o clic
    if st.button("Enviar"):
        handle_send(user_input, lang)
        st.rerun()
        chat_box.empty() 
         # Limpiar y volver a renderizar el chat

    # Botón para subir archivos
    uploaded_file = st.file_uploader("Sube un archivo", type=["txt", "docx"])

    # Verificamos si un archivo fue cargado y si aún no se ha procesado
    if uploaded_file and not st.session_state.file_uploaded:
        st.session_state.file_uploaded = True  # Marcamos que el archivo ya fue procesado
        
        file_type = uploaded_file.type.split("/")[1]
        if file_type in ["pdf", "jpeg", "png"]:
            result = recognize_entities(uploaded_file)
            st.session_state.messages.append({"role": "assistant", "text": result})
        else:
            text_converted = convert_file_to_text(uploaded_file)
            if language:
                bot_reply = chatbot_response(text_converted, lang)
            else:
                bot_reply = chatbot_response(text_converted)
            st.session_state.messages.append({"role": "assistant", "text": bot_reply})

        st.rerun()
        st.session_state.file_uploaded = False
        chat_box.empty()

    # Botón para limpiar el historial
    if st.button("Limpiar Chat"):
        st.session_state.messages = []
        st.session_state.file_uploaded = False  # Resetear el estado del archivo cargado
        chat_box.empty()  # Limpiar el contenedor del chat

if __name__ == "__main__":
    chat_ui()
