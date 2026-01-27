#!/usr/bin/env python3
"""
OpenLDAP Test User Generator
Generates 2500 test users with photos for OpenLDAP using randomuser.me API
"""

import requests
import base64
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed


def generate_uid(first_name, surname):
    """Generate UID as first character of given name + full surname"""
    if first_name and surname:
        return f"{first_name[0].lower()}{surname.lower()}"
    return ""


def generate_email(first_name, surname):
    """Generate email address as givenname.lastname@stoeps.home"""
    if first_name and surname:
        return f"{first_name.lower()}.{surname.lower()}@stoeps.home"
    return ""


def fetch_users_batch(seed, count=100):
    """Fetch a batch of users from randomuser.me API"""
    url = "https://randomuser.me/api/"
    params = {
        "results": count,
        "inc": "name,email,picture",
        "nat": "us,de,gb",
        "seed": seed,
        "noinfo": True,
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        print(f"Error fetching batch {seed}: {e}")
        return []


def download_and_encode_photo(url):
    """Download photo and encode as base64"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        print(f"Error downloading photo {url}: {e}")
        return ""


def create_ldif_entry(user, index, base_dn="ou=users,dc=stoeps,dc=home"):
    """Create LDIF entry for a single user"""
    first_name = user["name"]["first"]
    surname = user["name"]["last"]

    # Generate UID and email
    uid = generate_uid(first_name, surname)
    email = generate_email(first_name, surname)

    # Download and encode photo (use thumbnail for smaller size)
    photo_url = user["picture"]["thumbnail"]
    photo_base64 = download_and_encode_photo(photo_url)

    # Create unique cn to avoid conflicts
    cn = f"{first_name} {surname}"
    dn = f"uid={uid},{base_dn}"

    ldif = f"""dn: {dn}
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
objectClass: organizationalPerson
objectClass: person
objectClass: top
cn: {cn}
sn: {surname}
givenName: {first_name}
uid: {uid}
uidNumber: {10000 + index}
gidNumber: 100
homeDirectory: /home/{uid}
loginShell: /bin/bash
userPassword: {{SSHA}}ajjAhDMGYq16bjdJwvlwbn6qsGqbIvKV
mail: {email}
"""

    if photo_base64:
        ldif += f"jpegPhoto:: {photo_base64}\n"

    ldif += "\n"
    return ldif


def generate_ldif(total_users=2500, batch_size=500):
    """Generate LDIF file with specified number of users"""
    print(f"Starting generation of {total_users} users...")

    # Calculate number of batches needed
    num_batches = (total_users + batch_size - 1) // batch_size

    all_users = []

    # Fetch users in parallel batches
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_seed = {
            executor.submit(fetch_users_batch, f"seed{i}", batch_size): i
            for i in range(num_batches)
        }

        for future in as_completed(future_to_seed):
            batch_num = future_to_seed[future]
            try:
                users = future.result()
                all_users.extend(users)
                print(
                    f"Batch {batch_num + 1}/{num_batches}: {len(users)} users fetched"
                )
            except Exception as e:
                print(f"Batch {batch_num + 1} failed: {e}")

    # Trim to exact number if we got more
    all_users = all_users[:total_users]

    # Generate LDIF
    ldif_content = """version: 1

# Base DN
dn: dc=stoeps,dc=home
objectClass: dcObject
objectClass: organization
dc: stoeps
o: Stoeps Home Domain

dn: ou=users,dc=stoeps,dc=home
objectClass: organizationalUnit
ou: users

"""

    print("Generating LDIF entries...")
    successful_users = 0

    with open("test_users.ldif", "w", encoding="utf-8") as f:
        f.write(ldif_content)

        for i, user in enumerate(all_users):
            try:
                ldif_entry = create_ldif_entry(user, i)
                f.write(ldif_entry)
                successful_users += 1

                # Progress indicator
                if (i + 1) % 500 == 0:
                    print(f"Generated {i + 1}/{total_users} entries...")

            except Exception as e:
                print(f"Error creating entry {i}: {e}")

    print("\n✅ Generation complete!")
    print(f"Total users requested: {total_users}")
    print(f"Successfully generated: {successful_users}")
    print("LDIF file: test_users.ldif")

    # Generate a simple shell script to import
    create_import_script(successful_users)


def create_import_script(user_count):
    """Create shell script for importing LDIF"""
    script_content = (
        """#!/bin/bash
# Import script generated by test_user_generator.py

echo "Starting LDAP import..."
echo "Make sure your OpenLDAP server is running"

# Check if ldapadd is available
if ! command -v ldapadd &> /dev/null; then
    echo "Error: ldapadd not found. Install openldap-client package."
    exit 1
fi

# Import users
echo "Importing base structure..."
ldapadd -x -D "cn=admin,dc=stoeps,dc=home" -w adminpassword -f test_users.ldif

if [ $? -eq 0 ]; then
    echo "✅ Import successful!"
    echo "Total users imported: """
        + str(user_count)
        + """"
    echo ""
    echo "To search users: ldapsearch -x -b 'ou=users,dc=stoeps,dc=home'"
    echo "To delete all users: ldapdelete -x -D 'cn=admin,dc=stoeps,dc=home' -w adminpassword -r 'ou=users,dc=stoeps,dc=home'"
else
    echo "❌ Import failed. Check LDAP server configuration."
fi
"""
    )

    with open("import_users.sh", "w", encoding="utf-8") as f:
        f.write(script_content)
    import os

    os.chmod("import_users.sh", 0o755)
    print("Import script: import_users.sh")


if __name__ == "__main__":
    # Configuration
    TOTAL_USERS = 2500
    BATCH_SIZE = 500  # API limit is 5000, but we use 100 for reliability

    try:
        generate_ldif(TOTAL_USERS, BATCH_SIZE)
    except KeyboardInterrupt:
        print("\n⚠️ Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
