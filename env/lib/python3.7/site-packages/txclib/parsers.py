# -*- coding: utf-8 -*-

import os
import sys

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from txclib.utils import get_version


MAPPING, MAPPINGREMOTE, MAPPINGBULK = (
    'mapping', 'mapping-remote', 'mapping-bulk'
)


def tx_main_parser():
    description = "This is the Transifex command line client which"\
                  " allows you to manage your translations locally and sync"\
                  " them with the master Transifex server.\nIf you'd like to"\
                  " check the available commands issue `%(prog)s help` or if"\
                  " you just want help with a specific command issue"\
                  " `%(prog)s help command`"
    version = get_version()
    parser = ArgumentParser(
        description=description, add_help=False
    )
    # parser.disable_interspersed_args()
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument(
        "-d", "--debug", action="store_true", dest="debug",
        default=False, help=("enable debug messages")
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", dest="quiet",
        default=False, help="don't print status messages to stdout"
    )
    parser.add_argument(
        "--root", action="store", dest="root_dir", type=str,
        default=None, help="change root directory (default is cwd)"
    )
    parser.add_argument(
        "--traceback", action="store_true", dest="trace", default=False,
        help="print full traceback on exceptions"
    )
    parser.add_argument(
        "--disable-colors", action="store_true", dest="color_disable",
        default=(os.name == 'nt' or not sys.stdout.isatty()),
        help="disable colors in the output of commands"
    )
    parser.add_argument(
        "command", action="store", help="TX command", nargs='?', default=None
    )
    return parser


def delete_parser():
    """Return the command-line parser for the delete command."""
    description = (
        "This command deletes translations for a "
        "resource in the remote server."
    )
    epilog = (
        "\nExamples:\n"
        "To delete a translation:\n"
        "$ tx delete -r project.resource -l <lang_code>\n\n"
        "To delete a resource:\n  $ tx delete -r project.resource\n"
    )
    parser = ArgumentParser(description=description, epilog=epilog,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument(
        "-r", "--resource", action="store", dest="resources", default=None,
        help="Specify the resource you want to delete (defaults to all)"
    )
    parser.add_argument(
        "-l", "--language", action="store", dest="languages",
        default=None, help="Specify the translation you want to delete"
    )
    parser.add_argument(
        "--skip", action="store_true", dest="skip_errors", default=False,
        help="Don't stop on errors."
    )
    parser.add_argument(
        "-f", "--force", action="store_true", dest="force_delete",
        default=False, help="Delete an entity forcefully."
    )
    return parser


def help_parser():
    """Return the command-line parser for the help command."""
    description = "Lists all available commands in the transifex command "\
        "client. If a command is\nspecified, the help page of the specific "\
        "command is displayed instead."

    parser = ArgumentParser(description=description)
    parser.add_argument("command", action="store", nargs='?', default=None,
                        help="One of the tx commands.")
    return parser


def init_parser():
    """Return the command-line parser for the init command."""
    description = (
        "This command initializes a new project for use with Transifex. It "
        "is recommended to execute this command in the top level directory "
        "of your project so that you can include all files under it in "
        "Transifex. If no path is provided, the current working directory "
        "will be used."
    )
    parser = ArgumentParser(description=description)
    parser.add_argument("--host", action="store", dest="host", default=None,
                        help="Specify a default Transifex host.")
    parser.add_argument("--user", action="store", dest="user", default=None,
                        help="Specify username for Transifex server.")
    parser.add_argument("--pass", action="store", dest="password",
                        default=None,
                        help="Specify password for Transifex server.")
    parser.add_argument(
        "--force-save",
        action="store_true",
        dest="save",
        default=False,
        help="Override .transifexrc file with the given credentials."
    )
    parser.add_argument(
        "--skipsetup",
        action="store_true",
        dest="skipsetup",
        default=False,
        help="Don't start tx config interactive wizard after setting up "
             "credentials."
    )
    parser.add_argument("--token", action="store", dest="token", default=None,
                        help="Specify an api token.\nYou can get one from"
                        " user's settings")
    parser.add_argument("--no-interactive", action="store_true",
                        dest="no_interactive", default=False,
                        help="Don't require user input.")
    parser.add_argument("path_to_tx", action="store", nargs='?', default=None,
                        help="Path to tx root folder.")
    return parser


def pull_parser():
    """Return the command-line parser for the pull command."""
    description = \
        "This command pulls all outstanding changes from the remote "\
        "Transifex server to the local repository. By default, only the "\
        "files that are watched by Transifex will be updated but if you "\
        "want to fetch the translations for new languages as well, use the "\
        "-a|--all option. (Note: new translations are saved in the .tx "\
        "folder and require the user to manually rename them and add then in "\
        "Transifex using the set_translation command)."
    parser = ArgumentParser(description=description)
    parser.add_argument("-l", "--language", action="store", dest="languages",
                        default=[], help="Specify which translations "
                        "you want to pull (defaults to all)")
    parser.add_argument("-r", "--resource", action="store", dest="resources",
                        default=[], help="Specify the resource for which you "
                        "want to pull the translations (defaults to all)")
    parser.add_argument("-a", "--all", action="store_true", dest="fetchall",
                        default=False, help="Fetch all translation files from "
                        "server (even new ones)")
    parser.add_argument("-s", "--source", action="store_true",
                        dest="fetchsource", default=False,
                        help="Force the fetching of the source file (default: "
                        "False)")
    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        default=False, help="Force download of translations "
                        "files.")
    parser.add_argument("--skip", action="store_true", dest="skip_errors",
                        default=False, help="Don't stop on errors. Useful "
                        "when pushing many files concurrently.")
    parser.add_argument("--disable-overwrite", action="store_false",
                        dest="overwrite", default=True,
                        help="By default transifex will fetch new translations"
                        " files and replace existing ones. Use this flag if"
                        " you want to disable this feature")
    parser.add_argument("--minimum-perc", action="store", type=int,
                        dest="minimum_perc", default=0,
                        help="Specify the minimum acceptable percentage of "
                        "a translation in order to download it.")
    parser.add_argument("--pseudo", action="store_true", dest="pseudo",
                        default=False, help="Apply this option to download "
                        "a pseudo file.")
    parser.add_argument(
        "--mode", action="store", dest="mode", help=(
            "Specify the mode of the translation file to pull (e.g. "
            "'reviewed'). See https://docs.transifex.com/client/pull/ "
            "for available values."
        )
    )
    parser.add_argument(
        "-b", "--branch", action="store", dest="branch",
        default=None, nargs="?", const='-1',
        help=("Pull for a specific branch. If no branch is specified current "
              "branch will be used if exists.")
    )
    parser.add_argument("-x", "--xliff", action="store_true", dest="xliff",
                        default=False, help="Apply this option to download "
                        "file as xliff.")
    parser.add_argument("--parallel", action="store_true", default=False,
                        help="perform push/pull requests in parallel")
    parser.add_argument("--no-interactive", action="store_true",
                        dest="no_interactive", default=False,
                        help="Don't require user input.")
    return parser


