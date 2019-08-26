import json

class CoreShadow:

    def __init__(self):
        self.shadow = {
            "state" : {
                "reported" : {
                    "cpu" : {
                        "cores" : 0,
                        "temperatures" : {
                            "A53" : 0.0,
                            "A72" : 0.0
                        },
                        "usage" : 0.0
                    },
                    "gpu" : {
                        "cores" : 0,
                        "temperatures" : {
                            "GPU0" : 0.0,
                            "GPU1" : 0.0
                        },
                        "memoryUsage" : 0.0
                    },
                    "ram" : {
                        "free" : 0.0,
                        "total" : 0.0,
                        "usage" : 0.0
                    }
                }
            }
        }

    def gen_payload(self, cpu, gpu, ram):
        """ stateData as the object that goes into state/reported """

        # Get the JSON
        cpu = cpu.json()
        gpu = gpu.json()
        ram = ram.json()

        # CPU
        self.shadow["state"]["reported"]["cpu"]["cores"] = cpu["cores"]
        self.shadow["state"]["reported"]["cpu"]["temperatures"]["A53"] = cpu["temperatures"]["A53"]
        self.shadow["state"]["reported"]["cpu"]["temperatures"]["A72"] = cpu["temperatures"]["A72"]
        self.shadow["state"]["reported"]["cpu"]["usage"] = cpu["usage"]

        # GPU
        self.shadow["state"]["reported"]["gpu"]["cores"] = gpu["cores"]
        self.shadow["state"]["reported"]["gpu"]["temperatures"]["GPU0"] = gpu["temperatures"]["GPU0"]
        self.shadow["state"]["reported"]["gpu"]["temperatures"]["GPU1"] = gpu["temperatures"]["GPU1"]
        self.shadow["state"]["reported"]["gpu"]["memoryUsage"] = gpu["memoryUsage"]

        # RAM
        self.shadow["state"]["reported"]["ram"]["free"] = ram["free"]
        self.shadow["state"]["reported"]["ram"]["total"] = ram["total"]
        self.shadow["state"]["reported"]["ram"]["usage"] = ram["usage"]
        return json.dumps(self.shadow)