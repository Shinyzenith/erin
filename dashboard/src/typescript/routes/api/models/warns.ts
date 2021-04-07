import mongoose from 'mongoose';

// meh i might use this someday idk idc fuck u start ignoring this chunk and use the fucking api you nub.
const warnSchema = new mongoose.Schema({
    type:{type:String,required:true},
    reason:{type:String,required:true},
    time:{type:String,required:true},
    mod:{type:String,required:true}
})

const userWarnScheme = new mongoose.Schema(
    { 
        uid:{type:String,required :true},
        gid: mongoose.Schema.Types.Mixed
    }
);
const userWarnModel = mongoose.model('warns',userWarnScheme);
module.exports = userWarnModel;