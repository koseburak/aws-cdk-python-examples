import aws_cdk as core
import aws_cdk.assertions as assertions

from stacks.network import NetworkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in stacks/network.py
def test_sqs_queue_created():
    app = core.App()
    stack = NetworkStack(app, "network")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
