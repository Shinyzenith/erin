import * as express from 'express';

//Required constants
const router:express.Router = express.Router();             //express router constant

//api routes
const routes = {
    "baseURL":"/api/v1",
    "endpoints":{
        "warn":{
            "base url":"/api/v1/warn",
            "insert warn":{
                "path":"/insert",
                "protocol":"put"
            },
            "delete warn":{
                "path":"/delete",
                "protocol":"delete"
            },
            "fetch warn":{
                "path":"/",
                "protocol":"get"
            }
        }
    }
}
router.get('/',(req:express.Request,res:express.Response)=>{
    res.status(200).type('json').send(JSON.stringify(routes, null, "\t"));
});

module.exports = router;