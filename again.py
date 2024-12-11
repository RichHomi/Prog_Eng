import pexpect
import time
import paramiko

# A time-capsuled function is created to expect a specific pattern
# The arguments session, prompt(str), and timeout(s) are passed 
def wait_for_pattern(session, prompt, timeout=20):
    session.expect(prompt, timeout)

# A class is defined for the Telnet communication with a constructor method
# function with the ip_address, username, password, and new_hostname as attributes
class ConnectionToTelnet:
    def __init__(self, ipadd, un, pss, new_name):
        self.username = un
        self.ipadd = ipadd
        self.new_name = new_name
        self.password = pss

    # A function is created to connect to a device using a Telnet connection
    # A message is then displayed to communicate the connection process
    # Text handling using utf-8 with timeout of 20 seconds created to initiate
    # a Telnet session using self.ipadd which is sent to the intended device
    def connection(self):
        print(f'Establishing Telnet connection to {self.ipadd}...')
        telnet_com = pexpect.spawn(f'telnet {self.ipadd}', encoding='utf-8', timeout=20)
        results = telnet_com.expect(['Username: ', pexpect.TIMEOUT])
        telnet_com.sendline(self.username)

        # Login password attempts for a maximum of 3
        login_attempts = 3
        attempts = 0

        # A while loop is created to check password and a wait_for_input waits for the user input
        # which is sent to the intended device for the connection
        while attempts < login_attempts:
            wait_for_pattern(telnet_com, 'Password: ')
            telnet_com.sendline(self.password)

            # A try and except is used to give access only if credentials are 
            # correct within the given time of 20 seconds
            try:
                wait_for_pattern(telnet_com, '>', timeout=20)
                print("Login successful")
                break

            # If the login attempts equals 3, display the message and return to the menu requesting for 
            # credentials
            except pexpect.TIMEOUT:
                attempts += 1
                print('Login failed: Incorrect credentials')
                if attempts == login_attempts:
                    print('Maximum attempts reached. Exiting Telnet session')
                    return

        # To access the privilege executive mode, 'enable' is required as input
        # which is then displayed by the '#'
        telnet_com.sendline('enable')
        wait_for_pattern(telnet_com, '#')

        # To change the hostname, the user has to enter 'config terminal' and the 
        # new hostname is displayed in the next step
        telnet_com.sendline('configure terminal')
        wait_for_pattern(telnet_com, '(config)#')
        telnet_com.sendline(f'hostname {self.new_name}')  # Corrected the command format
        wait_for_pattern(telnet_com, '(config)#')

        # Show the details of the running configuration when the command is entered 
        telnet_com.sendline('show ip interface brief')
        wait_for_pattern(telnet_com, '#')

        # Write the output to a file
        with open("labs_assignment.txt", "w") as f:
            f.write(telnet_com.before.decode('utf-8'))

        print("Running configuration saved successfully to 'labs_assignment.txt'")

        # Closing Telnet session
        telnet_com.sendline('exit')
        print('Session closed')


# ............SSH CONNECTION.......

# A class is defined for the SSH communication with a constructor method
# function with the ip_address, username, password, and new_hostname as attributes
class ConnectionToSsh:
    def __init__(self, ipadd, un, pss, new_name):
        self.username = un
        self.ipadd = ipadd
        self.new_name = new_name
        self.password = pss

    def connection(self):
        print(f'Establishing SSH connection to {self.ipadd}...')

        # An instance is created to manage the SSH connection to the device and it is automatically added to the host keys
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Login password attempts for a maximum of 3
        login_attempts = 3
        attempts = 0

        while attempts < login_attempts:
            try:
                client.connect(self.ipadd, username=self.username, password=self.password, timeout=20)
                print("Login successful")
                break  # Exit the while loop when the connection is successful
            except paramiko.AuthenticationException:
                attempts += 1
                print(f'Login failed: Incorrect credentials. Attempt {attempts}/{login_attempts}.')
                if attempts == login_attempts:
                    print('Maximum attempts reached. Exiting SSH session.')
                    return
            except Exception as e:
                print(f"An error occurred: {e}")
                return
        
        # Executing commands after successful login
        stdin, stdout, stderr = client.exec_command('enable')
        stdin.write(self.password + '\n')  # Writing the password for enable mode
        stdin.flush()

        stdin, stdout, stderr = client.exec_command('configure terminal')
        stdin, stdout, stderr = client.exec_command(f'hostname {self.new_name}')  # Change the hostname
        print(stdout.read().decode())  # Output from the hostname command

        stdin, stdout, stderr = client.exec_command('show ip interface brief')
        channel = stdout.read().decode()  # Capture output from the command
        print(channel)  # Print the command output

        # Writing the output to a file
        with open("labs_assignment_ssh.txt", "w") as f:
            f.write(channel)

        client.close()  # Closing the SSH session
        print('Session closed.')

def menu():
    # This menu is displayed when the script is executed while collecting user information be it
    # Telnet or SSH

    while True:
        print('\n-----Menu-------')
        print('1. Telnet Connection')
        print('2. SSH Connection')
        print('3. Exit')

        option = input('Select an option from the choices above: ')  # Fixed prompt text

        if option == '1':
            # This is for Telnet connection
            host_ip = input('Enter the device IP address: ')
            username = input('Enter the Telnet username: ')
            password = input('Enter the Telnet password: ')
            hostname = input('Enter the new hostname for the device: ')
            telnet_connection = ConnectionToTelnet(host_ip, username, password, hostname)
            telnet_connection.connection()  # Call the connection method

        elif option == '2':
            # For SSH connection
            host_ip = input('Enter the device IP address: ')
            username = input('Enter the SSH username: ')
            password = input('Enter the SSH password: ')
            hostname = input('Enter the new hostname for the device: ')
            ssh_connection = ConnectionToSsh(host_ip, username, password, hostname)
            ssh_connection.connection()  # Call the connection method

        elif option == '3':
            # Close the program
            print("Cancelled. Goodbye")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    menu() 
