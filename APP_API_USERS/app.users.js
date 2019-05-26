const express = require('express');
const bodyParser = require('body-parser');
var cors = require('cors');
// create express app
const app = express();

var corsOptions = {
  origin: 'http://localhost',
  optionsSuccessStatus: 200 // some legacy browsers (IE11, various SmartTVs) choke on 204
}

// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: true ,limit:'50MB'}));

// parse application/json
app.use(bodyParser.json({limit:'50MB'}));

app.use(function (req, res, next) {

    var allowedOrigins = ['http://18.210.124.11', 'http://3.94.219.52'];
    var origin = req.headers.origin;
    if(allowedOrigins.indexOf(origin) > -1){
       res.setHeader('Access-Control-Allow-Origin', origin);
    }

    // Website you wish to allow to connect
    // res.setHeader('Access-Control-Allow-Origin', 'http://18.210.124.11');

    // Request methods you wish to allow
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');

    // Request headers you wish to allow
    // res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');

    // Set to true if you need the website to include cookies in the requests sent
    // to the API (e.g. in case you use sessions)
    // res.setHeader('Access-Control-Allow-Credentials', true);

    // Pass to next layer of middleware
    next();

});


// Configuring the database
const dbConfig = require('./config/database.config.js');
const mongoose = require('mongoose');
const urlConfig = require('./config/database.config.js');

mongoose.Promise = global.Promise;

// Connecting to the database
mongoose.connect(dbConfig.dbUrl, {
        useNewUrlParser: true
}).then(() => {
    console.log("Successfully connected to the database");
}).catch(err => {
    console.log('Could not connect to the database. Exiting now...', err);
    process.exit();
});

// define a simple route
// app.get('/', (req, res) => {
//     res.json({"message": "Welcome to Users Microservice."});
// });
//
// app.post('/',(req,res) => {
// 	console.log(req.body);
// 	res.send({status:'SUCCESS'});
// });

require('./app/routes/users.routes.js')(app);


// listen for requests
app.listen(3000, () => {
    console.log("Server is listening on port 3000");
});
