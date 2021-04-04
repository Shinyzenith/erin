import Express from 'express';
const router:Express.Router = Express.Router();

async function fetchData(gid:number){

}

router.get('/',(req:Express.Request,res:Express.Response)=>{
    res.send({'msg':'update api endpoint is still in prod'})
});

module.exports = router;