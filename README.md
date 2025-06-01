<h1 align="center">sᴛʀᴇᴀᴍ ʙᴏᴛ</h1>
<p align="center">
  <a href="https://github.com/svnig7/streambot">
    <img src="https://raw.githubusercontent.com/svnig7/images/refs/heads/main/streambotl.png" alt="Cover Image" width="550">
  </a>
</p>  

### 🍁 About :
<p align='center'>
  This bot provides stream links for Telegram files without the necessity of waiting for the download to complete, offering the ability to store files.
</p>

### ♢ How to Deploy :

<i>Either you could locally host, VPS, or deploy on [Heroku](https://heroku.com)</i>

#### ♢ Click on This Drop-down and get more details

<br>
<details>
  <summary><b>Deploy on Heroku (Paid)  :</b></summary>

- Fork This Repo
- Click on Deploy Easily
- Press the below button to Fast deploy on Heroku

   [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
- Go to <a href="#mandatory-vars">variables tab</a> for more info on setting up environmental variables. </details>

<details>
  <summary><b>Deploy Locally :</b></summary>
<br>

```
git clone https://github.com/svnig7/streambot.git
```
```
cd streambot
```
```
python3 -m venv ./venv
. ./venv/bin/activate
pip install -r requirements.txt
python3 -m streambot
```

- To stop the whole bot,
 do <kbd>CTRL</kbd>+<kbd>C</kbd>

- If you want to run this bot 24/7 on the VPS, follow these steps.
```
sudo apt install tmux -y
tmux
python3 -m streambot
```
- now you can close the VPS and the bot will run on it.

  </details>

<details>
  <summary><b>Deploy using Docker :</b></summary>
<br>
* Clone the repository:
  
  ```
  git clone https://github.com/svnig7/streambot.git
  ```
  ```
  cd streambot
  ```
  
* Build own Docker image:
  
  ```
  docker build -t file-stream .
  ```

* Create ENV and Start Container:

  ```
  docker run -d --restart unless-stopped --name fsb\ -v /PATH/TO/.env:/app/.env \
  -p 8000:8000 \
  file-stream
  ```
  
- if you need to change the variables in .env file after your bot was already started, all you need to do is restart the container for the bot settings to get updated:

  ```
  docker restart fsb
  ```

  </details>

<details>
  <summary><b>Setting up things :</b></summary>

If you're on Heroku, just add these in the Environmental Variables
or if you're Locally hosting, create a file named `.env` in the root directory and add all the variables there.
An example of `.env` file:

```sh
API_ID = 789456
API_HASH = ysx275f9638x896g43sfzx65
BOT_TOKEN = 12345678:your_bot_token
ULOG_CHANNEL = -100123456789
FLOG_CHANNEL = -100123456789
DATABASE_URL = mongodb://admin:pass@192.168.27.1
FQDN = 192.168.27.1
OWNER_ID = 987456321
PORT = 8080
```
</details>

<details>
  <summary><b>Vars and Details :</b></summary>

#### 📝 Mandatory Vars :

* `API_ID` : API ID of your Telegram account, can be obtained from [My Telegram](https://my.telegram.org). `int`
* `API_HASH` : API hash of your Telegram account, can be obtained from [My Telegram](https://my.telegram.org). `str`
* `OWNER_ID` : Your Telegram User ID, Send `/id` to [@missrose_bot](https://telegram.dog/MissRose_bot) to get Your Telegram User ID `int`
* `BOT_TOKEN` : Telegram API token of your bot, can be obtained from [@BotFather](https://t.me/BotFather). `str`
* `FLOG_CHANNEL` : ID of the channel where bot will store all Files from users `int`.
* `ULOG_CHANNEL` : ID of the channel where bot will send logs of New Users`int`.
* `DATABASE_URL` : MongoDB URI for saving User Data and Files List created by user. `str`
* `FQDN` : A Fully Qualified Domain Name if present without http/s. Defaults to `BIND_ADDRESS`. `str`

#### 🗼 MultiClient Vars :
* `MULTI_TOKEN1` : Add your first bot token or session strings here. `str`
* `MULTI_TOKEN2` : Add your second bot token or session strings here. `str`

#### 🪐 Optional Vars :

* `UPDATES_CHANNEL` : Channel Username without `@` to set channel as Update Channel `str`
* `FORCE_SUB_ID` : Force Sub Channel ID, if you want to use Force Sub. start with `-100` `int`
* `FORCE_UPDATES_CHANNEL` : Set to True, so every user have to Join update channel to use the bot. `bool`
* `FORCE_SUB_LINK` : Force Sub Channel Link, if you want to use Force Sub. `str`
* `AUTH_USERS` : Put authorized user IDs to use bot, separated by <kbd>Space</kbd>. `int`
* `FILE_PIC` : To set Image at `/files` command. Defaults to pre-set image. `str`
* `START_PIC` : To set Image at `/start` command. Defaults to pre-set image. `str`
* `VERIFY_PIC` : To set Image at Force Sub Verification. Defaults to pre-set image. `str`
* `PORT` : The port that you want your webapp to be listened to. Defaults to `8080`. `int`

</details>

<details>
  <summary><b>How to Use :</b></summary>

:warning: **Before using the  bot, don't forget to add the bot to the `LOG_CHANNEL` as an Admin**
 
#### ‍☠️ Bot Commands :

```sh
start - ᴛᴏ ᴄʜᴇᴄᴋ ᴛʜᴇ ʙᴏᴛ ɪs ᴀʟɪᴠᴇ ᴏʀ ɴᴏᴛ.
help - ᴛᴏ ɢᴇᴛ ʜᴇʟᴘ ᴍᴇssᴀɢᴇ.
about - ᴛᴏ ᴄʜᴇᴄᴋ ᴀʙᴏᴜᴛ ᴛʜᴇ ʙᴏᴛ.
files - ᴛᴏ ɢᴇᴛ ᴀʟʟ ғɪʟᴇs ʟɪsᴛ ᴏғ ᴜsᴇʀ.
del - ᴛᴏ ᴅᴇʟᴇᴛᴇ ғɪʟᴇs ғʀᴏᴍ ᴅʙ ᴡɪᴛʜ ғɪʟᴇɪᴅ. [ᴀᴅᴍɪɴ]
ban - ᴛᴏ ʙᴀɴ ᴀɴʏ ᴄʜᴀɴɴᴇʟ ᴏʀ ᴜsᴇʀ ᴛᴏ ᴜsᴇ ʙᴏᴛ. [ᴀᴅᴍɪɴ]
unban - ᴛᴏ ᴜɴʙᴀɴ ᴀɴʏ ᴄʜᴀɴɴᴇʟ ᴏʀ ᴜsᴇʀ ᴛᴏ ᴜsᴇ ʙᴏᴛ. [ᴀᴅᴍɪɴ]
status - ᴛᴏ ɢᴇᴛ ʙᴏᴛ sᴛᴀᴛᴜs ᴀɴᴅ ᴛᴏᴛᴀʟ ᴜsᴇʀs. [ᴀᴅᴍɪɴ]
broadcast - ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜsᴇʀs ᴏғ ʙᴏᴛ. [ᴀᴅᴍɪɴ]
```

#### 🍟 Channel Support :

*Bot also Supported with Channels. Just add bot Channel as Admin. If any new file comes in Channel it will edit it with **sᴛʀᴇᴀᴍ / ᴅᴏᴡɴʟᴏᴀᴅ** Button.*

</details>

### ❤️ To :

- [**sᴠɴ**](https://github.com/svnig7) : for his [sᴛʀᴇᴀᴍ ʙᴏᴛ](https://github.com/svnig7/streambot)

---
