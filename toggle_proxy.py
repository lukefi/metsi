import sys
from colorama import Fore
import subprocess

PROXY_ADDRESS = "http://suoja-proxy.vyv.fi:8080"

config_commands = {
    "git":{
        "name": "http.proxy",
        "base_command":["git", "config", "--global"],
        "list": "--list",
        "add": "--add",
        "remove":"--unset"
    },
    "pip":{
        "name": "global.proxy",
        "base_command":["pip", "config"],
        "list": "list",
        "add": "set",
        "remove":"unset"
    }
}

subprocess_args = {"capture_output": True, "shell":True, "encoding":"utf8"}

def proxy_on():
    for key in config_commands.keys():
        config = config_commands[key]
        base_command = config["base_command"]
        listing_command = base_command + [config["list"]]
        out = subprocess.run(listing_command, **subprocess_args)
        if out.returncode == 0:
            config_listing = out.stdout
            if config["name"] not in config_listing:
                setting_command = base_command + [config["add"], config["name"], PROXY_ADDRESS]
                set_pxy = subprocess.run(setting_command, **subprocess_args)
                if set_pxy.returncode != 0:
                    raise
                else:
                    print(f"Proxy was turned {Fore.GREEN + 'ON' + Fore.RESET} in {key} config.")
            else:
                print(f"Proxy already on in {key} config.")

def proxy_off():
    for key in config_commands.keys():
        config = config_commands[key]
        base_command = config["base_command"]
        listing_command = base_command + [config["list"]]
        out = subprocess.run(listing_command, **subprocess_args)
        if out.returncode == 0:
            config_listing = out.stdout
            if config["name"] in config_listing:
                unsetting_command = base_command + [config["remove"], config["name"]]
                set_pxy = subprocess.run(unsetting_command, **subprocess_args)
                if set_pxy.returncode != 0:
                    raise
                else:
                    print(f"Proxy was turned {Fore.RED + 'OFF' + Fore.RESET} in {key} config.")
            else:
                print(f"Proxy already off in {key} config.")

if len(sys.argv) == 2: 
    if str(sys.argv[1]).lower() == "on":
        proxy_on()
    elif str(sys.argv[1]).lower() == "off":
        proxy_off()
else:
    print(f"""To toggle proxy settings in git and pip configurations, call this script with a single argument: \n
            {Fore.YELLOW + 'python toggle_proxy.py [on | off]' + Fore.RESET}
    """)

