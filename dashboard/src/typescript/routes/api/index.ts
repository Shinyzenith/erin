import * as express from 'express';
import path from 'path';
import dotenv from "dotenv";

//configuring dotenv module to point to .env
dotenv.config({"path":path.join(__dirname,"../../../../.env")});

//Required constants
const router:express.Router = express.Router();             //express router constant

//api routes
router.get('/',(req:express.Request,res:express.Response)=>{
    res.status(400).json({ 'baseURL':'/api/v1','endpoints':'fetch, update' });
});

module.exports = router;