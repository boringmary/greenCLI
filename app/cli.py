import json
from pathlib import Path

from gevent import monkey; monkey.patch_all()

import dropbox
from app.gdrive import GoogleDrive
from app.dropbox import DropboxProvider
from app.helpers import get_root_path, create_root_file
from dropbox import DropboxOAuth2FlowNoRedirect

import click
import pickle
import httplib2

import googleapiclient
import google_auth_httplib2
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from app.constants import SCOPES


class Context(object):
    def __init__(self, provider):
        self.provider = provider
        self.config = {}


pass_provider = click.make_pass_decorator(Context)


@click.group()
@click.version_option("1.0")
def cli():
    """cliDrive is a command line tool which allow you to download/upload
    files from/to several sources like Google Drive, DropBox"""


@click.group()
@click.version_option("1.0")
@click.option("-v", "--verbose", default=False)
@click.pass_context
def drive(ctx, verbose):
    """Use Google Drive to upload/download files
    """
    creds = None
    path = get_root_path('token.pickle')
    if path.exists():
        with open(path, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            path = get_root_path('drive_credentials.json')
            if not path.exists():
                raise FileNotFoundError("drive_credentials.json file is not found")
            flow = InstalledAppFlow.from_client_secrets_file(
                path.name, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Create a new Http() object for every request
    def build_request(http, *args, **kwargs):
        new_http = google_auth_httplib2.AuthorizedHttp(creds, http=httplib2.Http())
        return googleapiclient.http.HttpRequest(new_http, *args, **kwargs)

    client = build('drive', 'v3', credentials=creds, requestBuilder=build_request)
    ctx.obj = Context(GoogleDrive(client))


@click.group()
@click.version_option("1.0")
@click.pass_context
def dbox(ctx):
    """
    Use Dropbox to upload/download files
    """
    path = Path(__file__).parent.parent.joinpath('db_credentials.json')
    if not path.exists():
        raise FileNotFoundError("db_credentials.json file is not found")

    with open(path, 'r') as f:
        creds = json.load(f)

    app_key = creds['APP_KEY']
    app_secret = creds['APP_SECRET']

    auth_flow = DropboxOAuth2FlowNoRedirect(
        app_key,
        app_secret,
        token_access_type='legacy',
        scope=['files.metadata.read', 'files.metadata.write', 'files.content.write', 'files.content.read']
    )

    path = Path(__file__).parent.parent.joinpath('db_token.pickle')
    if path.exists():
        with open(path, 'rb') as token:
            access_token = pickle.load(token).strip()
    else:
        authorize_url = auth_flow.start()
        print("1. Go to: " + authorize_url)
        print("2. Click \"Allow\" (you might have to log in first).")
        print("3. Copy the authorization code.")
        auth_code = input("Enter the authorization code here: ").strip()

        try:
            access_token = auth_flow.finish(auth_code).access_token
            with open(Path(__file__).parent.parent.joinpath('db_token.pickle'), 'wb') as token:
                pickle.dump(access_token, token)
        except Exception as e:
            raise e

    client = dropbox.Dropbox(oauth2_access_token=access_token, app_key=APP_KEY)
    ctx.obj = Context(DropboxProvider(client))


from app.cli_helper import helper
from app.upload_pipeline import upload
from app.download_pipeline import download


drive.add_command(helper)
drive.add_command(download)
drive.add_command(upload)

dbox.add_command(helper)
dbox.add_command(download)
dbox.add_command(upload)

cli.add_command(drive)
cli.add_command(dbox)

