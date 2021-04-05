"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const path_1 = __importDefault(require("path"));
const dotenv_1 = __importDefault(require("dotenv"));
const express_handlebars_1 = __importDefault(require("express-handlebars"));
const indexPage = require('./routes/index');
const formPage = require('./routes/formpage');
const updateEndpoint = require('./routes/api/update');
const fetchEndpoint = require('./routes/api/fetch');
const apiIndexPage = require('./routes/api/index');
dotenv_1.default.config({ "path": path_1.default.join(__dirname, "../../.env") });
const app = express_1.default();
const port = process.env.SERVER_PORT || 80;
app.engine('handlebars', express_handlebars_1.default({ defaultLayout: 'homepage' }));
app.set('view engine', 'handlebars');
app.set("views", path_1.default.join(__dirname, "./views"));
app.use(express_1.default.static(path_1.default.join(__dirname + "./../dist/assets")));
app.use(express_1.default.json());
app.use(express_1.default.urlencoded({ extended: false }));
app.use('/', indexPage);
app.use('/dashboard', formPage);
app.use('/api/v1', apiIndexPage);
app.use('/api/v1/fetch', fetchEndpoint);
app.use('/api/v1/update', updateEndpoint);
app.use(function (req, res, next) {
    res.status(404);
    if (req.accepts('html')) {
        res.status(400).render('NotFound');
        return;
    }
    if (req.accepts('json')) {
        res.json({ error: 'Not found' });
        return;
    }
    res.type('txt').send('Not found');
});
app.listen(port, () => console.log(`Server started at http://localhost:${port}`));
