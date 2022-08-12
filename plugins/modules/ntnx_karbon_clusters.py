#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Prem Karat
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ntnx_karbon_clusters
short_description: category module which supports pc category management CRUD operations
version_added: 1.5.0
description: "Create, Update, Delete clusters"
options:
    name:
        type: str
        description: Unique name of the k8s cluster.
    cluster_type:
        type: str
        choices: ["DEV", "PROD"]
        description: write
    cluster:
        type: dict
        description: write
        suboptions:
            name:
                type: str
                description: Cluster name
            uuid:
                type: str
                description: Cluster UUID
    k8s_version:
        type: str
        description: K8s version of the cluster.
    node_subnet:
        type: dict
        description: write
        suboptions:
            name:
                type: str
                description: write
            uuid:
                type: str
                description: write
    host_os:
        type: str
        description: The version of the node OS image.
    cni:
        type: dict
        description: K8s cluster networking configuration. The flannel or the calico configuration needs to be provided.
        suboptions:
            node_cidr_mask_size:
                type: int
                default: 24
                description: The size of the subnet from the pod_ipv4_cidr assigned to each host. A value of 24 would allow up to 255 pods per node.
            service_ipv4_cidr:
                type: str
                required: true
                description: Classless inter-domain routing (CIDR) for k8s services in the cluster.
            pod_ipv4_cidr:
                type: str
                required: true
                description: CIDR for pods in the cluster.
            network_provider:
                type: str
                choices: ["Calico", "Flannel"]
                default: "Flannel"
                description: write
    custom_node_configs:
        type: dict
        description: write
        suboptions:
            etcd:
                type: dict
                description: Configuration of the etcd cluster.
                suboptions:
                    num_instances:
                        type: int
                        description: Number of nodes in the node pool.
                    cpu:
                        type: int
                        description: The number of VCPUs allocated for each VM on the PE cluster.
                        default: 4
                    disk_gb:
                        type: int
                        description: Size of local storage for each VM on the PE cluster in GiB.
                        default: 120
                    memory_gb:
                        type: int
                        description: Memory allocated for each VM on the PE cluster in GiB.
                        default: 8
            masters:
                type: dict
                description:
                    - "Configuration of master nodes. Providing one of the following configurations is required:
                    single master, active-passive or the external load-balancer."
                suboptions:
                    num_instances:
                        type: int
                        description: Number of nodes in the node pool.
                    cpu:
                        type: int
                        description: The number of VCPUs allocated for each VM on the PE cluster.
                        default: 4
                    disk_gb:
                        type: int
                        description: Size of local storage for each VM on the PE cluster in GiB.
                        default: 120
                    memory_gb:
                        type: int
                        description: Memory allocated for each VM on the PE cluster in GiB.
                        default: 8
            workers:
                type: dict
                description: Configuration of the worker nodes.
                suboptions:
                    num_instances:
                        type: int
                        description: Number of nodes in the node pool.
                    cpu:
                        type: int
                        description: The number of VCPUs allocated for each VM on the PE cluster.
                        default: 4
                    disk_gb:
                        type: int
                        description: Size of local storage for each VM on the PE cluster in GiB.
                        default: 120
                    memory_gb:
                        type: int
                        description: Memory allocated for each VM on the PE cluster in GiB.
                        default: 8
    control_plane_virtual_ip:
        type: str
        description: write
    storage_class:
        type: dict
        description: write
        suboptions:
            default_storage_class:
                type: bool
                description:
                    - K8 uses the default storage class when the persistent volume claim (PVC)
                      create request does not specify a storage class to use for the new persistent volume (PV).
            name:
                type: str
                description: The name of the storage class.
                required: true
            reclaim_policy:
                type: str
                description: Reclaim policy for persistent volumes provisioned using the specified storage class.
                choices: ["ext4", "Delete"]
            storage_container:
                type: str
                description: Name of the storage container the storage container uses to provision volumes.
                required: true
            flash_mode:
                type: bool
                description: boolean to enable flash mode
            file_system:
                type: str
                description: Karbon uses either the ext4 or xfs file-system on the volume disk.
                choices: ["ext4", "xfs"]
extends_documentation_fragment:
      - nutanix.ncp.ntnx_credentials
      - nutanix.ncp.ntnx_operations
author:
    - Prem Karat (@premkarat)
    - Gevorg Khachatryan (@Gevorg-Khachatryan-97)
    - Alaa Bishtawi (@alaa-bish)
