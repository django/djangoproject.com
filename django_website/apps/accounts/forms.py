from registration.forms import RegistrationFormUniqueEmail

class RegistrationForm(RegistrationFormUniqueEmail):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        del self.fields["tos"]    