#!/usr/bin/env node
/**
 * Web app to listen for and process page tagging requests
 */

/**
 * We also require node.js libraries:
 * vows, request, and express
 */
 
var taggart = function(title) {

	// Set up the bot
	var bot = require('nodemw'),
		client = new bot('config.js');
    
	var MARKER = '{{Quality}}',
		REASON = 'Tagged for possible quality issues by Exbot';

	client.logIn(function() {

		console.log('-- Request to tag article ' + title);
		client.getArticle(title, function(content) {
			
			// Check page is not tagged already
			if (content.toLowerCase().indexOf(MARKER.toLowerCase()) > -1) {
					console.log(' * ' + title + ' is already tagged!');
					return;
			}

			content = MARKER + "\n\n" + content;

			client.edit(title, content, REASON, function() {
					console.log(' - Tagged '+ title);
				
			});
		});
	});

};

// Set up the server
var express = require('express'),
var app = express(),
var http = require('http'),
var server = http.createserver(app);

app.use(express.bodyParser());

app.post('/tag',function(req,res) {
    console.log(req.body);
    res.send(200);
    
    taggart(req.body)
    
    });
    
// Start the server
server.listen(8082, '127.0.0.1');

