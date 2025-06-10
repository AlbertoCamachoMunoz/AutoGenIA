import os
import uuid
import logging
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from pydantic import ValidationError
from pydub import AudioSegment

# Importaciones de la aplicación (Inyección de dependencias, enums y DTOs)
from application.dependency_injection import DependencyInjector
from application.enums.status_code import StatusCode
from application.enums.data_processing_type import DataProcessingType
from application.enums.llm_provider import LLMProvider
from application.dtos.data_processing_request import DataProcessingRequest
from application.dtos.application_response import ApplicationResponse

# Importación de configuraciones del sistema
from config.settings import AUDIO_INPUT_FOLDER, AUDIO_OUTPUT_FOLDER

# Configuración del sistema de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialización de la aplicación Flask y configuración de CORS
app = Flask(__name__, static_folder='./front_app', static_url_path='')
CORS(app)

# -------------------------
# RUTA: Página principal
# -------------------------

@app.route('/')
def serve_frontend():
    """Sirve el archivo HTML principal del frontend."""
    return send_from_directory(app.static_folder, 'index.html')

# -------------------------
# PROCESAMIENTO DE DATOS
# -------------------------

@app.route('/process', methods=['POST'])
def process_input():
    """Procesa una solicitud de texto o audio enviada desde el frontend."""
    try:
        data_type, llm_type = validate_request_params()
        processing_request = build_processing_request(data_type)

        logger.info(f"Procesando solicitud - Tipo: {data_type.value}, LLM: {llm_type.value}")

        # Obtener el procesador correspondiente e iniciar el procesamiento
        processor = DependencyInjector.get_chat_processor(data_type, llm_type)
        result = processor.process(data_type, llm_type, processing_request)

        return build_response(result, data_type, llm_type)

    except ValidationError as ve:
        return handle_exception("Error de validación", ve, 400)

    except ValueError as ve:
        return handle_exception("Error de parámetros", ve, 400)

    except Exception as e:
        return handle_exception("Error interno procesando solicitud", e, 500)

# -------------------------
# VALIDACIÓN DE PARÁMETROS
# -------------------------

def validate_request_params():
    """
    Valida y obtiene los parámetros de la solicitud.

    Returns:
        tuple: (DataProcessingType, LLMProvider)
    """
    data_type = DataProcessingType(request.form.get('data_type', 'text'))
    llm_type = LLMProvider(request.form.get('llm_type', 'llm_gemini'))
    return data_type, llm_type

# -------------------------
# CONSTRUCCIÓN DEL DTO DE PROCESAMIENTO
# -------------------------

def build_processing_request(data_type):
    """
    Construye el objeto DataProcessingRequest basado en el tipo de datos recibido.

    Args:
        data_type (DataProcessingType): Tipo de dato recibido en la solicitud.

    Returns:
        DataProcessingRequest: Objeto con la información de la solicitud.
    """
    if data_type == DataProcessingType.TEXT:
        return process_text_request()

    elif data_type == DataProcessingType.AUDIO:
        return process_audio_request()

# -------------------------
# PROCESAMIENTO DE TEXTO
# -------------------------

def process_text_request():
    """
    Procesa una solicitud de texto.

    Returns:
        DataProcessingRequest: Objeto de procesamiento con el texto recibido.

    Raises:
        ValueError: Si el texto está vacío.
    """
    text_content = request.form.get('input_text', '').strip()
    if not text_content:
        raise ValueError("El texto no puede estar vacío")
    
    return DataProcessingRequest(
        data_type=DataProcessingType.TEXT,
        text=text_content
    )

# -------------------------
# PROCESAMIENTO DE AUDIO
# -------------------------

def process_audio_request():
    """
    Procesa una solicitud de audio.

    Returns:
        DataProcessingRequest: Objeto de procesamiento con la ruta del archivo de audio.

    Raises:
        ValueError: Si el archivo de audio es inválido o hay errores en el procesamiento.
    """
    if 'audio_file' in request.files:
        file = request.files['audio_file']
        if file.filename == '' or not allowed_audio_file(file.filename):
            raise ValueError("Archivo de audio inválido")

        return convert_and_save_audio(file)
    else:
        return DataProcessingRequest(
            data_type=DataProcessingType.AUDIO,
            is_live=True
        )

