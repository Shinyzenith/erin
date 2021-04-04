import Express from 'express';
const router = Express.Router();

router.get('/',(req:Express.Request,res:Express.Response) => {
    res.render('index',{
        layout:'formpage',
        content:'OwO dis da form page >~<'
    })
});

module.exports = router;