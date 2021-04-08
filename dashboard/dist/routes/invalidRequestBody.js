"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const invalidRequestBody = (error, req, res, next) => {
    if (error instanceof SyntaxError) {
        return res.status(500).json({ 'message': 'Invalid json passed as request body' });
    }
    else {
        next();
        return true;
    }
};
module.exports = invalidRequestBody;