# -------------------------
# CONVERSIÓN Y GUARDADO DE AUDIO
# -------------------------

def convert_and_save_audio(file):
    """
    Convierte el archivo de audio a formato WAV PCM y lo guarda.

    Args:
        file: Archivo de audio recibido.

    Returns:
        DataProcessingRequest: Objeto de procesamiento con la ruta del archivo.

    Raises:
        ValueError: Si ocurre un error en la conversión o guardado.
    """
    try:
        audio = AudioSegment.from_file(file)
        audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)

        filename = "input.wav"
        file_path = os.path.join(AUDIO_INPUT_FOLDER, filename)
        audio.export(file_path, format="wav", codec="pcm_s16le")

        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise ValueError("Error al guardar el archivo de audio convertido")

        return DataProcessingRequest(
            data_type=DataProcessingType.AUDIO,
            audio_file_path=file_path,
            is_live=False
        )

    except Exception as e:
        raise ValueError(f"Error al procesar audio: {str(e)}")

# -------------------------
# RESPUESTA AL FRONTEND
# -------------------------

def build_response(result: ApplicationResponse, data_type: DataProcessingType, llm_type: LLMProvider):
    """
    Construye la respuesta JSON para el frontend.

    Args:
        result: Resultado del procesamiento.
        data_type (DataProcessingType): Tipo de dato procesado.
        llm_type (LLMProvider): Modelo LLM utilizado.

    Returns:
        Response: Respuesta en formato JSON.
    """
    if result.status == StatusCode.SUCCESS:
        response_data = {
            'status': 'success',
            'data_type': data_type.value,
            'llm_type': llm_type.value,
            'result': result.generated_text,
            'message': result.message
        }

        if data_type == DataProcessingType.AUDIO and isinstance(result.generated_text, str):
            # Generar un identificador único para evitar la caché del navegador
            unique_id = uuid.uuid4().hex[:8]
            filename = os.path.basename(result.generated_text)
            new_filename = f"{filename.split('.')[0]}_{unique_id}.wav"  # output_XXXXXX.wav
            new_audio_path = os.path.join(AUDIO_OUTPUT_FOLDER, new_filename)

            # Renombrar el archivo para que sea único en la respuesta
            os.rename(os.path.join(AUDIO_OUTPUT_FOLDER, filename), new_audio_path)

            if os.path.exists(new_audio_path):
                response_data['audio_url'] = f"/generated_audio/{new_filename}"
                response_data['message'] = result.message
            else:
                logger.warning(f"Archivo de salida no encontrado: {new_audio_path}")

        return jsonify(response_data), 200

    return jsonify({
        'status': 'error',
        'message': result.message,
        'data_type': data_type.value,
        'llm_type': llm_type.value,
        'message': result.message
    }), 400
# -------------------------
# MANEJO DE ERRORES
# -------------------------

def handle_exception(error_message, exception, status_code):
    """
    Maneja excepciones y retorna un mensaje JSON de error.

    Args:
        error_message (str): Mensaje de error general.
        exception (Exception): Excepción capturada.
        status_code (int): Código HTTP de respuesta.

    Returns:
        Response: Respuesta en formato JSON con el mensaje de error.
    """
    logger.error(f"{error_message}: {str(exception)}")
    return jsonify({
        'status': 'error',
        'message': str(exception)
    }), status_code

# -------------------------
# RUTA: Servir archivos de audio generados
# -------------------------

@app.route('/generated_audio/<path:filename>')
def serve_audio(filename):
    """Devuelve un archivo de audio generado en la ruta de salida."""
    file_path = os.path.join(AUDIO_OUTPUT_FOLDER, filename)

    if not os.path.exists(file_path):
        logger.error(f"Archivo no encontrado: {file_path}")
        abort(404, description="Archivo de audio no encontrado")

    return send_from_directory(AUDIO_OUTPUT_FOLDER, filename)

# -------------------------
# FUNCIÓN AUXILIAR: Validar tipos de archivo de audio
# -------------------------

def allowed_audio_file(filename: str) -> bool:
    """Verifica si la extensión del archivo de audio es válida."""
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'm4a', 'aac'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------------
# INICIO DE LA APLICACIÓN
# -------------------------

if __name__ == '__main__':
    app.run(debug=True)
