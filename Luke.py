
import pexpect  # To handle SSH session


# A CLASS TO MANAGE THE SSH NETWORK SESSION
class SSHTONetworkSession:
    def __init__(self, ip_address, username, password, hostname, enable_password=''):
        # SSH session is initialized with user input for ip address,username, password and hostname 
        # The privileged access mode is then accessed using the eneble password 
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.hostname = hostname
        self.enable_password = enable_password
        self.session = None  # Placeholder for the SSH session object

    # Initiate SSH session
    def ssh_session(self):
        # Spawn an SSH session to the network device using the provided credentials.
        # 'encoding' ensures the output is in UTF-8 format, 'timeout' specifies the session timeout.
        self.session = pexpect.spawn(f'ssh {self.username}@{self.ip_address}', encoding='utf-8', timeout=20)
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

        # Expect to match one of the expected responses: password prompt, timeout, or EOF.
        if result != 0:

            # If the session fails to establish, print an error and exit.
            print('Session failed to establish.')
            return
        
        # Send the password to authenticate the session.
        self.session.sendline(self.password)
        result = self.session.expect(['>', '#', pexpect.TIMEOUT, pexpect.EOF])
        if result != 0:

            # If authentication fails, print an error and exit.
            print('Authentication failed.')
            return

        # Attempt to enter enable mode for privileged commands.
        self.session.sendline('enable')
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
        if result == 0:
            # If prompted for an enable password, send it.
            self.session.sendline(self.enable_password)
            result = self.session.expect('#')
             # If entering enable mode fails, print an error and exit.
        if result != 0:
            print('Enable mode failed.')
            return

        # # Enter configuration mode to begin making changes.
        self.session.sendline('configure terminal')
        result = self.session.expect(r'\(config\)#')
        if result != 0:
            # If entering configuration mode fails, print an error and exit.
            print('Config mode failed.')
            return

        # # Set the hostname of the device.
        self.session.sendline(f'hostname {self.hostname}')
        result = self.session.expect(rf'{self.hostname}\(config\)#')
        if result == 0:
            # If the hostname is set successfully, print a confirmation message.
            print('Hostname set successfully.')
        else:
            # If setting the hostname fails, print an error and exit.
            print('Failed to set hostname.')
            return

        # # Exit configuration mode and print a readiness message.
        self.session.sendline('exit')
        print('Session ready for further commands.')
        # Call the configuration menu for further actions.
        self.compare_configs_menu()

    
    # Creating a loopback interface and saving it to startup configuration
    def creating_loopback(self):
        try:
            # Ask for IP address and subnet dynamically
            loopback_address = input("Enter loopback IP address: ")
            subnet = input("Enter subnet mask: ")
    
            # Enter configuration mode and create the loopback interface
            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
            self.session.sendline('interface loopback 0')
            self.session.expect(r'\(config-if\)#')

            # Configure the loopback interface with the provided IP address and subnet mask.
            self.session.sendline(f'ip address {loopback_address} {subnet}')
            self.session.expect(r'\(config-if\)#')
            
            # Save the configuration to startup to make it persistent
            self.session.sendline('end')  # Exit interface configuration mode
            self.session.expect(r'#')
            self.session.sendline('write memory')  # Save the running config to startup config
            self.session.expect(r'#')
            
            print('Loopback interface created and configuration saved successfully.')
            
            
      # Print an error message if an exception occurs during loopback creation.
        except Exception as e:
            print(f"Error creating loopback interface: {e}")


    
    # Creating and saving OSPF configuration
    def creating_ospf(self):
        try:
            # Get the process ID, network ID, wildcard, and area from the user
            process_id = input("Enter the process ID: ")
            net_id = input("Enter the network address: ")
            wildcard = input("Enter the wildcard mask: ")
            area = input("Enter the area: ")
    
            # Enter configuration mode
            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
    
            # Create the OSPF router process
            self.session.sendline(f'router ospf {process_id}')
            self.session.expect(r'\(config-router\)#')
    
            # Configure the network for OSPF
            self.session.sendline(f'network {net_id} {wildcard} area {area}')
            self.session.expect(r'\(config-router\)#')
    
            # Exit configuration mode
            self.session.sendline('end')
            self.session.expect(r'#')
    
            # Save the configuration to startup
            self.session.sendline('write memory')
            self.session.expect(r'#')
    
            print('OSPF configuration created and saved successfully.')
        
          # Print an error message if an exception occurs during OSPF configuration.
        except Exception as e:
            print(f"Error creating OSPF: {e}")




    def advertise_ospf(self):
        try:
            # Print a message indicating that OSPF configuration retrieval is in progress.
            print("Retrieving OSPF configuration...")

            # Send the command to show the OSPF section of the running configuration
            self.session.sendline('show running-config | section ospf')
            self.session.expect('#', timeout=10) 
    
            # Capture and print the OSPF configuration details
            raw_output = self.session.before
            output_lines = raw_output.splitlines()
            filtered_lines = [line.strip() for line in output_lines if line.strip()]
            
            # If no OSPF configuration lines were found, print a message indicating so.
            if not filtered_lines:
                print("No OSPF configuration found.")
            else:
                # Print a header for the OSPF configuration output.
                print("\n--- OSPF Configuration ---")
                # Print each line of the filtered OSPF configuration.
                for line in filtered_lines:
                    print(line)  # Print each line of the OSPF section
    
        except pexpect.exceptions.TIMEOUT:
            # Handle the timeout exception if the OSPF configuration retrieval takes too long.
            print("Timeout while retrieving OSPF configuration.")
        except Exception as e:
            # Print an error message if any other exception occurs during OSPF configuration retrieval.
            print(f"Error: {e}")

    
    def creating_eigrp(self):
        try:
            # Get the autonomous system(AS) number, network ID, and wildcard
            autonomous_system_number = input("Enter the autonomous system number: ")
            net_id = input("Enter the network address: ")
            wildcard = input("Enter the wildcard mask: ")

            # Enter configuration mode
            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
    
            # Create the OSPF router process
            self.session.sendline(f'router eigrp {autonomous_system_number}')
            self.session.expect(r'\(config-router\)#')
    
            # Configure the network for OSPF
            self.session.sendline(f'network {net_id} {wildcard}')
            self.session.expect(r'\(config-router\)#')
    
            # Exit configuration mode
            self.session.sendline('end')
            self.session.expect(r'#')
    
            # Save the configuration to startup
            self.session.sendline('write memory')
            self.session.expect(r'#')
    
            print('EIGRP configuration created and saved successfully.')
        
        # Handle any exceptions that occur and print an error message
        except Exception as e:
            print(f"Error creating EIGRP: {e}")

    def advertise_eigrp(self):
        try:
            # Send the command to show the eigrp section of the running configuration
            self.session.sendline('show running-config | section eigrp')
            self.session.expect('#', timeout=10)  
    
            # Capture and print the OSPF configuration details
            raw_output = self.session.before
            output_lines = raw_output.splitlines()
            filtered_lines = [line.strip() for line in output_lines if line.strip()]
            
            # Check if any filtered lines exist; if not, print a message indicating no EIGRP configuration was found
            if not filtered_lines:
                print("No eigrp configuration found.")
            else:
                print("\n--- EIGRP Configuration ---")
                for line in filtered_lines:
                    print(line)  # Print each line of the EIGRP section
    
        except pexpect.exceptions.TIMEOUT:
            # Handle timeout exception if the device does not respond in time
            print("Timeout while retrieving EIGRP configuration.")
        except Exception as e:
            # Handle any other exceptions and print an error message
            print(f"Error: {e}")




    # Show IP interface brief
    def show_ip_interface_brief(self):
        try:
            # Send the command to display interface brief status
            self.session.sendline('show ip interface brief')
            self.session.expect('#', timeout=10)  # Wait for the prompt to reappear

            # Capture and print the output
            raw_output = self.session.before
            output_lines = raw_output.splitlines()
            filtered_lines = [line.strip() for line in output_lines if line.strip()]  # Remove empty/whitespace lines

            print("\n--- IP Interface Brief ---")
            for line in filtered_lines:
                # Only print lines that contain "Interface", "up", or "down" to display the relevant interface status
                if "Interface" in line or "up" in line or "down" in line:
                    print(line)  # Print header and relevant lines

        except pexpect.exceptions.TIMEOUT:
            print("Timeout while retrieving interface information.")
        except Exception as e:
            print(f"Error: {e}")


    # Menu for cretaing and advertising interfaces
    def compare_configs_menu(self):
        while True:
            print("\n--- Interface Menu ---")
            print("1. Show IP interface brief")
            print("2. Create a loopback interface")
            print("3. Create an OSPF")
            print("4. Advertise OSPF")
            print("5. Create an EIGRP")
            print("6. Advertise EIGRP")
            print("7. Exit")
            
            # Prompt the user to choose an option
            option = input('Choose an option: ') 

            # Call the appropriate method based on the user's selection
            if option == '1':
                self.show_ip_interface_brief()  # Show the IP interface brief
            elif option == '2':
                self.creating_loopback() # Create a loopback interface (method assumed to be defined elsewhere)
            elif option == '3':
                self.creating_ospf() # Create an OSPF configuration (method assumed to be defined elsewhere)
            elif option == '4':
                self.advertise_ospf() # Advertise OSPF configuration (method assumed to be defined elsewhere)
            
            elif option == '5':
                self.creating_eigrp() # Create an EIGRP configuration
            
            elif option == '6':
                self.advertise_eigrp() # Advertise EIGRP configuration
             # Exit the loop and end the menu
            elif option == '7':
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
            print("SSH SESSION SELECTED")
            host_ip = input('Enter IP address: ')
            username = input('Enter username: ')
            password = input('Enter password: ')
            hostname = input('Enter new hostname: ')
            enable_password = input('Enter enable password (if any): ')
            
            # Create an instance of the SSH session class and start the session
            ssh = SSHTONetworkSession(host_ip, username, password, hostname, enable_password)
            ssh.ssh_session()

        elif option == 'b':
            print('Session cancelled. Goodbye.')
            break

        else:
            print("Invalid option.")


# Entry point of the program
if __name__ == "__main__":
    menu() # Call the menu function to start the program