def push_parser():
    """Return the command-line parser for the push command."""
    description = \
        "This command pushes all local files that have been added to "\
        "Transifex to the remote server. All new translations are merged "\
        "with existing ones and if a language doesn't exists then it gets "\
        "created. If you want to push the source file as well (either "\
        "because this is your first time running the client or because "\
        "you just have updated with new entries), use the -f|--force option. "\
        "By default, this command will push all files which are watched by "\
        "Transifex but you can filter this per resource or/and language. "
    parser = ArgumentParser(description=description)
    parser.add_argument("-l", "--language", action="store", dest="languages",
                        default=None, help="Specify which translations you "
                        "want to push (defaults to all)")
    parser.add_argument("-r", "--resource", action="store", dest="resources",
                        default=None, help="Specify the resource for which "
                        "you want to push the translations (defaults to all)")
    parser.add_argument("-f", "--force", action="store_true",
                        dest="force_creation", default=False,
                        help="Push source files without checking modification "
                        "times.")
    parser.add_argument("--skip", action="store_true", dest="skip_errors",
                        default=False, help="Don't stop on errors. "
                        "Useful when pushing many files concurrently.")
    parser.add_argument("-s", "--source", action="store_true",
                        dest="push_source", default=False,
                        help="Push the source file to the server.")

    parser.add_argument("-t", "--translations", action="store_true",
                        dest="push_translations", default=False,
                        help="Push the translation files to the server")
    parser.add_argument("--no-interactive", action="store_true",
                        dest="no_interactive", default=False,
                        help="Don't require user input when forcing a push.")
    parser.add_argument("-x", "--xliff", action="store_true", dest="xliff",
                        default=False, help="Apply this option to upload "
                        "file as xliff.")
    parser.add_argument(
        "-b", "--branch", action="store", dest="branch",
        default=None, nargs="?", const='-1',
        help=("Pull for a specific branch. Default is current"
              "branch if exists.")
    )
    parser.add_argument("--parallel", action="store_true", default=False,
                        help="perform push/pull requests in parallel")
    return parser


