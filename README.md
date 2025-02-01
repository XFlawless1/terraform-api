# Terraform + Ansible API for PostgreSQL Replication

This FastAPI application automates the provisioning and configuration of PostgreSQL database instances with replication using Terraform and Ansible. It provides endpoints to generate infrastructure code, execute Terraform plans, approve and apply Terraform changes, and deploy a PostgreSQL database with replication.

---

## Table of Contents
- [Overview](#overview)
- [How It Works](#how-it-works)
- [API Endpoints](#api-endpoints)
- [Payload Example](#payload-example)
- [Future Enhancements](#future-enhancements)
- [Approach](#approach)
- [Assumptions](#assumptions)

---

## Overview

This API enables infrastructure automation for setting up PostgreSQL with replication:
1. **Generates Terraform and Ansible configuration** based on user input.
2. **Executes Terraform plan** and awaits approval.
3. **Runs Terraform apply** to provision resources upon approval.
4. **Deploys PostgreSQL with replication** using Ansible.

This ensures a controlled, repeatable, and automated infrastructure setup.

---

## How It Works

1. **Generate Code** - The API generates Terraform and Ansible configurations based on the provided instance details.
2. **Terraform Plan** - The API runs `terraform plan` to preview changes.
3. **Terraform Approval** - Users approve or deny the Terraform apply execution.
4. **Terraform Apply** - Once approved, Terraform provisions the infrastructure.
5. **PostgreSQL Setup** - Ansible configures PostgreSQL with replication settings.

---

## API Endpoints

### 1. Generate Infrastructure Code
`POST /generate-code`
- Generates Terraform and Ansible configuration files based on provided parameters.
- **Input:** JSON payload with instance configuration.
- **Output:** Confirmation message and Terraform directory path.

### 2. Run Terraform Plan
`POST /terraform-plan`
- Executes `terraform plan` to preview infrastructure changes.
- **Output:** Terraform plan details for review.

### 3. Approve Terraform Apply
`POST /terraform-approve`
- Requires user approval before proceeding with `terraform apply`.
- **Input:** `{ "approved": true }` or `{ "approved": false }`.
- **Output:** Status message confirming approval or denial.

### 4. Check Terraform Apply Status
`GET /terraform-apply-status`
- Provides the status of Terraform apply execution.
- **Output:** Status message and apply output details.

---

## Payload Example

```json
{
  "instance_type": "t3a.medium",
  "num_replicas": 2,
  "aws_region": "us-east-1",
  "ssh_key_name": "stag-key",
  "subnet_id": "subnet-0d2b0680f68dca9f4",
  "postgres_version": "15",
  "max_connections": 100,
  "shared_buffers": "50MB",
  "replication_user": "reptile",
  "replication_password": "superStronGP@ssw0rD"
}
```

---

## Future Enhancements

### 1. **Enhance Security**
- Implement secure secret management (e.g., AWS Secrets Manager, HashiCorp Vault) for sensitive credentials.
- Enforce IAM roles and least privilege principles for Terraform execution.

### 2. **Extend Cloud Provider Support**
- Currently supports AWS. Future support for GCP and Azure is planned.

### 3. **Monitoring and Logging**
- Integrate AWS CloudWatch/Prometheus for monitoring PostgreSQL instances.
- Implement structured logging for debugging and audit trails.

### 4. **Support for High Availability (HA)**
- Automate failover setup for PostgreSQL.

### 5. **Dynamic Configuration Updates**
- Allow users to update Terraform configurations dynamically without manual intervention.

---

## Approach

1. **Infrastructure as Code (IaC)**
   - Uses Terraform for declarative infrastructure provisioning.
   - Uses Ansible for configuration management of PostgreSQL.

2. **Approval-based Execution**
   - Prevents unintended changes by requiring user approval before applying Terraform changes.

3. **Asynchronous Execution**
   - Uses `BackgroundTasks` in FastAPI to manage long-running Terraform and Ansible processes.
   
4. **Modular Design**
   - Terraform and Ansible scripts are modular, allowing reuse and easy customization.

---

## Assumptions

- **Terraform and Ansible are pre-installed** on the execution environment.
- **AWS credentials are configured** using environment variables or IAM roles.
- **Subnet, SSH key, and region details are valid** and correctly set up in AWS.
- **PostgreSQL replication is configured using primary-replica architecture** with a dedicated replication user.
- **Ansible manages PostgreSQL setup efficiently** without manual intervention.

---

## Author
Shrey Ratna
