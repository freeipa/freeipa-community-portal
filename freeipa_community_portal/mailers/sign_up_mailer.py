from mailer import Mailer
class SignUpMailer(Mailer):
    def __init__(self, user):
        self.user = user
        self.subject = "FreeIPA Community Portal: A user has signed up"
        self.template = "sign_up_email.txt"
        self.template_opts = {"user": self.user}
    
