from typing import List
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Message:
    def __init__(self, to: List[str], subject: str, content: str):
        self.to = to
        self.subject = subject
        self.content = content

    def create_message(self, email_from: str):
        message = MIMEMultipart()
        message["From"] = email_from
        message["To"] = ", ".join(self.to)
        message["Subject"] = self.subject
        message.attach(MIMEText(self.content, "html"))
        return message.as_string()
