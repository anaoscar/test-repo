# This file is part of Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from .prism import Prism
from .projects import Project


class SecurityRule(Prism):
    def __init__(self, module):
        resource_type = "/network_security_rules"
        super(SecurityRule, self).__init__(module, resource_type=resource_type)
        self.build_spec_methods = {
            "name": self._build_spec_name,
            "desc": self._build_spec_desc,
            "project": self._build_spec_project,
            "allow_ipv6_traffic": self._build_allow_ipv6_traffic,
            "is_policy_hitlog_enabled": self._build_is_policy_hitlog_enabled,
            "vdi_rule": self._build_vdi_rule,
            "app_rule": self._build_app_rule,
            "isolation_rule": self._build_isolation_rule,
            "quarantine_rule": self._build_quarantine_rule,
            "categories": self._build_spec_categories,
        }

    def _get_default_spec(self):
        return deepcopy(
            {
                "api_version": "3.1.0",
                "metadata": {"kind": "network_security_rule"},
                "spec": {
                    "name": None,
                    "resources": {
                        "is_policy_hitlog_enabled": False,
                    },
                },
            }
        )

    def _build_spec_name(self, payload, value):
        payload["spec"]["name"] = value
        return payload, None

    def _build_spec_desc(self, payload, value):
        payload["spec"]["description"] = value
        return payload, None

    def _build_spec_project(self, payload, param):
        if "name" in param:
            project = Project(self.module)
            name = param["name"]
            uuid = project.get_uuid(name)
            if not uuid:
                error = "Project {0} not found.".format(name)
                return None, error

        elif "uuid" in param:
            uuid = param["uuid"]

        payload["metadata"].update(
            {"project_reference": {"uuid": uuid, "kind": "project"}}
        )
        return payload, None

    def _build_allow_ipv6_traffic(self, payload, value):
        payload["spec"]["resources"]["allow_ipv6_traffic"] = value
        return payload, None

    def _build_is_policy_hitlog_enabled(self, payload, value):
        payload["spec"]["resources"]["is_policy_hitlog_enabled"] = value
        return payload, None

    def _build_vdi_rule(self, payload, value):
        ad_rule = payload["spec"]["resources"].get("ad_rule", {})
        payload["spec"]["resources"]["ad_rule"] = self._build_spec_rule(ad_rule, value)
        return payload, None

    def _build_app_rule(self, payload, value):
        app_rule = payload["spec"]["resources"].get("app_rule", {})
        payload["spec"]["resources"]["app_rule"] = self._build_spec_rule(app_rule, value)
        return payload, None

    def _build_isolation_rule(self, payload, value):
        # if payload["spec"]["resources"].get("isolation_rule"):
        isolation_rule = payload["spec"]["resources"].get("isolation_rule", {})
        if value.get("isolate_category"):
            isolation_rule["first_entity_filter"] = self._generate_filter_spec(
                {}, value["isolate_category"]
            )
        if value.get("from_category"):
            isolation_rule["second_entity_filter"] = self._generate_filter_spec(
                {}, value["from_category"]
            )
        if value.get("subset_category"):
            category_key = next(iter(value["subset_category"]))
            category_value = value["subset_category"][category_key]
            for category in isolation_rule.values():
                if category_key in category["params"]:
                    category["params"][category_key].extend(category_value)
                else:
                    category["params"].update(value["subset_category"])


        if self.module.params.get("policy_mode"): #todo
            isolation_rule["action"] = self.module.params["policy_mode"]
        payload["spec"]["resources"]["isolation_rule"] = isolation_rule
        return payload, None

    def _build_quarantine_rule(self, payload, value):
        if payload["spec"]["resources"].get("quarantine_rule"):
            quarantine_rule = payload["spec"]["resources"]["quarantine_rule"]
            payload["spec"]["resources"]["quarantine_rule"] = self._build_spec_rule(quarantine_rule, value)
        return payload, None

    def _build_spec_categories(self, payload, value):
        payload["metadata"]["categories_mapping"] = value
        payload["metadata"]["use_categories_mapping"] = True
        return payload, None

    def _build_spec_rule(self, payload, value):
        rule = payload
        if value.get("target_group"):
            rule["target_group"] = value["target_group"]
        if value.get("inbound_allow_list"):
            rule["inbound_allow_list"] = self._generate_bound_spec(
                rule.get("inbound_allow_list", []), value["inbound_allow_list"]
            )
        if value.get("outbound_allow_list"):
            rule["outbound_allow_list"] = self._generate_bound_spec(
                rule.get("outbound_allow_list", []), value["outbound_allow_list"]
            )
        if value.get("action"):
            rule["action"] = value["action"]
        return rule

    def _generate_bound_spec(self, payload, list_of_rules):
        for rule in list_of_rules:
            if rule.get("rule_id"):
                rule_spec = self._filter_by_uuid(rule["rule_id"], payload)
                if rule.get("state") == "absent":
                    payload.remove(rule_spec)
                    continue
            else:
                rule_spec = {}
            for key, value in rule.items():
                if key == "filter" and rule_spec.get(key):
                    self._generate_filter_spec(rule_spec[key], value)
                elif key == "protocol":
                    self._generate_protocol_spec(rule_spec, value)
                else:
                    rule_spec[key] = value
            if not rule_spec.get("rule_id"):
                payload.append(rule_spec)
        return payload

    def _generate_protocol_spec(self, payload, config):
        if config.get("tcp"):
            payload["protocol"] = "TCP"
            payload["tcp_port_range_list"] = config["tcp"]
        elif config.get("udp"):
            payload["protocol"] = "UDP"
            payload["udp_port_range_list"] = config["udp"]
        elif config.get("icmp"):
            payload["protocol"] = "ICMP"
            payload["icmp_type_code_list"] = config["icmp"]

    def _generate_filter_spec(self, payload, value):
        payload["type"] = "CATEGORIES_MATCH_ALL"
        payload["kind_list"] = ["vm"]

        payload["params"] = value
        return payload

    def _filter_by_uuid(self, uuid, items_list):
        try:
            return next(filter(lambda d: d.get("rule_id") == uuid, items_list))
        except BaseException:
            self.module.fail_json(
                msg="Failed generating VM Spec",
                error="Entity {0} not found.".format(uuid),
            )
