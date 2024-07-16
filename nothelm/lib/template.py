from jinja2 import Environment, FileSystemLoader, StrictUndefined
import os
import shutil
from typing import List, Dict, Any
from pathlib import Path
import yaml
import subprocess
from functools import reduce

def interpolate_env_vars_recursively(values: Dict[str, Any]) -> Dict[str, Any]:
    def interpolate(value: Any) -> Any:
        if isinstance(value, dict):
            return interpolate_dict(value)
        elif isinstance(value, list):
            return interpolate_list(value)
        elif isinstance(value, str):
            return interpolate_string(value)
        else:
            return value

    def interpolate_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        return {key: interpolate(value) for key, value in d.items()}

    def interpolate_list(l: List[Any]) -> List[Any]:
        return [interpolate(value) for value in l]
    
    # expand environment variables, they are available in "jinja" format {{ nothelm.env.VARIABLE_NAME }}
    def interpolate_jinja(s: str) -> str:
        env = Environment()
        template = env.from_string(s)
        return template.render(nothelm={"env": os.environ})

    def interpolate_string(s: str) -> str:
        # check if we need to interpolate the string
        if "{{" in s:
            return interpolate_jinja(s)

        return os.path.expandvars(s)

    return interpolate_dict(values)


def load_values(path: str) -> Dict[str, Any]:
    with open(path, "r") as stream:
        variables = yaml.safe_load(stream)
        
        if variables is None:
            return {}

        if not isinstance(variables, dict):
            raise ValueError(f"file at {path} did not contain a YAML dictionary at top level")
        
        if path.endswith('.j2') or path.endswith('.jinja2'):
            variables = interpolate_env_vars_recursively(variables)
        
        return variables


def merge_single(dictA: Dict[str, Any], dictB: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **dictA,
        **dictB
    }

def merge(dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    return reduce(merge_single, dicts, {})


def template_project(
    project_dir: str,
    target_dir: str,
    custom_values: Dict[str, Any],
    all_files_as_template: bool,
    strip_template_file_endings: bool
) -> None:
    """
    explicitly does not delete the folder before doing anything.

    This is so that we can merge multiple project folders into one
    """

    if os.path.exists(f'{project_dir}/values.yaml'):
        default_values = load_values(f'{project_dir}/values.yaml')
    else:
        default_values = dict()
    
    values = merge_single(default_values, custom_values)

    if os.path.exists(project_dir + '/templates'):
        template_dir(project_dir + '/templates', target_dir + '/templates', all_files_as_template, strip_template_file_endings, values)

    if os.path.exists(project_dir + '/commands'):
        template_dir(project_dir + '/commands', target_dir + '/commands', all_files_as_template, strip_template_file_endings, values)


def template_dir(
    src_dir: str,
    dest_dir: str,
    all_files_as_template: bool,
    strip_template_file_endings: bool,
    values: Dict[str, Any]
) -> None:
    environment = Environment(loader=FileSystemLoader(src_dir), undefined=StrictUndefined)

    def copy_template(src: str, dest: str) -> None:
        def opener(path, flags):
            return os.open(path, flags, 0o600)

        is_jinja = src.endswith('.j2') or  src.endswith('.jinja2')
        needs_templating = all_files_as_template or is_jinja

        if needs_templating:
            relative_path = os.path.relpath(src, src_dir)
            template = environment.get_template(relative_path)

            # if the file was a template file (ending with .j2/.jinja2 we might have to strip the ending)
            if strip_template_file_endings and is_jinja:
                dest_file_name = Path(dest).with_suffix('')
            else:
                dest_file_name = dest

            content = template.render(**values)
            with open(dest_file_name, 'w', opener=opener, encoding="utf-8") as file:
                file.write(content)
            return dest
        else:
            shutil.copy2(src, dest)

    shutil.copytree(
        src=src_dir,
        dst=dest_dir,
        copy_function=copy_template,
        dirs_exist_ok=True
    )


def call_command(base_dir: str, command: str) -> None:
    """
    by convention we enforce commands to be scripts that live in the commands folder.
    This can include arbitrary other tooling that you need
    to call when deploying things
    """
    subprocess.check_call(
        [
            "/bin/bash",
            f"../commands/{command}.sh"
        ],
        env={
            **os.environ,
        },
        cwd=base_dir,
    )