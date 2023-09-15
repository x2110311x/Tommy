const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const warnSchema = new Schema({
  time: {type: Number, required: true},
  reason: {type: String, required: true},
  warnedby: {type: Number, require: true}
});

const UserSchema = new Schema({
  _id: { type: Number, required: true },
  id: { type: Number, required: true },
  firstjoin: { type: Number, default: Math.floor(Date.now()/1000)},
  currentmember: { type: Boolean, required: true, default: true},
  level: { type: Number, default: 0 },
  monthlevel: { type: Number, deault: 0 },
  points: { type: Number, default: 0 },
  monthpoints: { type: Number, default: 0},
  nextPoint: {type: Number, default: 0 },
  goldcount: { type: Number, default: 0},
  dailycount: { type: Number, default: 0},
  nextDaily: {type: Number, default: 0},
  credits: { type: Number, default: 0},
  ownedRoles: [ Number ],
  warns: [ warnSchema ]
},
{ _id: false });

module.exports = mongoose.model('User', UserSchema);