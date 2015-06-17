from email.mime.multipart import MIMEMultipart
from email.MIMEText import MIMEText
# import smtplib

from jinja2 import Environment, FileSystemLoader

class Mailer(object):
    env = Environment(loader=FileSystemLoader('mailers/templates'))

    def __init__(self):
        self.subject = "FreeIPA Community Portal: Notice"
        pass

    def mail(self):
        """Send the mail"""
        contents = self._build(self.template, self.template_opts)
        self._send(contents)

    def _build(self, template, template_opts):
        msg = MIMEMultipart()
        # TODO: change this to be configurable
        msg['From'] = 'derny@redhat.com'
        msg['To'] = 'derny@redhat.com'
        msg['Subject'] = self.subject
        body = self.env.get_template(template).render(template_opts)
        msg.attach(MIMEText(body, 'plain'))
        return msg

    def _send(self, contents):
        # TODO: Actually send email
        print contents
