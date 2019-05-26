const mongoose = require('mongoose');

const ActSchema = mongoose.Schema({
    actId:{ type:Number, index:{unique:true}},
    category:String,
    caption:String,
    timestamp:String,
    imgB64:String,
    upVotes:Number,
    username: String
});

const CategorySchema = mongoose.Schema({
    categoryName:{ type:String, index:{unique:true}},
    count:Number
});

module.exports = {
    Act : mongoose.model('Act', ActSchema),
    Category : mongoose.model('Category', CategorySchema),
};
