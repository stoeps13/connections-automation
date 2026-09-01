CMD_VAULT := "--vault-password-file .vault-secret"

# Default recipe
default:
    @just banner
    @just --list

# Display banner
banner:
    @printf "\n\t   ___                            _   _                 "
    @printf "\n\t  / __\\___  _ __  _ __   ___  ___| |_(_) ___  _ __  ___ "
    @printf "\n\t / /  / _ \\| '_ \\| '_ \\ / _ \\/ __| __| |/ _ \\| '_ \\/ __|"
    @printf "\n\t/ /__| (_) | | | | | | |  __/ (__| |_| | (_) | | | \\__ \\"
    @printf "\n\t\\____/\\___/|_| |_|_| |_|\\___|\\___|\\__|_|\\___/|_| |_|___/"
    @printf "\n\t                                                         "
    @printf "\n\t   _         _                        _   _             "
    @printf "\n\t  /_\\  _   _| |_ ___  _ __ ___   __ _| |_(_) ___  _ __  "
    @printf "\n\t //_\\\\\| | | | __/ _ \\| '_ \` _ \\ / _\` | __| |/ _ \\| '_ \\ "
    @printf "\n\t/  _  \\ |_| | || (_) | | | | | | (_| | |_| | (_) | | | |"
    @printf "\n\t\\_/ \\_/\\__,_|\\__\\___/|_| |_| |_|\\__,_|\\__|_|\\___/|_| |_|"
    @printf "\n\t\n"

# Deploy HCL Connections complete
cnx env: banner
    #!/bin/bash
    ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/setup-connections-complete.yml

# Deploy new API Layer
apisix env: banner
    #!/bin/bash
    ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/hcl/harbor/setup-deploy-apisix.yml

# Deploy Componentpack latest
componentpack env: banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/setup-component-pack-complete-harbor.yml

# Deploy Load Balancer
haproxy env: banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/third_party/setup-haproxy.yml

# Deploy Nginx
nginx env: banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/third_party/setup-nginx.yml

# Deploy CNX Docs
docs env: banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/hcl/setup-connections-docs.yml

# Update all OS packages
osupdate env: banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/third_party/update-system.yml

# Deploy Tiny Editors
tinyeditors env: banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/third_party/setup-tiny-editors.yml

# Display facts for debugging
facts env: banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/ansible_facts.yml

# Start Connections
cnxstart env: banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/third_party/was-nd-start.yml
  ssh root@cnx8-db2-was.stoeps.home start-ihs9.sh

# Stop Connections
cnxstop env: banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/third_party/was-nd-stop.yml

# Install Postfix and Dovecot
mail env: banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/stoeps/setup-mail.yaml
 
