"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const error404page = (req, res) => {
    let invokedUrl = req.originalUrl;
    if (invokedUrl.endsWith('/')) {
        invokedUrl = invokedUrl.slice(0, -1);
    }
    res.status(400).render('NotFound', { 'layout': 'NotFound', 'name': `${invokedUrl}` });
    return;
};
module.exports = error404page;
