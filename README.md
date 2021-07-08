<h1 align="center">
  <a href="https://GitHub.com/AakashSharma7269/erin.git"><img src="https://raw.githubusercontent.com/AakashSharma7269/erin/main/erin.png?token=AOP54YUJCVK5WQY5LQ6AK5TAWOXYK" alt="Erin. - Discord Bot"></a>
  <p>Erin. Discord Bot</p>
</h1>

<h4 align="center">Music, Moderation, Trivia, Economy, Gambling, and NSFW commands!</h4>
<h4 align="center">Erin bot TOS: https://gist.github.com/actualdankcoder/d837174c5397101268d77bf573a7434f</h4>

<a href="https://github.com/Rapptz/discord.py/">
  <img src="https://img.shields.io/badge/discord-py-blue.svg" alt="discord.py">
</a>

<a href="https://www.python.org/downloads">
  <img src="https://img.shields.io/badge/development-(beta)-blue.svg" alt="dev badge">
</a>

<a href="https://www.python.org/downloads">
  <img src="http://ForTheBadge.com/images/badges/made-with-python.svg" height=20 alt="dev badge">
</a>

<h2>Join our Discord servers:</h2>

<ul>
  <li>
    <a href="https://www.discord.gg/davie504">Davie504's server</a>
    <div>
      <a href="https://discord.gg/davie504">
        <img src="https://discordapp.com/api/guilds/737690513876058203/widget.png?style=shield" alt="Davie504's Server">
      </a>
    </div>
  </li>
  <li>
    <a href="https://discord.gg/F5ey2M5GT">Support Discord Server</a>
    <div>
    <a href="https://discord.gg/F5ey2M5GTg">
      <img src="https://discordapp.com/api/guilds/809748698123993118/widget.png?style=shield" alt="Support Discord Server">
    </a>
    </div>
  </li>
</ul>

<p>
  Feel free to use Erin to learn how to make a bot!
  Make a GitHub issue if you want a new feature to be added to Erin.
  <br>
  Make sure to link the GitHub page or credit Erin if u do decide to fork or host a local instance of Erin!
</p>

<h2>Contribute</h2>

  Hey! we're certainly not pros when it comes to bot making, the bot does have some very clunky parts when it comes to caching and general code quality. We are working around the clock to make it better.
  We appreciate any support we can get from the community, including Patreon donations (coming soon!) and/or GitHub PR's with code quality fixes!!!
  <br>
  Note: The API, dashboard, and music module are still under development! and credits to <a href="https://nekos.life">https://nekos.life </a> for the image API!

  <h3>Monetary support</h3>

  Patreon donations are coming soon!

  <h3>Run locally</h3>

  If you want to run Erin locally, you'll need to set a couple of things up.

  <h4>Step 1: Fork, clone, and open on your machine</h4>

  You'll first want fork the repo and clone it to your machine!
  First, go to <a href="https://github.com/AakashSharma7269/erin">https://github.com/AakashSharma7269/erin </a> and click the <code>Fork</code> button in the top right.
  This will open your newly forked repo in another tab.
  Then, clone your repo to your machine.
  You can use the command line (via <code>git</code>) but I find it easier to have an IDE like PyCharm manage this for me.
  <br>
  Then, create a virtual environment (highly recommended but not required) and install all the dependencies in <a href="https://github.com/AakashSharma7269/erin/blob/main/requirements.txt"><code>requirements.txt</code></a>.

  <h4>Step 2: Download and install MongoDB</h4>

  Erin the bot uses MongoDB for storing data.
  If you do not have it installed on your machine, go to <a href=https://www.mongodb.com/try/download>https://www.mongodb.com/try/download </a> and download a server installer for your OS.
  (The community version is free and works well) Then run the installer.
  (It will take a couple of minutes, so you can just keep it running in the background)
  Once it is finished you can close out the installer.

  You can also optionally do the following: 
  1. Install docker.
  2. `docker image pull mongo` 
  3. `docker run --name erinDb -d -p <port of choice>:27017 -v <volume path>:/data/db/ mongo`
  4.  Edit the `CONNECTIONURI` field in the .env file and set it to `mongodb://localhost:<the port you chose in step 3>`
  5.  Step 4 should get you ready for development. If you restart your development machine then run `docker start erinDb` to start the container.
  <br>Note: On linux you will need to run `sudo systemctl start docker` and `sudo systemctl enable docker` 
  <br>
	I personally prefer docker as i don't need to install all the software i need individually, instead i can just install docker and pull the image as required (if it's available in the docker repo).
  <h4>Step 3: Create a Discord bot.</h4>

  Create a new application in your <a href="https://discord.com/developers/applications">developer portal page</a> on Discord and call it something like "ErinTestApp."
  Then create a new bot for that application and call it something like "ErinTest."
  If you are unsure of how to create a bot, I find this guide by <a href="https://realpython.com/how-to-make-a-discord-bot-python/#how-to-make-a-discord-bot-in-the-developer-portal">RealPython</a> helpful.
  Once you are finished, add the bot to a testing server which you don't really care about.
  For the permissions, you can just select <code>administrator</code> instead of manually selecting them all.
  You will also need to go to the "bot" tab and enable the server members and presence intents.

  <h4>Step 4: Fill in the variables in the <code>.env</code> file</h4>

  At the repo root, create a new file and call it <code>.env</code>.
  (you probably shouldn't commit it so don't add it / gitignore it)
  Copy and paste the contents of <a href="https://github.com/AakashSharma7269/erin/blob/main/demo.env"><code>demo.env</code></a> into the <code>.env</code> file you just made and fill in the Discord bot token and type <code>localhost</code> for the MongoDB URI, or another URI if you are using a database hosted in the cloud.

  <h4>Step 5: Run!</h4>

  Run the bot by running <code>starterin.sh</code> or <code>starterin.bat</code> depending on your OS. (You can also additionally run <code>yarn dev</code> or <code>npm run dev</code>.)
