/**
 * Script que maneja la interacción del usuario con la interfaz web.
 * - Permite enviar texto o grabar audio para su procesamiento.
 * - Selecciona el modelo de lenguaje (LLM) a utilizar.
 * - Recibe la respuesta del servidor y la muestra en pantalla.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Elementos del DOM
    const llmDropdown = document.getElementById('llmDropdown'); // Selector de modelo LLM
    const chatInput = document.getElementById('chatInput'); // Campo de entrada de texto
    const micButton = document.getElementById('micButton'); // Botón de micrófono
    const resultDiv = document.getElementById('result'); // Contenedor de resultados
    let selectedLLM = "llm_studio";  // Modelo LLM seleccionado por defecto
    let mediaRecorder;
    let audioChunks = [];

    /**
     * ✅ Manejo del dropdown para seleccionar LLM
     * - Permite cambiar dinámicamente el modelo de lenguaje seleccionado.
     */
    document.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', function () {
            selectedLLM = this.getAttribute('data-llm');
            llmDropdown.innerText = this.innerText;
        });
    });

    /**
     * ✅ Enviar mensaje con "Enter"
     * - Detecta cuando el usuario presiona la tecla "Enter" en el campo de texto.
     * - Llama a la función sendTextMessage para procesar el mensaje.
     */
    chatInput.addEventListener('keypress', function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendTextMessage(chatInput.value);
        }
    });

    /**
     * ✅ Nuevo manejo de grabación con presión de botón
     * - Inicia la grabación cuando el usuario presiona el botón del micrófono.
     * - Detiene la grabación cuando el usuario lo suelta.
     */
    micButton.addEventListener('mousedown', startRecording);
    micButton.addEventListener('mouseup', stopRecording);
    micButton.addEventListener('mouseleave', stopRecording);
    
    // ✅ Soporte para dispositivos táctiles
    micButton.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startRecording();
    });
    micButton.addEventListener('touchend', stopRecording);

    /**
     * ✅ Iniciar grabación de audio
     * - Solicita acceso al micrófono y graba el audio.
     * - Al finalizar la grabación, se llama a sendAudioMessage para enviar el audio.
     */
    async function startRecording() {
        try {
            if (mediaRecorder?.state === "recording") return;
            
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            micButton.innerText = "⏺️ Grabando...";

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendAudioMessage(audioBlob);
                micButton.innerText = "🎤";
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
        } catch (error) {
            console.error("Error al acceder al micrófono:", error);
        }
    }

    /**
     * ✅ Detener grabación
     * - Detiene la grabación de audio si está activa.
     */
    function stopRecording() {
        if (mediaRecorder?.state === "recording") {
            mediaRecorder.stop();
        }
    }

    /**
     * ✅ Enviar mensaje de texto
     * - Envía un mensaje de texto al servidor para su procesamiento.
     * - Muestra la respuesta en la interfaz.
     * @param {string} message - El mensaje de texto ingresado por el usuario.
     */
    async function sendTextMessage(message) {
        if (!message.trim()) return;
        
        resultDiv.innerHTML = "<p> (Yo): " + chatInput.value + " <strong>Procesando...</strong>" + "</p>";
        chatInput.value = "";

        const formData = new FormData();
        formData.append('data_type', 'text');
        formData.append('llm_type', selectedLLM);
        formData.append('input_text', message);

        try {
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (result.status === 'success') {
                resultDiv.innerHTML += `<div class="success-message"><strong>Respuesta:</strong> ${result.result} </div>`;
            } else {
                resultDiv.innerHTML += `<strong class="error-message">Error:</strong> ${result.message}`;
            }
        } catch (error) {
            resultDiv.innerHTML += `<strong class="error-message">Error:</strong> ${error.message}`;
        }
    }

    /**
     * ✅ Enviar mensaje de audio
     * - Envía un archivo de audio al servidor para su procesamiento.
     * - Si la respuesta es un archivo de audio, lo muestra como un reproductor.
     * @param {Blob} audioBlob - Archivo de audio grabado.
     */
    async function sendAudioMessage(audioBlob) {
        if (audioBlob.size <= 0) {
            resultDiv.innerHTML = "<strong class='error-message'>Error: No se detectó audio</strong>";
            return;
        }

        resultDiv.innerHTML = "<strong>Procesando audio...</strong>";

        const formData = new FormData();
        formData.append('data_type', 'audio');
        formData.append('llm_type', selectedLLM);
        formData.append('audio_file', audioBlob, "recording.wav");

        try {
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            // if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const result = await response.json();
            console.log(result)

            if (result.status === 'success') {
                if (result.audio_url) {
                    // Crear elemento de audio con reproducción automática
                    const audioElement = document.createElement("audio");
                    audioElement.src = result.audio_url;
                    audioElement.controls = true;
                    audioElement.autoplay = true; // ✅ Reproducción automática

                    resultDiv.innerHTML = "<p> (Yo): " + result.message + "</p>";
                    resultDiv.innerHTML += `<p><strong>Audio generado:</strong></p>`;

                    resultDiv.appendChild(audioElement);

                    // Opcional: Volumen bajo para evitar sonidos fuertes inesperados
                    audioElement.volume = 0.4;    

                } else {
                    resultDiv.innerHTML = `<strong>Respuesta:</strong> ${result.result}`;
                }
            } else {
                resultDiv.innerHTML = `<strong class="error-message">Error:</strong> ${result.message}`;
            }
        } catch (error) {
            resultDiv.innerHTML = `<strong class="error-message">Error:</strong> ${error.message}`;
        }
    }

    console.log("LLM seleccionado:", selectedLLM);
});
