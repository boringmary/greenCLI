from gevent import monkey; monkey.patch_all()

import click
import gevent

from app.cli import pass_provider
from app.helpers import get_folder


@click.command()
@click.option("-f", "--frm", help="Where to find files")
@click.option("-t", "--to", help="Where to put files")
@pass_provider
def upload(ctx, frm, to):
    """Upload files from the local folder to the target provider folder
    """
    provider = ctx.provider
    upload_dir(provider, frm, to)


def upload_dir(provider, frm, to):
    p = get_folder(frm)
    if not p:
        click.echo("Please specify existing directory", err=True)
        upload_dir(provider, p, to)

    source_folder = provider.get_source_folder(to)
    files = [f for f in p.iterdir() if f.is_file()]
    jobs = [gevent.spawn(provider.upload_file, file, source_folder) for file in files]
    gevent.wait(jobs)
