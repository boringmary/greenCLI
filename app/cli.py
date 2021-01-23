import abc
from pathlib import Path

from gevent import monkey;

from app.gdrive import GoogleDrive
from app.helpers import get_root_path

monkey.patch_all()
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
    """Use Google Drive to upload/download data
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
            path = get_root_path('credentials.json')
            if not path.exists():
                raise FileNotFoundError("credentials.json file is not found")
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


from app.cli_helper import helper
from app.upload_pipeline import upload
from app.download_pipeline import download


drive.add_command(helper)
drive.add_command(download)
drive.add_command(upload)

cli.add_command(drive)

