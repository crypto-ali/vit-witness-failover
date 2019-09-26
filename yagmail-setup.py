import yagmail
from dotenv import load_dotenv

load_dotenv()

# Variables
FROM = os.getenv('FROM_ADDRESS')
TO = os.getenv('TO_ADDRESS')

yag = yagmail.SMTP(FROM, oauth2_file='~/oauth2_creds.json')

to = TO
subject = 'Can you read me?'
body = "If so, then Yagmail is working with oauth2."

yag.send(to, subject, body)