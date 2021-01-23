import io

from gevent import monkey; monkey.patch_all()
from pathlib import Path
from pprint import pprint

import click
import gevent

from googleapiclient.http import MediaIoBaseDownload

from app.cli import pass_drive

from app.constants import FOLDER_MIMETYPE

@click.command()
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


