import os
import smtplib
import psycopg2
import datetime
from email.message import EmailMessage
from dotenv import load_dotenv

# Bibliotecas do Google Calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ==========================================
# 1. CARREGAR VARIÁVEIS DE AMBIENTE
# ==========================================
load_dotenv()

EMAIL = os.getenv("GMAIL_EMAIL")
SENHA = os.getenv("GMAIL_APP_PASSWORD")
DB_URL = os.getenv("DATABASE_URL")

SCOPES = ["https://www.googleapis.com/auth/calendar"]

if not EMAIL or not SENHA or not DB_URL:
    raise ValueError("❌ Variáveis de ambiente não carregadas. Verifique seu arquivo .env!")


# ==========================================
# 2. AUTENTICAÇÃO GOOGLE CALENDAR
# ==========================================
def autenticar_calendar():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_console()

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


# ==========================================
# 3. VERIFICAR DISPONIBILIDADE
# ==========================================
def verificar_disponibilidade(service, horario_inicio, horario_fim):
    try:
        corpo_freebusy = {
            "timeMin": horario_inicio,
            "timeMax": horario_fim,
            "items": [{"id": "primary"}]
        }

        resposta = service.freebusy().query(body=corpo_freebusy).execute()
        ocupado = resposta["calendars"]["primary"]["busy"]

        if not ocupado:
            print("✅ Agenda livre! Nenhum conflito encontrado.")
            return True

        print(f"⚠️ Conflito encontrado: {ocupado}")
        return False

    except Exception as e:
        print(f"❌ Erro ao checar agenda: {e}")
        return False


# ==========================================
# 4. ENVIAR E-MAIL
# ==========================================
def enviar_email_vip(nome_cliente, email_cliente, link_reuniao, data_hora_formatada):
    try:
        msg = EmailMessage()
        msg["Subject"] = f"[TESTE] Convite VIP - {nome_cliente}"
        msg["From"] = EMAIL

        # TESTE: envia tudo para você
        msg["To"] = EMAIL

        # PRODUÇÃO:
        # msg["To"] = email_cliente

        corpo_email = f"""Olá, {nome_cliente}!

Tudo bem?

Notamos que você é um dos nossos clientes VIP mais valiosos.
Como forma de agradecimento, liberamos uma Consultoria Técnica gratuita com nossos especialistas.

📅 Data e horário reservados: {data_hora_formatada}
📍 Acesse sua reunião: {link_reuniao}

Atenciosamente,
Equipe de Customer Success
(Automação Python)"""

        msg.set_content(corpo_email)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            print("🔐 Autenticando no Gmail...")
            server.starttls()
            server.login(EMAIL, SENHA)

            print(f"📤 Enviando e-mail para {nome_cliente}...")
            server.send_message(msg)

        print(f"✅ E-mail enviado com sucesso para {nome_cliente} | teste enviado para {EMAIL}\n")

    except Exception as e:
        print(f"❌ Erro ao enviar e-mail para {nome_cliente}: {e}\n")


# ==========================================
# 5. AGENTE PRINCIPAL
# ==========================================
def executar_agente():
    try:
        print("⏳ [1/3] Autenticando na API do Google Calendar...")
        service = autenticar_calendar()

        print("⏳ [2/3] Conectando ao PostgreSQL...")
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()

        query_vips = """
            SELECT c.nome, c.email
            FROM vendas v
            JOIN clientes c ON c.cliente_id = v.cliente_id
            JOIN pagamentos p ON p.venda_id = v.venda_id
            WHERE p.status = 'pago'
            GROUP BY c.nome, c.email
            ORDER BY SUM(p.valor_pago) DESC
            LIMIT 5;
        """

        cursor.execute(query_vips)
        clientes_vip = cursor.fetchall()

        cursor.close()
        conn.close()

        print("✅ [3/3] Dados extraídos! Iniciando validação de agenda e envios...\n")

        if not clientes_vip:
            print("⚠️ Nenhum cliente VIP encontrado.")
            return

        amanha = datetime.datetime.now() + datetime.timedelta(days=1)

        for i, cliente in enumerate(clientes_vip):
            nome = cliente[0]
            email = cliente[1]

            print(f"📨 Processando cliente: {nome} | {email}")

            inicio = amanha.replace(hour=14 + i, minute=0, second=0, microsecond=0)
            fim = inicio + datetime.timedelta(minutes=30)

            inicio_iso = inicio.strftime("%Y-%m-%dT%H:%M:%S-03:00")
            fim_iso = fim.strftime("%Y-%m-%dT%H:%M:%S-03:00")
            data_hora_amigavel = inicio.strftime("%d/%m/%Y às %H:%M")

            print(f"🔍 Verificando disponibilidade para {data_hora_amigavel}...")

            livre = verificar_disponibilidade(service, inicio_iso, fim_iso)

            if livre:
                link_meet = "https://meet.google.com/vip-setup-exemplo"
                enviar_email_vip(nome, email, link_meet, data_hora_amigavel)
            else:
                print(f"⏭️ Pulando {nome} por conflito na agenda.\n")

        print("🚀 Automação finalizada!")

    except Exception as e:
        print(f"❌ Erro crítico no sistema: {e}")


# ==========================================
# EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    executar_agente()