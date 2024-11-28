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




    def save_config(self):
        try:
            self.session.sendline('write memory')
            self.session.expect('#', timeout=10)
            print("Configuration saved successfully.")
        except pexpect.exceptions.TIMEOUT:
            print("Timeout occurred while saving the configuration.")
        except pexpect.exceptions.EOF:
            print("Connection closed unexpectedly during save.")
        except Exception as e:
            print(f"An error occurred while saving the configuration: {e}")


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

            

    # Menu for comparing configurations
    def menu(self):
        while True:
            print("\n--- Configurations ---")
            print("1. Show IP interface brief")
            print("2. Create a loopback interface")
            print("3. Create OSPF")
            print("4. Advertise OSPF")
            print("5. Create EIGRP")
            print("6. Advertise EIGRP")
            print("7. Create RIP.")
            print("8. Advertise RIP")
            print("9. Exit")

            option = input('Choose an option: ')

            if option == '1':
                # Show IP interface brief, including the new loopback
                self.show_ip_interface_brief()
                
            
            elif option == '2':
                # Create a loopback interface
                self.creating_loopback()

            elif option == '3':
                self.creating_ospf()
                
            elif option =='4':
                self.advertise_OSPF()

            elif option =='5':
                self.creating_eigrp()
            
            elif option =='6':
                self.advertise_EIGRP()
            
            elif option =='7':
                self.creating_rip()

            elif option =='8':
                self.advertise_RIP()



            elif option == '9':
                print("Exiting comparison menu.")
                break
            else:
                print("Invalid option.")


    
    
    

    def creating_ospf(self):
        try:
            # Get the process ID, network ID, wildcard, and area from the user
            process_id = input("Enter the process ID: ")
            net_id = input("Enter the network address: ")
            wildcard = input("Enter the wildcard mask: ")
            area = input("Enter the area: ")

            # Configure OSPF
            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
            self.session.sendline(f'router ospf {process_id}')
            self.session.expect(r'\(config-router\)#')
            self.session.sendline(f'network {net_id} {wildcard} area {area}')
            self.session.expect(r'\(config-router\)#')
            print('OSPF successfully created.')

            # Exit configuration mode
            self.session.sendline('exit')  # Exit OSPF config
            self.session.expect(r'\(config\)#')
            self.session.sendline('exit')  # Exit global config
            self.session.expect('#')

            # Save the configuration to ensure it persists
            self.session.sendline('write memory')  # Save the configuration
            self.session.expect('#')
            print("Configuration saved successfully.")

        except Exception as e:
            print(f"An error occurred while creating OSPF: {e}")

    
    def creating_eigrp(self):
        try:
            # Get the autonomous system(AS) number, network ID, and wildcard
            autonomous_system_number = input("Enter the autonomous system number: ")
            net_id = input("Enter the network address: ")
            wildcard = input("Enter the wildcard mask: ")

            # Configure EIGRP
            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
            self.session.sendline(f'router eigrp {autonomous_system_number}')
            self.session.expect(r'\(config-router\)#')
            self.session.sendline(f'network {net_id} {wildcard}')
            self.session.expect(r'\(config-router\)#')
            print('EIGRP successfully created.')

            # Exit configuration mode
            self.session.sendline('exit')  # Exit EIGRP config
            self.session.expect(r'\(config\)#')
            self.session.sendline('exit')  # Exit global config
            self.session.expect('#')

            # Save the configuration to ensure it persists
            self.session.sendline('write memory')  # Save the configuration
            self.session.expect('#')
            print("Configuration saved successfully.")

        except Exception as e:
            print(f"An error occurred while creating EIGRP: {e}")

    
    def creating_rip(self):
        try:
            version = input("Specify version (1/2): {version} ")
            net_id = input("Enter the network address: ")

            # Configure RIP
            self.session.sendline('configure terminal')
            self.session.expect(r'\(config\)#')
            self.session.sendline(f'router rip')
            self.session.expect(r'\(config-router\)#')
            self.session.sendline(f'network {net_id}')
            self.session.expect(r'\(config-router\)#')
            print('RIP successfully created.')

            # Exit configuration mode
            self.session.sendline('exit')
            self.session.expect(r'\(config\)#')
            self.session.sendline('exit')  # Exit global config
            self.session.expect('#')

            # Save the configuration to ensure it persists
            self.session.sendline('write memory')  # Save the configuration
            self.session.expect('#')
            print("Configuration saved successfully.")

        except Exception as e:
            print(f"An error occurred while creating rip: {e}")


    def advertise_RIP(self):
        try:
            self.session.sendline('show running-config | include router rip')
            self.session.expect('#')  # Wait for the prompt
            output = self.session.before  # Capture the output

            # Print the OSPF configuration
            print("\n--- rip Configuration ---")
            print(output)
            
        except Exception as e:
            print(f"An error occurred while fetching rip configuration: {e}")
        



        
    

    def advertise_EIGRP(self):
        try:
            self.session.sendline('show running-config | include router eigrp')
            self.session.expect('#')  # Wait for the prompt
            output = self.session.before  # Capture the output

            # Print the OSPF configuration
            print("\n--- eigrp Configuration ---")
            print(output)
            
        except Exception as e:
            print(f"An error occurred while fetching eigrp configuration: {e}")

            


    def advertise_OSPF(self):
        try:
            # Send the command to display the OSPF configuration (including the 'network' statements)
            self.session.sendline('show running-config | include router ospf')
            self.session.expect('#')  # Wait for the prompt
            output = self.session.before  # Capture the output

            # Print the OSPF configuration
            print("\n--- OSPF Configuration ---")
            print(output)
            
        except Exception as e:
            print(f"An error occurred while fetching OSPF configuration: {e}")




            



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
