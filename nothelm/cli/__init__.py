import click
import os
import tempfile
import shutil
from typing import List, Optional
from nothelm.lib.template import load_values, template_project, merge, call_deploy

@click.group()
def cli() -> None:
    """
    nothelm.py
    """
    pass


@click.command()
@click.option('-p', '--project-dir', type=click.STRING, required=True, multiple=True)
@click.option('-t', '--target-dir', type=click.STRING, required=False)
@click.option('-f', '--values', type=click.STRING, required=False, multiple=True)
@click.option('-v', '--verbose', count=True)
def deploy(
    project_dir: List[str],
    target_dir: Optional[str],
    values: List[str],
    verbose: int
) -> None:
    """
    deploy a project

    Notes:

    - To override files in a project you can specify --project-dir/-p multiple times
    - To override values multiple times, you can specify --values/-f multiple times
    """

    values_loaded = list(map(load_values, values))

    _use_temp_dir = target_dir is None
    _temp_dir: Optional[tempfile.TemporaryDirectory] = None

    try:
        if _use_temp_dir:
            _temp_dir = tempfile.TemporaryDirectory()
            target_dir = _temp_dir.name

        # clean directory if manually specified
        # TODO: make this configurable?
        if os.path.exists(target_dir):
            if os.path.isfile(target_dir):
                raise ValueError(f"{target_dir} is a file")
            # delete the old files
            shutil.rmtree(target_dir, ignore_errors=True)

        for project in project_dir:
            template_project(project, target_dir, merge(values_loaded))

        call_deploy(target_dir)
    finally:
        if _temp_dir is not None:
            _temp_dir.cleanup()

cli.add_command(deploy)
