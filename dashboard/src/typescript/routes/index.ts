import * as express from 'express';
const router:express.Router = express.Router();

router.get('/',(req:express.Request,res:express.Response)=>{
    res.render('index',{
        layout:'homepage',
        content:'OwO wot dis >~<'
    })
});

module.exports = router;