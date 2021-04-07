import * as express from 'express';
//@ts-ignore
import {insertWarn, fetchWarns,userWarnSchema} from './controllers/warns';
//Required constants
const router:express.Router = express.Router();             //express router constant

//api routes
router.get('/warns',(req:express.Request,res:express.Response)=>{
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
    fetchWarns(userID,guildID,res);
    return true;
});

router.put('/', (req:express.Request, res:express.Response)=>{
    const body = {...req.body}
    const warnObject:userWarnSchema = body.warn;
    if(typeof(warnObject)==="undefined"){
        return res.status(400).json({ 'message':'Warn object not found in request body' })
    }
    if(typeof(warnObject)!=="object"){
        return res.status(400).json({ 'message':'parameter should be of type object' });
    }
    insertWarn(warnObject,res)
    return true;
});

module.exports = router;