# AquilaX-CE
Aquila X Community Edition.

# Install
Follow below steps and you are all set.
## 1. Chrome extension
- `git clone https://github.com/Aquila-Network/AquilaX-browser-extension`
- in Chrome / Chromium browser, go to `chrome://extensions/` and enable "developer mode"
- click "Load unpacked" button and select "chrome" directory from the cloned repository above. You can make sure the extension gets installed when https://aquila.network website is opened automatically.
## 2. Server (Debian / Ubuntu)
> Prerequisites: You need [Docker and Docker-compose already installed](https://gist.github.com/freakeinstein/23360053b2c33630b4417549f8e82577) in your system (4G RAM min. recommended).

Now, run below command and wait a few minutes:
```
wget -O - https://raw.githubusercontent.com/Aquila-Network/AquilaX-CE/main/setup_aquilax.sh | /bin/bash
```
Once the installation is completed, visit `http://<localhost / server IP>`

In chrome extension, set the endpoint to `http://<localhost / server IP>/api/`
