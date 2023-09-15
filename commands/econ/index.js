const { Collection } = require('discord.js');
const fs = require('fs');
const { SlashCommandBuilder } = require('@discordjs/builders');

const subcommands = new Collection();

let econCommand = new SlashCommandBuilder()
                    .setName('econ')
                    .setDescription('Economy commands');

const subcommandFiles = fs.readdirSync('./commands/econ').filter(file => file.endsWith('.js'));
for (const file of subcommandFiles) {
    if (file != 'index.js') {
        try {
            const subcommand = require(`./${file}`);
            subcommands.set(`${file}`, subcommand);
            econCommand = subcommand.builder(econCommand);
        } catch (e) {
            console.log('Could not load econ subcommand %s', file);
            console.error(e);
        }
    }
}


const subcommandFolders = fs.readdirSync('./commands/econ',  { withFileTypes: true }).filter((item) => item.isDirectory()).map((item) => item.name);
for (const file of subcommandFolders) {
    try {
        const subcommand = require(`./${file}`);
        subcommands.set(`${file}`, subcommand);
        console.log(file);
        econCommand = subcommand.builder(econCommand);
    } catch (e) {
        console.log('Could not load fun subcommand %s', file);
        console.error(e);
    }
}

module.exports = {
	data: econCommand,
    async execute(interaction) {
        let subcommandName = interaction.options.getSubcommand() + '.js';
        let command = subcommands.get(subcommandName);
        await command.execute(interaction);
	},
};