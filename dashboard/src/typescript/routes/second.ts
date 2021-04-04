import Express from 'express';
const router = Express.Router();

router.get('/',(req:Express.Request,res:Express.Response) => {
    res.render('index',{
        content:'OwO send feet pics >~<'
    })
});

module.exports = router;