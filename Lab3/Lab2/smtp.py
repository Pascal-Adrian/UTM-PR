import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, login, password):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(login, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    send_email(
        sender_email="aa4033339@gmail.com",
        receiver_email="pascal.adrian.andrei@gmail.com",
        subject="Test Email",
        body="Hello! This is a test email from a Python SMTP client.",
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        login="aa4033339@gmail.com",
        password="zpdt efzz ijbc mkkv"
    )