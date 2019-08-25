#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

import time
import json

class CloudWatch:

    def __init__(self):
        self.payload_cpu_load = {
            "request": {
                "namespace": "Greengrass",
                "metricData": {
                    "metricName": "cpu_load",
                    "dimensions": [
                        {
                            "name": "cpu",
                            "value": "Data related to CPU"
                        },
                        {
                            "name": "cpu_load",
                            "value": "Percentage of CPU used"
                        }
                    ],
                    "timestamp" : self.time_ms(),
                    "value": 0,
                    "unit": "Percent"
                }
            }
        }
        self.payload_gpu_load = {
            "request": {
                "namespace": "Greengrass",
                "metricData": {
                    "metricName": "gpu_mem_usage",
                    "dimensions": [
                        {
                            "name": "SerialNumber",
                            "value": "0000000"
                        },
                        {
                            "name": "ModuleType",
                            "value": "Apalis iMX8"
                        },
                        {
                            "name": "ModuleVersion",
                            "value": "V1.0B"
                        }
                    ],
                    "timestamp" : int(time.time()*1000),
                    "value": 0,
                    "unit": "Kilobytes"
                }
            }
        }
    
    def form_payload_cpu_load(self, cpu_percent):
        """ Form the payload """
        self.payload_cpu_load["request"]["metricData"]["timestamp"] = self.time_ms()
        self.payload_cpu_load["request"]["metricData"]["value"] = cpu_percent
        return json.dumps(self.payload_cpu_load)

    def form_payload_gpu_load(self, gpu_mem):
        """ Form the payload """
        self.payload_gpu_load["request"]["metricData"]["timestamp"] = self.time_ms()
        self.payload_gpu_load["request"]["metricData"]["value"] = gpu_mem
        return json.dumps(self.payload_gpu_load)

    def time_ms(self):
        return int(time.time()*1000)