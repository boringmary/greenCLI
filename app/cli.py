from gevent import monkey; monkey.patch_all()
import os
import io


import click
import pickle
import os.path
import httplib2
from pathlib import Path
from pprint import pprint

import gevent

import google_auth_httplib2
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'


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
    # Create a repo object and remember it as as the context object.  From
    # this point onwards other commands can refer to it by using the
    # @pass_repo decorator.
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


@cli.command()
@click.option("-f", "--frm", help="Where to find files")
@click.option("-t", "--to", help="Where to put files")
@pass_drive
def upload(drive, frm, to):
    """List of all documents in current user's GDrive directory
    """
    p = Path(frm)
    if not p.is_dir() and not p.exists():
        click.echo("Please specify existing directory", err=True)
        return

    page_token = None
    drive_folders = drive.cli.files().list(
        q=f"mimeType = '{FOLDER_MIMETYPE}' and name = '{to}' and trashed = False",
        spaces='drive',
        pageToken=page_token
    ).execute()

    if not drive_folders:
        click.echo("Please specify existing drive folder")
    fid = drive_folders['files'][0]['id']

    from_files = [x for x in p.iterdir() if x.is_file()]
    print(from_files)

    jobs = [gevent.spawn(upload_file, drive.cli, file, fid) for file in from_files]
    gevent.wait(jobs)


@cli.command()
@click.option("-f", "--frm", help="Where to find files")
@click.option("-t", "--to", help="Where to put files")
@pass_drive
def download(drive, frm, to):
    """List of all documents in current user's GDrive directory
    """
    p = Path(to)
    if not p.is_dir() and not p.exists():
        click.echo("Please specify existing directory", err=True)
        return

    page_token = None
    drive_folders = drive.cli.files().list(
        q=f"mimeType = '{FOLDER_MIMETYPE}' and name = '{frm}' and trashed = False",
        spaces='drive',
        pageToken=page_token
    ).execute()
    if not drive_folders:
        click.echo("Please specify existing drive folder")
    fid = drive_folders['files'][0]['id']
    drive_files = drive.cli.files().list(
        q=f"'{fid}' in parents and trashed = False",
        spaces='drive',
        pageToken=page_token
    ).execute()
    pprint(drive_files)
    jobs = [gevent.spawn(download_file, drive.cli, f['id'], Path(f['name']).name, to) for f in drive_files['files']]
    gevent.wait(jobs)


def upload_file(cl, frm, fid):

    file_metadata = {
        'name': str(frm),
        'parents': [fid]
    }
    media = MediaFileUpload(
        str(frm),
        mimetype='image/jpeg',
    )
    print(f"I'm greenlet for the {frm}")
    cl.files().create(
        body=file_metadata,
        media_body=media,
        fields='id',
    ).execute()

    print(f"Downloaded for the {frm}")


def download_file(cl, fid, fname, to):
    request = cl.files().get_media(fileId=fid)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    print(f"I'm greenlet for the {fid}")
    while done is False:
        status, done = downloader.next_chunk()
        print
        "Download %d%%." % int(status.progress() * 100)
    with open(f"{to}/{fname}", "wb") as f:
        f.write(fh.getbuffer())
    print(f"Downloaded for the {fid}")
