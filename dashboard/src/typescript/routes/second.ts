import Express from 'express';
const router = Express.Router();

router.get('/',(req:Express.Request,res:Express.Response) => {
    res.render('index',{
        content:'OwO second page >~<'
    })
});

module.exports = router;