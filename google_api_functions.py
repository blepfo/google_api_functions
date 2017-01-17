"""--- Imports ---"""
# For making API requests
import httplib2

# For retrieving and storing credentials
import os

# For reading from an app_details.json
import json

# For printing date with log message
from datetime import datetime

# Email creation modules
from email.mime.text import MIMEText
import base64

# Google API modules
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# oauth2client.tools.run_flow() is a command-line tool, so it needs
# command-line flags. argeparse module is used to handle these
import argparse
flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()


def get_api_object(path):
	""" Gets details from an app_details.json and returns Google_API object
	created using the information. We assume the JSON has:
	{ 
		"APPLICATION_NAME" : "App Name",
		"CLIENT_SECRET_FILE" : "path/to/file",
		"SCOPES" : "path/to/file",
		"CREDENTIALS_PATH" : "path/to/file"
	}
	We also assume that the scopes file has each scope on its own line
	"""
	with open(path, 'r') as app_detailsJSON:
		app_details = json.loads(app_detailsJSON.read())
		api_object = Google_API(
							APPLICATION_NAME=app_details["APPLICATION_NAME"],
							CLIENT_SECRET_FILE=app_details["CLIENT_SECRET_FILE"],
							SCOPES=read_scopes(app_details["SCOPES"]),
							CREDENTIALS_FILE=app_details["CREDENTIALS_FILE"])
	return api_object

def read_scopes(path):
	""" Reads scopes from a text file with one scope per line 
	"""
	with open(path, 'r') as scopes_file:
			return " ".join(scopes_file.read().splitlines())


class Google_API:
	""" Provides easier access to Google Api functions
	Automatically gets credentials on instantiation and
	stores an authorized httplib2.Http object as an instance
	variable.
	"""
	def __init__(self, APPLICATION_NAME="APPLICATION_NAME", 
										 CLIENT_SECRET_FILE="client_secret.json",
										 SCOPES=None,
										 CREDENTIALS_FILE=None):
		self.APPLICATION_NAME = APPLICATION_NAME
		self.CLIENT_SECRET_FILE = CLIENT_SECRET_FILE
		self.SCOPES = SCOPES
		self.http = self.get_authorized_http(CREDENTIALS_FILE)
		self.sheets_service = None
		self.gmail_service = None

	def get_credentials(self, CREDENTIAL_FILE=None):
		""" Retreive user credentials so we can access the spreadsheet.
		This function works as follows:
		1) Check if there are credentials already stored (in Storage object)
		2) If there are, return the Credentials object (using store.get())
		3) If not, initiate flow_from_clientsecrets(), which will use a Flow
			 object to launch the browser, prompt user for authorization, and
			 store credentials.
		"""
		# Credentials will be stored in ~/.credentials/google_api_credentials.json 
		if (CREDENTIAL_FILE == None):
			# If no path is given, use ~/.credentials
			home_dir = os.path.expanduser('~')
			credential_dir = os.path.join(home_dir, '.credentials')
			if not os.path.exists(credential_dir):
				os.makedirs(credential_dir)
				credential_path = os.path.join(credential_dir, 'google_api_credentials.json')
		else:
			credential_path = CREDENTIAL_FILE 
		# Check if there are credentials in storage. If not, run flow
		store = Storage(credential_path)
		credentials = store.get()
		if not credentials or credentials.invalid:
			print('No stored credentials. Initiating flow...')
			flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
			flow.user_agent = self.APPLICATION_NAME
			credentials = tools.run_flow(flow, store, flags)
			print('Storing credentials to ' + credential_path)
		return credentials

	def get_authorized_http(self, path=None):
		""" Create an authorized httplib2.Http object
		in order to acces user data
		"""
		credentials = self.get_credentials(path)
		return credentials.authorize(httplib2.Http())

	def get_sheets_service(self):
		""" Return service object for the Sheets API """
		# Store sheets service internally so we don't get duplicates
		# If the function is called repeatedly
		if self.sheets_service == None:
			sheets_discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?' 
						'version=v4')
			self.sheets_service = discovery.build('sheets', 'v4', http=self.http,
								discoveryServiceUrl=sheets_discoveryUrl)
		return self.sheets_service

	def get_gmail_service():
		""" Return service object for the Gmail API """
		# Store the gmail service internally so we don't get duplicates
		if self.gmail_service == None:
			self.gmail_service = discovery.build('gmail', 'v1', http=self.http)
		return self.gmail_service

	def create_email(sender, to, subject, message_text):
		""" Create message to send using the Gmail API
		This function creates a MIME format email and encodes it using
		base64 so that it can be sent using the Gmail API. To send
		the message returned by this function, use the send_message()
		function
		"""
		# Construct the email using the MIME format
		message = MIMEText(message_text)
		message['to'] = to
		message['from'] = sender
		message['subject'] = subject
		
		""" String probelms in Python 3
		base64.urlsafe_b64encode() takes a byte string.
		message.as_string() returns a Python 3 str string, so we have to encode it
		"""

		byte_string = base64.urlsafe_b64encode(message.as_string().encode('ascii'))

		""" More string problems in Python 3
		base64.urlsafe_b64encode() returns a byte string, so we have to decode it
		to be an str type string so give to the Gmail API so that the string will
		JSON Serializable 
		"""

		raw = byte_string.decode()
		return {'raw' : raw}

	def send_email(service, user_id, message):
		""" Send message to the Gmail API
		This function assumes that service is a Service object fir the Gmail API,
		and that message is constructed using create_message()
		"""

		try:
			message = (service.users().messages().send(userId = user_id, body=message)
					.execute())
			print('Sending email')
		except:
			print('Error sending email')

	def log_message(self, sheet_id, message, logfile=None):
		""" Publish log messages to a Google Sheet
		Make sure that the sheet has a tab named "Log"
		The first two columns of the "Log" tab will be used to log the time
		and the message, respectively.
		Optionally: Give the path to a logfile to which messages
		will be saved locally
		"""
		# Get the current time
		now = datetime.now()
		time_str = "%d-%d-%d %d:%d" % (
							 now.year, now.month, now.day, now.hour, now.minute)
		if logfile != None:
			# Save message to the logfile
			with open(logfile, "a") as log_file:
				log_file.write(time_str + "\n" + message + "\n")
		# Save message to the Google Sheet
		# Get the next usable row on the spreadsheet
		sheets_service = self.get_sheets_service()
		# Skip the first row, which has column labels
		sheet_range = "Log!A2:B"
		values_result = sheets_service.spreadsheets().values().get(
					spreadsheetId=sheet_id, range=sheet_range).execute()
		# First usable row will be 2
		empty_row = str(len(values_result.get("values",[])) + 2)
		sheets_range = "Log!A" + empty_row + ":B" + empty_row
		values = [[time_str, message]]
		body = {"values" : values}
		update_result = sheets_service.spreadsheets().values().update(
					spreadsheetId=sheet_id, range=sheets_range,
					valueInputOption="RAW", body=body).execute()
