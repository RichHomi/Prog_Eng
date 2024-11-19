import difflib  # To handle the comparisons
import pexpect  # To handle SSH session
from netmiko import ConnectHandler  # Optional if you expand with Netmiko later

# SSH class for managing network sessions
class SSHTONetworkSession:
    def __init__(self, ip_address, username, password, hostname, loopback_address, subnet, enable_password=''):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.hostname = hostname
        self.ip = loopback_address
        self.subnet = subnet
        self.enable_password = enable_password
        self.session = None

    # Initiate SSH session
    def ssh_session(self):
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

    # Creating a loopback interface
    def creating_loopback(self):
        self.session.sendline('configure terminal')
        self.session.expect(r'\(config\)#')
        self.session.sendline('interface loopback 0')
        self.session.expect(r'\(config-if\)#')
        self.session.sendline(f'ip address {self.ip} {self.subnet}')
        self.session.expect(r'\(config-if\)#')
        print('Loopback interface created successfully.')
        self.session.sendline('exit')

    # Menu for comparing configurations
    def compare_configs_menu(self):
        while True:
            print("\n--- Compare Configurations ---")
            print("1. Compare running config with local version")
            print("2. Compare running config with startup config on device")
            print("3. Show IP interface brief")
            print("4. Exit")

            option = input('Choose an option: ')

            if option == '1':
                self.compare_configs('labs_assignment_ssh.txt', 'devices-06.txt')
            elif option == '2':
                self.compare_with_startup_config_ssh()
            elif option == '3':
                self.session.sendline('show ip interface brief')
                self.session.expect('#')
                print(self.session.before)
            elif option == '4':
                print("Exiting comparison menu.")
                break
            else:
                print("Invalid option.")

    # Compare two configuration files
    def compare_configs(self, saved_config_path, compare_config_path):
        try:
            with open(saved_config_path, "r") as f:
                saved_config = f.readlines()

            with open(compare_config_path, "r") as f:
                compare_config = f.readlines()

            differences = difflib.unified_diff(saved_config, compare_config, fromfile=saved_config_path,
                                               tofile=compare_config_path, lineterm='')
            print("\n--- Configuration Differences ---")
            for line in differences:
                print(line)

        except FileNotFoundError:
            print(f"File {saved_config_path} or {compare_config_path} not found.")

    # Compare running config with startup config on the device
    def compare_with_startup_config_ssh(self):
        print("\n--- Running Config vs Startup Config ---")
        try:
            self.session.sendline('show startup-config')
            self.session.expect('#', timeout=30)
            startup_config = self.session.before.splitlines()

            self.session.sendline('show running-config')
            self.session.expect('#', timeout=30)
            running_config = self.session.before.splitlines()

            differences = difflib.unified_diff(startup_config, running_config, fromfile='Startup Config',
                                               tofile='Running Config', lineterm='')
            print("\n--- Differences ---")
            for line in differences:
                print(line)

        except pexpect.exceptions.TIMEOUT:
            print("Timeout. Device may not be responding.")
        except pexpect.exceptions.EOF:
            print("Session unexpectedly closed.")
        except Exception as e:
            print(f"Error during comparison: {e}")

# Menu to start SSH session
def menu():
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
            loopback_address = input('Enter loopback IP address: ')
            subnet = input('Enter subnet mask: ')
            enable_password = input('Enter enable password (if any): ')

            ssh = SSHTONetworkSession(host_ip, username, password, hostname, loopback_address, subnet, enable_password)
            ssh.ssh_session()

        elif option == 'b':
            print('Session cancelled. Goodbye.')
            break

        else:
            print("Invalid option.")

# Entry point of the program
if __name__ == "__main__":
    menu()
