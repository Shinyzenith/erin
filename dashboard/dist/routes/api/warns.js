"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const express = __importStar(require("express"));
const warns_1 = require("./controllers/warns");
const router = express.Router();
router.get('/', (req, res) => {
    const body = { ...req.body };
    const guildID = body.gid;
    const userID = body.uid;
    if (typeof (guildID) === "undefined" || typeof (userID) === "undefined") {
        return res.status(400).json({ 'message': 'GuildID or UserID not found in request body' });
    }
    if (typeof (guildID) !== "string" || typeof (userID) !== "string") {
        return res.status(400).json({ 'message': 'GuildID and UserID should be of type string' });
    }
    warns_1.fetchWarns(userID, guildID, res);
    return true;
});
router.put('/insert', (req, res) => {
    const body = { ...req.body };
    const warnObject = body.warn;
    const guildID = Object.keys(warnObject.gid)[0];
    const warnBody = Object.keys(warnObject.gid[guildID][0]);
    const warns = warnObject.gid[guildID];
    if (typeof (warnObject) === "undefined") {
        return res.status(400).json({ 'message': 'Warn object not found in request body' });
    }
    if (typeof (warnObject) !== "object") {
        return res.status(400).json({ 'message': 'parameter should be of type object' });
    }
    if (!warnObject.hasOwnProperty('gid')) {
        return res.status(500).json({ 'message': 'Request body must contain a warn object with a "gid" key' });
    }
    if (Object.keys(warnObject.gid).length >= 2) {
        return res.status(500).json({ 'message': 'sorry you can only pass in one guild at a time. F' });
    }
    if (warns.length >= 2) {
        return res.status(500).json({ 'message': 'Sorry you can only pass in one warn object at a time. F' });
    }
    if (warnBody.length >= 5 || (!warnBody.includes('type') || !warnBody.includes('mod') || !warnBody.includes('time') || !warnBody.includes('reason'))) {
        return res.status(500).json({ 'message': 'Warn object schema was incorrect, insertion cancelled' });
    }
    warns_1.insertWarn(warnObject, res);
    return true;
});
router.delete('/delete', (req, res) => {
    const body = { ...req.body };
    const delIndex = body.index;
    const guildID = body.gid;
    const userID = body.uid;
    if (typeof (guildID) === "undefined" || typeof (userID) === "undefined" || typeof (delIndex) === "undefined") {
        return res.status(400).json({ 'message': 'GuildID, UserID or delete index not found in request body' });
    }
    if (typeof (guildID) !== "string" || typeof (userID) !== "string" || typeof (delIndex) !== "number") {
        return res.status(400).json({ 'message': 'GuildID and UserID should be of type string and delete index should be of type number.' });
    }
    warns_1.deleteWarn(delIndex, userID, guildID, res);
    return true;
});
module.exports = router;
