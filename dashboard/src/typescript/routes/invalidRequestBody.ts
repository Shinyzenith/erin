//invalid request body middleware
import * as express from 'express';

const invalidRequestBody = (error, req:express.Request, res:express.Response, next:express.NextFunction) => {
    if (error instanceof SyntaxError) {
      return res.status(500).json({ 'message':'Invalid json passed as request body' })
    } else {
      next();
      return true;
    }
}

module.exports = invalidRequestBody;