import pexpect  # To handle SSH sessions

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
        try:
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
            result = self.session.expect(r'\\(config\\)#')
            if result != 0:
                print('Config mode failed.')
                return

            # Set hostname
            self.session.sendline(f'hostname {self.hostname}')
            result = self.session.expect(rf'{self.hostname}\\(config\\)#')
            if result == 0:
                print('Hostname set successfully.')
            else:
                print('Failed to set hostname.')
                return

            # Exit configuration mode
            self.session.sendline('exit')
            self.session.expect('#')
            print('Session ready for further commands.')
            self.menu()
        except Exception as e:
            print(f"An error occurred during SSH session setup: {e}")

    # Creating a loopback interface
    def creating_loopback(self):
        try:
            # Get loopback IP and subnet
            loopback_address = input("Enter loopback IP address: ")
            subnet = input("Enter subnet mask: ")

            # Configure the loopback interface
            self.session.sendline('configure terminal')
            self.session.expect(r'\\(config\\)#')
            self.session.sendline('interface loopback 0')
            self.session.expect(r'\\(config-if\\)#')
            self.session.sendline(f'ip address {loopback_address} {subnet}')
            self.session.expect(r'\\(config-if\\)#')
            print('Loopback interface created successfully.')
            self.session.sendline('no shutdown')
            self.session.expect(r'\\(config-if\\)#')

            # Exit configuration mode
            self.session.sendline('exit')  # Exit interface config
            self.session.expect(r'\\(config\\)#')
            self.session.sendline('exit')  # Exit global config
            self.session.expect('#')

            # Save the configuration
            self.save_config()
            print("Configuration saved successfully.")
        except pexpect.TIMEOUT:
            print("Timeout occurred while creating loopback interface.")
        except Exception as e:
            print(f"An error occurred while creating the loopback interface: {e}")

    def save_config(self):
        try:
            # Save the running configuration to the startup configuration
            self.session.sendline('write memory')
            self.session.expect('#')
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

    # Menu for configuring the device
    def menu(self):
        while True:
            print("\n--- Configurations ---")
            print("1. Show IP interface brief")
            print("2. Create a loopback interface")
            print("3. Create OSPF")
            print("4. Advertise OSPF")
            print("5. Create EIGRP")
            print("6. Advertise EIGRP")
            print("7. Create RIP")
            print("8. Advertise RIP")
            print("9. Exit")

            option = input('Choose an option: ')

            if option == '1':
                self.show_ip_interface_brief()
            elif option == '2':
                self.creating_loopback()
            elif option == '3':
                self.creating_ospf()
            elif option == '4':
                self.advertise_ospf()
            elif option == '5':
                self.creating_eigrp()
            elif option == '6':
                self.advertise_eigrp()
            elif option == '7':
                self.creating_rip()
            elif option == '8':
                self.advertise_rip()
            elif option == '9':
                print("Exiting configuration menu.")
                break
            else:
                print("Invalid option.")

    def creating_ospf(self):
        try:
            process_id = input("Enter the process ID: ")
            net_id = input("Enter the network address: ")
            wildcard = input("Enter the wildcard mask: ")
            area = input("Enter the area: ")

            self.session.sendline('configure terminal')
            self.session.expect(r'\\(config\\)#')
            self.session.sendline(f'router ospf {process_id}')
            self.session.expect(r'\\(config-router\\)#')
            self.session.sendline(f'network {net_id} {wildcard} area {area}')
            self.session.expect(r'\\(config-router\\)#')
            print('OSPF successfully created.')

            self.session.sendline('exit')
            self.session.expect(r'\\(config\\)#')
            self.session.sendline('exit')
            self.session.expect('#')

            self.save_config()
        except Exception as e:
            print(f"An error occurred while creating OSPF: {e}")

    def creating_eigrp(self):
        try:
            autonomous_system_number = input("Enter the autonomous system number: ")
            net_id = input("Enter the network address: ")
            wildcard = input("Enter the wildcard mask: ")

            self.session.sendline('configure terminal')
            self.session.expect(r'\\(config\\)#')
            self.session.sendline(f'router eigrp {autonomous_system_number}')
            self.session.expect(r'\\(config-router\\)#')
            self.session.sendline(f'network {net_id} {wildcard}')
            self.session.expect(r'\\(config-router\\)#')
            print('EIGRP successfully created.')

            self.session.sendline('exit')
            self.session.expect(r'\\(config\\)#')
            self.session.sendline('exit')
            self.session.expect('#')

            self.save_config()
        except Exception as e:
            print(f"An error occurred while creating EIGRP: {e}")

    def creating_rip(self):
        try:
            version = input("Specify version (1/2): ")
            net_id = input("Enter the network address: ")

            self.session.sendline('configure terminal')
            self.session.expect(r'\\(config\\)#')
            self.session.sendline('router rip')
            self.session.expect(r'\\(config-router\\)#')
            self.session.sendline(f'network {net_id}')
            self.session.expect(r'\\(config-router\\)#')
            self.session.sendline(f'version {version}')
            self.session.expect(r'\\(config-router\\)#')
            print('RIP successfully created.')

            self.session.sendline('exit')
            self.session.sendline('exit')
            self.session.expect(r'\\(config\\)#')
            self.session.sendline('exit')
            self.session.expect('#')

            self.save_config()
        except Exception as e:
            print(f"An error occurred while creating RIP: {e}")
