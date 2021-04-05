"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
//imports
const express_1 = __importDefault(require("express"));
const path_1 = __importDefault(require("path"));
const dotenv_1 = __importDefault(require("dotenv"));
const express_handlebars_1 = __importDefault(require("express-handlebars"));
//importing the website routes into const's
const indexPage = require('./routes/index');
const formPage = require('./routes/formpage');
//api endpoint imports
const updateEndpoint = require('./routes/api/update');
const fetchEndpoint = require('./routes/api/fetch');
//project config
dotenv_1.default.config({ "path": path_1.default.join(__dirname, "../../.env") }); //dotenv config
const app = express_1.default(); //express app const
const port = process.env.SERVER_PORT || 80; //express port constant 
//initializing the express app 
app.engine('handlebars', express_handlebars_1.default({ defaultLayout: 'homepage' })); //Handlebars middleware
app.set('view engine', 'handlebars'); // setting the view engine aka the template renderer
app.set("views", path_1.default.join(__dirname, "./views")); // overwriting the default view folder path
app.use(express_1.default.static(path_1.default.join(__dirname + "./../dist/assets"))); //setting the assets folder as static so the handlebar files can import the css and js as needed
//setting up the routes
app.use('/', indexPage);
app.use('/dashboard', formPage);
app.use('/api/fetch', fetchEndpoint);
app.use('/api/update', updateEndpoint);
//Running the files
app.listen(port, () => console.log(`Server started at http://localhost:${port}`));
