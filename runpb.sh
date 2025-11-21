#!/usr/bin/env bash

# Check if commandline argument is given
if [ $# -eq 0 ]; then
 printf "\n\tPlease add the environment name after the script\n"
 printf "\tExample: $(basename $BASH_SOURCE) stoeps-cnx8-db2\n\n"
 exit 1
fi

ANSIBLE_ENV=$1
CMD_OPT="-i environments/${ANSIBLE_ENV}/inventory.ini --vault-password-file .vault-secret"

# ansible-playbook ${CMD_OPT} playbooks/setup-connections-complete.yml
# ansible-playbook ${CMD_OPT} playbooks/third_party/setup-nginx.yml 
# ansible-playbook ${CMD_OPT} playbooks/third_party/setup-containerd.yml
# ansible-playbook ${CMD_OPT} playbooks/setup-component-pack-complete-harbor.yml
# ansible-playbook ${CMD_OPT} playbooks/hcl/harbor/setup-deploy-apisix.yml
# ansible-playbook ${CMD_OPT} playbooks/third_party/setup-tiny-editors.yml
# ansible-playbook ${CMD_OPT} playbooks/hcl/setup-connections-docs.yml
# ansible-playbook ${CMD_OPT} playbooks/third_party/update-system.yml
#
printf "\nEnvironment: \t$1"
printf "\nPlaybook: \t$2\n"

case $2 in

  apisix)
    ansible-playbook ${CMD_OPT} playbooks/hcl/harbor/setup-deploy-apisix.yml
    ;;

  cnx)
    ansible-playbook ${CMD_OPT} playbooks/setup-connections-complete.yml
    ;;

  componentpack)
    ansible-playbook ${CMD_OPT} playbooks/setup-component-pack-complete-harbor.yml
    ;;

  docs)
    ansible-playbook ${CMD_OPT} playbooks/hcl/setup-connections-docs.yml
    ;;

  osupdate)
    ansible-playbook ${CMD_OPT} playbooks/third_party/update-system.yml
    ;;

  tiny)
    ansible-playbook ${CMD_OPT} playbooks/third_party/setup-tiny-editors.yml
    ;;

  *)
    printf "\nSelect a deployment\n"
    printf "\tapisix         - Deploy new Api layer\n"
    printf "\tcnx            - Deploy Connections complete\n"
    printf "\tcomponentpack  - Deploy Componentpack latest\n"
    printf "\tdocs           - Deploy CNX Docs\n"
    printf "\tosupdate       - Update all OS packages\n"
    printf "\ttiny           - Deploy Tiny Editors\n"
    printf "\n"
    ;;
esac

