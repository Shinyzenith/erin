import express from "express";
import path from "path";
import dotenv from "dotenv";

dotenv.config({"path":path.join(__dirname,"../../../.env")});

const app:express.Application = express();
const port = process.env.SERVER_PORT || 8080; 

// app.set( "views", path.join( __dirname, "./../html/" ) );
// app.set( "view engine", "ejs" );

// app.get( "/", ( req:express.Request, res:express.Response) => {
//     res.render( "index" );
// });

app.use(express.static(path.join(__dirname,'./../../dist/')))

app.listen( port, () => console.log( `Server started at http://localhost:${ port }`));