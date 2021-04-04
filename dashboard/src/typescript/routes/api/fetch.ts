import Express from 'express';
const router:Express.Router = Express.Router();

router.get('/',(req:Express.Request,res:Express.Response)=>{
    res.send({'msg':'fetch api endpoint is still in prod'})
});

module.exports = router;