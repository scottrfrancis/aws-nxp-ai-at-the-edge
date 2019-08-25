import json
#from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

class CoreShadow:

    def __init__(self):
        self.shadow = {
            "state" : {
                "reported" : {
                    "color" : "red",
                    "power" : "on"
                }
            }
        }

    def gen_payload(self, stateData):
        """ stateData as the object that goes into state/reported """
        self.shadow["state"]["reported"] = stateData
        return json.dumps(self.shadow)