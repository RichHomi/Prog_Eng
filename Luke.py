import difflib  # To handle the comparisons
import pexpect  # To handle SSH sessions


class SSHTONetworkSession:
    def __init__(self, ip_address, username, password, hostname, enable_password=''):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.hostname = hostname
        self.enable_password = enable_password
        self.session = None

    def ssh_session(self):
        try:
            # Start SSH session
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

            # Disable pagination
            self.session.sendline('terminal length 0')
            self.session.expect('#')

            # Enter enable mode
            self.session.sendline('enable')
            result = self.session.expect(['Password:', '#', pexpect.TIMEOUT])
            if result == 0:
                self.session.sendline(self.enable_password)
                self.session.expect('#')

            # Enter configuration mode
            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')

            # Set hostname
            self.session.sendline(f'hostname {self.hostname}')
            self.session.expect(rf'{self.hostname}\(config\)#')
            print('Hostname set successfully.')

            # Exit configuration mode
            self.session.sendline('exit')
            self.session.expect('#')
            self.save_config()
            print('Session ready for further commands.')
            self.compare_configs_menu()

        except pexpect.exceptions.TIMEOUT:
            print("Timeout occurred. Device may not be responding.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def save_config(self):
        # Save running configuration to startup configuration
        self.session.sendline('copy running-config startup-config')
        result = self.session.expect(['Destination filename', '#'], timeout=30)
        if result == 0:  # If prompted for filename
            self.session.sendline('')
            self.session.expect('#', timeout=30)
        print('Configuration saved to startup configuration.')

    def creating_loopback(self):
        try:
            # Get loopback IP and subnet
            loopback_address = input("Enter loopback IP address: ")
            subnet = input("Enter subnet mask: ")

            # Configure the loopback interface
            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
            self.session.sendline('interface loopback 0')
            self.session.expect(r'\(config-if\)#')
            self.session.sendline(f'ip address {loopback_address} {subnet}')
            self.session.expect(r'\(config-if\)#')
            print('Loopback interface created successfully.')

            # Exit configuration mode and save configuration
            self.session.sendline('exit')  # Exit interface config
            self.session.expect(r'\(config\)#')
            self.session.sendline('exit')  # Exit global config
            self.session.expect('#')
            self.save_config()

        except pexpect.exceptions.TIMEOUT:
            print("Timeout occurred while creating loopback interface.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def compare_configs_menu(self):
        while True:
            print("\n--- Compare Configurations ---")
            print("1. Compare running config with local version")
            print("2. Compare running config with startup config on device")
            print("3. Show running config")
            print("4. Create a loopback interface")
            print("5. Exit")

            option = input('Choose an option: ')

            if option == '1':
                self.compare_configs('labs_assignment_ssh.txt', 'devices-06.txt')
            elif option == '2':
                self.compare_with_startup_config_ssh()
            elif option == '3':
                try:
                    self.session.sendline('show running-config')
                    while True:  # Handle pagination
                        index = self.session.expect(['--More--', '#'], timeout=30)
                        print(self.session.before)  # Print the output
                        if index == 0:
                            self.session.send(' ')  # Continue
                        elif index == 1:
                            break
                except pexpect.exceptions.TIMEOUT:
                    print("Timeout occurred while fetching running configuration.")
            elif option == '4':
                self.creating_loopback()
            elif option == '5':
                print("Exiting comparison menu.")
                break
            else:
                print("Invalid option.")

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

    def compare_with_startup_config_ssh(self):
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
        except Exception as e:
            print(f"Error during comparison: {e}")


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
            enable_password = input('Enter enable password (if any): ')

            ssh = SSHTONetworkSession(host_ip, username, password, hostname, enable_password)
            ssh.ssh_session()

        elif option == 'b':
            print('Session cancelled. Goodbye.')
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    menu()
