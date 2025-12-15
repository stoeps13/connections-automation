#!/usr/bin/env bash

printf "\n\t   ___                            _   _                 ";
printf "\n\t  / __\\___  _ __  _ __   ___  ___| |_(_) ___  _ __  ___ ";
printf "\n\t / /  / _ \\| '_ \\| '_ \\ / _ \\/ __| __| |/ _ \\| '_ \\/ __|";
printf "\n\t/ /__| (_) | | | | | | |  __/ (__| |_| | (_) | | | \\__ \\";
printf "\n\t\\____/\\___/|_| |_|_| |_|\\___|\\___|\\__|_|\\___/|_| |_|___/";
printf "\n\t                                                        ";
printf "\n\t   _         _                        _   _             ";
printf "\n\t  /_\\  _   _| |_ ___  _ __ ___   __ _| |_(_) ___  _ __  ";
printf "\n\t //_\\\\\| | | | __/ _ \\| '_ \` _ \\ / _\` | __| |/ _ \\| '_ \\ ";
printf "\n\t/  _  \\ |_| | || (_) | | | | | | (_| | |_| | (_) | | | |";
printf "\n\t\\_/ \\_/\\__,_|\\__\\___/|_| |_| |_|\\__,_|\\__|_|\\___/|_| |_|";
printf "\n\t\n";

# Check if commandline argument is given
if [ $# -eq 0 ]; then
 printf "\n\tPlease add the environment name after the script\n"
 printf "\tExample:\n\t\t\t$(basename $BASH_SOURCE) stoeps-cnx8-db2\n\n"
 exit 1
fi

ANSIBLE_ENV=$1
CMD_OPT="-i environments/${ANSIBLE_ENV}/inventory.ini --vault-password-file .vault-secret"

printf "\n\tEnvironment: \t$1"
printf "\n\tPlaybook: \t$2\n"

case $2 in

  apisix | api | apilayer)
    ansible-playbook ${CMD_OPT} playbooks/hcl/harbor/setup-deploy-apisix.yml
    ;;

  cnx | connections | blue | hclcnx)
    ansible-playbook ${CMD_OPT} playbooks/setup-connections-complete.yml
    ;;

  componentpack | cp | pink)
    ansible-playbook ${CMD_OPT} playbooks/setup-component-pack-complete-harbor.yml
    ;;

  haproxy | lb)
    ansible-playbook ${CMD_OPT} playbooks/third_party/setup-haproxy.yml
    ;;

  nginx | ngx)
    ansible-playbook ${CMD_OPT} playbooks/third_party/setup-nginx.yml
    ;;

  docs | hcldocs | cnxdocs)
    ansible-playbook ${CMD_OPT} playbooks/hcl/setup-connections-docs.yml
    ;;

  osupdate)
    ansible-playbook ${CMD_OPT} playbooks/third_party/update-system.yml
    ;;

  tiny | editors | tinyeditors)
    ansible-playbook ${CMD_OPT} playbooks/third_party/setup-tiny-editors.yml
    ;;

  facts)
    ansible-playbook ${CMD_OPT} playbooks/ansible_facts.yml
    ;;

  cnxstart)
    ansible-playbook ${CMD_OPT} playbooks/third_party/was-cluster-start.yml
    ;;

  cnxstop)
    ansible-playbook ${CMD_OPT} playbooks/third_party/was-cluster-stop.yml
    ;;

  *)
    printf "\n\tSelect a deployment\n"
    printf "\t===================\n"
    printf "\tapisix        \tDeploy new Api layer\n"
    printf "\tcnx           \tDeploy Connections complete\n"
    printf "\tcomponentpack \tDeploy Componentpack latest\n"
    printf "\thaproxy       \tDeploy Load Balancer\n"
    printf "\tnginx         \tDeploy Nginx \n"
    printf "\tdocs          \tDeploy CNX Docs\n"
    printf "\tosupdate      \tUpdate all OS packages\n"
    printf "\ttiny          \tDeploy Tiny Editors\n"
    printf "\tcnxstart      \tStart Application Cluster\n"
    printf "\tcnxstop       \tStop Application Cluster\n"
    printf "\n"
    printf "\tUse the name as second commandline option\n"
    printf "\tExample:\n"
    printf "\t\t\t$(basename $BASH_SOURCE) stoeps-cnx8-db2 apisix\n\n"
    ;;
esac

