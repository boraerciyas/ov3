#!/usr/bin/env python3

import os
import getopt
import sys
import shutil
import getpass
import subprocess


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

# Options
options = "hcdsil"

# Long options
long_options = ["help", "connect", "disconnect", "status", "install", "list"]

_USERNAME = os.getenv("SUDO_USER") or os.getenv("USER")

_HOME = os.path.expanduser('~'+_USERNAME)

SCRIPT_FILE_PATH = os.path.realpath(__file__)

CONFIG_FILE_PATH = f"{_HOME}/.config/ov3/"

FILENAMES_FILE_PATH = f"{CONFIG_FILE_PATH}.confignames"

DEFAULT_OVPN_PATH = f"{CONFIG_FILE_PATH}default.ovpn"

OV3_SYMLINK_PATH = "/usr/local/bin/ov3"

# Help Message
HELP = """
ov3: Simple OpenVPN3 Operations
    Command line interface to manage basic personal 
    OpenVPN 3 sessions.

    Available Commands:
    -h | --help                                               - This help screen
    -c | --connect <CONFIG_NUMBER>                            - Connects to the VPN configuration file 
                                                                (optionally with the number of 
                                                                listed(--list) configs)
                                                                Default {}
    -d | --disconnect <SESSION_PATH>                          - Disconnect from the current VPN session
    -s | --status                                             - Shows the current VPN sessions
    -i | --install [CONF_FILE_PATH]  [CONF_FILE_PATH2]        - Puts your ovpn file into {} and 
                                                                installs script
    -l | --list                                               - Lists installed config files.
""".format(DEFAULT_OVPN_PATH, DEFAULT_OVPN_PATH)


def disconnect():
    output = os.popen('openvpn3 sessions-list | grep Path').readline()

    print(str(output).strip())

    if output is None or output == "":
        return "No sessions available"
    else:
        if isinstance(output, str):
            output = output.strip().replace('Path: ', '').replace('\n', '')
            # print(output)
            outputDisconnect = os.popen(
                'openvpn3 session-manage --disconnect --session-path ' + output).readlines()

            return outputDisconnect
        else:
            return "Output can not be processed!"


def connect(values=None):

    disconnect()
    name = DEFAULT_OVPN_PATH
    if values is not None and type(values) is type([]) and len(values) == 1 and int(values[0]) > 1:
        nameTmp = f"{CONFIG_FILE_PATH}default{(int(values[0]) - 1)}.ovpn"
        if os.path.isfile(nameTmp):
            name = nameTmp
    print("Connecting to {}".format(name))
    return os.popen('openvpn3 session-start --config {}'.format(name)).readlines()


def install(pathArr):

    if len(pathArr) == 0:
        print(bcolors.FAIL +
              "At least one config file path should be given." + bcolors.ENDC)
        exit()

    if not os.path.exists(CONFIG_FILE_PATH):
        os.makedirs(CONFIG_FILE_PATH)
        try:
            f = open(FILENAMES_FILE_PATH, "w+")
            f.close()
        except getopt.error as err:
            # output error, and return with an error code
            print(bcolors.FAIL + str(err) + bcolors.ENDC)

    for idx, path in enumerate(pathArr):

        if path is None:
            raise Exception("The path of ovpn file can not be empty")

        if not os.path.isfile(path):
            raise FileExistsError("File cannot be found")

        if not path.endswith('.ovpn'):
            raise Exception("File's extension should be ovpn")

        name = DEFAULT_OVPN_PATH
        if idx != 0:
            name = f"{CONFIG_FILE_PATH}default{idx}.ovpn"
        else:
            filenames_file = open(FILENAMES_FILE_PATH, "w").close()

        print(f"Copying {path} to {name}")

        filename = os.path.basename(path)
        filenames_file = open(FILENAMES_FILE_PATH, "a")
        filenames_file.write(str(idx + 1) + "." + filename + '\n')
        filenames_file.close()

        print(shutil.copyfile(path, name))

    # if not os.path.isfile(OV3_SYMLINK_PATH):
    print("ov3 is installing...\n")
    sudo_password = getpass.getpass(prompt='sudo password: ')
    p = subprocess.Popen(
        ["sudo", 'ln', '-sf', SCRIPT_FILE_PATH, OV3_SYMLINK_PATH],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )

    try:
        out, err = p.communicate(sudo_password.encode(), timeout=60)
        if err is not None and str(err) != "b''":
            print(bcolors.FAIL + err + bcolors.ENDC)
            exit()

    except subprocess.TimeoutExpired:
        p.kill()

    print(bcolors.OKGREEN + "ov3 is successfully installed" + bcolors.ENDC)


def status():
    output = os.popen('openvpn3 sessions-list').readlines()
    a = "".join(output)
    print(f"{a}")


def list():
    output = os.popen(f"cat {FILENAMES_FILE_PATH}").readlines()
    a = "".join(output)
    print(f"{a}")


try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)

    # Checks arguments
    if len(arguments) == 0:
        print(HELP)
        exit()

    elif len(arguments) > 1:
        print(bcolors.FAIL + "This command only accepts 1 option" + bcolors.ENDC)
        exit()

    # checking each argument
    for currentArgument, currentValue in arguments:

        if currentArgument in ("-h", "--help"):
            print(HELP)

        elif currentArgument in ("-c", "--connect"):
            print("\n".join(connect(values)))

        elif currentArgument in ("-d", "--disconnect"):
            a = "".join(disconnect())
            print(f"{a}")

        elif currentArgument in ("-i", "--install"):
            install(values)

        elif currentArgument in ("-s", "--status"):
            status()

        elif currentArgument in ("-l", "--list"):
            list()

except getopt.error as err:
    # output error, and return with an error code
    print(bcolors.FAIL + str(err) + bcolors.ENDC)
