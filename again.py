import pexpect  # To handle SSH session


# SSH class for managing network sessions
class SSHTONetworkSession:
    def __init__(self, ip_address, username, password, hostname, enable_password=''):
        # Initialize the SSH session with the provided IP address, username, password, and hostname.
        # The enable_password is optional and used for accessing privileged mode.
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.hostname = hostname
        self.enable_password = enable_password  # Password required for 'enable' mode
        self.session = None  # Placeholder for the SSH session object

    # Initiate SSH session
    def ssh_session(self):
        # Spawn an SSH session to the network device using the provided credentials.
        # 'encoding' ensures the output is in UTF-8 format, 'timeout' specifies the session timeout.
        self.session = pexpect.spawn(f'ssh {self.username}@{self.ip_address}', encoding='utf-8', timeout=20)
        
        # Expect to match one of the expected responses: password prompt, timeout, or EOF.
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
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
        if result != 0:
            # If entering enable mode fails, print an error and exit.
            print('Enable mode failed.')
            return

        # Enter configuration mode to begin making changes.
        self.session.sendline('configure terminal')
        result = self.session.expect(r'\(config\)#')
        if result != 0:
            # If entering configuration mode fails, print an error and exit.
            print('Config mode failed.')
            return

        # Set the hostname of the device.
        self.session.sendline(f'hostname {self.hostname}')
        result = self.session.expect(rf'{self.hostname}\(config\)#')
        if result == 0:
            # If the hostname is set successfully, print a confirmation message.
            print('Hostname set successfully.')
        else:
            # If setting the hostname fails, print an error and exit.
            print('Failed to set hostname.')
            return

        # Exit configuration mode and print a readiness message.
        self.session.sendline('exit')
        print('Session ready for further commands.')

        # Call the configuration menu for further actions.
        self.compare_configs_menu()

    # Creating a loopback interface
    # Creating a loopback interface and saving it to startup configuration
    def creating_loopback(self):
        try:
            # Prompt the user to enter the IP address and subnet mask for the loopback interface.
            loopback_address = input("Enter loopback IP address: ")
            subnet = input("Enter subnet mask: ")

            # Enter configuration mode to create the loopback interface.
            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
            self.session.sendline('interface loopback 0')
            self.session.expect(r'\(config-if\)#')

            # Configure the loopback interface with the provided IP address and subnet mask.
            self.session.sendline(f'ip address {loopback_address} {subnet}')
            self.session.expect(r'\(config-if\)#')
            
            # Exit interface configuration mode.
            self.session.sendline('end')
            self.session.expect(r'#')

            # Save the running configuration to the startup configuration to ensure persistence.
            self.session.sendline('write memory')
            self.session.expect(r'#')
            
            # Print a success message if the loopback is created and saved successfully.
            print('Loopback interface created and configuration saved successfully.')
        
        except Exception as e:
            # Print an error message if an exception occurs during loopback creation.
            print(f"Error creating loopback interface: {e}")

    # Creating and saving OSPF configuration
    def creating_ospf(self):
        try:
            # Prompt the user to enter details for OSPF configuration.
            process_id = input("Enter the process ID: ")
            net_id = input("Enter the network address: ")
            wildcard = input("Enter the wildcard mask: ")
            area = input("Enter the area: ")

            # Enter configuration mode to create OSPF configuration.
            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')

            # Create the OSPF router process with the given process ID.
            self.session.sendline(f'router ospf {process_id}')
            self.session.expect(r'\(config-router\)#')

            # Configure the network statement for OSPF.
            self.session.sendline(f'network {net_id} {wildcard} area {area}')
            self.session.expect(r'\(config-router\)#')

            # Exit configuration mode.
            self.session.sendline('end')
            self.session.expect(r'#')

            # Save the configuration to startup configuration.
            self.session.sendline('write memory')
            self.session.expect(r'#')

            # Print a success message if the OSPF configuration is created and saved successfully.
            print('OSPF configuration created and saved successfully.')
        
        except Exception as e:
            # Print an error message if an exception occurs during OSPF configuration.
            print(f"Error creating OSPF: {e}")

    def advertise_ospf(self):
        try:
            # Print a message indicating that OSPF configuration retrieval is in progress.
            print("Retrieving OSPF configuration...")

            # Send the command to show the OSPF section of the running configuration.
            self.session.sendline('show running-config | section ospf')
            self.session.expect('#', timeout=10) 

            # Capture the output before the prompt and process the raw output.
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
