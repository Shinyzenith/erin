import Express from 'express';
const router = Express.Router();

router.get('/',(req:Express.Request,res:Express.Response)=>{
    res.render('index',{
        content:'OwO denc >~<'
    })
});

module.exports = router;