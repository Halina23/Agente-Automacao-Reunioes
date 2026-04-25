import smtplib

EMAIL = "oliveirahalina71@gmail.com"
SENHA = "ifdjydtttljtnvzi"

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(EMAIL, SENHA)

print("Conectou!")