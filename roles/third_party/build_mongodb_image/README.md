build-mongodb image
=========

Build mongoDb image like described in https://opensource.hcltechsw.com/connections-doc/admin/install/installing_mongodb_5_for_component_pack_8.html?h=mongodb5.

Role Variables
--------------

- Repository_url

Dependencies
------------

Role works only as part of https://github.com/HCL-TECH-SOFTWARE/connections-automation

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: build-mongodb }

License
-------

Apache 2.0

Author Information
------------------

Author: Christoph Stoettner
Email: christoph.stoettner@stoeps.de
Blog: https://stoeps.de
