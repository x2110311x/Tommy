const { Collection } = require('discord.js');
const fs = require('fs');
const { SlashCommandBuilder } = require('@discordjs/builders');

const subcommands = new Collection();

let tagsCommand = new SlashCommandBuilder()
                    .setName('tags')
                    .setDescription('Tag commands');

const subcommandFiles = fs.readdirSync('./commands/tags').filter(file => file.endsWith('.js'));
for (const file of subcommandFiles) {
    if (file != 'index.js') {
        try {
            const subcommand = require(`./${file}`);
            subcommands.set(`${file}`, subcommand);
            tagsCommand = subcommand.builder(tagsCommand);
        } catch (e) {
            console.log('Could not load tags subcommand %s', file);
            console.error(e);
        }
    }
}


const subcommandFolders = fs.readdirSync('./commands/tags',  { withFileTypes: true }).filter((item) => item.isDirectory()).map((item) => item.name);
for (const file of subcommandFolders) {
    try {
        const subcommand = require(`./${file}`);
        subcommands.set(`${file}`, subcommand);
        console.log(file);
        tagsCommand = subcommand.builder(tagsCommand);
    } catch (e) {
        console.log('Could not load fun subcommand %s', file);
        console.error(e);
    }
}

module.exports = {
	data: tagsCommand,
    async execute(interaction) {
        let subcommandName = interaction.options.getSubcommand() + '.js';
        let command = subcommands.get(subcommandName);
        await command.execute(interaction);
	},
};