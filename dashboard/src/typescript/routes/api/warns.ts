import * as express from 'express';
//@ts-ignore
import {insertWarn, fetchWarns, deleteWarn,userWarnSchema} from './controllers/warns';
//Required constants
const router:express.Router = express.Router();             //express router constant

//api routes
router.get('/', (req:express.Request, res:express.Response)=>{
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

router.put('/insert', (req:express.Request, res:express.Response)=>{
    const body = {...req.body};
    const warnObject:userWarnSchema = body.warn;
    const guildID:string = Object.keys(warnObject.gid)[0];
    const warnBody:string[] = Object.keys(warnObject.gid[guildID][0]);
    const warns:object[] = warnObject.gid[guildID]
    if(typeof(warnObject)==="undefined"){
        return res.status(400).json({ 'message':'Warn object not found in request body' });
    }
    if(typeof(warnObject)!=="object"){
        return res.status(400).json({ 'message':'parameter should be of type object' });
    }
    if(!warnObject.hasOwnProperty('gid')){
        return res.status(500).json({ 'message':'Request body must contain a warn object with a "gid" key'});
    }
    if(Object.keys(warnObject.gid).length>=2){
        return res.status(500).json({ 'message':'sorry you can only pass in one guild at a time. F' });
    }
    if(warns.length>=2){
        return res.status(500).json({ 'message':'Sorry you can only pass in one warn object at a time. F' })
    }
    if(warnBody.length>=5 || (!warnBody.includes('type') || !warnBody.includes('mod') || !warnBody.includes('time') || !warnBody.includes('reason') )){
        return res.status(500).json({ 'message':'Warn object schema was incorrect, insertion cancelled' })
    }
    insertWarn(warnObject,res)
    return true;
});

router.delete('/delete', (req:express.Request, res:express.Response)=>{
    const body = {...req.body};
    const delIndex:number= body.index;
    const guildID:string = body.gid;
    const userID:string[] = body.uid;
    if(typeof(guildID)==="undefined" || typeof(userID)==="undefined" || typeof(delIndex)==="undefined"){
        return res.status(400).json({ 'message':'GuildID, UserID or delete index not found in request body' })
    }
    if(typeof(guildID)!=="string" || typeof(userID)!=="string" || typeof(delIndex)!=="number"){
        return res.status(400).json({ 'message':'GuildID and UserID should be of type string and delete index should be of type number.' })
    }
    deleteWarn(delIndex,userID,guildID,res)
    return true;
});

module.exports = router;