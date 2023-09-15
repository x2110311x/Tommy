module.exports = {
  builder: function (SlashCommandBuilder){
      SlashCommandBuilder.addSubcommand(subcommand =>
          subcommand
              .setName('kick')
              .setDescription('Kick a user')
              .addUserOption(option =>
                  option.setName('user')
                      .setDescription('The user to kick.')
                      .setRequired(true)));
                  
      return SlashCommandBuilder;
  },
  execute: async function(interaction){
      let user = interaction.options.getUser('user');
      console.log(user);
      
      user.kick().then(() =>
        interaction.reply(`Kick ${user.tag}`)
      );
  }
};