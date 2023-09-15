const mongoose = require("mongoose");
exports.connectDB = async function(){
  let db_host = process.env.db_host;
  let db_name = process.env.db_name;
  let db_url = `mongodb://${db_host}:27017/${db_name}`;
  await mongoose.connect(db_url);
  console.log("Database connected");``
}

exports.disconnectDB = async function(){
  mongoose.connection.close();
}

exports.users = require("./helpers/user.js");