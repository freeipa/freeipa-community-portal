FreeIPA Community Portal
========================

The FreeIPA Community Portal is a web frontend for FreeIPA that allows
anonymous users to interact with FreeIPA without authenticating. It is designed
for users in communities with a public FreeIPA setup, where administrators may
be volunteers or geographically dispersed, and where helpdesk-like setups
aren't feasible 

Currently, the FreeIPA Community Portal has two features: self-service
registration, and self-service password reset. Both of these features
previously required emailing an administrator.

Self-Service User Registration
------------------------------

The self-service registration workflow is very simple. The user is presented a
form into which they can enter basic biographical information, i.e. name, email
address, and username. The user also fills out the answer to a captcha. The
form is sent to the server and checked for validity. 

If the form is not valid, the user is sent back to the form with all the fields
filled as the user submitted them (except the captcha) and displayed an error
message explaining what has gone wrong. If the form is valid, the user is sent
to a completion page informing them that their sign-up will be reviewed.

All other portions of the workflow (user's first sign in, sign up approval,
etc.) take place inside the existing IPA WebUI and are outside of the scope of
this application.

Self-Service Password Reset
---------------------------

The self-service password reset workflow is marginally more complicated. It
consists of two main portions.

In the first part, the user navigates to a page to request a reset. The user is
presented with a form prompting a username and a captcha. The user submits the
form and it is checked for the presence of text in the username and the
correctness of the captcha. If the username field is blank or the captcha is
incorrect, the user is sent back to the page with a message explaining the
error. Regardless of whether a username exists, the user is sent to a
completion page informing them to check their email. At this point, an email
with the username and a token is sent to the user.

The user is then directed to page with a form to input the username requesting
the password reset and the token that arrived in the email. The user inputs the
username and token (or clicks a link provided in the email, which pre-fills the
form for the user) and submits the form. If the username and token match, the
user's password is changed in the IPA system to a random string of characters.
The user is then sent to a new page which displays this temporary password and
explains that their password has been changed, that this is the only chance to
view the password, and if this temporary password is lost before first login,
another password reset will have to be initiated. The user immediately
navigates to the WebUI and logs in with this temporary password.

If the username has not requested a password reset, if the token for the
username is over three days old, or if the token does not coorespond to the
username, the user is sent to an error page. The user is informed that one of
these errors has occurred, but not which error in particular, and that if they
entered the correct username but an incorrect token, the old token has been
expired and they must restart the process. The user is not informed what
specific error has occurred, to avoid using the password reset feature to probe
for the existance of usernames. 

More Information
----------------

A more technical guide to the workings of the Community Portal can be found at
these pages:

http://www.freeipa.org/page/V4/Community_Portal
http://www.freeipa.org/page/V4/Self_Service_Password_Reset
