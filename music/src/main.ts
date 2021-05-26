import * as discord from "discord.js";
import dotenv from "dotenv";
import path from "path";

dotenv.config({ path: path.join(__dirname, "../../.env") });
const client = new discord.Client();
const prefix = "-";

client.once("ready", ()=>{
    console.log("Bot is online")
})

client.on("message",(message:discord.Message)=>{
    if(!message.content.startsWith(prefix) || message.author.bot) return;
})

client.login(process.env['TOKEN'])