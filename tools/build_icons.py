#!/usr/bin/env python3
"""Inject the official AWS Architecture Icons (as an inline SVG <symbol> sprite)
into index.html, between the markers <!-- ICONS:START --> and <!-- ICONS:END -->.

Icons come from the npm package `aws-icons` (a repackaging of the official
AWS Architecture Icons SVG set). Usage in index.html:

    <use href="#ic-ec2" x="10" y="10" width="48" height="48"/>

To add an icon: add an entry to ICONS below, then run
    python3 tools/build_icons.py
"""
import io
import pathlib
import re
import tarfile
import urllib.request

PKG_URL = "https://registry.npmjs.org/aws-icons/-/aws-icons-3.3.0.tgz"
ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

# sprite id -> path inside package/icons/
ICONS = {
    # --- services (64x64, coloured square) ---
    "ec2": "architecture-service/AmazonEC2.svg",
    "cloudwatch": "architecture-service/AmazonCloudWatch.svg",
    "ssm": "architecture-service/AWSSystemsManager.svg",
    "lambda": "architecture-service/AWSLambda.svg",
    "dynamodb": "architecture-service/AmazonDynamoDB.svg",
    "eventbridge": "architecture-service/AmazonEventBridge.svg",
    "config": "architecture-service/AWSConfig.svg",
    "iam": "architecture-service/AWSIdentityandAccessManagement.svg",
    "backup": "architecture-service/AWSBackup.svg",
    "kms": "architecture-service/AWSKeyManagementService.svg",
    "imagebuilder": "architecture-service/AmazonEC2ImageBuilder.svg",
    "cloudformation": "architecture-service/AWSCloudFormation.svg",
    "rds": "architecture-service/AmazonRDS.svg",
    "ec2autoscaling": "architecture-service/AmazonEC2AutoScaling.svg",
    "health": "architecture-service/AWSHealthDashboard.svg",
    "cloudshell": "architecture-service/AWSCloudShell.svg",
    "marketplace": "architecture-service/AWSMarketplace.svg",
    "sns": "architecture-service/AmazonSimpleNotificationService.svg",
    "ebs": "architecture-service/AmazonElasticBlockStore.svg",
    "s3": "architecture-service/AmazonSimpleStorageService.svg",
    "athena": "architecture-service/AmazonAthena.svg",
    "cloudtrail": "architecture-service/AWSCloudTrail.svg",
    "securityhub": "architecture-service/AWSSecurityHub.svg",
    "secretsmanager": "architecture-service/AWSSecretsManager.svg",
    "elb": "architecture-service/ElasticLoadBalancing.svg",
    "acm": "architecture-service/AWSCertificateManager.svg",
    "sqs": "architecture-service/AmazonSimpleQueueService.svg",
    "autoscaling": "architecture-service/AWSAutoScaling.svg",
    "efs": "architecture-service/AmazonEFS.svg",
    "glue": "architecture-service/AWSGlue.svg",
    "apigateway": "architecture-service/AmazonAPIGateway.svg",
    "cloudfront": "architecture-service/AmazonCloudFront.svg",
    "kinesis": "architecture-service/AmazonKinesisDataStreams.svg",
    "stepfunctions": "architecture-service/AWSStepFunctions.svg",
    # --- resources (48x48, single colour) ---
    "r-instance": "resource/AmazonEC2Instance.svg",
    "r-instances": "resource/AmazonEC2Instances.svg",
    "r-ami": "resource/AmazonEC2AMI.svg",
    "r-volume": "resource/AmazonElasticBlockStoreVolume.svg",
    "r-snapshot": "resource/AmazonElasticBlockStoreSnapshot.svg",
    "r-alarm": "resource/AmazonCloudWatchAlarm.svg",
    "r-logs": "resource/AmazonCloudWatchLogs.svg",
    "r-param": "resource/AWSSystemsManagerParameterStore.svg",
    "r-endpoint": "resource/AmazonVPCEndpoints.svg",
    "r-role": "resource/AWSIdentityAccessManagementRole.svg",
    "r-topic": "resource/AmazonSimpleNotificationServiceTopic.svg",
    "r-ebrule": "resource/AmazonEventBridgeRule.svg",
    "r-table": "resource/AmazonDynamoDBTable.svg",
    "r-lambdafn": "resource/AWSLambdaLambdaFunction.svg",
    "r-cwagent": "resource/AmazonEC2InstancewithCloudWatch.svg",
    "r-eip": "resource/AmazonEC2ElasticIPAddress.svg",
    "r-key": "resource/AWSIdentityAccessManagementDataEncryptionKey.svg",
    "r-igw": "resource/AmazonVPCInternetGateway.svg",
    "r-user": "resource/User.svg",
    "r-users": "resource/Users.svg",
    "r-client": "resource/Client.svg",
    "r-server": "resource/Server.svg",
    "r-internet": "resource/Internet.svg",
    "r-json": "resource/JSONScript.svg",
    "r-doc": "resource/Document.svg",
    "r-bucket": "resource/AmazonSimpleStorageServiceBucket.svg",
    "r-asg": "resource/AmazonEC2AutoScaling.svg",
    "r-ssm-automation": "resource/AWSSystemsManagerAutomation.svg",
    "r-ssm-documents": "resource/AWSSystemsManagerDocuments.svg",
    "r-ssm-runcommand": "resource/AWSSystemsManagerRunCommand.svg",
    "r-ssm-session": "resource/AWSSystemsManagerSessionManager.svg",
    "r-ssm-state": "resource/AWSSystemsManagerStateManager.svg",
    "r-ssm-inventory": "resource/AWSSystemsManagerInventory.svg",
    "r-ssm-patch": "resource/AWSSystemsManagerPatchManager.svg",
    "r-ssm-maint": "resource/AWSSystemsManagerMaintenanceWindows.svg",
    "r-ssm-opscenter": "resource/AWSSystemsManagerOpsCenter.svg",
    "r-ssm-distributor": "resource/AWSSystemsManagerDistributor.svg",
    "r-ssm-compliance": "resource/AWSSystemsManagerCompliance.svg",
    "r-alb": "resource/ElasticLoadBalancingApplicationLoadBalancer.svg",
    "r-nlb": "resource/ElasticLoadBalancingNetworkLoadBalancer.svg",
    "r-gwlb": "resource/ElasticLoadBalancingGatewayLoadBalancer.svg",
    "r-clb": "resource/ElasticLoadBalancingClassicLoadBalancer.svg",
    "r-queue": "resource/AmazonSimpleQueueServiceQueue.svg",
    "r-firewall": "resource/Firewall.svg",
    "r-router": "resource/AmazonVPCRouter.svg",
    "r-efs-fs": "resource/AmazonElasticFileSystemFileSystem.svg",
    "r-dlm": "resource/AmazonElasticBlockStoreAmazonDataLifecycleManager.svg",
    "r-objects": "resource/AmazonSimpleStorageServiceBucketWithObjects.svg",
    "r-s3-replication": "resource/AmazonSimpleStorageServiceS3Replication.svg",
    "r-s3-standard": "resource/AmazonSimpleStorageServiceS3Standard.svg",
    "r-s3-ia": "resource/AmazonSimpleStorageServiceS3StandardIA.svg",
    "r-s3-onezone": "resource/AmazonSimpleStorageServiceS3OneZoneIA.svg",
    "r-s3-it": "resource/AmazonSimpleStorageServiceS3IntelligentTiering.svg",
    "r-s3-gir": "resource/AmazonSimpleStorageServiceS3GlacierInstantRetrieval.svg",
    "r-s3-gfr": "resource/AmazonSimpleStorageServiceS3GlacierFlexibleRetrieval.svg",
    "r-s3-gda": "resource/AmazonSimpleStorageServiceS3GlacierDeepArchive.svg",
    "r-s3-express": "resource/AmazonSimpleStorageServiceS3ExpressOneZone.svg",
    "r-edge": "resource/AmazonCloudFrontEdgeLocation.svg",
    "r-glue-catalog": "resource/AWSGlueDataCatalog.svg",
    # --- groups (40x40) ---
    "g-cloud": "architecture-group/AWSCloud.svg",
    "g-region": "architecture-group/Region.svg",
    "g-vpc": "architecture-group/VirtualprivatecloudVPC.svg",
    "g-private": "architecture-group/Privatesubnet.svg",
    "g-public": "architecture-group/Publicsubnet.svg",
    "g-account": "architecture-group/AWSAccount.svg",
    "g-dc": "architecture-group/Corporatedatacenter.svg",
    "g-asg": "architecture-group/AutoScalinggroup.svg",
}

