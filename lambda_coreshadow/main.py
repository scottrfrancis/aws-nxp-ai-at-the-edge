#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

# greengrass
import greengrasssdk
from coreShadow import CoreShadow

shadowThing = "colibri_imx6_leo_Core"

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')

# Shadow payload generation class
shadow = CoreShadow()

# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
	print("Incoming event: " + context.client_context.custom['subject'])

	if context.client_context.custom['subject'] == "$aws/things/colibri_imx6_leo_Core/shadow/update/accepted":
		# Print confirmation
		print("Device shadow updated: " + str(event))
	else:
		# Generate payload and update device shadow for our core
		shadowPayload = shadow.gen_payload(event, context.client_context.custom['subject'])
		res = client.update_thing_shadow(
			thingName = shadowThing,
			payload = shadowPayload
		) # res is not being checked for success
	return