from freeipa_community_portal.mailers.mailer import Mailer
class SignUpMailer(Mailer):
    def __init__(self, user):
        super(self.__class__, self).__init__()
        self.user = user
        self.subject = "FreeIPA Community Portal: A user has signed up"
        self.template = "sign_up_email.txt"
        self.template_opts = {"user": self.user}
    
