CMD_VAULT := "--vault-password-file .vault-secret"
# Ensure the local software repository server is running before deployments.
ensure-file-server:
    #!/usr/bin/env bash
    set -euo pipefail
    server="$HOME/data/software/SimpleHTTPServer.py"
    test -f "$server" || { echo "Missing $server" >&2; exit 1; }
    if ! pgrep -f '[S]impleHTTPServer.py' >/dev/null; then
        nohup python3 "$server" >"$HOME/data/software/SimpleHTTPServer.log" 2>&1 &
        sleep 1
    fi
    pgrep -f '[S]impleHTTPServer.py' >/dev/null || { echo "Failed to start $server" >&2; exit 1; }

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
cnx env: ensure-file-server banner
    #!/bin/bash
    ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/setup-connections-complete.yml

# Deploy new API Layer
apisix env: ensure-file-server banner
    #!/bin/bash
    ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/hcl/harbor/setup-deploy-apisix.yml

# Deploy Componentpack latest
componentpack env: ensure-file-server banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/setup-component-pack-complete-harbor.yml

# Deploy Collabora Online
collabora env: ensure-file-server banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/hcl/harbor/setup-collabora.yml

# Deploy CEC v2
cec2 env: ensure-file-server banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/hcl/harbor/setup-cnx-cec.yml

# Deploy Load Balancer
haproxy env: ensure-file-server banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/third_party/setup-haproxy.yml

# Deploy Nginx
nginx env: ensure-file-server banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/third_party/setup-nginx.yml

# Deploy CNX Docs
docs env: ensure-file-server banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/hcl/setup-connections-docs.yml

# Update all OS packages
osupdate env: ensure-file-server banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/third_party/update-system.yml

# Deploy Tiny Editors
tinyeditors env: ensure-file-server banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/third_party/setup-tiny-editors.yml

# Display facts for debugging
facts env: ensure-file-server banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/ansible_facts.yml

# Start Connections
cnxstart env: ensure-file-server banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/third_party/was-nd-start.yml
  ssh root@cnx8-db2-was.stoeps.home start-ihs9.sh

# Stop Connections
cnxstop env: ensure-file-server banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/third_party/was-nd-stop.yml

# Install Postfix and Dovecot
mail env: ensure-file-server banner
  ansible-playbook -i environments/{{ env }}/inventory.ini {{ CMD_VAULT }} playbooks/stoeps/setup-mail.yaml
 
