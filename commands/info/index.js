const { Collection } = require('discord.js');
const fs = require('fs');
const { SlashCommandBuilder } = require('@discordjs/builders');

const subcommands = new Collection();

let infoCommand = new SlashCommandBuilder()
                    .setName('info')
                    .setDescription('Info commands');

const subcommandFiles = fs.readdirSync('./commands/info').filter(file => file.endsWith('.js'));
for (const file of subcommandFiles) {
    if (file != 'index.js') {
        try {
            const subcommand = require(`./${file}`);
            subcommands.set(`${file}`, subcommand);
            infoCommand = subcommand.builder(infoCommand);
        } catch (e) {
            console.log('Could not load info subcommand %s', file);
            console.error(e);
        }
    }
}


const subcommandFolders = fs.readdirSync('./commands/info',  { withFileTypes: true }).filter((item) => item.isDirectory()).map((item) => item.name);
for (const file of subcommandFolders) {
    try {
        const subcommand = require(`./${file}`);
        subcommands.set(`${file}`, subcommand);
        console.log(file);
        infoCommand = subcommand.builder(infoCommand);
    } catch (e) {
        console.log('Could not load fun subcommand %s', file);
        console.error(e);
    }
}

module.exports = {
	data: infoCommand,
    async execute(interaction) {
        let subcommandName = interaction.options.getSubcommand() + '.js';
        let command = subcommands.get(subcommandName);
        await command.execute(interaction);
	},
};