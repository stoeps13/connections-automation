#!/usr/bin/env bash
# Configure STDOUT_CALLBACK if -v is attached to the command
# so the output is better readable during troubleshooting

echo -n "$@" | grep -q -- "-v" && export ANSIBLE_STDOUT_CALLBACK=yaml

ansible-playbook -i environments/stoeps-cnx8-db2/inventory.ini playbooks/third_party/update-system.yml "$@"
# ansible-playbook -i environments/stoeps-cnx8-db2/inventory.ini playbooks/third_party/setup-nginx.yml "$@"
# ansible-playbook -i environments/stoeps-cnx8-db2/inventory.ini playbooks/third_party/setup-containerd.yml "$@"
# ansible-playbook -i environments/stoeps-cnx8-db2/inventory.ini playbooks/setup-component-pack-complete-harbor.yml "$@"
# ansible-playbook -i environments/stoeps-cnx8-db2/inventory.ini playbooks/third_party/setup-tiny-editors.yml "$@"
# ansible-playbook -i environments/stoeps-cnx8-db2/inventory.ini playbooks/hcl/setup-connections-docs.yml "$@"

