import * as express from 'express';
//@ts-ignore
import {insertWarn, fetchWarns} from './controllers/warns';
//Required constants
const router:express.Router = express.Router();             //express router constamt

//api routes
router.get('/',(req:express.Request,res:express.Response)=>{
    res.status(400).json({ 'message':'This is the fetch data endpoint, pass gid and uid in the request body to interact with it.' })
});

router.post('/', (req:express.Request, res:express.Response)=>{
    const body = {...req.body}
    const guildID:string = body.gid;
    const userID:string = body.uid;
    if(typeof(guildID)==="undefined" || typeof(userID)==="undefined"){
        return res.status(400).json({ 'message':'GuildID or UserID not found in request body' })
    }
    if(typeof(guildID)!=="string" || typeof(userID)!=="string"){
        return res.status(400).json({ 'message':'GuildID and UserID should be of type string' })
    }
    const warns = fetchWarns(userID,guildID,res);
    return true;
});

module.exports = router;