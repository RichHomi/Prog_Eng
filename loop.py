def main_menu(ssh_session):
    while True:
        print("\n--- Main Menu ---")
        print("1. Create Loopback Interface")
        print("2. Configure OSPF")
        print("3. Display OSPF Configuration")
        print("4. Configure EIGRP")
        print("5. Display EIGRP Configuration")
        print("6. Display Interfaces")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            ssh_session.creating_loopback()
        elif choice == '2':
            ssh_session.creating_ospf()
        elif choice == '3':
            ssh_session.advertise_ospf()
        elif choice == '4':
            ssh_session.creating_eigrp()
        elif choice == '5':
            ssh_session.advertise_eigrp()
        elif choice == '6':
            ssh_session.display_interfaces()
        elif choice == '7':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

# Sample instantiation and method call
ip_address = input("Enter device IP address: ")
username = input("Enter username: ")
password = input("Enter password: ")
hostname = input("Enter hostname: ")

session = SSHTONetworkSession(ip_address, username, password, hostname)
session.ssh_session()
main_menu(session)
