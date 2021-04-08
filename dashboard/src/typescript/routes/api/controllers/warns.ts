import mongoose from 'mongoose';
import path from 'path';
import dotenv from "dotenv";
import express from 'express';
import mongodb from 'mongodb';
const warns = require('./../models/warns')

//configuring dotenv module to point to .env
dotenv.config({"path":path.join(__dirname,"../../../../../.env")});

// const connectionUri:string = process.env.CONNECTION_URI;
const connectionUri:string = 'mongodb://127.0.0.1:27017/erin?compressors=zlib'

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

export interface userWarnSchema{ 
    uid:string;
    gid:[warnSchema];
}
async function deleteWarn(index:number,uid:string,gid:string,res:express.Response){
    //@ts-ignore
    const updateUser = await warns.findOne({uid:uid},(err:mongoose.Error)=>{
        if(err){
            return res.status(500).json({ 'message':'Unable to delete record',err });
        }
    })
    if(typeof(updateUser)==="undefined" || updateUser===null){
        return res.status(500).json({ 'message':'User doesn\'t exist' });
    }
    const userWarns = Object.keys(updateUser.gid[gid])
    if(index > userWarns.length){
        return res.status(500).json({ 'message':'index not found.' })
    }
    const deletedWarn = updateUser.gid[gid].pop(index-1)
    //@ts-ignore
    await warns.updateOne({ uid:uid },updateUser,(err:mongoose.Error)=>{
        if(err){
            return res.status(500).json({ 'message':'databse delete',err });
            
        }
    });
    return res.status(500).json({ 'message':'Deleted warning.',deletedWarn })
    
}
//@ts-ignore
async function insertWarn(record:userWarnSchema,res:express.Response){
    //@ts-ignore
    const updateUser= await warns.findOne({uid:record.uid.toString()},(err:mongoose.Error)=>{
        if(err){
            return res.status(500).json({ 'message':'Unable to fetch data for uid checking before insert',err });
        }
    })
    if(typeof(updateUser)==="undefined" || updateUser===null){
        try{
            //@ts-ignore
            await warns.create(record,(err:mongoose.Error)=>{
                if(err){
                    return res.status(500).json({ 'message':'databse entry failed',err });
                    
                }
            });
            try{
                return res.status(200).json({ 'message':'successfully created object.',record })
            }
            catch(err){}
        }
        catch(err){
            return res.status(500).json({ 'message':'databse entry failed',err });
        }
    } else {
        const guildID:string = Object.keys(record.gid)[0];
        const newWarn:object = record.gid[guildID][0];
        updateUser.gid[guildID].push(newWarn)
        //@ts-ignore
        await warns.updateOne({ uid:record.uid.toString() },updateUser,(err:mongoose.Error)=>{
            if(err){
                return res.status(500).json({ 'message':'databse entry failed',err });
                
            }
        });
        return res.status(500).json({ 'message':'User object already exists. Updating user values.' })
    }
};

async function fetchWarns(userID:string,guildID:string,res:express.Response){
    const searchDocument:object ={ uid:userID};
    const records = await warns.findOne(searchDocument,(err:mongoose.Error)=>{
        if(err){
            res.status(500).json({ 'message':'fetchWarn function failed with status code 500',err });
        }
    })
    try{
        const warns = records.gid[guildID]
        if (typeof(warns)==="undefined"){
            return res.status(500).json({ 'message':'No entry found.'});    
        }
        else{
            return res.status(200).json(warns);
        }
    } catch {
        return res.status(500).json({ 'message':'No entry found' });
    }
};
/*
demo put request body for the inset warn function
{
    "warn":{
        "uid":"6566656654",
        "gid":{
            "987654231":[
                {
                    "type":"OwO",
                    "reason":"cuz yes",
                    "time":"lol current time",
                    "mod":"456789"
                }
            ]
        }
    }
}


demo delete request for the deletewarn function and fetchWarn function
{
    "index":2,
    "gid":"987654231",
    "uid":"6566656654"
}


*/

module.exports = {insertWarn, fetchWarns, deleteWarn}