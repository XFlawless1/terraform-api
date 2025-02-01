import os
import json
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import subprocess
import shutil
from ansible.cli.playbook import PlaybookCLI

def generate_inventory_file(primary_ip, replica_ips, ssh_key, user, ansible_dir):
    """
    Generate inventory.ini using primary and replica IPs with SSH configuration.
    """
    inventory_content = f"""[primary]
{primary_ip} ansible_user={user} ansible_ssh_private_key_file={ssh_key}

[replica]
""" + "\n".join([f"{ip} ansible_user={user} ansible_ssh_private_key_file={ssh_key}" for ip in replica_ips])

    inventory_path = os.path.join(ansible_dir, "inventory.ini")

    try:
        with open(inventory_path, "w") as f:
            f.write(inventory_content)
        print(f"Inventory file created at {inventory_path}")
    except Exception as e:
        print(f"Error writing inventory file: {e}")

def generate_ansible_playbook(config, ansible_dir):
    """
    Generate Ansible playbook using Jinja2 templates.
    """
    env = Environment(loader=FileSystemLoader(ansible_dir))
    try:
        vars_content = env.get_template("vars.yml.j2").render(config=config)
    except TemplateNotFound:
        raise FileNotFoundError("The specified Jinja2 template 'vars.yml.j2' was not found.")
    playbook_path = f"{ansible_dir}/playbook.yml.j2"
    with open(playbook_path, 'r') as file:
        playbook_content = file.read()
    playbook_path = os.path.join(ansible_dir, "playbook.yml")
    with open(playbook_path, "w") as f:
        f.write(playbook_content)
    vars_path = os.path.join(ansible_dir, "vars.yml")
    with open(vars_path, "w") as f:
        f.write(vars_content)

def run_ansible_playbook(ansible_dir):
    """
    Run Ansible playbook using Ansible's Python API instead of ansible_runner.
    """
    os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"
    os.environ["ANSIBLE_SSH_ARGS"] = "-o StrictHostKeyChecking=no"
    inventory_file = os.path.join(ansible_dir, "inventory.ini")
    playbook_file = os.path.join(ansible_dir, "playbook.yml")

    args = [
        "ansible-playbook",
        "-i", inventory_file,
        playbook_file
    ]

    cli = PlaybookCLI(args)
    try:
        cli.parse()
        cli.run()
    except SystemExit as e:
        if e.code != 0:
            raise Exception(f"Ansible playbook execution failed with exit code {e.code}")

    return "Playbook executed successfully."