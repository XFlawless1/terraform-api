from pydantic import BaseModel

class InstanceConfig(BaseModel):
    instance_type: str
    num_replicas: int
    aws_region: str = "us-east-1"
    ssh_key_name: str = "spyne-stag-key"
    subnet_id: str
    postgres_version: str
    max_connections: int
    shared_buffers: str
    replication_user: str = "reptile"
    replication_password: str = "superStronGP@ssw0rD"