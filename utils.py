import os
from dotenv import load_dotenv
import yagmail
import re

# Funciones utilitarias

def cargar_lista_correos(nombre_archivo):
    """Carga la lista de correos electrónicos desde un archivo."""
    try:
        with open(nombre_archivo, 'r') as file:
            correos = [line.strip() for line in file if line.strip()]
        return correos
    except FileNotFoundError:
        print(f"Archivo {nombre_archivo} no encontrado.")
        return []

def registrar_log(mensaje):
    """Registra mensajes en un archivo de log."""
    with open('envio_correo.log', 'a') as log_file:
        log_file.write(mensaje + '\n')

def validar_email(correo):
    """Valida el formato de un correo electrónico."""
    patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(patron, correo) is not None

def cargar_plantilla(ruta_plantilla):
    """Carga el contenido de una plantilla HTML."""
    try:
        with open(ruta_plantilla, 'r', encoding='utf-8') as archivo:
            return archivo.read()
    except FileNotFoundError:
        print(f"Plantilla {ruta_plantilla} no encontrada.")
        return ""

def solicitar_datos_configuracion():
    """Solicita al usuario los datos de configuración para el correo."""
    email = input("Ingrese su dirección de correo: ")
    password = input("Ingrese su contraseña de aplicación de correo: ")
    smtp_server = input("Ingrese el servidor SMTP (ej. smtp.gmail.com): ")
    smtp_port = input("Ingrese el puerto SMTP (ej. 587): ")
    
    # Guardar configuración en el archivo .env
    with open('.env', 'w') as env_file:
        env_file.write(f"EMAIL_ADDRESS={email}\n")
        env_file.write(f"EMAIL_PASSWORD={password}\n")
        env_file.write(f"SMTP_SERVER={smtp_server}\n")
        env_file.write(f"SMTP_PORT={smtp_port}\n")

# Cargar variables de entorno
if not os.path.exists('.env'):
    solicitar_datos_configuracion()

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")

def enviar_correos_interactivo():
    """Función principal para enviar correos de forma interactiva."""
    # Solicitar detalles del correo
    ruta_plantilla = input("Ingrese la ruta de la plantilla del newsletter en formato HTML: ")
    cuerpo = cargar_plantilla(ruta_plantilla)

    if not cuerpo:
        print("No se pudo cargar la plantilla. Verifique la ruta y vuelva a intentarlo.")
        return

    asunto = input("Ingrese el asunto del correo: ")
    archivos_adjuntos = input("Ingrese la ruta de los archivos adjuntos separados por comas (deje vacío si no hay): ").split(',')

    # Cargar lista de destinatarios
    destinatarios = cargar_lista_correos("correos.txt")
    if not destinatarios:
        print("No hay correos en la lista.")
        return

    # Validar correos
    destinatarios_validos = [correo for correo in destinatarios if validar_email(correo)]
    if not destinatarios_validos:
        print("No hay correos válidos en la lista.")
        return

    # Enviar correos
    try:
        yag = yagmail.SMTP(EMAIL_ADDRESS, EMAIL_PASSWORD)
        for destinatario in destinatarios_validos:
            yag.send(
                to=destinatario,
                subject=asunto,
                contents=[cuerpo],
                attachments=[archivo.strip() for archivo in archivos_adjuntos if archivo.strip()]
            )
            print(f"Correo enviado a {destinatario}")
            registrar_log(f"Correo enviado a {destinatario}")
    except Exception as e:
        print(f"Error al enviar correos: {e}")
        registrar_log(f"Error al enviar correos: {e}")

if __name__ == "__main__":
    enviar_correos_interactivo()