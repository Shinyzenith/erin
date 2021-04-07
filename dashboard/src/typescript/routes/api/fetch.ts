import * as express from 'express';

//Required constants
const router:express.Router = express.Router();             //express router constamt

//api routes
router.get('/',(req:express.Request,res:express.Response)=>{
    res.status(400).json({ 'message':'This is the fetch data endpoint, pass gid in the request body to interact with it.' })
});

router.post('/', (req:express.Request, res:express.Response)=>{
    const body = {...req.body}
    const guildID:number = body.gid;
    if(typeof(guildID)==="undefined"){
        return res.status(400).json({ 'message':'GuildID not found in request body' })
    }
    if(typeof(guildID)==="string"){
        return res.status(400).json({ 'message':'GuildID should be of type number' })
    }
    return res.status(200).json({ 'message':'successful','gid':`recieved guild id ${guildID}` })
});

module.exports = router;