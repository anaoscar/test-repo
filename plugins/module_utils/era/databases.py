# This file is part of Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


from .era import Era


class Database(Era):
    kind = "registry"

    def __init__(self, module, resource_type="/v0.9/databases"):
        super(Database, self).__init__(module, resource_type=resource_type)
