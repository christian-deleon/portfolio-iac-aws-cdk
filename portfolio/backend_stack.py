from aws_cdk import (
    Stack, 
    Environment, 
    RemovalPolicy, 
    aws_s3 as s3, 
    aws_route53 as route53, 
    aws_cloudfront as cloudfront, 
    aws_route53_targets as route53_targets,
    aws_cloudfront_origins as cloudfront_origins, 
    aws_certificatemanager as certificatemanager,
)
from constructs import Construct

from config import config


class BackendStack(Stack):

    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        env: Environment, 
        **kwargs
        ) -> None:

        super().__init__(scope, construct_id, env=env, **kwargs)

        if config['route53.zone_name'] in ['None', None]:
            certificate = None
            bucket_name = f"{config['owner']-config['repo']}"
            hosted_zone = None
            domain_names = None

        else:
            hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone",
                domain_name=config['route53.zone_name'],
            )

            certificate = certificatemanager.Certificate(self, "Certificate",
                domain_name=config['route53.domain_name'],
                validation=certificatemanager.CertificateValidation.from_dns(hosted_zone=hosted_zone)
            )

            bucket_name = config['route53.domain_name']
            domain_names = [config['route53.domain_name']]

        self.bucket = s3.Bucket(self, "Bucket", 
            bucket_name=bucket_name, 
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=True, 
            auto_delete_objects=True, 
            removal_policy=RemovalPolicy.DESTROY
        )

        distribution = cloudfront.Distribution(self, "Distribution",
            default_root_object="index.html", 
            certificate=certificate, 
            domain_names=domain_names, 
            default_behavior=cloudfront.BehaviorOptions(
                origin=cloudfront_origins.S3Origin(self.bucket), 
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            ), 
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404, 
                    response_http_status=200,
                    response_page_path="/index.html"
                )
            ],
        )

        if hosted_zone:
            route53.ARecord(self, "ARecord",
                zone=hosted_zone, 
                record_name=config['route53.domain_name'], 
                target=route53.RecordTarget.from_alias(
                    route53_targets.CloudFrontTarget(distribution)
                ),
            )
