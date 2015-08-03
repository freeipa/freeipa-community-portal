# Setting up a development environment

The application should run in a development environment without trouble. 
Install the dependencies described in deploy.md except the application itself,
and then do

    pip install -e .

in the root of the tree. This should install a local, editable copy of the app,
and put all of the configuration files and assets where they are expected.

You will also have to create a key file for the captcha. Because this is 
development, you can probably just do

    touch key

and the empty file will work. There just needs to be a key file available to
read.

You can configure exactly where the application spews its files by editing the
freeipa_community_portal_dev.ini file and plugging in values that make you 
happy.

To run the application in-tree, do

    python freeipa_community_portal/app.py
