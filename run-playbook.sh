#!/usr/bin/env bash

echo -n "$@" | grep -q -- "-v" && export ANSIBLE_STDOUT_CALLBACK=yaml

ansible-playbook -u root "$@" playbooks/third_party/setup-webspherend.yml
ansible-playbook "$@" site.yml
