#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Prem Karat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ntnx_era_databases_info
short_description: database  info module
version_added: 1.7.0
description: 'Get database info'
options:
      db_name:
        description:
            - database name
        type: str
      db_id:
        description:
            - database id
        type: str
extends_documentation_fragment:
      - nutanix.ncp.ntnx_credentials
author:
 - Prem Karat (@premkarat)
 - Gevorg Khachatryan (@Gevorg-Khachatryan-97)
 - Alaa Bishtawi (@alaa-bish)
"""
EXAMPLES = r"""
  - name: List databases
    ntnx_era_databases_info:
      nutanix_host: "{{ ip }}"
      nutanix_username: "{{ username }}"
      nutanix_password: "{{ password }}"
      validate_certs: False
    register: result

  - name: Get databases using name
    ntnx_databases_info:
      nutanix_host: "{{ ip }}"
      nutanix_username: "{{ username }}"
      nutanix_password: "{{ password }}"
      validate_certs: False
      db_name: "database-name"
    register: result

  - name: Get databases using id
    ntnx_databases_info:
      nutanix_host: "{{ ip }}"
      nutanix_username: "{{ username }}"
      nutanix_password: "{{ password }}"
      validate_certs: False
      db_id: "database-id"
    register: result

"""
RETURN = r"""
"""

from ..module_utils.era.base_info_module import BaseEraInfoModule  # noqa: E402
from ..module_utils.era.databases import Database  # noqa: E402


def get_module_spec():

    module_args = dict(
        db_name=dict(type="str"),
        db_id=dict(type="str"),
    )

    return module_args


def get_database(module, result):
    database = Database(module, resource_type="/v0.8/databases")
    if module.params.get("db_name"):
        db_name = module.params["db_name"]
        db_option = "{0}/{1}".format("name", db_name)
    else:
        db_option = "{0}".format(module.params["db_id"])

    resp = database.read(db_option)

    result["response"] = resp


def get_databases(module, result):
    database = Database(module)

    resp = database.read()

    result["response"] = resp


def run_module():
    module = BaseEraInfoModule(
        argument_spec=get_module_spec(),
        supports_check_mode=False,
        skip_info_args=True,
        mutually_exclusive=[("db_name", "db_id")],
    )
    result = {"changed": False, "error": None, "response": None}
    if module.params.get("db_name") or module.params.get("db_id"):
        get_database(module, result)
    else:
        get_databases(module, result)
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()