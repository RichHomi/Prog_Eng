import difflib  # to handle the comparisons
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
        self.session = pexpect.spawn('ssh ' + self.username + '@' + self.ip_address, encoding='utf-8', timeout=20)
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

        # Error handling for establishing the session
        if result != 0:
            print('-------- Establishing session failed for', self.ip_address)
            return

        # Send password when prompted
        self.session.sendline(self.password)
        result = self.session.expect(['>', '#', pexpect.TIMEOUT, pexpect.EOF])

        # Check if password is correct
        if result != 0:
            print('-------- Incorrect password. Session failed:')
            return

        # Entering enable mode
        self.session.sendline('enable')
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

        # Check if enable password is needed
        if result == 0:
            self.session.sendline(self.enable_password)
            result = self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

        # Check for success in entering enable mode
        if result != 0:
            print('-------- Session failed to enter enable mode')
            return

        # Enter configuration mode
        self.session.sendline('configure terminal')
        result = self.session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

        if result != 0:
            print('-------- Session failed to enter config mode')
            return

        # Change the hostname
        self.session.sendline(f'hostname {self.hostname}')
        result = self.session.expect([rf'{self.hostname}\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

        if result != 0:
            print(f'-------- Session failed setting hostname to {self.hostname}')
            return
        else:
            # Exit configuration mode
            self.session.sendline('exit')
            self.session.sendline('exit')

            # Display success message
            print('----------------------------')
            print('Success! Connected to:', self.ip_address)
            print('Username:', self.username)
            print('Hostname:', self.hostname)
            print('----------------------------')

            # Save running config to a file
            running_config = self.session.before  # save the output of the session as a string
            with open("labs_assignment_ssh.txt", "w") as f:
                f.write(running_config)
            print("Running config saved successfully to 'labs_assignment_ssh.txt'")

        # Keep the session open and ask for comparison
        self.compare_configs_menu()

    def compare_configs_menu(self):
        # User chooses from the menu
        print("\n--- Menu ---")
        print("1. Show ip interface brief")
        print("2. Creating loopback")
        print("3. Exit")

        option = input('Choose an option: ')

        if option == '1':
            #show ip interface brief
            self.show_ip_interface_brief()

        elif option == '2':
            # Compare running config with startup config on the device
            self.creating_loopback()

        elif option == '3':
            print("Exiting comparison. Goodbye!")

        else:
            print("Invalid option")
    
    def save_config(self):
            try:
                # Save the running configuration to the startup configuration
                self.session.sendline('write memory')
                self.session.expect('#')
            except Exception as e:
                print(f"An error occurred while saving the configuration: {e}")


            except pexpect.exceptions.TIMEOUT:
                print("Timeout occurred while creating loopback interface.")
            except Exception as e:
                print(f"An error occurred: {e}")

    # Show IP interface brief
    def show_ip_interface_brief(self):
        try:
            # Send the command to the device
            self.session.sendline('show ip interface brief')
            self.session.expect('#')  # Wait for the prompt
            output = self.session.before  # Capture the output

            # Print the output to the user
            print("\n--- IP Interface Brief ---")
            print(output)
        except Exception as e:
            print(f"An error occurred while fetching interface details: {e}")


    # Creating a loopback interface
    def creating_loopback(self):
        try:
            # Get loopback IP and subnet
            loopback_address = input("Enter loopback IP address: ")
            subnet = input("Enter subnet mask: ")

            # Enter configuration mode
            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#', timeout=10)
            
            # Configure the loopback interface
            self.session.sendline('interface loopback 0')
            self.session.expect(r'\(config-if\)#', timeout=10)
            
            self.session.sendline(f'ip address {loopback_address} {subnet}')
            self.session.expect(r'\(config-if\)#', timeout=10)
            self.session.sendline('no shutdown')
            self.session.expect(r'\(config-if\)#', timeout=10)

            print('Loopback interface created successfully.')

            # Exit configuration mode
            self.session.sendline('exit')  # Exit interface config
            self.session.expect(r'\(config\)#', timeout=10)
            self.session.sendline('exit')  # Exit global config
            self.session.expect('#', timeout=10)

            # Save the configuration
            self.save_config()

        except pexpect.exceptions.TIMEOUT:
            print("Timeout occurred while creating loopback interface.")
        except pexpect.exceptions.EOF:
            print("Connection closed unexpectedly. Check the SSH session or device configuration.")
        except Exception as e:
            print(f"An error occurred while creating the loopback interface: {e}")

    def get_running_config(self):
        # Retrieve current running configurations from the device
        try:
            self.session.sendline('show running-config')
            self.session.expect('#', timeout=30)
            return self.session.before
        except pexpect.exceptions.TIMEOUT:
            print("Timeout while waiting for running config.")
        except pexpect.exceptions.EOF:
            print("The SSH session was unexpectedly closed.")
        return ""  # In case of an error, return an empty string
    
    


def menu():
    while True:
        print('---------MENU---------')
        print('a. SSH Session')
        print('b. Exit')

        options = input('Choose from the below options: ')

        if options == 'a':
            # For SSH connection
            print("SSH SESSION SELECTED")
            host_ip = input('Enter IP address: ')
            username = input('Enter username: ')
            password = input('Enter password: ')
            hostname = input('Enter new hostname: ')
            enable_password = input('Enter enable password (if any): ')
            ssh = SSHTONetworkSession(host_ip, username, password, hostname, enable_password)
            ssh.ssh_session()

        elif options == 'b':
            # Exit
            print('Session cancelled. Goodbye')
            break

        else:
            print("Invalid option")


# Program entry point
if __name__ == "__main__":
    menu()
