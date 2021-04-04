import Express from 'express';
const router:Express.Router = Express.Router();

router.get('/',(req:Express.Request,res:Express.Response) => {
    res.render('index',{
        layout:'homepage',
        content:'OwO send feet pics >~<'
    })
});

module.exports = router;