# General (dark navy) resource icons follow the text colour so they work in dark mode.
NAVY = re.compile(r'fill="#(242f3e|232f3d|232f3e)"')


def main():
    data = urllib.request.urlopen(PKG_URL).read()
    tar = tarfile.open(fileobj=io.BytesIO(data))
    out = ['<svg xmlns="http://www.w3.org/2000/svg" style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true">']
    for sid, rel in ICONS.items():
        svg = tar.extractfile(f"package/icons/{rel}").read().decode()
        vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
        inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", svg, flags=re.S)
        inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
        if rel.startswith("resource/"):
            inner = NAVY.sub('fill="currentColor"', inner)
        out.append(f'<symbol id="ic-{sid}" viewBox="{vb}">{inner}</symbol>')
    out.append("</svg>")
    sprite = "\n".join(out)

    html = INDEX.read_text(encoding="utf-8")
    new, n = re.subn(
        r"(<!-- ICONS:START -->).*?(<!-- ICONS:END -->)",
        lambda m: f"{m.group(1)}\n{sprite}\n{m.group(2)}",
        html,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("ICONS markers not found in index.html")
    INDEX.write_text(new, encoding="utf-8")
    print(f"Injected {len(ICONS)} icons into {INDEX}")


if __name__ == "__main__":
    main()
