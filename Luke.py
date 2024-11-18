import pexpect
import difflib  # for comparisons

class SSHToANetwork:
    def __init__(self, ip_address, username, password, hostname, enable_password=''):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.enable_password = enable_password
        self.hostname = hostname
        self.session = None  # Will hold the SSH session

    def ssh_session(self):
        # Create the SSH session
        self.session = pexpect.spawn('ssh ' + self.username + '@' + self.ip_address, encoding='utf-8', timeout=20)
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

        # Check for error in creating the session
        if result != 0:
            print('---- Failure! creating session for:', self.ip_address)
            return

        # Session expecting password, enter details
        self.session.sendline(self.password)
        result = self.session.expect(['>', '#', pexpect.TIMEOUT, pexpect.EOF])

        # Check for error in entering password
        if result != 0:
            print('---- Failure! entering password:', self.password)
            return

        # Enter enable mode
        self.session.sendline('enable')
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

        # Check if enable password is required
        if result == 0:
            self.session.sendline(self.enable_password)
            result = self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

        # Check for error in entering enable mode
        if result != 0:
            print('---- Failure! entering enable mode')
            return

        # Enter configuration mode
        self.session.sendline('configure terminal')
        result = self.session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

        # Check for error in entering config mode
        if result != 0:
            print('---- Failure! entering config mode')
            return

        # Change the hostname to the new one
        self.session.sendline(f'hostname {self.hostname}')
        result = self.session.expect([rf'{self.hostname}\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

        # Check for error in setting hostname
        if result != 0:
            print(f'---- Failure! setting hostname to {self.hostname}')
        else:
            # Exit configuration mode
            self.session.sendline('exit')

            # Exit enable mode
            self.session.sendline('exit')

            # Display success message
            print('----------------------------')
            print('Success! Connected to:', self.ip_address)
            print('Username:', self.username)
            print('Hostname:', self.hostname)
            print('----------------------------')

            # Save the running config to a file
            running_config = self.session.before  # Capture the output of the SSH session directly as a string
            with open("Labs_assignment_ssh.txt", "w") as f:
                f.write(running_config)
            print("Running configuration successfully saved to 'Labs_assignment_ssh.txt'")

        # Now, ask for comparison and keep session open
        self.compare_configs_menu()

    def compare_configs_menu(self):
        # Ask user for comparison options
        print("\n--- Compare Configurations ---")
        print("1. Compare Labs_assignment_ssh.txt with devices-06.txt")
        print("2. Compare running config with startup config on device")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            # Compare Labs_assignment_ssh.txt with devices-06.txt
            self.compare_configs('Labs_assignment_ssh.txt', 'devices-06.txt')
        elif choice == '2':
            # Compare running config with startup config
            self.compare_with_startup_config_ssh()
        elif choice == '3':
            print("Exiting comparison. Goodbye!")
        else:
            print("Invalid option")

    def compare_configs(self, saved_config_path, compare_config_path):
        try:
            # Read the saved configuration and the file to compare it with
            with open(saved_config_path, "r") as f:
                saved_config = f.readlines()

            with open(compare_config_path, "r") as f:
                compare_config = f.readlines()

            # Use difflib to compare both configs
            differences = difflib.unified_diff(saved_config, compare_config, fromfile=saved_config_path, tofile=compare_config_path, lineterm='')
            print("\n--- Configuration Differences ---")
            for line in differences:
                print(line)

        except FileNotFoundError:
            print(f"File {saved_config_path} or {compare_config_path} not found for comparison.")

    def compare_with_startup_config_ssh(self):
        print("\n--- Comparing Running Config with Startup Config ---")
        
        try:
            # Get startup configuration
            self.session.sendline('show startup-config')
            self.session.expect('#', timeout=30)  # Wait for the prompt after the command
            startup_config = self.session.before.splitlines()  # Split into lines

            # Get running configuration
            running_config = self.get_running_config().splitlines()  # Split into lines

            # Compare the startup and running configurations
            differences = difflib.unified_diff(startup_config, running_config, fromfile='Startup Config', tofile='Running Config', lineterm='')
            for line in differences:
                print(line)

        except pexpect.exceptions.TIMEOUT:
            print("Timeout waiting for the prompt. The session may have timed out or disconnected.")
        except pexpect.exceptions.EOF:
            print("The SSH session was unexpectedly closed.")
        except Exception as e:
            print(f"An error occurred during comparison: {e}")

    def get_running_config(self):
        # Function to retrieve the current running configuration from the device
        try:
            self.session.sendline('show running-config')
            self.session.expect('#', timeout=30)  # Wait for the prompt after the command
            return self.session.before  # Return the running config as a string
        except pexpect.exceptions.TIMEOUT:
            print("Timeout while waiting for running config.")
        except pexpect.exceptions.EOF:
            print("The SSH session was unexpectedly closed.")
        return ""  # Return an empty string if there was an error


def menu():
    while True:
        print('---------MENU---------')
        print('a. SSH Session')
        print('b. Exit')

        option = input('Please choose from the options: ')

        if option == 'a':
            # For SSH connection
            print("SSH SESSION SELECTED")
            host_ip = input('Enter IP address: ')
            username = input('Enter username: ')
            password = input('Enter password: ')
            hostname = input('Enter new hostname: ')
            enable_password = input('Enter enable password (if any): ')
            ssh = SSHToANetwork(host_ip, username, password, hostname, enable_password)
            ssh.ssh_session()

        elif option == 'b':
            # Exit
            print('Session cancelled. Goodbye')
            break

        else:
            print("Invalid option")


# Entry point for the program
if __name__ == "__main__":
    menu()
