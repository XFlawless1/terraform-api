from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import subprocess
import os
import asyncio
from app.schemas import InstanceConfig
from app.utils.terraform import generate_terraform_code, run_terraform_plan, run_terraform_apply
from app.utils.code_ansible import generate_ansible_playbook
from dotenv import load_dotenv
app = FastAPI()
load_dotenv()
# Environment variables
TERRAFORM_DIR = os.getenv("TERRAFORM_DIR", "app/terraform")
ANSIBLE_DIR = os.getenv("ANSIBLE_DIR", "app/ansible")
terraform_lock = asyncio.Lock()
ansible_lock = asyncio.Lock()

# Shared state for approval flow
terraform_plan_output = None
approval_granted = False
terraform_apply_output = None
terraform_apply_in_progress = False

class ApprovalRequest(BaseModel):
    approved: bool


@app.post("/generate-code")
async def generate_code(config: InstanceConfig):
    """
    Generate Terraform and Ansible code based on input configuration.
    """
    try:
        async with terraform_lock:
            generate_terraform_code(config, TERRAFORM_DIR)
            generate_ansible_playbook(config, ANSIBLE_DIR)
        return {"message": "Code generated successfully", "terraform_dir": TERRAFORM_DIR}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/terraform-plan")
async def terraform_plan():
    """
    Run `terraform plan` and store the output for approval.
    """
    global terraform_plan_output, approval_granted

    try:
        async with terraform_lock:
            terraform_plan_output = run_terraform_plan(TERRAFORM_DIR)
            approval_granted = False  # Reset approval flag for new plan

        return {
            "message": "Terraform plan executed. Awaiting approval.",
            "plan_output": terraform_plan_output,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/terraform-approve")
async def terraform_approve(request: ApprovalRequest, background_tasks: BackgroundTasks):
    """
    Approve and trigger Terraform apply.
    """
    global approval_granted, terraform_apply_output

    if request.approved:
        approval_granted = True
        terraform_apply_output = None
        background_tasks.add_task(terraform_apply)
        return {"message": "Approval granted. Terraform apply is being executed."}
    else:
        return {"message": "Approval denied. Terraform apply will not be executed."}


async def terraform_apply():
    """
    Run `terraform apply` only if approval has been granted.
    Store the output in a global variable.
    """
    global approval_granted, terraform_apply_output, terraform_apply_in_progress

    if not approval_granted:
        terraform_apply_output = "Terraform apply cannot proceed without approval."
        return
    
    terraform_apply_in_progress = True

    try:
        async with terraform_lock:
            output = run_terraform_apply(TERRAFORM_DIR)
            terraform_apply_output = output
    except Exception as e:
        terraform_apply_output = f"Error: {str(e)}"
    finally:
        terraform_apply_in_progress = False

@app.get("/terraform-apply-status")
async def terraform_apply_status():
    """
    Check the status of Terraform apply execution.
    """
    global terraform_apply_output, terraform_apply_in_progress

    if terraform_apply_in_progress:
        return {"status": "running", "message": "Terraform apply is in progress."}

    if terraform_apply_output is None:
        return {"status": "pending", "message": "Terraform apply has not been executed yet."}

    # Check if state has changed
    try:
        result = subprocess.run(["terraform", "plan", "-detailed-exitcode"], capture_output=True, text=True)
        if result.returncode == 2:  # 2 means state has changed
            return {
                "status": "drift-detected",
                "message": "Terraform state has changed since the last apply. Please review changes before applying again.",
                "output": result.stdout
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return {"status": "completed", "output": terraform_apply_output}