import express from "express";
import path from "path";

const app = express();
const port = process.env.PORT || 8080; 

// Configure Express to use EJS
app.set( "views", path.join( __dirname, "dashboard/html/" ) );
app.set( "view engine", "ejs" );

// define a route handler for the default home page
app.get( "/", ( req, res ) => {
    res.render( "index" );
} );

app.listen( port, () => {
    console.log( `server started at http://localhost:${ port }` );
} );