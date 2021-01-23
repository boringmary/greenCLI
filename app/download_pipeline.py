from gevent import monkey; monkey.patch_all()

import click
import gevent

from app.cli import pass_provider
from app.gdrive import GoogleDrive
from app.helpers import get_folder


@click.command()
@click.option("-f", "--frm", help="Where to find files")
@click.option("-t", "--to", help="Where to put files")
@pass_provider
def download(ctx, frm, to):
    """List of all documents in current user's GDrive directory
    """
    provider = ctx.provider
    download_dir(provider, frm, to)


def download_dir(provider, frm, to):
    local_folder = get_folder(to)
    if not local_folder:
        click.echo("Please specify existing directory", err=True)
        download(provider, frm, to)

    p_folder = provider.get_source_folder(frm)
    files = provider.get_source_files(p_folder['id'])
    jobs = [gevent.spawn(provider.download_file, file, local_folder) for file in files]
    gevent.wait(jobs)
