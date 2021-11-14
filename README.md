<div align="center">
  <a href="https://aquila.network">
    <img
      src="https://user-images.githubusercontent.com/19545678/133918727-5a37c6be-676f-427b-8c86-dd50f58d1287.png"
      alt="Aquila Network Logo"
      height="64"
    />
  </a>
  <br />
  <p>
    <h3>
      <b>
        Aquila X (Community Edition)
      </b>
    </h3>
  </p>
  <p>
    <b>
      A no-brainer user interface to Aquila Network Ecosystem
    </b>
  </p>
  <br/>
</div>

Aquila X is the gateway to Aquila Network and it's applications. Here is where Aquila X fits in the entire ecosystem:
<div align="center">
  <img
    src="https://user-images.githubusercontent.com/19545678/133918445-fe8aab2a-0eb3-483a-bac0-dd6125adddeb.png"
    alt="Aquila DB Architecture"
    height="400"
  />
 <br/>
</div>

# Install
Follow below steps and you are all set.

Alternatively, follow this [video tutorial](https://chrome-ext-aquila.s3-ap-southeast-1.amazonaws.com/aquila+network+-+setup+Aquila+X.mov).
## Step 1. Chrome extension
### Install from web store (recommended)
[<img height=46px src="https://user-images.githubusercontent.com/68724239/111738541-92476300-88a7-11eb-8444-3f2baa515b9c.png"/>](https://chrome.google.com/webstore/detail/aquila-x/albdahjdcmldbcpjmbnbcbckgndaibnk)
[<img height=46px src="https://user-images.githubusercontent.com/19545678/137582002-85df2d6f-2ad5-43ca-a673-04f4925b8c41.png"/>](https://addons.mozilla.org/en-US/firefox/addon/aquilax/)
### Install from source code (alternative option)
- `git clone https://github.com/Aquila-Network/AquilaX-browser-extension`
- in Chrome / Chromium / Brave browser, go to `chrome://extensions/` and enable "developer mode"
- click "Load unpacked" button and select "chrome" directory from the cloned repository above. You can make sure the extension gets installed when https://aquila.network website is opened automatically.
## Step 2. Server (Debian / Ubuntu)
> Prerequisites: You need [Docker and Docker-compose already installed](https://gist.github.com/freakeinstein/23360053b2c33630b4417549f8e82577) in your system (4G RAM min. recommended).

Now, run below command and wait a few minutes:
```
wget -O - https://raw.githubusercontent.com/Aquila-Network/AquilaX-CE/main/setup_aquilax.sh | /bin/bash
```
Once the installation is completed, visit `http://<localhost / server IP>`

In chrome extension, set the endpoint to `http://<localhost / server IP>/api/`

# Considerations
## 1. Security
This software is still in its alpha version. Any wire security measures (inc. ssl, vpn) should be concern of and must be employed by the user.
## 2. Changes
Current implementations of Aquila Network Modules comply with latest draft specifications. Changes are subject to specification updates.
