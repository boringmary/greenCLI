from gevent import monkey; monkey.patch_all()
import os

import click
import pickle
import os.path
import httplib2
from pprint import pprint

import googleapiclient
import google_auth_httplib2
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from app.constants import SCOPES

class GDrive(object):
    def __init__(self, client):
        self.cli = client
        self.config = {}
        self.verbose = False

    def set_config(self, key, value):
        self.config[key] = value
        if self.verbose:
            click.echo(f"  config[{key}] = {value}", file=sys.stderr)

    def __repr__(self):
        return f"<Google Drive {self.client.whoami}>"


pass_drive = click.make_pass_decorator(GDrive)



@click.group()
# @click.option("--verbose", "-v", is_flag=True, help="Enables verbose mode.")
@click.version_option("1.0")
@click.option("-v", "--verbose", default=False)
@click.pass_context
def cli(ctx, verbose):
    """Gdrive is a command line tool that provides CLI for Google Drive interactions.
    """

    creds = None
    if os.path.exists('../token.pickle'):
        with open('../token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Create a new Http() object for every request
    def build_request(http, *args, **kwargs):
        new_http = google_auth_httplib2.AuthorizedHttp(creds, http=httplib2.Http())
        return googleapiclient.http.HttpRequest(new_http, *args, **kwargs)

    client = build('drive', 'v3', credentials=creds, requestBuilder=build_request)
    ctx.obj = GDrive(client)
    ctx.obj.verbose = verbose


@cli.command()
@pass_drive
def lst(drive):
    """List of all documents in current user's GDrive directory
    """
    items = drive.cli.files().list().execute()['items']
    for i in items:
        pprint(dict(
            owner=i['ownerNames'],
            title=i['title'],
            link=i['alternateLink'],
            type=i['kind']
        ))
        print("\n")


from app.upload_pipeline import upload
from app.download_pipeline import download


cli.add_command(download)
cli.add_command(upload)

