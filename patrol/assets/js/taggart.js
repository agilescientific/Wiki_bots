function(title){

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

}