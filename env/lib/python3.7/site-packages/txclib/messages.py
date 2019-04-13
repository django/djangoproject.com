# -*- coding: utf-8 -*-
init_intro = """
 _____                    _  __
|_   _| __ __ _ _ __  ___(_)/ _| _____  __
  | || '__/ _` | '_ \/ __| | |_ / _ \ \/ /
  | || | | (_| | | | \__ \ |  _|  __/>  <
  |_||_|  \__,_|_| |_|___/_|_|  \___/_/\_\\


Welcome to the Transifex Client! Please follow the instructions to
initialize your project.
"""
init_initialized = "It seems that this project is already initialized."

init_reinit = "Do you want to delete it and reinit the project?"
init_host = "Transifex instance"

token_instructions = """
Transifex Client needs a Transifex API token to authenticate.
If you don’t have one yet, you can generate a token at
https://www.transifex.com/user/settings/api/.
"""

token_validation_failed = """
Error: Invalid token. You can generate a new token at
https://www.transifex.com/user/settings/api/.
"""
update_txrc = "Overwrite credentials in .transifexrc?"

token_msg = "[?] Enter your api token: "

running_tx_set = "Running tx config command for you..."


create_project_instructions = """To create a new project, head to {host}/{org}/add.
Once you’ve created the project, you can continue.
"""

TEXTS = {
    "source_file": {
        "description": ("""
The Transifex Client syncs files between your local directory and Transifex.
The mapping configuration between the two is stored in a file called .tx/config
in your current directory. For more information, visit
https://docs.transifex.com/client/config/.
"""),
        "error": ("No file was found in that path. Please correct the path "
                  "or make sure a file exists in that location."),
        "message": "[?] Enter the path to your local source file: "
    },
    "expression": {
        "description": ("""
Next, we’ll need a path expression pointing to the location of the
translation files (whether they exist yet or not) associated with
the source file ‘{source_file}’. You should include <lang> as a
wildcard for the language code.
"""),
        "error": "The path expression doesn’t contain the <lang> placeholder.",
        "message": "[?] Enter a path expression: "
    },
    "formats": {
        "description": ("""
Here’s a list of the supported file formats. For more information,
check our docs at https://docs.transifex.com/formats/.
"""),
        "error": "Error: Invalid choice. Enter the number corresponding with the format you wish to select.",
        "empty": "No formats found for this file extension. For more information, check our docs at https://docs.transifex.com/formats/",
        "message": "[?] Select the file format type [{r}]: ",
    },
    "organization": {
        "description": ("""
You’ll now choose a project in a Transifex organization to sync with your
local files. You belong to these organizations in Transifex:
"""),
        "error": ("""
Error: Invalid choice. Enter the number corresponding with the organization you wish to select."""),
        "message": "[?] Select the organization to use [{r}]: ",
    },
    "projects": {
        "description": ("""We found these projects in your organization."""),
        "error": """
Error: Invalid choice. Enter the number corresponding with the project you wish to select.""",
        "message": "[?] Select the project to use [{r}]: ",
    },
}

epilog = """
The Transifex Client syncs files between your local directory and Transifex.
The mapping configuration between the two is stored in a file called
.tx/config in your current directory. For more information, visit
https://docs.transifex.com/client/config/.
"""

final_instr = """
Here’s the content of the .tx/config file that was created:

    [{resource}]
    source_file = {source_file}
    file_filter = {file_filter}
    source_lang = {source_lang}
    type = {type}

You could also have generated the same configuration by running a single command like:

    tx config mapping -r {resource} -f {source_file} -s {source_lang} -t {type} '{file_filter}'

To learn more about the Config command, visit https://docs.transifex.com/client/config.

Here are some useful commands for your next steps:

Upload source files to Transifex:
    tx push  --source

Download translation files from Transifex once translations are done:
    tx pull --all
"""
