#!/usr/bin/env bash

echo -n "$@" | grep -q -- "-v" && export ANSIBLE_STDOUT_CALLBACK=yaml

ansible-playbook "$@"