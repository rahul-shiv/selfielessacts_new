const mongoose = require('mongoose');

const UserSchema = mongoose.Schema({
    username:{ type:String, index:{unique:true}},
    password:String
});


module.exports = {
    User : mongoose.model('User',UserSchema)
};
