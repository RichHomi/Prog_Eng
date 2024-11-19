import difflib  # to handle the comparisons
import pexpect  # to handle ssh session


class SSHTONetworkSession:

    def __init__(self, ip_address, username, password, hostname, enable_password=''):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.enable_password = enable_password
        self.hostname = hostname
        self.session = None

    def ssh_session(self):
        self.session = pexpect.spawn(f'ssh {self.username}@{self.ip_address}', encoding='utf-8', timeout=20)
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

        if result != 0:
            print(f'-------- Establishing session failed for {self.ip_address}')
            return

        self.session.sendline(self.password)
        result = self.session.expect(['>', '#', pexpect.TIMEOUT, pexpect.EOF])

        if result != 0:
            print('-------- Incorrect password. Session failed:')
            return

        self.session.sendline('enable')
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

        if result == 0:
            self.session.sendline(self.enable_password)
            result = self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

        if result != 0:
            print('-------- Failed to enter enable mode')
            return

        self.session.sendline('configure terminal')
        result = self.session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

        if result != 0:
            print('-------- Failed to enter config mode')
            return

        self.session.sendline(f'hostname {self.hostname}')
        result = self.session.expect([rf'{self.hostname}\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

        if result != 0:
            print(f'-------- Failed to set hostname to {self.hostname}')
            return
        else:
            self.session.sendline('exit')
            self.session.sendline('exit')

            print('----------------------------')
            print('Success! Connected to:', self.ip_address)
            print('Username:', self.username)
            print('Hostname:', self.hostname)
            print('----------------------------')

            running_config = self.session.before
            with open("labs_assignment_ssh.txt", "w") as f:
                f.write(running_config)
            print("Running config saved successfully to 'labs_assignment_ssh.txt'")

        self.compare_configs_menu()

    def creating_loopback(self):
    #"""
    #Creates a loopback interface on the remote device, assigns an IP address,
    #and ensures successful configuration through verification.
    #"""
        try:
            # Enter global configuration mode
            self.session.sendline('configure terminal')
            result = self.session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                print('-------- Failed to enter config mode.')
                return

            # Enter the loopback interface configuration
            self.session.sendline('interface loopback0')
            result = self.session.expect([r'\(config-if\)#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                print('-------- Failed to create loopback interface.')
                return

            # Assign an IP address to the loopback interface
            ip_address = input('Enter IP address for loopback interface (e.g., 192.168.56.89): ')
            subnet_mask = input('Enter subnet mask (e.g., 255.255.255.0): ')

            self.session.sendline(f'ip address {ip_address} {subnet_mask}')
            result = self.session.expect([r'\(config-if\)#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                print('-------- Failed to assign IP address to loopback interface.')
                return

            # Exit to global configuration mode
            self.session.sendline('exit')
            self.session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

            # Exit configuration mode
            self.session.sendline('exit')
            self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

            print(f"Loopback interface configured successfully with IP {ip_address}/{subnet_mask}.")

        except pexpect.exceptions.TIMEOUT:
            print("Timeout while configuring loopback interface.")
        except pexpect.exceptions.EOF:
            print("Session unexpectedly closed while configuring loopback interface.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    def compare_configs_menu(self):
        print("\n--- Compare Configurations ---")
        print("1. Compare running config with local version")
        print("2. Compare running config with startup config on device")
        print("3. Create loopback interface")
        print("4. Exit")

        option = input('Choose an option: ')

        if option == '1':
            self.compare_configs('labs_assignment_ssh.txt', 'devices-06.txt')

        elif option == '2':
            self.compare_with_startup_config_ssh()

        elif option == '3':
            self.creating_loopback()

        elif option == '4':
            print("Exiting comparison. Goodbye!")

        else:
            print("Invalid option")

    


def menu():
    while True:
        print('---------MENU---------')
        print('a. SSH Session')
        print('b. Exit')

        options = input('Choose from the below options: ')

        if options == 'a':
            print("SSH SESSION SELECTED")
            host_ip = input('Enter IP address: ')
            username = input('Enter username: ')
            password = input('Enter password: ')
            hostname = input('Enter new hostname: ')
            enable_password = input('Enter enable password (if any): ')
            ssh = SSHTONetworkSession(host_ip, username, password, hostname, enable_password)
            ssh.ssh_session()

        elif options == 'b':
            print('Session cancelled. Goodbye')
            break

        else:
            print("Invalid option")


if __name__ == "__main__":
    menu()



def creating_loopback(self):
    """
    Creates a loopback interface on the remote device and assigns an IP address.
    Handles device prompt mismatches, privilege level issues, and session states.
    """
    try:
        # Confirm the current session state (must be in privileged exec mode, '#')
        self.session.sendline('')
        result = self.session.expect([r'#', r'>', pexpect.TIMEOUT, pexpect.EOF])

        if result == 1:
            print("-------- Not in enable mode. Attempting to enter enable mode.")
            self.session.sendline('enable')
            enable_result = self.session.expect(['Password:', '#', pexpect.TIMEOUT, pexpect.EOF])
            if enable_result == 0:  # If password is prompted
                self.session.sendline(self.enable_password)
                enable_result = self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])
            if enable_result != 1:
                print("-------- Failed to enter enable mode.")
                return

        # Enter global configuration mode
        print("Entering global configuration mode...")
        self.session.sendline('configure terminal')
        result = self.session.expect([r'\(config\)#', r'#', pexpect.TIMEOUT, pexpect.EOF])

        if result != 0:
            print("-------- Failed to enter config mode. Check privileges or device response.")
            return

        # Configure the loopback interface
        self.session.sendline('interface loopback0')
        result = self.session.expect([r'\(config-if\)#', pexpect.TIMEOUT, pexpect.EOF])
        if result != 0:
            print("-------- Failed to create loopback interface.")
            return

        # Assign an IP address to the loopback interface
        ip_address = input('Enter IP address for loopback interface (e.g., 192.168.56.89): ')
        subnet_mask = input('Enter subnet mask (e.g., 255.255.255.0): ')
        self.session.sendline(f'ip address {ip_address} {subnet_mask}')
        result = self.session.expect([r'\(config-if\)#', pexpect.TIMEOUT, pexpect.EOF])
        if result != 0:
            print("-------- Failed to assign IP address to loopback interface.")
            return

        # Exit interface and global configuration modes
        self.session.sendline('exit')  # Exit from interface configuration mode
        self.session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])
        self.session.sendline('exit')  # Exit from global configuration mode
        self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

        print(f"Loopback interface configured successfully with IP {ip_address}/{subnet_mask}.")

    except pexpect.exceptions.TIMEOUT:
        print("Timeout while configuring loopback interface.")
    except pexpect.exceptions.EOF:
        print("Session unexpectedly closed while configuring loopback interface.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

