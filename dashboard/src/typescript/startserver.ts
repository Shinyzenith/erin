import express from "express";
import path from "path";
import dotenv from "dotenv";
import expresshandlebars  from 'express-handlebars';

dotenv.config({"path":path.join(__dirname,"../../.env")});

const app:express.Application = express();
const port = process.env.SERVER_PORT || 8080; 

//Handlebars middleware
app.engine('handlebars',expresshandlebars({defaultLayout:'main'}));
app.set('view engine','handlebars');

app.get('/',(req:express.Request,res:express.Response)=>{
    res.render('index',{
        layout:'home',
        content:'OwO wot dis >~<'
    })
});

app.get('/alt',(req:express.Request,res:express.Response)=>{
    res.render('index',{
        layout:'test',
        content:'OwO wot dis >~<'
    })
});
//@TODO: SETUP ./routes instead of this one dirty huge ass file for all the routes > ~ <
app.listen( port, () => console.log( `Server started at http://localhost:${ port }`));