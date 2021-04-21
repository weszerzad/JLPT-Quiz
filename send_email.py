from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib
import os

def send_email(EMAIL_SUBJECT, EMAIL_FROM, EMAIL_TO, MESSAGE_BODY,
               FILEPATH_AND_FILENAME_DICT, SMTP_USERNAME, SMTP_PASSWORD,
               SMTP_SERVER='smtp.gmail.com', SMTP_PORT=587):
    try:

        # Create a multipart message
        msg = MIMEMultipart()
        body_part = MIMEText(MESSAGE_BODY, 'plain')
        msg['Subject'] = EMAIL_SUBJECT
        msg['From'] = EMAIL_FROM

        if type(EMAIL_TO) == str:
            msg['TO'] = EMAIL_TO
        if type(EMAIL_TO) == list:
            for recipient in EMAIL_TO:
                msg['TO'] = recipient
                print(recipient)

        # Add body to email
        msg.attach(body_part)

        #Make a list of files
        files = FILEPATH_AND_FILENAME_DICT

        #Loop over the files and attach them to email body
        for file in files:

            # open and read the file in binary
            with open(file, 'rb') as f:
                # Attach the file with filename to the email
                msg.attach(MIMEApplication(f.read(), Name=files[file]))

        # Create SMTP object
        smtp_obj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        # smtp_obj.set_debuglevel(1)

        # Set up connection
        smtp_obj.starttls()

        # Login to the server
        smtp_obj.login(SMTP_USERNAME, SMTP_PASSWORD)

        # # Convert the message to a string and send it
        # smtp_obj.send_message(msg['From'], msg['To'], msg.as_string())

        smtp_obj.send_message(msg)

        smtp_obj.close()

        print("Sent the email!")

    except Exception as e:
        print(str(e))
        print("Failed to send the email")

if __name__ == '__main__':

    EMAIL_SUBJECT = 'mp3 file'
    MESSAGE_BODY = 'send mp3 file'

    FILEPATH_AND_FILENAME_DICT = {'/Users/phuocpham/OneDrive - Shizuoka University/pythonProject/pdf/code_base/pdf_files/N1 2010.7 Test/聴解 問題2.jpg':'chokai2.jpg',
                                  '/Users/phuocpham/OneDrive - Shizuoka University/pythonProject/pdf/code_base/pdf_files/N1 2010.7 Test/聴解 問題2.mp3':'chokai2.mp3'}

    send_email(EMAIL_SUBJECT, os.environ['EMAIL_FROM'], os.environ['EMAIL_TO'], MESSAGE_BODY,
               FILEPATH_AND_FILENAME_DICT, os.environ['SMTP_USERNAME'],
               os.environ['SMTP_PASSWORD'])