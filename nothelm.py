from jinja2 import Environment, FileSystemLoader, StrictUndefined
import os
import shutil
from typing import Dict, Any
import yaml

PROJECT_DIR = 'sample-stack'

def load_variables(path: str) -> Dict[str, Any]:
    with open(path, "r") as stream:
        variables = yaml.safe_load(stream)
        
        if variables is None:
            return {}

        if not isinstance(variables, dict):
            raise ValueError(f"file at {path} did not contain a YAML dictionary at top level")
        
        return variables


def merge(dictA: Dict[str, Any], dictB: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **dictA,
        **dictB
    }


def template_project(project_dir: str, target_dir: str, custom_variables: Dict[str, Any]) -> None:
    source_dir = project_dir + '/templates'

    default_variables = load_variables(f'{project_dir}/variables.yaml')
    variables = merge(default_variables, custom_variables)

    environment = Environment(loader=FileSystemLoader(source_dir), undefined=StrictUndefined)

    def copy_template(src, dest) -> None:
        def opener(path, flags):
            return os.open(path, flags, 0o600)
        
        # TODO: only template some files, not all?

        relative_path = os.path.relpath(src, source_dir)
        template = environment.get_template(relative_path)

        content = template.render(**variables)
        with open(dest, 'w', opener=opener, encoding="utf-8") as file:
            file.write(content)
        return dest

    shutil.copytree(
        src=source_dir,
        dst=target_dir,
        copy_function=copy_template,
        dirs_exist_ok=True
    )


# TODO: overrides in projects
#       simply do that by invoking it multiple times?

variables = load_variables("example-usage/variables.yaml")


template_project('example', 'example-gen', variables)