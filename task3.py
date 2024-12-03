import pexpect  # to handle ssh session

# An SSH class is defined
class SSHTONetworkSession:

    # Constructor method to initialize the SSH session with parameters
    def __init__(self, ip_address, username, password, hostname, enable_password=''):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.enable_password = enable_password
        self.hostname = hostname
        self.session = None  # Will hold the SSH session once connected

    # Function to initiate the SSH session
    def ssh_session(self):
        try:
            self.session = pexpect.spawn(f'ssh {self.username}@{self.ip_address}', encoding='utf-8', timeout=20)
            result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                print(f'Error: Unable to establish session with {self.ip_address}')
                return

            self.session.sendline(self.password)
            result = self.session.expect(['>', '#', pexpect.TIMEOUT, pexpect.EOF])

            if result not in [0, 1]:
                print('Error: Authentication failed. Please check your password.')
                return

            self.session.sendline('enable')
            result = self.session.expect(['Password:', '#', pexpect.TIMEOUT, pexpect.EOF])

            if result == 0:
                self.session.sendline(self.enable_password)
                result = self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                print('Error: Failed to enter enable mode.')
                return

            self.session.sendline('configure terminal')
            result = self.session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                print('Error: Failed to enter configuration mode.')
                return

            self.session.sendline(f'hostname {self.hostname}')
            result = self.session.expect([rf'{self.hostname}\\(config\\)#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                print(f'Error: Failed to set hostname to {self.hostname}')
                return

            self.session.sendline('exit')
            self.session.expect('#', timeout=10)

            print('----------------------------')
            print(f'Success! Connected to: {self.ip_address}')
            print(f'Username: {self.username}')
            print(f'Hostname: {self.hostname}')
            print('----------------------------')

            self.compare_configs_menu()

        except pexpect.exceptions.TIMEOUT:
            print('Error: Connection timed out.')
        except pexpect.exceptions.EOF:
            print('Error: SSH session closed unexpectedly.')
        except Exception as e:
            print(f'Error: {e}')

    def compare_configs_menu(self):
        print("\n--- Menu ---")
        print("1. Create a loopback")
        print("2. Exit")

        option = input('Choose an option: ')

        if option == '1':
            self.creating_loopback()
        elif option == '2':
            print("Exiting. Goodbye!")
        else:
            print("Invalid option.")

    def creating_loopback(self):
        try:
            loopback_address = input("Enter loopback IP address: ")
            subnet = input("Enter subnet mask: ")

            self.session.sendline('configure terminal')
            result = self.session.expect(r'\\(config\\)#', timeout=10)
            if result != 0:
                raise Exception("Failed to enter configuration mode.")

            self.session.sendline('interface loopback 0')
            result = self.session.expect(r'\\(config-if\\)#', timeout=10)
            if result != 0:
                raise Exception("Failed to enter interface configuration mode.")

            self.session.sendline(f'ip address {loopback_address} {subnet}')
            result = self.session.expect(r'\\(config-if\\)#', timeout=10)
            if result != 0:
                raise Exception("Failed to configure IP address on loopback interface.")

            self.session.sendline('no shutdown')
            result = self.session.expect(r'\\(config-if\\)#', timeout=10)
            if result != 0:
                raise Exception("Failed to bring up the loopback interface.")

            self.session.sendline('exit')
            self.session.expect(r'\\(config\\)#', timeout=10)

            self.session.sendline('exit')
            self.session.expect(r'#', timeout=10)

            self.save_config()
            print("Loopback interface created and configuration saved successfully.")

        except pexpect.exceptions.TIMEOUT:
            print("Timeout occurred while creating loopback interface.")
        except pexpect.exceptions.EOF:
            print("The SSH session was unexpectedly closed.")
        except Exception as e:
            print(f"An error occurred while creating the loopback interface: {e}")

    def save_config(self):
        try:
            self.session.sendline('write memory')
            result = self.session.expect('#', timeout=10)
            if result != 0:
                raise Exception("Failed to save configuration to startup-config.")
            print("Configuration saved successfully.")
        except pexpect.exceptions.TIMEOUT:
            print("Timeout occurred while saving the configuration.")
        except Exception as e:
            print(f"An error occurred while saving the configuration: {e}")


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
            print('Session cancelled. Goodbye!')
            break

        else:
            print("Invalid option.")


# Program entry point
if __name__ == "__main__":
    menu()
