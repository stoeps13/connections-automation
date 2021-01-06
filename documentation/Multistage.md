# Use an Ansible Vault

Cleartext passwords in Git repository are not a good idea. Ansible supports [Ansible Vault](https://docs.ansible.com/ansible/2.5/user_guide/playbooks_vault.html), which encrpyts the file with passwords.

## Example environment with variables and vault

Read more details on [multistage environments here](https://www.digitalocean.com/community/tutorials/how-to-manage-multistage-environments-with-ansible).

    environments/
    └── cnx7-hyperv
        ├── group_vars
        │   ├── all
        │   │   ├── all.yml
        │   │   ├── download.yml
        │   │   └── vault.yml
        │   ├── db2_servers
        │   │   └── db2_servers.yml
        │   ├── ihs_servers
        │   │   └── ihs_servers.yml
        │   └── ldap_servers
        │       └── ldap_servers.yml
        └── inventory

For variable inheritance it is easier to move the variables from inventory to group and host variables. So I added all variables with passwords to the vault.yml file:

    db_password: password
    ihs_password: password
    ldap_user_password: password
    ldap_user_admin_password: password
    ldap_bind_pass: password
    was_password: password

### Encrypt the Vault:

    ansible-vault encrypt environments/cnx7-hyperv/group_vars/all/vault.yml

Result of this encryption:

    $ANSIBLE_VAULT;1.1;AES256
    63656263633263303739626235303562303234666163643739303864396665633337626364346532
    6337656361386338646431666234353236306664643838640a323432643161353530633130356565
    63383766303230663736623334613437306630313231663332343762383961646636336366386663
    ...

### Decrypt the Vault:

When you want to add or change a password, just decrypt the file, add the variable and then encrypt it again.

    ansible-vault decrypt environments/cnx7-hyperv/group_vars/all/vault.yml

### Run playbook with a vault

Just add `--ask-vault-password` to the `ansible-playbook` command.

Example:

    ansible-playbook -i environments/cnx7-hyperv/inventory playbooks/setup-connections-complete.yml --private-key=../.ssh/cnx6.key --ask-vault-pass

Alternativly you can use a password file:

    ansible-playbook -i environments/cnx7-hyperv/inventory playbooks/setup-connections-complete.yml --private-key=../.ssh/cnx6.key --vault-password-file .vault_pass.txt

Don't forget to add the `.vault_pass.txt` to [`.gitignore`](https://git-scm.com/docs/gitignore), that it is not stored in the repository!