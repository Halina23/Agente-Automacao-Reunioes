import os
import smtplib
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

EMAIL = os.getenv("GMAIL_EMAIL")
SENHA = os.getenv("GMAIL_APP_PASSWORD")

def enviar_email():
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL, SENHA)

            mensagem = "Subject: Teste\n\nFuncionou!"

            server.sendmail(
                EMAIL,
                EMAIL,
                mensagem
            )

            print("✅ Email enviado com sucesso!")

    except Exception as e:
        print("❌ Erro ao enviar email:", e)

if __name__ == "__main__":
    enviar_email()