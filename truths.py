import difflib  # To handle the comparisons
import pexpect  # To handle SSH session
import threading  # For multithreading
from flask import Flask, render_template, request, jsonify  # Flask for web interface
import sqlite3  # For database storage

# Flask web interface setup
app = Flask(__name__)

# Database setup
def setup_database():
    conn = sqlite3.connect('network_configurations.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configurations (
            id INTEGER PRIMARY KEY,
            type TEXT,
            details TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_configuration(config_type, config_details):
    """Saves a configuration to the database."""
    conn = sqlite3.connect('network_configurations.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO configurations (type, details) VALUES (?, ?)',
                   (config_type, config_details))
    conn.commit()
    conn.close()

# SSH class for managing network sessions
class SSHTONetworkSession:
    def __init__(self, ip_address, username, password, hostname, enable_password=''):
        """Initializes the SSH session with the given parameters."""
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.hostname = hostname
        self.enable_password = enable_password
        self.session = None

    def ssh_session(self):
        """Establishes an SSH session and sets the hostname."""
        self.session = pexpect.spawn(f'ssh {self.username}@{self.ip_address}', encoding='utf-8', timeout=20)
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
        if result != 0:
            print('Session failed to establish.')
            return

        self.session.sendline(self.password)
        result = self.session.expect(['>', '#', pexpect.TIMEOUT, pexpect.EOF])
        if result != 0:
            print('Authentication failed.')
            return

        # Enter enable mode
        self.session.sendline('enable')
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
        if result == 0:
            self.session.sendline(self.enable_password)
            result = self.session.expect('#')
        if result != 0:
            print('Enable mode failed.')
            return

        # Enter configuration mode
        self.session.sendline('configure terminal')
        result = self.session.expect(r'\(config\)#')
        if result != 0:
            print('Config mode failed.')
            return

        # Set hostname
        self.session.sendline(f'hostname {self.hostname}')
        result = self.session.expect(rf'{self.hostname}\(config\)#')
        if result == 0:
            print('Hostname set successfully.')
        else:
            print('Failed to set hostname.')
            return

        # Exit configuration mode
        self.session.sendline('exit')
        print('Session ready for further commands.')
        self.compare_configs_menu()

    def creating_loopback(self, ip_address, subnet):
        """Creates a loopback interface with the given IP address and subnet."""
        try:
            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
            self.session.sendline('interface loopback 0')
            self.session.expect(r'\(config-if\)#')
            self.session.sendline(f'ip address {ip_address} {subnet}')
            self.session.expect(r'\(config-if\)#')
            self.session.sendline('end')
            self.session.expect(r'#')
            self.session.sendline('write memory')
            self.session.expect(r'#')
            print('Loopback interface created and configuration saved successfully.')
            save_configuration("Loopback", f"IP: {ip_address}, Subnet: {subnet}")
        except Exception as e:
            print(f"Error creating loopback interface: {e}")

    def creating_ospf(self):
        """Configures OSPF with user input for process ID, network, and area."""
        try:
            process_id = input("Enter the process ID: ")
            net_id = input("Enter the network address: ")
            wildcard = input("Enter the wildcard mask: ")
            area = input("Enter the area: ")

            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
            self.session.sendline(f'router ospf {process_id}')
            self.session.expect(r'\(config-router\)#')
            self.session.sendline(f'network {net_id} {wildcard} area {area}')
            self.session.expect(r'\(config-router\)#')
            self.session.sendline('end')
            self.session.expect(r'#')
            self.session.sendline('write memory')
            self.session.expect(r'#')
            print('OSPF configuration created and saved successfully.')
            save_configuration("OSPF", f"Process ID: {process_id}, Network: {net_id} {wildcard}, Area: {area}")
        except Exception as e:
            print(f"Error creating OSPF: {e}")

    def creating_eigrp(self):
        """Configures EIGRP with user input for AS number, network, and wildcard mask."""
        try:
            autonomous_system_number = input("Enter the autonomous system number: ")
            net_id = input("Enter the network address: ")
            wildcard = input("Enter the wildcard mask: ")

            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
            self.session.sendline(f'router eigrp {autonomous_system_number}')
            self.session.expect(r'\(config-router\)#')
            self.session.sendline(f'network {net_id} {wildcard}')
            self.session.expect(r'\(config-router\)#')
            self.session.sendline('end')
            self.session.expect(r'#')
            self.session.sendline('write memory')
            self.session.expect(r'#')
            print('EIGRP configuration created and saved successfully.')
            save_configuration("EIGRP", f"AS: {autonomous_system_number}, Network: {net_id} {wildcard}")
        except Exception as e:
            print(f"Error creating EIGRP: {e}")
    def show_ip_interface_brief(self):
        """Displays the brief summary of IP interfaces."""
        try:
            self.session.sendline('show ip interface brief')
            self.session.expect('#', timeout=10)
            raw_output = self.session.before
            output_lines = raw_output.splitlines()
            filtered_lines = [line.strip() for line in output_lines if line.strip()]
            print("\n--- IP Interface Brief ---")
            for line in filtered_lines:
                if "Interface" in line or "up" in line or "down" in line:
                    print(line)
        except pexpect.exceptions.TIMEOUT:
            print("Timeout while retrieving interface information.")
        except Exception as e:
            print(f"Error: {e}")

    def advertise_ospf(self):
        """Advertises OSPF with user input for network and area."""
        try:
            network = input("Enter the OSPF network to advertise (e.g., 192.168.1.0): ")
            wildcard = input("Enter the wildcard mask (e.g., 0.0.0.255): ")
            area = input("Enter the OSPF area (e.g., 0): ")

            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
            self.session.sendline(f'router ospf 1')  # Assumes process ID is 1; modify as needed
            self.session.expect(r'\(config-router\)#')
            self.session.sendline(f'network {network} {wildcard} area {area}')
            self.session.expect(r'\(config-router\)#')
            self.session.sendline('end')
            self.session.expect('#')
            self.session.sendline('write memory')
            self.session.expect('#')
            print('OSPF advertisement configured and saved successfully.')
            save_configuration("OSPF Advertisement", f"Network: {network}, Wildcard: {wildcard}, Area: {area}")
        except Exception as e:
            print(f"Error advertising OSPF: {e}")

    def advertise_eigrp(self):
        """Advertises EIGRP with user input for network and wildcard mask."""
        try:
            network = input("Enter the EIGRP network to advertise (e.g., 192.168.1.0): ")
            wildcard = input("Enter the wildcard mask (e.g., 0.0.0.255): ")

            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
            self.session.sendline(f'router eigrp 1')  # Assumes AS number is 1; modify as needed
            self.session.expect(r'\(config-router\)#')
            self.session.sendline(f'network {network} {wildcard}')
            self.session.expect(r'\(config-router\)#')
            self.session.sendline('end')
            self.session.expect('#')
            self.session.sendline('write memory')
            self.session.expect('#')
            print('EIGRP advertisement configured and saved successfully.')
            save_configuration("EIGRP Advertisement", f"Network: {network}, Wildcard: {wildcard}")
        except Exception as e:
            print(f"Error advertising EIGRP: {e}")

    def compare_configs_menu(self):
        """Displays a menu for different configuration options."""
        while True:
            print("\n--- Interface Menu ---")
            print("1. Show IP interface brief")
            print("2. Create a loopback interface")
            print("3. Create an OSPF")
            print("4. Create an EIGRP")
            print("5. Advertise OSPF")
            print("6. Advertise EIGRP")
            print("7. Exit")

            option = input('Choose an option: ')
            if option == '1':
                self.show_ip_interface_brief()
            elif option == '2':
                ip_address = input("Enter loopback IP address: ")
                subnet = input("Enter subnet mask: ")
                threading.Thread(target=self.creating_loopback, args=(ip_address, subnet)).start()
            elif option == '3':
                threading.Thread(target=self.creating_ospf).start()
            elif option == '4':
                threading.Thread(target=self.creating_eigrp).start()
            elif option == '5':
                threading.Thread(target=self.advertise_ospf).start()
            elif option == '6':
                threading.Thread(target=self.advertise_eigrp).start()
            elif option == '7':
                print("Exiting comparison menu.")
                break
            else:
                print("Invalid option.")

# Flask app to run in a separate thread
def run_flask_app():
    """Runs the Flask application on a separate thread."""
    app.run(port=5000, debug=True, use_reloader=False)

# Menu to start SSH session
def menu():
    """Displays the main menu to choose between SSH session and exiting."""
    while True:
        print('--------- MENU ---------')
        print('a. SSH Session')
        print('b. Exit')

        option = input('Choose an option: ')
        if option == 'a':
            print("SSH SESSION SELECTED")
            host_ip = input('Enter IP address: ')
            username = input('Enter username: ')
            password = input('Enter password: ')
            hostname = input('Enter new hostname: ')
            enable_password = input('Enter enable password (if applicable): ')

            ssh_session = SSHTONetworkSession(host_ip, username, password, hostname, enable_password)
            ssh_session.ssh_session()
        elif option == 'b':
            print('Exiting the program.')
            break
        else:
            print('Invalid option. Please try again.')

# Start Flask app in a separate thread
flask_thread = threading.Thread(target=run_flask_app)
flask_thread.start()

# Start the menu
menu()
