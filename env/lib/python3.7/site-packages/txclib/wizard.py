import os

from slugify import slugify
from txclib import messages
from txclib import utils
from txclib.api import Api
from txclib.project import Project
from txclib.log import logger
from six.moves import input


COLOR = "CYAN"

try:
    import readline
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
except ImportError:
    pass


def validate_source_file(path):
    return os.path.isfile(os.path.abspath(path))


def validate_expression(expression):
    return '<lang>' in expression


def validate_int(choice, length):
    try:
        choice = int(choice)
    except ValueError:
        return False
    return 0 < choice <= length


def choice_prompt(l, key):
    """
    l: A list of tuples (key, display_value) with the valid choices
    key: one of 'formats', 'organizations', 'projects'
    returns the key of the selected choice
    """
    a = "\n".join(["  {}. {}".format(i+1, f[1])
                   for i, f in enumerate(l)])
    a = a + "\n"
    print(a)

    choice = ''
    first_time = True
    r = '1' if len(l) == 1 else '1-{}'.format(len(l))

    while not validate_int(choice, len(l)):
        if not first_time:
            print(messages.TEXTS[key]["error"])
        choice = input(utils.color_text(
            messages.TEXTS[key]['message'].format(r=r), COLOR))
        first_time = False
    return l[int(choice) - 1][0]


def input_prompt(key, validation_method):
    user_input = ''
    first_time = True
    while not validation_method(user_input):
        if not first_time:
            print(messages.TEXTS[key]['error'])

        user_input = input(
            utils.color_text(messages.TEXTS[key]['message'], COLOR))
        first_time = False
    return user_input


class Wizard(object):

    def __init__(self, path_to_tx):
        p = Project(path_to_tx)
        self.host = p.config.get('main', 'host')
        username, token_or_password = p.getset_host_credentials(
            self.host, only_token=True)

        self.api = Api(username=username, password=token_or_password,
                       host=self.host, path_to_tx=p.txrc_file)

    def get_organizations(self):
        try:
            organizations = self.api.get('organizations')
        except Exception as e:
            logger.error(e)
            raise

        # return org list sorted by name
        return sorted(
            [(o['slug'], o['name']) for o in organizations],
            key=lambda x: x[1]
        )

    def get_projects_for_org(self, organization):
        try:
            projects = self.api.get('projects', organization=organization)
        except Exception as e:
            logger.error(e)
            raise

        # return project list sorted by name
        return sorted(
            [p for p in projects if not p['archived']],
            key=lambda x: x['name']
        )

    def get_formats(self, filename):
        _, extension = os.path.splitext(filename)
        try:
            formats = self.api.get('formats')
        except Exception as e:
            logger.error(e)
            raise

        def display_format(v):
            return '{} - {}'.format(v['description'], v['file-extensions'])

        formats = [(k, display_format(v)) for k, v in formats.items()
                   if extension in v['file-extensions']]
        if not formats:
            raise Exception(messages.TEXTS['formats']['empty'])
        return sorted(formats, key=lambda x: x[0])

    def run(self):
        """
        Runs the interactive wizard for `tx set` command and populates the
        parser's options with the user input. Options `local` and `execute`
        are by default True when interactive wizard is run.

        Returns: the options dictionary.
        """

        TEXTS = messages.TEXTS

        print(TEXTS['source_file']['description'])
        source_file = input_prompt('source_file', validate_source_file)

        print(
            TEXTS['expression']['description'].format(source_file=source_file)
        )
        expression = input_prompt('expression', validate_expression)

        formats = self.get_formats(os.path.basename(source_file))
        print(TEXTS['formats']['description'])
        i18n_type = choice_prompt(formats, 'formats')

        organizations = self.get_organizations()
        print(TEXTS['organization']['description'])
        org_slug = choice_prompt(organizations, 'organization')

        projects = []
        first_time = True
        create_project = ("tx:new_project",
                          "Create new project (show instructions)...")
        project = None
        while not project:
            if not first_time:
                retry_message = "Hit Enter to try selecting a project again: "
                input(utils.color_text(retry_message, COLOR))

            projects = self.get_projects_for_org(org_slug)
            p_choices = [(p['slug'], p['name']) for p in projects]
            p_choices.append(create_project)
            if projects:
                print(TEXTS['projects']['description'])
            else:
                print("We found no projects in this organization!")
            first_time = False
            project_slug = choice_prompt(p_choices, 'projects')

            if project_slug == 'tx:new_project':
                print(messages.create_project_instructions.format(
                    host=self.host, org=org_slug
                ))
            else:
                project = [p for p in projects
                           if p['slug'] == project_slug][0]
                source_language = project['source_language']['code']

        resource_slug = slugify(os.path.basename(source_file))
        resource = '{}.{}'.format(project_slug, resource_slug)

        options = {
            'source_file': source_file,
            'expression': expression,
            'i18n_type': i18n_type,
            'source_language': source_language,
            'resource': resource,
        }
        return options
