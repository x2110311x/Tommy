const User = require('../models/user.js');

exports.get = async function(id){
  return User.findById(id);
}

exports.add = async function(id){
  const userQuery = await User.findById(id);
  console.log(userQuery);
  var newuser;
  if (userQuery == null){
    newuser = new User({
      id: id,
      _id: id
    });
  } else {
    newuser = userQuery;
    newuser.currentmember = true;
  }
  await newuser.save();
}

exports.daily = async function(user) {
  user.dailycount = user.dailycount + 1;
  user.nextDaily = Math.floor(Date.now()/1000 + 86400);
  user.credits = user.credits + 200;
  await user.save();
}

exports.addGold = async function(user){
  user.goldcount = user.goldcount + 1;
  await user.save();
}

exports.userLeave = async function(user){
  user.currentmember = false;
  await user.save();
}

exports.addPoint = async function(user){
  user.points = user.points + 1;
  user.monthpoints = user.points +1;
  user.nextPoint = Math.floor(Date.now()/1000 + 30);
  if ((Math.floor((59.8 * Math.sqrt(user.points) - 59.8) / 120)) > user.level){
    user.level = Math.floor((59.8 * Math.sqrt(user.points) - 59.8) / 120);
    user.credits = user.credits + Math.ceil(user.points * 0.05);
  }
  if ((Math.floor((59.8 * Math.sqrt(user.monthpoints) - 59.8) / 120)) > user.monthlevel){
    user.monthlevel = Math.floor((59.8 * Math.sqrt(user.monthpoints) - 59.8) / 120);
  }
  await user.save();
}

exports.warn = async function(user, warnreason, warnedBy){
  const warning = {
    time: Math.floor(Date.now()/1000),
    reason: warnreason,
    warnedby: warnedBy
  };
  user.warnings.push(warning);
  await user.save();
}

exports.addOwnedRole = async function(user, role){
  user.ownedRoles.push(role);
  await user.save();
}