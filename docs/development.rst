Setting up a development environment
====================================

The application should run in a development environment without trouble. 
Install the dependencies described in deploy.md except the application itself,
and then do::

    pip install -e .

in the root of the tree. This should install a local, editable copy of the app,
and put all of the configuration files and assets where they are expected.

You can configure exactly where the application spews its files by editing the
freeipa_community_portal_dev.ini file in freeipa_community_portal/conf and
plugging in values that make you happy. By default the development server uses
var/ in your current working directory to store its database and captcha key
file. The directory, sqlite database and key files are created automatically.

Before you run the app, even in tree, you should kinit as a user with 
sufficient permissions as outlined in the deployment doc. You can also drop
a client keytab in your var/ directory.

To run the application in-tree, do::

    python -m freeipa_community_portal

On an IPA server Dogtag PKI is already occupying port 8080. For that reason
the development server listens on port 10080 on localhost. You can change
the port in freeipa_community_port/__main__.py if the port is already used
on your machine.