def set_main_parser():
    main_parser = ArgumentParser(add_help=False)
    main_parser.add_argument(
        "-r", "--resource", action="store", dest="resource", required=True,
        help="Specify the slug of the resource that you're setting up "
        "(This must be in the following format: `project_slug.resource_slug`)."
    )
    main_parser.add_argument(
        "--source", action="store_true", dest="is_source", default=False,
        help="Specify that the given file is a source file."
    )
    main_parser.add_argument("-l", "--language", action="store",
                             dest="language", default=None,
                             help="Specify the source language of the "
                             "resource")
    main_parser.add_argument("-t", "--type", action="store", dest="i18n_type",
                             help=("Specify the i18n type of the resource(s). "
                                   "This is only needed, if the resource(s) "
                                   "does not exist yet in Transifex. For a "
                                   "list of available i18n types, see "
                                   "http://docs.transifex.com/formats/"
                                   ))
    return main_parser


def set_extra_parser():
    extra_parser = ArgumentParser(add_help=False)
    extra_parser.add_argument("--minimum-perc", action="store",
                              dest="minimum_perc",
                              help=("Specify the minimum acceptable "
                                    "percentage of a translation in "
                                    "order to download it."))
    extra_parser.add_argument(
        "--mode", action="store", dest="mode", help=(
            "Specify the mode of the translation file to pull (e.g. "
            "'reviewed'). See https://docs.transifex.com/client/pull/ "
            "for the available values."
        )
    )
    return extra_parser


