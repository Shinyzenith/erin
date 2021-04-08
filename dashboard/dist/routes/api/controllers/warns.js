"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose_1 = __importDefault(require("mongoose"));
const path_1 = __importDefault(require("path"));
const dotenv_1 = __importDefault(require("dotenv"));
const warns = require('./../models/warns');
dotenv_1.default.config({ "path": path_1.default.join(__dirname, "../../../../../.env") });
const connectionUri = 'mongodb://127.0.0.1:27017/erin?compressors=zlib';
mongoose_1.default.set('useNewUrlParser', true);
mongoose_1.default.set('useUnifiedTopology', true);
mongoose_1.default.connect(connectionUri, (err) => {
    if (err) {
        console.log(err);
    }
});
async function deleteWarn(index, uid, gid, res) {
    const updateUser = await warns.findOne({ uid: uid }, (err) => {
        if (err) {
            return res.status(500).json({ 'message': 'Unable to delete record', err });
        }
    });
    if (typeof (updateUser) === "undefined" || updateUser === null) {
        return res.status(500).json({ 'message': 'User doesn\'t exist' });
    }
    const userWarns = Object.keys(updateUser.gid[gid]);
    if (index > userWarns.length) {
        return res.status(500).json({ 'message': 'index not found.' });
    }
    const deletedWarn = updateUser.gid[gid].pop(index - 1);
    await warns.updateOne({ uid: uid }, updateUser, (err) => {
        if (err) {
            return res.status(500).json({ 'message': 'databse delete', err });
        }
    });
    return res.status(500).json({ 'message': 'Deleted warning.', deletedWarn });
}
async function insertWarn(record, res) {
    const updateUser = await warns.findOne({ uid: record.uid.toString() }, (err) => {
        if (err) {
            return res.status(500).json({ 'message': 'Unable to fetch data for uid checking before insert', err });
        }
    });
    if (typeof (updateUser) === "undefined" || updateUser === null) {
        try {
            await warns.create(record, (err) => {
                if (err) {
                    return res.status(500).json({ 'message': 'databse entry failed', err });
                }
            });
            try {
                return res.status(200).json({ 'message': 'successfully created object.', record });
            }
            catch (err) { }
        }
        catch (err) {
            return res.status(500).json({ 'message': 'databse entry failed', err });
        }
    }
    else {
        const guildID = Object.keys(record.gid)[0];
        const newWarn = record.gid[guildID][0];
        updateUser.gid[guildID].push(newWarn);
        await warns.updateOne({ uid: record.uid.toString() }, updateUser, (err) => {
            if (err) {
                return res.status(500).json({ 'message': 'databse entry failed', err });
            }
        });
        return res.status(500).json({ 'message': 'User object already exists. Updating user values.' });
    }
}
;
async function fetchWarns(userID, guildID, res) {
    const searchDocument = { uid: userID };
    const records = await warns.findOne(searchDocument, (err) => {
        if (err) {
            res.status(500).json({ 'message': 'fetchWarn function failed with status code 500', err });
        }
    });
    try {
        const warns = records.gid[guildID];
        if (typeof (warns) === "undefined") {
            return res.status(500).json({ 'message': 'No entry found.' });
        }
        else {
            return res.status(200).json(warns);
        }
    }
    catch {
        return res.status(500).json({ 'message': 'No entry found' });
    }
}
;
module.exports = { insertWarn, fetchWarns, deleteWarn };
