from gevent import monkey; monkey.patch_all()

from pathlib import Path

import click
import gevent

from googleapiclient.http import MediaFileUpload

from app.cli import pass_drive
from app.constants import FOLDER_MIMETYPE


@click.command()
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