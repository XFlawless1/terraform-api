from utils.code_ansible import run_ansible_playbook
import os
ANSIBLE_DIR = os.getenv("ANSIBLE_DIR", "app/ansible")
run_ansible_playbook(ANSIBLE_DIR)