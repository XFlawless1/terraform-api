import os
import subprocess
from jinja2 import Environment, FileSystemLoader
import re
import json
import time
from app.utils.code_ansible import generate_inventory_file,run_ansible_playbook

ANSIBLE_DIR = os.getenv("ANSIBLE_DIR", "app/ansible")
def generate_terraform_code(config, terraform_dir):
    """
    Generate Terraform code using Jinja2 templates.
    """
    env = Environment(loader=FileSystemLoader(terraform_dir))
    
    main_tf = env.get_template("main.tf.j2").render(config=config)
    variables_tf = env.get_template("variables.tf.j2").render(config=config)
    outputs_tf = env.get_template("outputs.tf.j2").render(config=config)
    
    with open(os.path.join(terraform_dir, "main.tf"), "w") as f:
        f.write(main_tf)
    with open(os.path.join(terraform_dir, "variables.tf"), "w") as f:
        f.write(variables_tf)
    with open(os.path.join(terraform_dir, "outputs.tf"), "w") as f:
        f.write(outputs_tf)

def run_terraform_plan(terraform_dir):
    """
    Runs `terraform plan -out=tfplan`, converts it to JSON, and returns a prettified output.
    Handles missing directories, missing files, and Terraform errors.
    """
    try:
        if not os.path.exists(terraform_dir):
            return json.dumps({"error": f"Terraform directory '{terraform_dir}' not found."})
        
        plan_file = "tfplan"
        json_file = "plan.json"
        
        # Run terraform plan
        subprocess.run(["terraform", "plan", "-out", plan_file], cwd=terraform_dir, check=True)
        
        with open(json_file, "w") as f:
            subprocess.run(["terraform", "show", "-json", plan_file], cwd=terraform_dir, stdout=f, check=True)

        if not os.path.exists(json_file):
            return json.dumps({"error": f"Terraform JSON output '{json_file}' not found."})

        with open(json_file, "r") as f:
            plan_data = json.load(f)
        response = {
            "message": "Terraform plan executed successfully",
            "output": plan_data  # Directly assign the parsed JSON object
        }

        return response

    except FileNotFoundError as e:
        return json.dumps({"error": f"File not found: {str(e)}"})
    except subprocess.CalledProcessError as e:
        return json.dumps({"error": f"Terraform command failed: {str(e)}"})
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse Terraform JSON output."})
    except PermissionError:
        return json.dumps({"error": f"Permission denied: Cannot write to '{terraform_dir}'."})
    except Exception as e:
        return json.dumps({"error": str(e)})

def run_terraform_apply(terraform_dir):
    """
    Run `terraform apply` with a tfplan file and run the ansible playbook.
    """
    result = subprocess.run(["terraform", "apply", "tfplan"], cwd=terraform_dir, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Terraform apply failed:\n{result.stderr}")

    print("Terraform apply completed successfully.")

    output_result = subprocess.run(["terraform", "output", "-json"], cwd=terraform_dir, capture_output=True, text=True)

    if output_result.returncode != 0:
        raise Exception(f"Failed to get Terraform outputs:\n{output_result.stderr}")

    outputs = json.loads(output_result.stdout)
    
    primary_instance_ip = outputs.get("primary_instance_ip", {}).get("value")
    replica_0_instance_ip = outputs.get("replica_0_instance_ip", {}).get("value")
    replica_1_instance_ip = outputs.get("replica_1_instance_ip", {}).get("value")
    print("Sleeping for 30, let instances boot up.")
    time.sleep(30)
    generate_inventory_file(primary_instance_ip, [replica_0_instance_ip, replica_1_instance_ip], '/Users/shreyratna/Downloads/my-key-pair', 'ubuntu', ANSIBLE_DIR)
    response = run_ansible_playbook(ANSIBLE_DIR)
    return response
