from ipalib import api, errors

class User(object):
    def __init__(self, args = {}):
        self.given_name = args.get("given_name", "")
        self.family_name = args.get("family_name", "")
        self.email = args.get("email", "")

    def isValid(self):
        """Check to see if the model is valid, before it is saved"""
        return self.given_name and self.family_name and self.email

    def save(self):
        """Save the model

        This method saves the newly constructed user to the backing store. If
        the model is invalid, the model will not be saved

        If there are validation errors, returns the error message. Otherwise
        returns None
        """
        error = None
        try:
            api.Command.stageuser_add(
                givenname=self.given_name, 
                sn=self.family_name,
                mail=self.email
            )
        except (errors.ValidationError, errors.RequirementError) as e:
            error = e.msg
        except AttributeError as e:
            print e
        return error
