from email.message import EmailMessage
import smtplib

# Configuración de email (debes completar con tus datos)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "rogelprogrammer@gmail.com"
EMAIL_PASSWORD = "jcmh fgdf wrim jswt"


def send_verification_email(email: str, code: int):
    msg = EmailMessage()
    msg["Subject"] = "Fadiar - Verificación de Cuenta"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

    # Versión texto plano
    text_content = f"""\
    Gracias por registrarte en Fadiar, tu tienda online de confianza.

    Código de verificación: {code}

    Este código es válido por 15 minutos. Si no realizaste esta solicitud, 
    por favor ignora este mensaje.

    Atentamente,
    Equipo Fadiar
    Soporte: rogelprogrammer@gmail.com
    """

    # Versión HTML
    html_content = f"""\
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="border-bottom: 2px solid #f0f0f0; padding: 1rem 0;">
            <h1 style="color: #2d3748; margin: 0;">FADIAR</h1>
            <p style="color: #718096; margin: 0.5rem 0 0;">Tu tienda online premium</p>
        </div>

        <div style="padding: 2rem 0;">
            <p style="color: #4a5568;">Gracias por registrarte en nuestra plataforma.</p>
            <p style="color: #4a5568; font-size: 1.1rem; background: #f7fafc; 
               padding: 1rem; border-radius: 4px; display: inline-block;">
               Código de verificación: 
               <strong style="color: #2b6cb0;">{code}</strong>
            </p>
            <p style="color: #718096; font-size: 0.9rem; margin-top: 1.5rem;">
                ⚠️ Este código es válido por 15 minutos.<br>
                ¿No reconoces esta actividad? <a href="mailto:rogelprogrammer@gmail.com" 
                style="color: #4299e1;">Contactar a soporte</a>
            </p>
        </div>

        <div style="background: #f7fafc; padding: 1rem; text-align: center; 
            font-size: 0.8rem; color: #718096;">
            <p style="margin: 0.5rem 0;">© 2024 Fadiar. Todos los derechos reservados</p>
            <div style="margin-top: 0.5rem;">
                <a href="https://www.fadiar.com" style="color: #4299e1; text-decoration: none;">Visita nuestra tienda</a> 
                | 
                <a href="https://blog.fadiar.com" style="color: #4299e1; text-decoration: none;">Blog</a>
            </div>
        </div>
    </div>
    """

    msg.set_content(text_content)
    msg.add_alternative(html_content, subtype="html")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)