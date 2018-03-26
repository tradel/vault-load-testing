Load Tests for Vault
====================

This project aims to generate realistic load against Vault (and, by extension,
Consul) by exercising various secrets engines and auth methods.

## Prerequisites

You need to have Vault running, obviously, and the vault must be unsealed before 
starting the test.

If you want to test dynamic secret generation via the database backends (MySQL, 
MongoDB), you must have those database engines running during the test. You will
need to set up environment variables with the connection strings in the appropriate 
formats, for example:

    export MONGODB_URL="mongodb://localhost:27017/admin"
    export MYSQL_URL="root:password@tcp(127.0.0.1:3306)/mysql"

If you don't have the databases available, remove the database locusts from the
`locustfile`.

## Setup

 1. Clone this repo.
 2. `pip install -r requirements.txt`.
 3. Run the `prepare.py` script to populate Vault with random secrets.
 4. Run `locust` to start a test.
 
 
## Preparing Vault for the test

The `prepare.py` script fills Vault with a bunch of random secrets that are
then queried during the test. The paths are random strings of hex characters
with two levels, like this:

    fd/410a7adef1cd7ce6fbfaebc3b4eb49b9
    e3/c0a0bafa86e81e2b4b8775f9b9dacfcf
    fd/8f4293e2fd64cadda5f6cb936ff054e4
    
Each secret consists of a single key whose value is a string of random bytes.
The length of the string is controlled by the `--secret-size` parameter 
(default: 1024 bytes), and the number of secrets created is controlled by the
`--num-secrets` parameter (default: 1000).

The script assumes that the target Vault instance lives at 
http://localhost:8200. If this is not correct, use the `--host` or `-h` option
to specify the correct URL.  

The final argument to `prepare.py` must be a Vault token for authentication.
The token can instead be passed in the environment variable `TOKEN` if you 
prefer.

Example usage:

    TOKEN="72e7ff6e-8f44-5414-75a8-99d308649954" ./prepare.py --num-secrets=1000000 --host="http://localhost:8200"


## Running the test

Run the `locust` command to start an interactive web interface at 
http://localhost:8089. If you needed to use the `--host` parameter above, 
make sure you use it here too. The test will not start until you open the
web page and click the **Start Swarming** button.

If you'd prefer to run the test non-interactively, you can specify additional
command-line parameters along with `--no-web`.

For example, to start a test with 25 locusts (25 simulated users), starting 5
per second until all 25 are running:

    locust -H http://localhost:8200 -c 25 -r 5 --no-web


## What the test does

The test simulates several different patterns of access:

 1. Reading, writing, and listing secrets with the KV engine.
 2. Generating certificates from the PKI engine.
 3. Encrypting data via the Transit engine.
 4. Generating dynamic secrets from the MySQL, MongoDB, and TOTP engines.
 5. Authenticating via username/password and AppRole.
 
The tests are weighted so that 60% of the users are interacting with the KV
engine, 20% with the PKI engine, and 20% with the Transit engine. These weights
can be adjusted by changing the `weight` parameter in each of the files in
the `locusts` folder.

## Future enhancements

 - [x] Authentication
 - [x] Dynamic secret generation
 - [ ] Reports and analysis?
 