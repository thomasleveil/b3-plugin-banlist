banlist plugin for Big Brother Bot (www.bigbrotherbot.net)
==========================================================

By Courgette


Description
-----------

This plugin as been made to allow easy sharing of cheater banlist between clans.
It also as the advantage of not requiering any game server reboot after banlist updates.



Features :
----------

IP banlists / whitelists :
 * specify as many banlist files as you want.
 * understands range ip ban. (ie: ip ending with '.0')
 * option to enfore range ip ban as if all ip addresses where ending with ".0"
 
GUID banlists / whitelists :
 * specify as many guid banlist files as you want.

Rules of Combat banlists : 
 * enforce Homefront banlists from www.rulesofcombat.com

For all banlists :
 * an url can be specified to hourly update.
 * a specific message can be set to be displayed upon kick. (keywords understood: $id, $ip, $guid, $name) 



Installation
------------

 * copy banlist.py into b3/extplugins
 * copy banlist.xml into b3/extplugins/conf
 * update your main b3 config file with :

<plugin name="banlist" config="@b3/extplugins/conf/banlist.xml"/>



Changelog
---------

09/07/2008 - Courgette
- allows to define multiple banlists
- understands guid banlists

09/07/2008 - courgette
- minor fix

21/07/2008 - 1.0.0 - Courgette
- banlist can be updated hourly from an url

26/07/2008 - 1.1.0 - Courgette
- makes use of thread while updating banlist from url
- makes use of thread while checking a player
- fails nicely on http error (thanks to flinkaflenkaflrsk's bug report)
- when loading config, check all connected players
- when loading config, if possible, update banlist files older than an hour
- upon player check, if banlist file is missing, fail nicely
- upon player check, if banlist file is missing and url is provided, update file from url and check player
- fix minor bug when using command !reconfig

26/07/2008 - 1.1.1 - Courgette
- better network error handling
- add command !banlistinfo

08/08/2008 - 1.1.2 - Courgette
- manage cases where client ip/guid is unknown (thx to Anubis report and fix)

27/03/2009 - 2.0.0 - Courgette
/!\ UPGRADING USERS : beware of major changes in config file format /!\
- add immunity level, so admin won't be checked against banlists
- add ip whitelist
- add guid whitelist
- add general "auto update" option
- add command !banlistupdate that will update all banlist with a URL
- add command !banlistcheck that will check all connected players
- the force_ip_range option is now per banlist
- message can contains the following keywords : $id, $ip, $guid, $name
- a player found in a banlist but 'immunized' by its level is given a notice, (so it can be seen in Echelon)

27/11/2009 - 2.1.0 - Courgette
- in guid banlists, search is now case-insensitive

29/11/2009 - 2.1.1 - Courgette
- better handling of situations that can raise exceptions
- add tests

16/12/2009 - 2.1.2 - Courgette
- fix typo in config file example (ip_whitelist)

13/09/2010 - 2.2 - Courgette
- in config, '~', '@b3' and '@conf' are now expanded for 'file'

13/04/2011 - 2.3 - Courgette
- add support for Rules of Combat banlist format www.rulesofcombat.com

15/04/2011 - 2.3.1 - Courgette
- explicit encoding for downloading from www.rulesofcombat.com

29/04/2011 - 2.4 - Courgette
- makes use of ETag and Last-Modified HTTP headers to avoid downloading unchanged banlist
- supports gzip encoding while downloading banlists



Support
-------

http://www.bigbrotherbot.net/forums/index.php?topic=389.0
