# ov3
Easy common OpenVPN3 operations


## Install

ov3 requires [Python3](https://www.python.org/download/releases/3.0/) and [OpenVPN3](https://openvpn.net/cloud-docs/openvpn-3-client-for-linux/) to run.

```sh
git clone https://github.com/boraerciyas/ov3.git
cd ov3
python3 ov3.py -i /path/to/config/file.ovpn
```

## Usage
Command line interface to manage basic personal 
    OpenVPN 3 sessions.

    Available Commands:
    -h | --help                                            - This help screen
    -c | --connect <CONFIG_NUMBER>                         - Connects to the VPN configuration file 
                                                             (optionally with the number of 
                                                            listed(--list) configs)
    -d | --disconnect <SESSION_PATH>                       - Disconnect from the current VPN session
    -s | --status                                          - Shows the current VPN sessions
    -i | --install [CONFIG_FILE_PATH] [CONF_FILE_PATH2]    - Installs script
    -l | --list                                            - Lists installed config files.


## License

MIT