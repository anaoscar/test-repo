#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Prem Karat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ntnx_ndb_vlans
short_description: Module for create, update and delete of single instance vlan. Currently, postgres type vlan is officially supported.
version_added: 1.8.0-beta.1
description: Module for create, update and delete of single instance vlan in Nutanix vlan Service
options:
  vlan_uuid:
    description:
      - uuid for update or delete of vlan instance
    type: str
  name:
    description:
      - name of vlan instance
      - update allowed
    type: str
extends_documentation_fragment:
  - nutanix.ncp.ntnx_ndb_base_module
  - nutanix.ncp.ntnx_operations
author:
  - Prem Karat (@premkarat)
  - Pradeepsingh Bhati (@bhati-pradeep)
"""

EXAMPLES = r"""
- name: Create postgres vlan instance using with new vm
  ntnx_ndb_vlans:
    name: "test"
    vlan_type: "DHCP"
  register: vlan
"""

RETURN = r"""
response:
  description: vlan creation response after provisioning
  returned: always
  type: dict
  sample: {}
vlan_uuid:
  description: created vlan UUID
  returned: always
  type: str
  sample: "be524e70-60ad-4a8c-a0ee-8d72f954d7e6"
"""

from ..module_utils.ndb.base_module import NdbBaseModule  # noqa: E402
from ..module_utils.ndb.vlans import VLAN  # noqa: E402
from ..module_utils.utils import remove_param_with_none_value  # noqa: E402


def get_module_spec():
    mutually_exclusive = [("name", "uuid")]
    entity_by_spec = dict(name=dict(type="str"), uuid=dict(type="str"))
    ip_pool_spec = dict(start_ip=dict(type="str"), end_ip=dict(type="str"))

    module_args = dict(
        name=dict(type="str"),
        vlan_type=dict(type="str", choices=["DHCP", "Static"]),
        vlan_uuid=dict(type="str"),
        cluster=dict(
            type="dict", options=entity_by_spec, mutually_exclusive=mutually_exclusive
        ),
        ip_pool=dict(
            type="dict",
            options=ip_pool_spec,
            required_together=[("start_ip", "end_ip")],
        ),
        gateway=dict(type="str"),
        subnet_mask=dict(type="str"),
        primary_dns=dict(type="str"),
        secondary_dns=dict(type="str"),
        dns_domain=dict(type="str"),
    )
    return module_args


def create_vlan(module, result):
    vlan = VLAN(module)

    name = module.params["name"]
    uuid, err = vlan.get_uuid(name)
    if uuid:
        module.fail_json(msg="vlan instance with given name already exists", **result)

    spec, err = vlan.get_spec()
    if err:
        result["error"] = err
        module.fail_json(msg="Failed generating create vlan instance spec", **result)

    if module.check_mode:
        result["response"] = spec
        return

    resp = vlan.create(data=spec)
    result["response"] = resp
    vlan_uuid = resp["id"]
    result["vlan_uuid"] = vlan_uuid
    #
    # if module.params.get("wait"):
    #     ops_uuid = resp["operationId"]
    #     operations = Operation(module)
    #     time.sleep(5)  # to get operation ID functional
    #     operations.wait_for_completion(ops_uuid)
    #     resp = vlan.read(vlan_uuid)
    #     result["response"] = resp

    result["changed"] = True


def check_for_idempotency(old_spec, update_spec):
    if (
        old_spec["name"] != update_spec["name"]
        or old_spec["description"] != update_spec["description"]
    ):
        return False

    if len(old_spec["tags"]) != len(update_spec["tags"]):
        return False

    old_tag_values = {}
    new_tag_values = {}
    for i in range(len(old_spec["tags"])):
        old_tag_values[old_spec["tags"][i]["tagName"]] = old_spec["tags"][i]["value"]
        new_tag_values[update_spec["tags"][i]["tagName"]] = update_spec["tags"][i][
            "value"
        ]

    if old_tag_values != new_tag_values:
        return False

    return True


def update_vlan(module, result):
    _vlan = VLAN(module)

    uuid = module.params.get("db_uuid")
    if not uuid:
        module.fail_json(msg="uuid is required field for update", **result)

    resp = _vlan.read(uuid)
    old_spec = _vlan.get_default_update_spec(override_spec=resp)

    update_spec, err = _vlan.get_spec(old_spec=old_spec)

    # due to field name changes
    if update_spec.get("vlanDescription"):
        update_spec["description"] = update_spec.pop("vlanDescription")

    if err:
        result["error"] = err
        module.fail_json(msg="Failed generating update vlan instance spec", **result)

    if module.check_mode:
        result["response"] = update_spec
        return

    if check_for_idempotency(old_spec, update_spec):
        result["skipped"] = True
        module.exit_json(msg="Nothing to change.")

    resp = _vlan.update(data=update_spec, uuid=uuid)
    result["response"] = resp
    result["vlan_uuid"] = uuid
    result["changed"] = True


def delete_vlan(module, result):
    vlan = VLAN(module)

    uuid = module.params.get("vlan_uuid")
    if not uuid:
        module.fail_json(msg="uuid is required field for delete", **result)

    resp = vlan.delete(uuid)

    # if module.params.get("wait"):
    #     ops_uuid = resp["operationId"]
    #     time.sleep(5)  # to get operation ID functional
    #     operations = Operation(module)
    #     resp = operations.wait_for_completion(ops_uuid)

    result["response"] = resp
    result["changed"] = True


def run_module():
    mutually_exclusive_list = [
        ("vlan_uuid", ""),
    ]
    module = NdbBaseModule(
        argument_spec=get_module_spec(),
        mutually_exclusive=mutually_exclusive_list,
        required_if=[
            ("state", "present", ("name", "vlan_uuid"), True),
            ("state", "absent", ("vlan_uuid",)),
        ],
        supports_check_mode=True,
    )
    remove_param_with_none_value(module.params)
    result = {"changed": False, "error": None, "response": None, "vlan_uuid": None}
    if module.params["state"] == "present":
        if module.params.get("vlan_uuid"):
            update_vlan(module, result)
        else:
            create_vlan(module, result)
    else:
        delete_vlan(module, result)
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
