import json

class CoreShadow:

    def __init__(self):
        return

    def gen_payload(self, payload_data):
        """ stateData as the object that goes into state/reported.
        Works well for cpu/data, gpu/data and ram/data.
        Will work well with any other payloads that already come as JSON
        friendly objects """

        payload = {
            "state" : {
                    "reported" : payload_data
            }
        }

        return json.dumps(payload)