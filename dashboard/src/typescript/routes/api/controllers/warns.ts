import mongoose from 'mongoose';
import path from 'path';
import dotenv from "dotenv";
import express, { response } from 'express';
import mongodb from 'mongodb';
const warns = require('./../models/warns')

//configuring dotenv module to point to .env
dotenv.config({"path":path.join(__dirname,"../../../../../.env")});

// const connectionUri:string = process.env.CONNECTION_URI;
const connectionUri:string = 'mongodb://127.0.0.1:27017/erin?compressors=snappy'

//connecting to the database
mongoose.set('useNewUrlParser', true);
mongoose.set('useUnifiedTopology',true );
mongoose.connect(connectionUri,(err:mongodb.MongoError)=>{
    if(err){
        console.log(err);
    }
});

interface  warnSchema{
    type:string;
    reason:string;
    time:string;
    mod:string;
}

interface userWarnSchema{ 
    uid:string;
    gid:[warnSchema];
}

async function insertWarn(record:userWarnSchema,res:express.Response){
    const response = await warns.create(record,(err:mongoose.Error)=>{
        if(err){
            res.status(500).json({ 'message':'databse entry failed',err });
            return;
        }
    });
};

async function fetchWarns(userID:string,guildID:string,res?:express.Response){
    let searchDocument:object ={ uid:userID};
    const records = await warns.findOne(searchDocument,(err:mongoose.Error)=>{
        if(err){
            res.status(500).json({ 'message':'fetchWarn function failed with status code 500',err });
        }
    })
    try{
        const warns = records.records.gid[guildID]
        if (typeof(warns)==="undefined"){
            res.status(500).json({ 'message':'No entry found.'});
            return;    
        }
        else{
            console.log(warns);
            return;
        }
    } catch {
        res.status(500).json({ 'message':'No entry found.'});
    }
};
fetchWarns("751485005993213995","820125704649572373")
module.exports = {insertWarn, fetchWarns};