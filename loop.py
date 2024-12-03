import difflib  # For comparing configurations
import pexpect  # For SSH session handling
import sqlite3  # For database storage

# Database setup
def setup_database():
    conn = sqlite3.connect('network_config.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    action TEXT
                )''')
    conn.commit()
    conn.close()

setup_database()

class SSHTONetworkSession:
    def __init__(self, ip_address, username, password, hostname, enable_password=''):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.hostname = hostname
        self.enable_password = enable_password
        self.session = None

    def ssh_session(self):
        self.session = pexpect.spawn(f'ssh {self.username}@{self.ip_address}', encoding='utf-8', timeout=20)
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
        if result != 0:
            print('Session failed to establish.')
            self.log_to_database('Session failed to establish')
            return

        self.session.sendline(self.password)
        result = self.session.expect(['>', '#', pexpect.TIMEOUT, pexpect.EOF])
        if result != 0:
            print('Authentication failed.')
            self.log_to_database('Authentication failed')
            return

        self.session.sendline('enable')
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
        if result == 0:
            self.session.sendline(self.enable_password)
            result = self.session.expect('#')
        if result != 0:
            print('Enable mode failed.')
            self.log_to_database('Enable mode failed')
            return

        self.session.sendline('configure terminal')
        result = self.session.expect(r'\(config\)#')
        if result != 0:
            print('Config mode failed.')
            self.log_to_database('Config mode failed')
            return

        self.session.sendline(f'hostname {self.hostname}')
        result = self.session.expect(rf'{self.hostname}\(config\)#')
        if result == 0:
            print('Hostname set successfully.')
            self.log_to_database(f'Hostname set to {self.hostname}')
        else:
            print('Failed to set hostname.')
            self.log_to_database('Failed to set hostname')
            return

        self.session.sendline('exit')
        print('Session ready for further commands.')
        self.log_to_database('Session ready for further commands')
        self.compare_configs_menu()

    def log_to_database(self, action):
        conn = sqlite3.connect('network_config.db')
        c = conn.cursor()
        c.execute("INSERT INTO logs (timestamp, action) VALUES (datetime('now'), ?)", (action,))
        conn.commit()
        conn.close()


    def creating_loopback(self):
        try:
            loopback_address = input("Enter loopback IP address: ")
            subnet = input("Enter subnet mask: ")

            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
            self.session.sendline('interface loopback 0')
            self.session.expect(r'\(config-if\)#')
            self.session.sendline(f'ip address {loopback_address} {subnet}')
            self.session.expect(r'\(config-if\)#')

            self.session.sendline('end')
            self.session.expect(r'#')
            self.session.sendline('write memory')
            self.session.expect(r'#')

            print('Loopback interface created and configuration saved successfully.')
            self.log_to_database('Loopback interface created and saved successfully')
        except Exception as e:
            print(f"Error creating loopback interface: {e}")
            self.log_to_database(f"Error creating loopback interface: {e}")

    def creating_ospf(self):
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
            self.log_to_database('OSPF configuration created and saved successfully')
        except Exception as e:
            print(f"Error creating OSPF: {e}")
            self.log_to_database(f"Error creating OSPF: {e}")

    def advertise_ospf(self):
        try:
            self.session.sendline('show running-config | section ospf')
            self.session.expect('#', timeout=10)

            raw_output = self.session.before
            output_lines = raw_output.splitlines()
            filtered_lines = [line.strip() for line in output_lines if line.strip()]

            if not filtered_lines:
                print("No OSPF configuration found.")
                self.log_to_database("No OSPF configuration found.")
            else:
                print("\n--- OSPF Configuration ---")
                for line in filtered_lines:
                    print(line)

                self.log_to_database('OSPF configuration retrieved and displayed')
        except pexpect.exceptions.TIMEOUT:
            print("Timeout while retrieving OSPF configuration.")
            self.log_to_database("Timeout while retrieving OSPF configuration")
        except Exception as e:
            print(f"Error: {e}")
            self.log_to_database(f"Error retrieving OSPF configuration: {e}")

    def creating_eigrp(self):
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
            self.log_to_database('EIGRP configuration created and saved successfully')
        except Exception as e:
            print(f"Error creating EIGRP: {e}")
            self.log_to_database(f"Error creating EIGRP: {e}")

    def advertise_eigrp(self):
        try:
            self.session.sendline('show running-config | section eigrp')
            self.session.expect('#', timeout=10)

            raw_output = self.session.before
            output_lines = raw_output.splitlines()
            filtered_lines = [line.strip() for line in output_lines if line.strip()]

            if not filtered_lines:
                print("No EIGRP configuration found.")
                self.log_to_database("No EIGRP configuration found.")
            else:
                print("\n--- EIGRP Configuration ---")
                for line in filtered_lines:
                    print(line)

                self.log_to_database('EIGRP configuration retrieved and displayed')
        except pexpect.exceptions.TIMEOUT:
            print("Timeout while retrieving EIGRP configuration.")
            self.log_to_database("Timeout while retrieving EIGRP configuration")
        except Exception as e:
            print(f"Error: {e}")
            self.log_to_database(f"Error retrieving EIGRP configuration: {e}")


    def display_interfaces(self):
        try:
            self.session.sendline('show ip interface brief')
            self.session.expect('#', timeout=10)

            raw_output = self.session.before
            print("\n--- Interface Details ---")
            print(raw_output)

            self.log_to_database('Interface details displayed')
        except pexpect.exceptions.TIMEOUT:
            print("Timeout while retrieving interface details.")
            self.log_to_database("Timeout while retrieving interface details")
        except Exception as e:
            print(f"Error: {e}")
            self.log_to_database(f"Error retrieving interface details: {e}")

def main_menu(ssh_session):
    while True:
        print("\n--- Main Menu ---")
        print("1. Create Loopback Interface")
        print("2. Configure OSPF")
        print("3. Display OSPF Configuration")
        print("4. Configure EIGRP")
        print("5. Display EIGRP Configuration")
        print("6. Display Interfaces")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            ssh_session.creating_loopback()
        elif choice == '2':
            ssh_session.creating_ospf()
        elif choice == '3':
            ssh_session.advertise_ospf()
        elif choice == '4':
            ssh_session.creating_eigrp()
        elif choice == '5':
            ssh_session.advertise_eigrp()
        elif choice == '6':
            ssh_session.display_interfaces()
        elif choice == '7':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

ip_address = input("Enter device IP address: ")
username = input("Enter username: ")
password = input("Enter password: ")
hostname = input("Enter hostname: ")

session = SSHTONetworkSession(ip_address, username, password, hostname)
session.ssh_session()
main_menu(session)
