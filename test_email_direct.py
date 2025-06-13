# test_email_direct.py
import smtplib
from email.message import EmailMessage

# === CONFIGURACIÓN SMTP - A FUEGO ===
SMTP_SERVER = "sandbox.smtp.mailtrap.io"
SMTP_PORT = 2525
SMTP_USERNAME = "0b8912a4ed76be"
SMTP_PASSWORD = "226639342b6cff"
SMTP_FROM_EMAIL = "AutoGenIA <autogenia@example.com>"
SMTP_TO_EMAIL = "test@autogenia.mailtrap.io"

def send_test_email():
    print("📧 [Test] Preparando envío de correo...")

    # Crear mensaje
    msg = EmailMessage()
    msg.set_content("Este es un mensaje de prueba desde Python.\n\n¡Correo enviado correctamente!")
    msg["Subject"] = "Prueba de envío desde script directo"
    msg["From"] = SMTP_FROM_EMAIL
    msg["To"] = SMTP_TO_EMAIL

    try:
        print(f"📨 [Test] Conectando a {SMTP_SERVER}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            print("🔐 [Test] Iniciando sesión SMTP...")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            print("📤 [Test] Enviando correo...")
            server.send_message(msg)
        print("✅ [Test] Correo enviado con éxito.")

    except Exception as e:
        print(f"❌ [Test] Error al enviar el correo: {str(e)}")


if __name__ == "__main__":
    send_test_email()