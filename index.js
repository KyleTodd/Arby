var favicon = require('serve-favicon');
const express = require('express');
const path = require('path');

const app = express();
const port = process.env.PORT || "8080";

app.use(favicon(path.join(__dirname, 'arbyico.ico')));
app.use(express.static(__dirname));

app.get("/", (req, res) => {
    res.status(200).sendFile(__dirname + '/index.html');
  });

app.get("/style.css", (req, res) => {
    res.status(200).sendFile(__dirname + '/style.css');
});

app.get("/arbylogo.png", (req, res) => {
    res.status(200).sendFile(__dirname + '/arbylogo.png');
});

app.get("/arbyico.ico", (req, res) => {
    res.status(200).sendFile(__dirname + '/arbyico.ico');
  });

app.listen(port, () => {
    console.log(`Listening to requests on http://localhost:${port}`);
});