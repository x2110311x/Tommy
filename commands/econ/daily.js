/* eslint-disable no-undef */
const { EmbedBuilder, DiscordAPIError } = require('discord.js');
const db = require("../../database");

module.exports = {
    builder: function (SlashCommandBuilder){
        SlashCommandBuilder.addSubcommand(subcommand =>
            subcommand
                .setName('daily')
                .setDescription('Claim your daily credits'));
        return SlashCommandBuilder;
    },
    execute: async function(interaction){
      await interaction.deferReply();
      const member = await db.users.get(interaction.member.id);
      let currentTime = (Date.now()/1000);
      if (currentTime > member.nextDaily){
        await db.users.daily(member);
        await interaction.editReply("You've earned 200 credits!");
      } else {
        await interaction.editReply("It is not time for your daily yet");
      }
    }
};