"""

EXAMPLES = r"""

"""

RETURN = r"""

"""

from ..module_utils import utils  # noqa: E402
from ..module_utils.base_module import BaseModule  # noqa: E402
from ..module_utils.karbon.clusters import Cluster  # noqa: E402
from ..module_utils.prism.tasks import Task  # noqa: E402


def get_module_spec():
    mutually_exclusive = [("name", "uuid")]

    entity_by_spec = dict(name=dict(type="str"), uuid=dict(type="str"))

    resource_spec = dict(
        num_instances=dict(type="int"),
        cpu=dict(type="int", default=4),
        memory_gb=dict(type="int", default=8),
        disk_gb=dict(type="int", default=120),
    )

    cni_spec = dict(
        node_cidr_mask_size=dict(type="int", default=24),
        service_ipv4_cidr=dict(type="str", required=True),
        pod_ipv4_cidr=dict(type="str", required=True),
        network_provider=dict(
            type="str", choices=["Calico", "Flannel"], default="Flannel"
        ),
    )

    storage_class_spec = dict(
        default_storage_class=dict(type="bool"),
        name=dict(type="str", required=True),
        reclaim_policy=dict(type="str", choices=["Retain", "Delete"]),
        storage_container=dict(type="str", required=True),
        file_system=dict(type="str", choices=["ext4", "xfs"]),
        flash_mode=dict(type="bool"),
    )
    custom_node_spec = dict(
        etcd=dict(type="dict", apply_defaults=True, options=resource_spec),
        masters=dict(type="dict", apply_defaults=True, options=resource_spec),
        workers=dict(type="dict", apply_defaults=True, options=resource_spec),
    )
    module_args = dict(
        name=dict(type="str"),
        cluster_type=dict(type="str", choices=["DEV", "PROD"]),
        cluster=dict(
            type="dict", options=entity_by_spec, mutually_exclusive=mutually_exclusive
        ),
        k8s_version=dict(type="str"),
        host_os=dict(type="str"),
        node_subnet=dict(
            type="dict", options=entity_by_spec, mutually_exclusive=mutually_exclusive
        ),
        cni=dict(type="dict", options=cni_spec),
        custom_node_configs=dict(
            type="dict", apply_defaults=True, options=custom_node_spec
        ),
        control_plane_virtual_ip=dict(type="str"),
        storage_class=dict(type="dict", options=storage_class_spec),
    )

    return module_args


def create_cluster(module, result):
    cluster = Cluster(module)

    spec, error = cluster.get_spec()
    if error:
        result["error"] = error
        module.fail_json(msg="Failed generating create cluster spec", **result)

    if module.check_mode:
        result["response"] = spec
        return

    resp = cluster.create(spec)
    cluster_uuid = resp["cluster_uuid"]
    task_uuid = resp["task_uuid"]
    result["cluster_uuid"] = cluster_uuid
    result["changed"] = True

    if module.params.get("wait"):
        task = Task(module)
        task.wait_for_completion(task_uuid)
        resp = cluster.read(resp["cluster_name"])

    result["response"] = resp


def delete_cluster(module, result):
    cluster_name = module.params["name"]
    if not cluster_name:
        result["error"] = "Missing parameter name in playbook"
        module.fail_json(msg="Failed deleting cluster", **result)

    cluster = Cluster(module)
    resp = cluster.delete(cluster_name)
    result["changed"] = True
    result["cluster_name"] = cluster_name
    task_uuid = resp["task_uuid"]
    result["task_uuid"] = task_uuid

    if module.params.get("wait"):
        task = Task(module)
        resp = task.wait_for_completion(task_uuid)

    result["response"] = resp


def run_module():
    module = BaseModule(
        argument_spec=get_module_spec(),
        supports_check_mode=True,
        mutually_exclusive=[("cluster_type", "custom_node_configs")],
        required_if=[
            ("state", "present", ("cluster_type", "custom_node_configs"), True),
        ],
        required_together=[
            (
                "cluster",
                "k8s_version",
                "host_os",
                "node_subnet",
                "cni",
                "storage_class",
            ),
        ],
    )
    utils.remove_param_with_none_value(module.params)
    result = {
        "response": {},
        "error": None,
        "changed": False,
    }
    state = module.params["state"]
    if state == "present":
        create_cluster(module, result)
    else:
        delete_cluster(module, result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
