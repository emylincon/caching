import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = "spicetala@gmail.com"
EMAIL_PASSWORD = "dumbaccount123"

msg = EmailMessage()

msg['Subject'] = 'Grab dinner this weekend?!'

msg['From'] = EMAIL_ADDRESS

msg['To'] = 'suitelabb@gmail.com'
msg.set_content('file')

fg = r"C:\Users\emyli\OneDrive\Documents\Predictive caching\model pred\yes.zip"
with open(fg, 'rb') as f:
    file_data = f.read()
    #file_type = imghdr.what(f.name)
    file_name = f.name

msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)
