import Express from 'express';
const router = Express.Router();

router.get('/',(req:Express.Request,res:Express.Response)=>{
    res.render('index',{
        layout:'homepage',
        content:'OwO wot dis >~<'
    })
});

module.exports = router;