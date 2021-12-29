#!/usr/bin/env python3

import os, getopt, sys, shutil, getpass, subprocess

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
options = "hcdsi:"

# Long options
long_options = ["help", "connect", "disconnect", "status", "install="]

_USERNAME = os.getenv("SUDO_USER") or os.getenv("USER")

_HOME = os.path.expanduser('~'+_USERNAME)

SCRIPT_FILE_PATH = os.path.realpath(__file__)

CONFIG_FILE_PATH = f"{_HOME}/.config/ov3/"

DEFAULT_OVPN_PATH = f"{CONFIG_FILE_PATH}default.ovpn"

OV3_SYMLINK_PATH = "/usr/local/bin/ov3"

# Help Message
HELP = """
ov3: Simple OpenVPN3 Operations
    Command line interface to manage basic personal 
    OpenVPN 3 sessions.

    Available Commands:
    -h | --help                             - This help screen
    -c | --connect <CONF_FILE_PATH>         - Connects to the VPN configuration file
                                              Default {}
    -d | --disconnect <SESSION_PATH>        - Disconnect from the current VPN session
    -s | --status                           - Shows the current VPN sessions
    -i | --install [CONF_FILE_PATH]         - Puts your ovpn file into {} and installs script
""".format(DEFAULT_OVPN_PATH, DEFAULT_OVPN_PATH)

def disconnect(): 
    output = os.popen('openvpn3 sessions-list | grep Path').readline()

    print(str(output).strip())

    if output is None or output == "":
        return "No sessions available"
    else:
        if isinstance(output, str) : 
            output = output.strip().replace('Path: ', '').replace('\n', '')
            # print(output)
            outputDisconnect = os.popen('openvpn3 session-manage --disconnect --session-path ' + output).readlines()

            return outputDisconnect
        else: 
            return "Output can not be processed!"

def connect(): 
    return os.popen('openvpn3 session-start --config {}'.format(DEFAULT_OVPN_PATH)).readlines()

def install(path): 
    print(f"Copying {path} to {CONFIG_FILE_PATH}")

    if path is None:
        raise Exception("The path of ovpn file can not be empty")

    if not os.path.isfile(path):
        raise FileExistsError("File cannot be found")

    if not path.endswith('.ovpn'):
        raise Exception("File's extension should be ovpn")
    
    if not os.path.exists(CONFIG_FILE_PATH):
        os.makedirs(CONFIG_FILE_PATH)

    print(shutil.copyfile(path, DEFAULT_OVPN_PATH))

    if not os.path.isfile(OV3_SYMLINK_PATH):
        print("ov3 is installing...\n")
        sudo_password = getpass.getpass(prompt='sudo password: ')
        p = subprocess.Popen(
                ["sudo", 'ln', '-s', SCRIPT_FILE_PATH, OV3_SYMLINK_PATH], 
                stderr=subprocess.PIPE, 
                stdout=subprocess.PIPE,  
                stdin=subprocess.PIPE
            )

        try:
            out, err = p.communicate(sudo_password.encode(), timeout=50)
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
            print (HELP)
             
        elif currentArgument in ("-c", "--connect"):
            print ("\n".join(connect()))
             
        elif currentArgument in ("-d", "--disconnect"):
            a = "".join(disconnect())
            print(f"{a}")

        elif currentArgument in ("-i", "--install"):
            install(currentValue)

        elif currentArgument in ("-s", "--status"):
            status()

except getopt.error as err:
    # output error, and return with an error code
    print (bcolors.FAIL + str(err) + bcolors.ENDC)
 
