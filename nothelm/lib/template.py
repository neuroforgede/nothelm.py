from jinja2 import Environment, FileSystemLoader, StrictUndefined
import os
import shutil
from typing import List, Dict, Any
import yaml
import subprocess
from functools import reduce

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


def call_deploy(base_dir: str) -> None:
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