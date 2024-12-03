from flask import Flask, request, render_template_string
import difflib  # To handle the comparisons
import pexpect  # To handle SSH session

# Flask App Initialization
app = Flask(__name__)

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
            return False

        self.session.sendline(self.password)
        result = self.session.expect(['>', '#', pexpect.TIMEOUT, pexpect.EOF])
        if result != 0:
            print('Authentication failed.')
            return False

        # Enter enable mode
        self.session.sendline('enable')
        result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
        if result == 0:
            self.session.sendline(self.enable_password)
            result = self.session.expect('#')
        if result != 0:
            print('Enable mode failed.')
            return False

        # Enter configuration mode
        self.session.sendline('configure terminal')
        result = self.session.expect(r'\(config\)#')
        if result != 0:
            print('Config mode failed.')
            return False

        # Set hostname
        self.session.sendline(f'hostname {self.hostname}')
        result = self.session.expect(rf'{self.hostname}\(config\)#')
        if result == 0:
            print('Hostname set successfully.')
        else:
            print('Failed to set hostname.')
            return False

        # Exit configuration mode
        self.session.sendline('exit')
        print('Session ready for further commands.')
        return True

    # Method to execute arbitrary commands
    def run_command(self, command):
        try:
            self.session.sendline(command)
            self.session.expect('#', timeout=10)
            output = self.session.before
            return output
        except pexpect.exceptions.TIMEOUT:
            return "Command execution timed out."
        except Exception as e:
            return f"Error executing command: {e}"

# Global SSH Session Object
ssh_session = None

# HTML Template for Web Interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Web CLI Interface</title>
</head>
<body>
    <h1>Network Device Web CLI</h1>
    <form method="post">
        <label for="command">Enter Command:</label><br>
        <input type="text" id="command" name="command" required><br><br>
        <button type="submit">Run Command</button>
    </form>
    {% if output %}
    <h2>Command Output:</h2>
    <pre>{{ output }}</pre>
    {% endif %}
</body>
</html>
"""

# Flask Route for Web CLI
@app.route("/", methods=["GET", "POST"])
def web_cli():
    global ssh_session
    output = None

    # Handle Command Submission
    if request.method == "POST":
        command = request.form.get("command")
        if ssh_session:
            output = ssh_session.run_command(command)
        else:
            output = "SSH session is not active. Please restart the program."

    return render_template_string(HTML_TEMPLATE, output=output)

# Menu to start SSH session
def menu():
    global ssh_session

    while True:
        print('--------- MENU ---------')
        print('a. Start SSH Session')
        print('b. Start Web Interface')
        print('c. Exit')

        option = input('Choose an option: ')

        if option == 'a':
            print("SSH SESSION SELECTED")
            host_ip = input('Enter IP address: ')
            username = input('Enter username: ')
            password = input('Enter password: ')
            hostname = input('Enter new hostname: ')
            enable_password = input('Enter enable password (if any): ')

            ssh_session = SSHTONetworkSession(host_ip, username, password, hostname, enable_password)
            if ssh_session.ssh_session():
                print("SSH session established successfully.")
            else:
                print("Failed to establish SSH session.")
        elif option == 'b':
            if ssh_session:
                print("Starting Web Interface. Open your browser at http://127.0.0.1:5000/")
                app.run(debug=True)
            else:
                print("Start an SSH session first.")
        elif option == 'c':
            print('Session cancelled. Goodbye.')
            break
        else:
            print("Invalid option.")

# Entry point of the program
if __name__ == "__main__":
    menu()
