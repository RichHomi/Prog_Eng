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
        print("\n--- Compare Configurations ---")
        print("1. Compare running config with local version")
        print("2. Compare running config with startup config on device")
        print("3. Exit")

        option = input('Choose an option: ')

        if option == '1':
            # Compare running config (labs_assignment_ssh.txt) with local device (devices-06.txt)
            self.compare_configs('labs_assignment_ssh.txt', 'devices-06.txt')

        elif option == '2':
            # Compare running config with startup config on the device
            self.compare_with_startup_config_ssh()

        elif option == '3':
            print("Exiting comparison. Goodbye!")

        else:
            print("Invalid option")

    def compare_configs(self, saved_config_path, compare_config_path):
        try:
            # Compare the file after reading the configurations
            with open(saved_config_path, "r") as f:
                saved_config = f.readlines()

            with open(compare_config_path, "r") as f:
                compare_config = f.readlines()

            # Compare both configurations using difflib
            differences = difflib.unified_diff(saved_config, compare_config, fromfile=saved_config_path, tofile=compare_config_path, lineterm='')
            print("\n--- Configuration Differences ---")
            for line in differences:
                print(line)

        except FileNotFoundError:
            print(f"File {saved_config_path} or {compare_config_path} not found for comparison.")

    def compare_with_startup_config_ssh(self):
        print("\n--- Running Config vs Startup Config ---")

        try:
            # Get startup configuration
            self.session.sendline('show startup-config')
            self.session.expect('#', timeout=30)  # Wait for the prompt after the command
            startup_config = self.session.before.splitlines()  # Split into lines

            # Get running configuration
            running_config = self.get_running_config().splitlines()  # Split into lines

            # Compare running configurations with the startup configuration
            differences = difflib.unified_diff(startup_config, running_config, fromfile='Startup Config', tofile='Running Config', lineterm='')
            for line in differences:
                print(line)

        except pexpect.exceptions.TIMEOUT:
            print("Timeout. Session may be disconnected or timed out.")
        except pexpect.exceptions.EOF:
            print("SSH session unexpectedly closed.")
        except Exception as e:
            print(f"Error during comparison: {e}")

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
