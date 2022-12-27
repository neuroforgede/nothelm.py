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
@click.option('--all-files-as-template', default=False, help="""
    whether to treat all files inside the templates/ folder as a template.
    By default only files ending in .j2/.jinja2 are treated as templates
    """,
    is_flag=True
)
@click.option('--strip-template-file-endings/--no-strip-template-file-endings', default=None, is_flag=True, 
    help="""
    wether to strip template file endings (.j2/.jinja2) defaults to --strip-template-file-endings, 
    if --all-files-as-template is set, this defaults to --no-strip-template-file-endings.
    """,
    callback=lambda c, p, v: v if v is not None else not c.params['all_files_as_template'])
@click.option('-t', '--target-dir', type=click.STRING, required=False)
@click.option('-f', '--values', type=click.STRING, required=False, multiple=True)
@click.option('--dry-run',
    default=False,
    help='whether to do a dry-run. A dry-run skips executing the deployment.',
    is_flag=True)
@click.option('-v', '--verbose', count=True)
def deploy(
    project_dir: List[str],
    target_dir: Optional[str],
    values: List[str],
    verbose: int,
    dry_run: bool,
    all_files_as_template: bool,
    strip_template_file_endings: bool
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
            template_project(project, target_dir, merge(values_loaded), all_files_as_template, strip_template_file_endings)

        if not dry_run:
            call_deploy(target_dir)
    finally:
        if _temp_dir is not None:
            _temp_dir.cleanup()

cli.add_command(deploy)
