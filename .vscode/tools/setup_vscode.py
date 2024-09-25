"""This script sets up the vs-code settings for the Isaac Lab template project.

This script merges the python.analysis.extraPaths from the "_isaac_sim/.vscode/settings.json" file into
the ".vscode/settings.json" file.

This is necessary because Isaac Sim 2022.2.1 does not add the necessary python packages to the python path
when the "setup_python_env.sh" is run as part of the vs-code launch configuration.
"""

import argparse
import os
import pathlib
import re

WS_DIR = pathlib.Path(__file__).parents[2]
"""Path to the template directory."""


def overwrite_python_default_interpreter_path(ws_settings: str, isaac_sim_dir: str) -> str:
    """Overwrite the python.defaultInterpreterPath in the workspace settings file.

    The defaultInterpreterPath is replaced with the absolute path to Isaac Sim's bundled Python.

    Args:
        ws_settings: The settings string to manipulate.

    Returns:
        The settings string with overwritten python analysis extra paths.
    """
    settings = re.sub(
        r"\"python.defaultInterpreterPath\": \".*?\"",
        f'"python.defaultInterpreterPath": "{os.path.join(isaac_sim_dir, "python.sh")}"',
        ws_settings,
        flags=re.DOTALL,
    )

    return settings


def overwrite_python_analysis_extra_paths(ws_settings: str, isaac_sim_dir: str) -> str:
    """Overwrite the python.analysis.extraPaths in the workspace settings file.

    The extraPaths are replaced with the path names from the isaac-sim settings file that exists in the
    "_isaac_sim/.vscode/settings.json" file.

    Args:
        ws_settings: The settings string to use as template.

    Returns:
        The settings string with overwritten python analysis extra paths.

    Raises:
        FileNotFoundError: If the isaac-sim settings file does not exist.
    """
    # Read isaac-sim settings
    isaacsim_vscode_filename = os.path.join(isaac_sim_dir, ".vscode", "settings.json")
    if not os.path.exists(isaacsim_vscode_filename):
        raise FileNotFoundError(f"Could not find the isaac-sim settings file: {isaacsim_vscode_filename}")
    with open(isaacsim_vscode_filename) as f:
        vscode_settings = f.read()

    # search for the python.analysis.extraPaths section and extract the contents
    settings = re.search(r"\"python.analysis.extraPaths\": \[.*?\]", vscode_settings, flags=re.MULTILINE | re.DOTALL)
    settings = settings.group(0)
    settings = settings.split('"python.analysis.extraPaths": [')[-1]
    settings = settings.split("]")[0]

    # change the path names to be relative to the Isaac Lab directory
    path_names = settings.split(",")
    path_names = [path_name.strip().strip('"') for path_name in path_names]
    path_names = ['"' + isaac_sim_dir + "/" + path_name + '"' for path_name in path_names if len(path_name) > 0]
    path_names = ",\n\t\t".expandtabs(4).join(path_names)  # combine them into a single string

    # replace the path names in the Isaac Lab settings file with the path names from the isaac-sim settings file
    ws_settings = re.sub(
        r"\"python.analysis.extraPaths\": \[.*?\]",
        '"python.analysis.extraPaths": [\n\t\t'.expandtabs(4) + path_names + "\n\t]".expandtabs(4),
        ws_settings,
        flags=re.DOTALL,
    )

    # return the Isaac Lab settings string
    return ws_settings


def header_msg(src: str):
    return (
        "// This file is a template and is automatically generated by the setup_vscode.py script.\n"
        "// Do not edit this file directly.\n"
        "// \n"
        f"// Generated from: {src}\n"
    )


def main():
    # Read arguments
    parser = argparse.ArgumentParser(description="Setup VSCode.")
    parser.add_argument("--isaacsim_path", type=str, help="The absolute path to your Isaac Sim installation.")
    args = parser.parse_args()

    # SETTINGS.JSON ----------------------------------------------------------------------------------------------------

    # Read workspace template settings
    settings_template_path = os.path.join(WS_DIR, ".vscode", "tools", "settings.template.json")
    if not os.path.exists(settings_template_path):
        raise FileNotFoundError(f"Could not find the Isaac Lab template settings file: {settings_template_path}")
    with open(settings_template_path) as f:
        settings_template = f.read()

    # Overwrite the python.analysis.extraPaths in the Isaac Lab settings file with the path names
    isaacsim_path = args.isaacsim_path
    settings = overwrite_python_analysis_extra_paths(settings_template, isaacsim_path)

    # Overwrite the python.defaultInterpreterPath
    settings = overwrite_python_default_interpreter_path(settings, isaacsim_path)

    # add template notice to the top of the file
    settings = header_msg(settings_template_path) + settings

    # write the Isaac Lab settings file
    settings_path = os.path.join(WS_DIR, ".vscode", "settings.json")
    with open(settings_path, "w") as f:
        f.write(settings)


if __name__ == "__main__":
    main()
