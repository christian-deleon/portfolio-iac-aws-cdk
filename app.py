import aws_cdk as cdk

from portfolio.pipeline_stack import PipelineStack
from portfolio.github_connection_stack import GitHubConnectionStack
from portfolio.backend_stack import BackendStack

from config import config


app = cdk.App()

env = cdk.Environment(
    account=config['account.id'], 
    region="us-east-1"
)

github_connection_stack = GitHubConnectionStack(app, 
    "GitHubConnection", 
    env=env
)

backend = BackendStack(app, 
    "BackendStack", 
    env=env
)

PipelineStack(app, 
    "PipelineStack", 
    github_connection_arn=github_connection_stack.connection_arn, 
    website_bucket=backend.bucket, 
    distribution_id=backend.distribution.distribution_id,
    env=env
)

app.synth()
