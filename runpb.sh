#!/usr/bin/env bash
# Configure STDOUT_CALLBACK if -v is attached to the command
# so the output is better readable during troubleshooting

echo -n "$@" | grep -q -- "-v" && export ANSIBLE_STDOUT_CALLBACK=yaml

# Check if commandline argument is given
if [ $# -eq 0 ]; then
 printf "\n\tPlease add the environment name after the script\n"
 printf "\tExample: $(basename $BASH_SOURCE) stoeps-cnx8-db2\n\n"
 exit 1
fi

ANSIBLE_ENV=$1
CMD_OPT="-i environments/${ANSIBLE_ENV}/inventory.ini --vault-password-file .vault-secret"

ansible-playbook ${CMD_OPT} playbooks/setup-connections-complete.yml "$@"
# ansible-playbook ${CMD_OPT} playbooks/third_party/setup-nginx.yml "$@"
# ansible-playbook ${CMD_OPT} playbooks/third_party/setup-containerd.yml "$@"
# ansible-playbook ${CMD_OPT} playbooks/setup-component-pack-complete-harbor.yml "$@"
# ansible-playbook ${CMD_OPT} playbooks/hcl/harbor/setup-deploy-apisix.yml
# ansible-playbook ${CMD_OPT} playbooks/third_party/setup-tiny-editors.yml "$@"
# ansible-playbook ${CMD_OPT} playbooks/hcl/setup-connections-docs.yml "$@"

