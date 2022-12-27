from jinja2 import Environment, FileSystemLoader, StrictUndefined
import os
import shutil
from typing import List, Dict, Any, Optional
import yaml
import subprocess
from functools import reduce
import click
import tempfile

PROJECT_DIR = 'sample-stack'

def load_values(path: str) -> Dict[str, Any]:
    with open(path, "r") as stream:
        variables = yaml.safe_load(stream)
        
        if variables is None:
            return {}

        if not isinstance(variables, dict):
            raise ValueError(f"file at {path} did not contain a YAML dictionary at top level")
        
        return variables


def merge_single(dictA: Dict[str, Any], dictB: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **dictA,
        **dictB
    }

def merge(dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    return reduce(merge_single, dicts, {})


def template_project(project_dir: str, target_dir: str, custom_values: Dict[str, Any]) -> None:
    """
    explicitly does not delete the folder before doing anything.

    This is so that we can merge multiple project folders into one
    """

    source_dir = project_dir + '/templates'

    default_values = load_values(f'{project_dir}/values.yaml')
    values = merge_single(default_values, custom_values)

    environment = Environment(loader=FileSystemLoader(source_dir), undefined=StrictUndefined)

    def copy_template(src, dest) -> None:
        def opener(path, flags):
            return os.open(path, flags, 0o600)
        
        # TODO: only template some files, not all?

        relative_path = os.path.relpath(src, source_dir)
        template = environment.get_template(relative_path)

        content = template.render(**values)
        with open(dest, 'w', opener=opener, encoding="utf-8") as file:
            file.write(content)
        return dest

    shutil.copytree(
        src=source_dir,
        dst=target_dir,
        copy_function=copy_template,
        dirs_exist_ok=True
    )


def deploy(base_dir: str) -> None:
    """
    by convention we enforce a deploy.sh script.
    This can include arbitrary other tooling that you need
    to call when deploying things
    """
    subprocess.check_call(
        [
            "/bin/bash",
            "deploy.sh"
        ],
        env={
            **os.environ,
        },
        cwd=base_dir,
    )


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
    project_dir: str,
    target_dir: Optional[str],
    values: List[str],
    verbose: int
):
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
            # TODO: overrides in projects
            #       simply do that by invoking it multiple times?
            template_project(project, target_dir, merge(values_loaded))

        deploy('example-gen')
    finally:
        if _temp_dir is not None:
            _temp_dir.cleanup()


cli.add_command(deploy)

if __name__ == '__main__':
    cli()