def set_parser(subparser=False, is_legacy=False):
    """Return the command-line parser for the config command."""
    set_warning = ""
    if is_legacy:
        set_warning = "Warning: This command will be deprecated in a future "\
            "release of the client. \nYou should use the `tx config` command."\
            " For more information, visit \n"\
            "https://docs.transifex.com/client/config/.\n\n"

    description = set_warning + "This command can be used to create a mapping"\
        " between files and projects either\nusing local files or using files"\
        " from a remote Transifex server."
    epilog = "\nSubcommands:\n"\
        "    {autolocal}\n"\
        "    {autoremote}\n"\
        "    {bulk}\n\n"\
        "Examples:\n"\
        "To set the source file:\n\
        $ %(prog)s -r project.resource --source -l en <file>\n\n"\
        "To set a single translation file:\n\
        $ %(prog)s -r project.resource -l de <file>\n".format(
        autolocal=MAPPING, autoremote=MAPPINGREMOTE, bulk=MAPPINGBULK
    )
    auto_local_description = "This command can be used to create a mapping "\
                             "for a local file using the path expression "\
                             "argument to automatically detect source and "\
                             "translation files."
    auto_remote_description = "This command can be used to create mappings "\
                              "for resources existing on the remote server."
    auto_local_epilog = "\nExamples:\n"\
        "To automatically detect and assign the source file and translations:"\
        "\n $ %(prog)s -r project.resource 'expr' --source-language en\n\n"\
        "To set a specific file as a source and auto detect translations:\n"\
        " $ %(prog)s -r project.resource 'expr' --source-language en "\
        "--source-file <file>\n\n"
    auto_remote_epilog = "\nExamples:\n"\
        "To set a remote resource/project:\n"\
        "  $ %(prog)s <transifex-url>\n"
    bulk_description = "This command can be used to create a mapping between "\
        "files and projects for multiple resources at once, using local files."
    bulk_epilog = "\nExamples:\n"\
        "To set a series of HTML source files that reside inside locale/:\n"\
        " $ %(prog)s -p project --source-language en --type HTML"\
        " -f '.html' --source-file-dir locale\n\n"\
        "To set a series of KEYVAlUEJSON source files that reside " \
        "inside locale/ but exclude files in locale/es/ and locale/jp/:\n"\
        " $ %(prog)s -p project --source-language en --type KEYVAlUEJSON " \
        "-f '.json' --source-file-dir locale -i es -i jp\n\n"

    main_parser = set_main_parser()
    extra_parser = set_extra_parser()
    if subparser:
        parents = []
    else:
        parents = [main_parser, extra_parser]

    prog = 'tx config'
    if is_legacy:
        prog = 'tx set'
    parser = ArgumentParser(
        prog=prog, description=description, epilog=epilog,
        parents=parents, formatter_class=RawDescriptionHelpFormatter
    )
    # return parser that should be used when set is run without a subcommand
    if not subparser:
        # These arguments are valid only for the bare command and not for the
        # subcommands
        parser.add_argument(
            "filename", action="store",
            help="The source or translation file of the resource."
        )
        parser.add_argument("--auto-local", action="store_true",
                            dest="local", default=False,
                            help="Alias of {} subcommand".format(MAPPING))
        parser.add_argument(
            "--auto-remote", action="store_true", dest="local",
            default=False, help="Alias of {} subcommand".format(MAPPINGREMOTE)
        )
        return parser

    # SUBPARSERS
    # auto-local subparser
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')
    auto_local_parser = subparsers.add_parser(
        MAPPING, prog="{} {}".format(prog, MAPPING),
        parents=[main_parser, extra_parser], epilog=auto_local_epilog,
        description=auto_local_description,
        formatter_class=RawDescriptionHelpFormatter,
        help="Use to auto configuring local project."
    )
    auto_local_parser.add_argument(
        "-s", "--source-language", action="store", dest="source_language",
        default=False, required=True, help="Source language of the resource.")
    auto_local_parser.add_argument(
        "-f", "--source-file", action="store", dest="source_file",
        default=None, help="Specify the source file of a resource.")
    auto_local_parser.add_argument(
        "--execute", action="store_true", dest="execute", default=False,
        help="Execute commands.")
    auto_local_parser.add_argument(
        "--expression", action="store",
        help=("Expression defining where translation files should be saved. "
              "Default value is: "
              "'locale/<lang>/{filepath}/{filename}{extension}'")
    )
    auto_local_parser.add_argument(
        "expression_legacy", action="store", nargs="?",
        help="DEPRECATED: Use --expression instead."
    )

    # auto-remote subparser
    auto_remote_parser = subparsers.add_parser(
        MAPPINGREMOTE, prog="{} {}".format(prog, MAPPINGREMOTE),
        parents=[extra_parser], description=auto_remote_description,
        epilog=auto_remote_epilog, formatter_class=RawDescriptionHelpFormatter,
        help="Use to configure remote files from Transifex server."
    )
    auto_remote_parser.add_argument("project_url", action="store",
                                    help="Url of Transifex project.")
    # auto-bulk subparser
    auto_bulk_parser = subparsers.add_parser(
        MAPPINGBULK, parents=[extra_parser],
        prog="{} {}".format(prog, MAPPINGBULK),
        description=bulk_description, epilog=bulk_epilog,
        help="Use to auto configure multiple local files.",
        formatter_class=RawDescriptionHelpFormatter
    )
    auto_bulk_parser.add_argument(
        "-p", "--project", action="store", dest="project", default=None,
        required=True,
        help="Specify the slug of the project that you're setting up."
    )
    auto_bulk_parser.add_argument(
        "--source-file-dir", action="store", dest="source_file_dir",
        default=None, required=True, help=(
            "Directory to find source files to be mapped. "
            "Example: locale/en/"
        )
    )
    auto_bulk_parser.add_argument(
        "-t", "--type", action="store", dest="i18n_type",
        help="Specify the i18n type of the resources. This is only needed, "
             "if the resource(s) does not exist yet in Transifex. For a list "
             "of available i18n types, see http://docs.transifex.com/formats/"
    )
    auto_bulk_parser.add_argument(
        "-s", "--source-language", action="store", dest="source_language",
        default=None, required=True,
        help="Specify the source language of the resources ")
    auto_bulk_parser.add_argument(
        "-f", "--file-extension", action="store", dest="file_extension",
        default=None, required=True,
        help="File extension of files to be mapped.")
    auto_bulk_parser.add_argument(
        "-i", "--ignore-dir", action="append", dest="ignore_dirs", default=[],
        help="Directory to ignore while looking for source "
             "files. Can be called multiple times. Example: `-i es -i fr`.'.")
    auto_bulk_parser.add_argument(
        "--expression", action="store",
        default='locale/<lang>/{filepath}/{filename}{extension}',
        help="Expression defining where translation files should be saved. "
             "Default value is: "
             "'locale/<lang>/{filepath}/{filename}{extension}'"
    )
    auto_bulk_parser.add_argument(
        "--execute", action="store_true", dest="execute", default=False,
        help="Execute commands.")
    return parser


def status_parser():
    """Return the command-line parser for the status command."""
    description = "Prints the status of the current project by reading the "\
                  "data in the configuration file."
    parser = ArgumentParser(description=description)
    parser.add_argument("-r", "--resource", action="store", dest="resources",
                        default=[], help="Specify resources")
    return parser


def parse_csv_option(option):
    """Return a list out of the comma-separated option or an empty list."""
    if option:
        return option.split(',')
    else:
        return []
