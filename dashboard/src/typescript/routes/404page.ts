//404 error page not found middleware
import * as express from 'express';
// const router:express.Router = express.Router();

// router.use
const error404page=(req:express.Request,res:express.Response)=>{
    let invokedUrl=req.originalUrl;
    if(invokedUrl.endsWith('/')){
        invokedUrl=invokedUrl.slice(0,-1)
    }
    res.status(400).render('NotFound',{'layout':'NotFound','name':`${invokedUrl}`})
    return;
}

module.exports = error404page;