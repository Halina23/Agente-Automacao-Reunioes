import os
import datetime as dt
import smtplib
import csv
from email.message import EmailMessage
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ==========================================
# CARREGAR VARIÁVEIS DE AMBIENTE E DADOS
# ==========================================
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']
EMAIL_REMETENTE = os.getenv("GMAIL_EMAIL")
SENHA_APP = os.getenv("GMAIL_APP_PASSWORD")
ARQUIVO_ANEXO = "pauta.pdf"

# Validação de segurança
if not EMAIL_REMETENTE or not SENHA_APP:
    raise ValueError("❌ Variáveis de ambiente não carregadas. Verifique o arquivo .env")

# ==========================================
# FUNÇÃO PRINCIPAL DO AGENTE MASTER
# ==========================================
def agente_master():
    try:
        # 1. LER O ARQUIVO CSV
        convidados = []
        with open('convidados.csv', mode='r', encoding='utf-8') as file:
            leitor_csv = csv.DictReader(file)
            for linha in leitor_csv:
                convidados.append(linha)
        print(f"✅ Arquivo CSV lido com sucesso. {len(convidados)} convidado(s) encontrado(s).")

        # 2. AUTENTICAR NO GOOGLE CALENDAR
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                
        service = build('calendar', 'v3', credentials=creds)

        # 3. AUTENTICAR NO SERVIDOR DE E-MAIL (SMTP DO GMAIL)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_REMETENTE, SENHA_APP)

        # 4. LAÇO DE REPETIÇÃO: CALENDAR + E-MAIL
        agora = dt.datetime.now()
        
        for convidado in convidados:
            nome = convidado['Nome']
            email_destino = convidado['Email']
            
            print(f"\n🔄 Processando agendamento para {nome} ({email_destino})...")
            
            # --- PARTE A: AGENDAR NO CALENDAR ---
            # Define a reunião para amanhã, das 14h às 15h
            inicio_reuniao = (agora + dt.timedelta(days=1)).replace(hour=14, minute=0, second=0).isoformat()
            fim_reuniao = (agora + dt.timedelta(days=1)).replace(hour=15, minute=0, second=0).isoformat()
            
            evento = {
                'summary': f'Entrevista Técnica - {nome}',
                'description': 'Discussão sobre arquitetura de dados e projetos do portfólio.',
                'start': {'dateTime': inicio_reuniao, 'timeZone': 'America/Sao_Paulo'},
                'end': {'dateTime': fim_reuniao, 'timeZone': 'America/Sao_Paulo'},
                'attendees': [{'email': email_destino}],
            }
            
            evento_criado = service.events().insert(calendarId='primary', body=evento).execute()
            link_reuniao = evento_criado.get('htmlLink')
            
            # --- PARTE B: ENVIAR E-MAIL PERSONALIZADO COM ANEXO ---
            msg = EmailMessage()
            msg['Subject'] = f"Convite Oficial: Entrevista Técnica - {nome}"
            msg['From'] = EMAIL_REMETENTE
            msg['To'] = email_destino
            
            corpo_email = f"""Olá, {nome}!
            
Tudo bem?
Sua Entrevista Técnica para a área de Engenharia de Dados foi agendada com sucesso. 

📍 Para acessar a nossa sala virtual no dia e horário marcados, por favor, clique no link abaixo:
{link_reuniao}

Em anexo, enviamos a pauta da nossa reunião para que você possa conhecer mais sobre o nosso fluxo de dados.
            
Qualquer dúvida antes da entrevista, fique à vontade para responder este e-mail.

Atenciosamente,
Halina Oliveira
(Mensagem enviada automaticamente pelo Agente Python)"""
            
            msg.set_content(corpo_email)
            
            # Lógica para adicionar o anexo (PDF)
            if os.path.exists(ARQUIVO_ANEXO):
                with open(ARQUIVO_ANEXO, 'rb') as f:
                    file_data = f.read()
                    file_name = f.name
                msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)
                print("📎 Anexo adicionado com sucesso.")
            else:
                print("⚠️ Aviso: Arquivo pauta.pdf não encontrado. O e-mail será enviado sem anexo.")
                
            server.send_message(msg)
            print(f"✅ E-mail e link do Calendar enviados para {nome}!")

        # Encerra conexão com o Gmail
        server.quit()
        print("\n🎉 Automação concluída com sucesso para todos os contatos!")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro crítico: {e}")

# ==========================================
# EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    agente_master()