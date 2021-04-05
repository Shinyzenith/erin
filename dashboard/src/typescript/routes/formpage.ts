import * as express from 'express';
import * as path from 'path';
const router:express.Router = express.Router();

router.get('/',(req:express.Request,res:express.Response) => {
    res.render('index',{
        layout:'formpage',
        content:'OwO dis da form page >~<'
    })
});

module.exports = router;