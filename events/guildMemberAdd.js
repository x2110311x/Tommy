const db = require("../database");

module.exports = {
	name: 'guildMemberAdd',
	once: false,
	async execute(member, client) {
		console.log('User join');
		client.user.setActivity(`${member.guild.memberCount} members`, { type: 'WATCHING' });
		await db.users.add(member.id);
	},
};