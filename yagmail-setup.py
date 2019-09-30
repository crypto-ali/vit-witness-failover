import os
import yagmail
from dotenv import load_dotenv

load_dotenv()

# Variables
FROM = os.getenv('FROM_ADDRESS')
FROM_PASS = os.getenv('FROM_PASS')
TO = os.getenv('TO_ADDRESS')

#yag = yagmail.SMTP(FROM, oauth2_file='~/oauth2_creds.json')
yag = yagmail.SMTP(FROM, FROM_PASS)

to = TO
subject = 'Can you read me?'
body = "If so, then Yagmail is working with oauth2."
body2 = "If so, then Yagmail is working with email & app password."

#yag.send(to, subject, body)
yag.send(to, subject, body2)