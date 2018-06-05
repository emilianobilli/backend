var player_version='HotGo Player v0.1 @2016';
var jw_player_configure=function(config){
var player_config;player_config={abouttext:player_version,aboutlink:'http://www.hotgo.tv',primary:'html5',}
if('title'in config){player_config['title']=config.title;}
if('image'in config){player_config['image']=config.image;}
if('aspectratio'in config){player_config['aspectratio']=config.aspectratio;}
if('width'in config){player_config['width']=config.width;}
if('tracks'in config){player_config['tracks']=config.tracks;}
if('captions'in config){player_config['captions']=config.captions;}
if('autostart'in config){player_config['autostart']=config.autostart;}
if('skin'in config){player_config['skin']=config.skin;}
return player_config;}
var primary=function(config){var player_config;player_config=jw_player_configure(config);player_config['sources']=[{file:config.video.primary.url,type:config.video.primary.type,'default':'true'}];
return player_config;}
var low_quality_first=function(config){var player_config;player_config=jw_player_configure(config);player_config['sources']=[{file:config.video.low_quality.url,type:config.video.low_quality.type,label:config.video.low_quality.label,'default':'true'},{file:config.video.medium_quality.url,type:config.video.medium_quality.type,label:config.video.medium_quality.label,'default':'false'},{file:config.video.high_quality.url,type:config.video.high_quality.type,label:config.video.high_quality.label,'default':'false'}];return player_config;}
var high_quality_first=function(config){var player_config;player_config=jw_player_configure(config);player_config['sources']=[{file:config.video.low_quality.url,type:config.video.low_quality.type,label:config.video.low_quality.label,'default':'false'},{file:config.video.medium_quality.url,type:config.video.medium_quality.type,label:config.video.medium_quality.label,'default':'false'},{file:config.video.high_quality.url,type:config.video.high_quality.type,label:config.video.high_quality.label,'default':'true'}];return player_config;}
var HotgoPlayer=function(element,config,onReady)
{var md=new MobileDetect(window.navigator.userAgent);jw_player=jwplayer(element);var mobile;if(md.mobile()||md.phone()||md.tablet())
{config.meta.device="Mobile";mobile=true;}
else
{config.meta.device="Desktop";mobile=false;}
this.player_config=primary(config);this.start=function(){this.player_instance=jw_player;jw_player.setup(this.player_config);jw_player.once('setupError',function(error){if(mobile){jw_player.setup(low_quality_first(config));}
else{jw_player.setup(high_quality_first(config));}
jw_player.onReady(function(){jw_player.seek(0);if(onReady){onReady(jw_player,config.meta);}});});jw_player.once('error',function(error){if(mobile){jw_player.load(low_quality_first(config));}
else{jw_player.load(high_quality_first(config));}
jw_player.play();if(onReady){jw_player.onReady(function(){onReady(jw_player,config.meta);});}});if(onReady){jw_player.onReady(function(){onReady(jw_player,config.meta);});}}}