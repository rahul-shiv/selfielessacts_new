const schemas = require('../models/users.model.js');
const isBase64 = require('is-base64');
const date = require('date-and-time');
const User = schemas.User;

var numberOfRequests = 0;



function isEmpty(obj) {
    for(var key in obj) {
        if(obj.hasOwnProperty(key))
            return false;
    }
    return true;
}

exports.allUser = (req,res) => {
    numberOfRequests++;
    if(req.method=='POST'){
        if(!req.body) {
            return res.status(400).send({
                message: "Empty JSON"
            });
        }
        console.log(req.body);
        const user = new User({
            username:req.body.username,
            password:req.body.password
        });

        if(!user.password.match("^[a-fA-F0-9]{40}$")){
            return res.status(400).send({});
        }

        user.save().then(data => {
            res.status(201).send({
                // Act Created Successfully!
            });
        }).catch(err => {
            res.status(400).send({
                message: "ActId provided is not unique!"
            });
        });
    }
    else if(req.method == 'GET'){
        if(!req.body){
            res.status(400).send({
                message: "user Name missing!"
            });
        }

        User.find({}).then(data=>{
            var newjson = [];
            var count = 0;
            for(var i=0;i<data.length;i++){
                newjson.push(data[i].username);
                count++;
            }
            // console.log(newjson);
            if(count){
                res.status(200).send(newjson);
            }
            else{
                res.status(204).send(newjson);
            }
        }).catch(err=>{
        });
            // User.find({}, 'username', function(err, someValue){
            //         // if(err)
            //         // {
            //         //     res.status(400).send({
            //         //         message: "user Name missing!"
            //         //     });
            //         // }
            //         // if(someValue){
            //         //
            //         //     res.status(200).send(someValue);
            //         // }
            //         // else{
            //         //     res.status(204).send({});
            //         // }
            //     });
            // User.find({username})
            //     .then(data => {
            //     if(data.length){
            //               res.status(200).send(data);
            //     }
            //     else{
            //         res.status(204).send({});
            //     }
            // });
    }
    else{
        res.status(405).send({});
    }
};

exports.removeUser = (req,res) => {
    numberOfRequests++;
    if(req.method=="DELETE"){
        if(!req.body) {
            return res.status(400).send({
                message: "Empty JSON"
            });
        }

        console.log(req.params.username);
        User.findOneAndDelete({username:req.params.username},function(err,callback){
            if(callback)
                res.status(200).send({});
            else
                res.status(400).send({});

        });
    }
    else{
        res.status(405).send({});
        console.log(req.method);
    }
};



//Counts or Resets the number of requests made to this microservice
exports.countRequests = (req, res) => {
    if(req.method=='GET'){
        res.status(200).send([numberOfRequests]);
    }
    else if(req.method=='DELETE'){
        numberOfRequests = 0;
        res.status(200).send();
    }
    else{
        res.status(405).send();
    }
};

exports.add = function(){
    numberOfRequests++;
    console.log(numberOfRequests);
}
