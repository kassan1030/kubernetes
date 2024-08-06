const express = require("express");
const app = express();
const ip = require('ip');

const hostname = ip.address();
const port = 3000;

/* 2. listen()メソッドを実行して3000番ポートで待ち受け。*/
var server = app.listen(port, function(){
    console.log(`Server running at http://${hostname}:${port}/`);
});


app.get("/", function(req, res, next){
    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/plain');
    res.end('Express Hello, World!\n');
});