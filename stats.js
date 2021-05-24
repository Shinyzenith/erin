async function stats(message){
	const notSupported = "Unavailable at this current time";
      const full = '█'
      const empty = '░'
      const precision = 20
      
      const freeRAM = os.freemem()
      const usedRAM = os.totalmem() - freeRAM;
      
      const diagramMaker = (used, free) => {
        const total = used + free;
        used = Math.round((used / total) * precision)
        free = Math.round((free / total) * precision)
        return full.repeat(used) + empty.repeat(free)
      }
      
      let cpuUsage;
      
      const p1 = osu.cpu.usage().then(cpuPercentage => {
        cpuUsage = cpuPercentage;
      })
      
      let processes;
      
      const p2 = osu.proc.totalProcesses().then(process => {
        processes = process;
      })
      
      let driveUsed, driveFree;
      
      const p3 = osu.drive.info().then(i => {
        driveUsed = i.usedPercentage;
        driveFree = i.freePercentage;
      }).catch(() => {
        driveUsed = false;
      })
      
      let networkUsage, networkUsageIn, networkUsageOut;
      
      const p4 = osu.netstat.inOut().then(i => {
        networkUsage = i.total;
        networkUsageIn = networkUsage.inputMb;
        networkUsageOut = networkUsage.outputMb;
      }).catch(() => {
        networkUsage = false;
      })
      
      await Promise.all([p1, p2, p3, p4]);
      
      let totalSeconds = (client.uptime / 1000);
      let days = Math.floor(totalSeconds / 86400);
      totalSeconds %= 86400;
      let hours = Math.floor(totalSeconds / 3600);
      totalSeconds %= 3600;
      let minutes = Math.floor(totalSeconds / 60);
      let seconds = Math.floor(totalSeconds % 60);
      const cores = os.cpus().length
      const cpuModel = os.cpus()[0].model
    let cmdsran = db.get('cmdsran_')

      const statsembed = new Discord.MessageEmbed()
        .setColor('RANDOM')
        .addField(`Main Package Version:`, `Discord.js Version: 12.2.0\nNode.js Version: 12.x \n Total Packages: ${Object.keys(require("./package.json").dependencies).length}`)
        .addField(`Used:`,(`RAM: ${diagramMaker(usedRAM, freeRAM)} [${Math.round(100 * usedRAM / (usedRAM + freeRAM))}%]\n`+
        `CPU: ${diagramMaker(cpuUsage, 100-cpuUsage)} [${Math.round(cpuUsage)}%]\n`+
        `BOT PROCESS: ${(process.memoryUsage().heapUsed / 1000000).toFixed(2)}MB\n`+
        `STORAGE: ${driveUsed ? `${diagramMaker(driveUsed, driveFree)} [${Math.round(driveUsed)}%]` : notSupported}\n`+
        `PROCESSES: ${processes != 'not supported'? processes : notSupported}`).trim())
        .addField(`Machine Specs:`,`CPU Cores: ${cores}\nCPU Model: ${cpuModel}\nCPU Speed: ${os.cpus()[0].speed}MHz
    	${osu.os.platform() != "win32" ? `Storage: ${diagramMaker(driveUsed,driveFree)} [${driveUsed}%]`: ""}`)
        .addField(`System Specs:`,`System Type: ${osu.os.type()}\nSystem Architecture: ${osu.os.arch()}\nSystem Platform: ${osu.os.platform()}`)
        .addField(`Bot`,`Uptime: ${days}d, ${hours}h, ${minutes}m, ${seconds}s\n Ping: ${client.ws.ping}ms \n Commands Ran: ${cmdsran}`)
        .addField(`Info`, `Servers : ${client.guilds.cache.size}\n Channels : ${client.channels.cache.size}\n Users : ${client.users.cache.size}`);    
            
	  message.channel.send(statsembed);
};