import difflib  # To handle the comparisons
import pexpect  # To handle SSH session


# SSH class for managing network sessions
class SSHTONetworkSession:
    def __init__(self, ip_address, username, password, hostname, enable_password=''):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.hostname = hostname
        self.enable_password = enable_password
        self.session = None

    # Initiate SSH session
    def ssh_session(self):
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

        # Enter enable mode
        self.session.sendline('enable')
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
        if result == 0:
            self.session.sendline(self.enable_password)
            result = self.session.expect('#')
        if result != 0:
            print('Enable mode failed.')
            return

        # Enter configuration mode
        self.session.sendline('configure terminal')
        result = self.session.expect(r'\(config\)#')
        if result != 0:
            print('Config mode failed.')
            return

        # Set hostname
        self.session.sendline(f'hostname {self.hostname}')
        result = self.session.expect(rf'{self.hostname}\(config\)#')
        if result == 0:
            print('Hostname set successfully.')
        else:
            print('Failed to set hostname.')
            return

        # Exit configuration mode
        self.session.sendline('exit')
        print('Session ready for further commands.')
        self.compare_configs_menu()

    # Creating a loopback interface
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
            self.session.sendline(f'ip address {loopback_address} {subnet}')
            self.session.expect(r'\(config-if\)#')
            
            # Save the configuration to startup to make it persistent
            self.session.sendline('end')  # Exit interface configuration mode
            self.session.expect(r'#')
            self.session.sendline('write memory')  # Save the running config to startup config
            self.session.expect(r'#')
            
            print('Loopback interface created and configuration saved successfully.')
            
            
    
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
    
        except Exception as e:
            print(f"Error creating OSPF: {e}")




    def advertise_ospf(self):
        try:
            print("Retrieving OSPF configuration...")
            # Send the command to show the OSPF section of the running configuration
            self.session.sendline('show running-config | section ospf')
            self.session.expect('#', timeout=10)  # Adjust timeout as needed
    
            # Capture and print the OSPF configuration details
            raw_output = self.session.before
            output_lines = raw_output.splitlines()
            filtered_lines = [line.strip() for line in output_lines if line.strip()]
    
            if not filtered_lines:
                print("No OSPF configuration found.")
            else:
                print("\n--- OSPF Configuration ---")
                for line in filtered_lines:
                    print(line)  # Print each line of the OSPF section
    
        except pexpect.exceptions.TIMEOUT:
            print("Timeout while retrieving OSPF configuration.")
        except Exception as e:
            print(f"Error: {e}")

    
    def advertise_eigrp(self):
        try:
            print("Retrieving EIGRP network configurations...")
            # Send the command to show the lines that include network statements in the running configuration
            self.session.sendline('show running-config | include network')
            self.session.expect('#', timeout=10)  # Adjust timeout as needed
    
            # Capture and print the network configuration details
            raw_output = self.session.before
            output_lines = raw_output.splitlines()
            filtered_lines = [line.strip() for line in output_lines if line.strip()]
    
            if not filtered_lines:
                print("No EIGRP network configuration found.")
            else:
                print("\n--- EIGRP Network Configuration ---")
                for line in filtered_lines:
                    print(line)  # Print each line of the network section, including wildcard mask
    
        except pexpect.exceptions.TIMEOUT:
            print("Timeout while retrieving EIGRP network configuration.")
        except Exception as e:
            print(f"Error: {e}")


   def advertise_eigrp(self):
        try:
            print("Retrieving EIGRP configuration...")
            # Send the command to show the EIGRP section of the running configuration
            self.session.sendline('show running-config | section eigrp')
            self.session.expect('#', timeout=10)  # Adjust timeout as needed
    
            # Capture and print the EIGRP configuration details
            raw_output = self.session.before
            output_lines = raw_output.splitlines()
            filtered_lines = [line.strip() for line in output_lines if line.strip()]
    
            if not filtered_lines:
                print("No EIGRP configuration found.")
            else:
                print("\n--- EIGRP Configuration ---")
                for line in filtered_lines:
                    print(line)  # Print each line of the EIGRP section
    
        except pexpect.exceptions.TIMEOUT:
            print("Timeout while retrieving EIGRP configuration.")
        except Exception as e:
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
                if "Interface" in line or "up" in line or "down" in line:
                    print(line)  # Print header and relevant lines

        except pexpect.exceptions.TIMEOUT:
            print("Timeout while retrieving interface information.")
        except Exception as e:
            print(f"Error: {e}")


    # Menu for comparing configurations
    def compare_configs_menu(self):
        while True:
            print("\n--- Compare Configurations ---")
            print("1. Compare running config with local version")
            print("2. Compare running config with startup config on device")
            print("3. Show IP interface brief")
            print("4. Create a loopback interface")
            print("5. Create an OSPF")
            print("6. Advertise OSPF")
            print("7. Create an EIGRP")
            print("8. Advertise EIGRP")
            print("9. Exit")

            option = input('Choose an option: ')

            if option == '1':
                self.compare_configs('labs_assignment_ssh.txt', 'devices-06.txt')
            elif option == '2':
                self.compare_with_startup_config_ssh()
            elif option == '3':
                self.show_ip_interface_brief()
            elif option == '4':
                self.creating_loopback()
            
            elif option == '5':
                self.creating_ospf()
            
            elif option == '6':
                self.advertise_ospf()
            
            elif option == '7':
                self.creating_eigrp()

            elif option == '8':
                self.advertise_eigrp()

            elif option == '9':
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

            ssh = SSHTONetworkSession(host_ip, username, password, hostname, enable_password)
            ssh.ssh_session()

        elif option == 'b':
            print('Session cancelled. Goodbye.')
            break

        else:
            print("Invalid option.")


# Entry point of the program
if __name__ == "__main__":
    menu()
