import difflib  # For comparing configurations
import pexpect  # For handling SSH sessions
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


# Save action logs to the database
def save_log(action):
    from datetime import datetime
    conn = sqlite3.connect('network_config.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO logs (timestamp, action) VALUES (?, ?)", (timestamp, action))
    conn.commit()
    conn.close()


# SSH class for managing network sessions
class SSHTONetworkSession:
    def __init__(self, ip_address, username, password, hostname, enable_password=''):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.hostname = hostname
        self.enable_password = enable_password
        self.session = None


    # Initiate SSH session
    def ssh_session(self):
        try:
            self.session = pexpect.spawn(f'ssh {self.username}@{self.ip_address}', encoding='utf-8', timeout=20)
            result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
            if result != 0:
                print('Session failed to establish.')
                save_log('Failed to establish SSH session.')
                return

            self.session.sendline(self.password)
            result = self.session.expect(['>', '#', pexpect.TIMEOUT, pexpect.EOF])
            if result != 0:
                print('Authentication failed.')
                save_log('Authentication failed during SSH session.')
                return

            # Enter enable mode
            self.session.sendline('enable')
            result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
            if result == 0:
                self.session.sendline(self.enable_password)
                result = self.session.expect('#')
            if result != 0:
                print('Enable mode failed.')
                save_log('Failed to enter enable mode.')
                return

            # Enter configuration mode
            self.session.sendline('configure terminal')
            result = self.session.expect(r'\(config\)#')
            if result != 0:
                print('Config mode failed.')
                save_log('Failed to enter configuration mode.')
                return

            # Set hostname
            self.session.sendline(f'hostname {self.hostname}')
            result = self.session.expect(rf'{self.hostname}\(config\)#')
            if result == 0:
                print('Hostname set successfully.')
                save_log(f'Successfully set hostname to {self.hostname}.')
            else:
                print('Failed to set hostname.')
                save_log('Failed to set hostname.')
                return

            # Exit configuration mode
            self.session.sendline('exit')
            print('Session ready for further commands.')
            save_log('SSH session established and ready.')
            self.compare_configs_menu()

        except Exception as e:
            print(f"Error during SSH session: {e}")
            save_log(f'Error during SSH session: {e}')

    # Show IP interface brief
    def show_ip_interface_brief(self):
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
            save_log('Displayed IP interface brief.')
        except pexpect.exceptions.TIMEOUT:
            print("Timeout while retrieving interface information.")
            save_log('Timeout while retrieving interface information.')
        except Exception as e:
            print(f"Error: {e}")
            save_log(f"Error: {e}")

    # Create a loopback interface
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
            save_log(f'Created loopback interface with IP {loopback_address} and subnet {subnet}.')
        except Exception as e:
            print(f"Error creating loopback interface: {e}")
            save_log(f"Error creating loopback interface: {e}")


    # OSPF Configuration
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
            save_log(f'Created OSPF configuration: Process ID {process_id}, Network {net_id}, Area {area}.')
        except Exception as e:
            print(f"Error creating OSPF: {e}")
            save_log(f"Error creating OSPF: {e}")

    # Main menu for configuration
    def compare_configs_menu(self):
        while True:
            print("\n--- Interface Menu ---")
            print("1. Show IP interface brief")
            print("2. Create a loopback interface")
            print("3. Create an OSPF configuration")
            print("4. Exit")
            option = input('Choose an option: ')
            if option == '1':
                self.show_ip_interface_brief()
            elif option == '2':
                self.creating_loopback()
            elif option == '3':
                self.creating_ospf()
            elif option == '4':
                print("Exiting comparison menu.")
                break
            else:
                print("Invalid option.")

# Menu to start SSH session
def menu():
    while True:
        print('--------- MENU ---------')
        print('a. SSH Session')
        print('b. Exit')
        option = input('Choose an option: ')
        if option == 'a':
            host_ip = input('Enter IP address: ')
            username = input('Enter username: ')
            password = input('Enter password: ')
            hostname = input('Enter new hostname: ')
            enable_password = input('Enter enable password (if any): ')
            ssh = SSHTONetworkSession(host_ip, username, password, hostname, enable_password)
            ssh.ssh_session()
        elif option == 'b':
            print('Session cancelled. Goodbye.')
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    setup_database()
    menu()
