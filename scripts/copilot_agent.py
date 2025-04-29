import os
import configparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ConfigValidatorBot:
    def __init__(self, file_path):
        self.file_path = file_path
        self.mandatory_fields = ['index', 'sourcetype', 'disabled']
        self.errors = []
        self.corrected_content = []

    def validate_file(self):
        """
        Validate the inputs.conf file and capture errors.
        """
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(self.file_path)

        for section in config.sections():
            for field in self.mandatory_fields:
                if field not in config[section]:
                    self.errors.append(f"Missing '{field}' in section [{section}]")
                    config[section][field] = "ADD_VALUE_HERE"

        # Generate corrected content
        with open(self.file_path, 'r') as file:
            self.corrected_content = file.readlines()

        for section in config.sections():
            for field in self.mandatory_fields:
                if field not in config[section]:
                    self.corrected_content.append(f"{field} = ADD_VALUE_HERE")

    def send_email(self, recipients, sender_email, sender_password):
        """
        Send an email with the validation results and corrected file if errors are found.
        """
        if self.errors:
            subject = "Errors Found in Configuration File - Corrected Version Attached"
            body = f"The following errors were found in {self.file_path}:\n\n" + "\n".join(self.errors)

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Attach corrected file
            corrected_file = MIMEText("\n".join(self.corrected_content))
            corrected_file.add_header('Content-Disposition', 'attachment', filename="corrected_inputs.conf")
            msg.attach(corrected_file)

            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                print("Connecting to SMTP server...")
                server.starttls()
                print("Starting TLS...")
                server.login(sender_email, sender_password)
                print("Logged in to SMTP server.")
                server.sendmail(sender_email, recipients, msg.as_string())
                server.quit()
                print("Email sent successfully.")
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
        else:
            print("No errors found. No email sent.")

    def run(self, recipients, sender_email, sender_password):
        """
        Run the bot: validate file and send email if errors are found.
        """
        self.validate_file()
        self.send_email(recipients, sender_email, sender_password)


# Usage
if __name__ == "__main__":
    # File path to validate
    file_path = r"C:\Program Files\Splunk\etc\apps\logs_splunk\local\inputs.conf"  # Use raw string (r"") for Windows paths

    # Email credentials (fetched from environment variables)
    sender_email ="yaswanthkumarch2001@gmail.com" # Your email ID
    sender_password ="uqjc bszf djfw bsor" # Your email password (from environment variable)
    recipients = ["yaswanth@middlewaretalents.com"]  # Recipient email ID

    # Check if required environment variables are set
    if not sender_email or not sender_password:
        print("Error: Missing environment variables for email credentials.")
        print("Please set SENDER_EMAIL and EMAIL_PASSWORD environment variables.")
    else:
        # Initialize and run the bot
        bot = ConfigValidatorBot(file_path)

        bot.run(recipients, sender_email, sender_password)
