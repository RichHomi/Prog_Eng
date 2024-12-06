import pexpect  # To handle SSH session

# SSH class for managing network sessions
class SSHTONetworkSession:
    def __init__(self, ip_address, username, password, hostname, enable_password=''):
        # Initialize class attributes with provided parameters
        self.ip_address = ip_address  # IP address of the target device
        self.username = username  # Username for SSH authentication
        self.password = password  # Password for SSH authentication
        self.hostname = hostname  # Desired hostname for the target device
        self.enable_password = enable_password  # Enable password (if required)
        self.session = None  # Placeholder for the SSH session object

    # Initiate SSH session
    def ssh_session(self):
        try:
            # Start an SSH session
            self.session = pexpect.spawn(f'ssh {self.username}@{self.ip_address}', encoding='utf-8', timeout=20)
            result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

            # Check if the session was established
            if result != 0:
                print('Session failed to establish.')
                return

            # Provide the login password
            self.session.sendline(self.password)  # Send the SSH password
            result = self.session.expect(['>', '#', pexpect.TIMEOUT, pexpect.EOF])  # Check if login was successful
            if result != 0:
                print('Authentication failed.')
                return

            # Enter enable mode
            self.session.sendline('enable')  # Enter privileged EXEC mode
            result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
            if result == 0:
                self.session.sendline(self.enable_password)  # Provide enable password
                result = self.session.expect('#')

            if result != 0:
                print('Enable mode failed.')
                return

            # Enter configuration mode
            self.session.sendline('configure terminal')  # Enter global configuration mode
            result = self.session.expect(r'\(config\)#')
            if result != 0:
                print('Config mode failed.')
                return

            # Set hostname
            self.session.sendline(f'hostname {self.hostname}')  # Change the device hostname
            result = self.session.expect(rf'{self.hostname}\(config\)#')  # Check if hostname change succeeded
            if result == 0:
                print('Hostname set successfully.')
            else:
                print('Failed to set hostname.')
                return

            # Exit configuration mode
            self.session.sendline('exit')  # Exit configuration mode
            print('Session ready for further commands.')
            self.compare_configs_menu()  # Open the menu for further configuration

        except Exception as e:
            # Handle unexpected errors
            print(f"Error during SSH session: {e}")

    # Creating a loopback interface
    def creating_loopback(self):
        try:
            # Get IP address and subnet mask from the user
            loopback_address = input("Enter loopback IP address: ")  # Prompt user for loopback IP
            subnet = input("Enter subnet mask: ")  # Prompt user for subnet mask

            # Enter configuration mode and create the loopback interface
            self.session.sendline('configure terminal')  # Enter global configuration mode
            self.session.expect(r'\(config\)#')
            self.session.sendline('interface loopback 0')  # Create loopback interface
            self.session.expect(r'\(config-if\)#')
            self.session.sendline(f'ip address {loopback_address} {subnet}')  # Assign IP and subnet mask
            self.session.expect(r'\(config-if\)#')

            # Save the configuration to startup config
            self.session.sendline('end')  # Exit interface configuration mode
            self.session.expect(r'#')
            self.session.sendline('write memory')  # Save configuration
            self.session.expect(r'#')

            print('Loopback interface created and configuration saved successfully.')

        except Exception as e:
            # Handle unexpected errors
            print(f"Error creating loopback interface: {e}")

    # Display IP interface brief
    def show_ip_interface_brief(self):
        try:
            # Send the command to display interface brief status
            self.session.sendline('show ip interface brief')  # Execute command
            self.session.expect('#', timeout=10)  # Wait for the command output

            # Capture and print the output
            raw_output = self.session.before  # Capture command output
            output_lines = raw_output.splitlines()  # Split output into lines
            filtered_lines = [line.strip() for line in output_lines if line.strip()]  # Filter out empty lines

            print("\n--- IP Interface Brief ---")
            for line in filtered_lines:
                if "Interface" in line or "up" in line or "down" in line:
                    print(line)  # Print header and relevant lines

        except pexpect.exceptions.TIMEOUT:
            # Handle timeout errors
            print("Timeout while retrieving interface information.")
        except Exception as e:
            # Handle unexpected errors
            print(f"Error: {e}")

    # Menu for creating and advertising interfaces
    def compare_configs_menu(self):
        while True:
            # Display menu options
            print("\n--- Interface Menu ---")
            print("1. Show IP interface brief")
            print("2. Create a loopback interface")
            print("3. Exit")

            # Get user input
            option = input('Choose an option: ')

            if option == '1':
                # Show IP interface brief
                self.show_ip_interface_brief()
            elif option == '2':
                # Create loopback interface
                self.creating_loopback()
            elif option == '3':
                # Exit the menu
                print("Exiting comparison menu.")
                break
            else:
                # Handle invalid input
                print("Invalid option.")

# Menu to start SSH session
def menu():
    while True:
        # Display main menu options
        print('--------- MENU ---------')
        print('a. SSH Session')
        print('b. Exit')

        # Get user input
        option = input('Choose an option: ')

        if option == 'a':
            # Start SSH session
            print("SSH SESSION SELECTED")
            host_ip = input('Enter IP address: ')  # Prompt for IP address
            username = input('Enter username: ')  # Prompt for username
            password = input('Enter password: ')  # Prompt for password
            hostname = input('Enter new hostname: ')  # Prompt for hostname
            enable_password = input('Enter enable password (if any): ')  # Prompt for enable password

            ssh = SSHTONetworkSession(host_ip, username, password, hostname, enable_password)  # Initialize SSH session
            ssh.ssh_session()  # Start session

        elif option == 'b':
            # Exit the program
            print('Session cancelled. Goodbye.')
            break

        else:
            # Handle invalid input
            print("Invalid option.")

# Entry point of the program
if __name__ == "__main__":
    menu()  # Run the menu
