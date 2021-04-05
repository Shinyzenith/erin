import * as express from 'express';
import * as path from 'path';
const router:express.Router = express.Router();

router.get('/',(req:express.Request,res:express.Response)=>{
    res.render('index',{
        layout:'homepage',
        content:'OwO wot dis >~<'
    })
});

module.exports = router;