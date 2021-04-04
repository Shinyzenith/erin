//imports
import express from "express";
import path from "path";
import dotenv from "dotenv";
import expresshandlebars  from 'express-handlebars';

//importing the routes into const's
const indexPage:express.Router = require('./routes/index');
const secondPage:express.Router = require('./routes/second');

//project config
dotenv.config({"path":path.join(__dirname,"../../.env")}); //dotenv config
const app:express.Application = express(); //express app const
const port = process.env.SERVER_PORT || 8080; //express port constant 

//initializing the express app 
app.engine('handlebars',expresshandlebars({defaultLayout:'homepage'})); //Handlebars middleware
app.set('view engine','handlebars'); // setting the view engine aka the template renderer
app.set( "views", path.join( __dirname, "./views" ) ); // overwriting the default view folder path
app.use(express.static(path.join(__dirname + "./../dist/assets"))); //setting the assets folder as static so the handlebar files can import the css and js as needed

//setting up the routes
app.use('/',indexPage);
app.use('/owo',secondPage);

//Running the files
app.listen( port, () => console.log( `Server started at http://localhost:${ port }`));