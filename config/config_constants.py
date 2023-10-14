import os
import subprocess

# Paths

NPS_PATH = os.getcwd()
NODELIST_FILE_PATH = f"{NPS_PATH}/files/nodelist.txt"
GRAPH_FILE_PATH = f"{NPS_PATH}/files/graph.txt"
GROUPS_FILE_PATH = f"{NPS_PATH}/files/groups.txt"
HOSTS_FILE_PATH = f"{NPS_PATH}/files/hosts.txt"

SCRIPT_FOLDER_PATH = f"{NPS_PATH}/scripts/nodes/"
SRC_SCRIPT_FOLDER = f"{NPS_PATH}/scripts/"
DST_SCRIPT_FOLDER = "/home/clusternode/MininetScripts/"

PARAMIKO_LOG_PATH = f"{NPS_PATH}/logs/paramiko.log"
NPS_LOG_PATH = f"{NPS_PATH}/logs/nps.log"

PYTHON_PATH = subprocess.run(['pipenv', '--venv'], capture_output=True, text=True).stdout.strip() + '/bin/python3'

# Flags

DRAWING_FLAG = True
SAVE_GRAPH_FIG_FLAG = False

# Constants

FIRST_HOST_IP = "1.2.3.1"
HOST_NETMASK = 16
LINK_DELAY = 5
NO_DELAY_FLAG = True

# MALWARE MODE
INFECTED_HOSTS_FILENAME = "infected_hosts.db"
NPS_CONTROL_NODE_IP = "10.0.2.100"

MALWARE_MODE_ON = True
MALWARE_CENTER_IP = NPS_CONTROL_NODE_IP
MALWARE_CENTER_PORT = 56565

# MININET SIMULATION MODES CONSTANTS
CLI_MODE = True
CLI_PROMPT_STRING = ""

# Other
