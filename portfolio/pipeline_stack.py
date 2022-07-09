from aws_cdk import (
    Stack, 
    Duration, 
    aws_s3 as s3, 
    aws_iam as iam, 
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
)
from constructs import Construct

from config import config


class PipelineStack(Stack):
    
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        github_connection_arn: str, 
        website_bucket: s3.Bucket, 
        **kwargs
        ) -> None:
        
        super().__init__(scope, construct_id, **kwargs)

        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            action_name="GitHub_Source",
            connection_arn=github_connection_arn, 
            owner=config['github.owner'],
            repo=config['github.repo'],
            output=source_output,
        )

        role = iam.Role(self, "Role",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=['s3:*'],
                # resources=[website_bucket.bucket_arn]
                resources=['*']
            )
        )

        bucket_uri = website_bucket.s3_url_for_object()

        project = codebuild.PipelineProject(self, "Project",
            role=role,
            timeout=Duration.minutes(10), 
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.CUSTOM), 
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_4_0, 
            ),
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "pre_build": {
                        "commands": [
                            "echo installing modules...", 
                            "npm ci"
                        ]
                    },
                    "build": {
                        "commands": [
                            "echo building webapp...", 
                            "npm run build"
                        ]
                    },
                    "post_build": {
                        "commands": [
                            "echo cleaning up bucket...", 
                            f"aws s3 rm {bucket_uri} --recursive", 
                            f"aws s3 cp ./build {bucket_uri} --recursive"
                        ]
                    }
                },
                # "artifacts": {
                #     "files": [
                #         "**/*"
                #     ], 
                #     "base-directory": "build"
                # },
                "cache": {
                    "paths": [
                        "/root/.npm"
                    ], 
                },
            })
        )

        # build_output = codepipeline.Artifact()
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=project,
            input=source_output, 
            # outputs=[build_output]
        )

        # deploy_action = codepipeline_actions.S3DeployAction(
        #     action_name="S3Deploy", 
        #     bucket=website_bucket, 
        #     input=build_output
        # )

        codepipeline.Pipeline(self, "Pipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        source_action
                    ]
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        build_action
                    ]
                ), 
                # codepipeline.StageProps(
                #     stage_name="Deploy",
                #     actions=[
                #         deploy_action
                #     ]
                # )
            ]
        )
