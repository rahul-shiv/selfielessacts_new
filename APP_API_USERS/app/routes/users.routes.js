module.exports = (app) => {
    const acts = require('../controllers/users.controller.js');

    var cors = require('cors');
    app.options('*', cors());
    //Add a user
    app.all('/api/v1/users',acts.allUser);
    //Remove a user
    app.all('/api/v1/users/:username',acts.removeUser);
    //Count and reset number of requests made to microservice
    app.all('/api/v1/_count',acts.countRequests);

    // app.all("*",function(){
    //     var add = require("../controllers/users.controller.js");
    //     // add.add();
    // });
};
