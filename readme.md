banlist plugin for Big Brother Bot (www.bigbrotherbot.net)
==========================================================


Description
-----------

This plugin as been made to allow easy sharing of cheater banlist between clans.
It also as the advantage of not requiering any game server reboot after banlist updates.

You can enforce an unlimited number of banlists and whitelists which can be composed of either IP addresses
GUIDs or PBids.
It also can work with banlists from Rules of Combat www.rulesofcombat.com


******
*NOTE: since B3 v1.10.1 beta this plugin has been included in the standard plugins set, thus all patches and updates will be performed in the official B3 repository.*
******


Features :
----------

### IP banlists / whitelists :

 * specify as many banlist files as you want.
 * understands range ip ban. (ie: banlist file having IP addresses ending with '.0', '.0.0' or '.0.0.0')
 * option to enfore range IP ban as if all ip addresses where ending with ".0"
 
### GUID banlists / whitelists :

 * specify as many guid banlist files as you want.

### PBid banlists / whitelists :

 * specify as many PBid banlist files as you want.

### Rules of Combat banlists :

 * enforce Homefront banlists from www.rulesofcombat.com

### For all banlists :

 * an url can be specified to hourly update.
 * a specific message can be set to be displayed upon kick. (keywords understood: $id, $ip, $guid, $pbid, $name)



Installation
------------

 * copy banlist.py into b3/extplugins
 * copy plugin_banlist.xml in the same directory as your b3.xml
 * update your main b3 config file with :

    ```
    <plugin name="banlist" config="@conf/plugin_banlist.xml"/>
    ```



Changelog
---------

### 0.1 - 09/07/2008

- allows to define multiple banlists
- understands guid banlists


### 0.2 - 09/07/2008

- minor fix


### 1.0.0 - 21/07/2008

- banlist can be updated hourly from an url


### 1.1.0 - 26/07/2008

- makes use of thread while updating banlist from url
- makes use of thread while checking a player
- fails nicely on http error (thanks to flinkaflenkaflrsk's bug report)
- when loading config, check all connected players
- when loading config, if possible, update banlist files older than an hour
- upon player check, if banlist file is missing, fail nicely
- upon player check, if banlist file is missing and url is provided, update file from url and check player
- fix minor bug when using command !reconfig


### 1.1.1 - 26/07/2008

- better network error handling
- add command !banlistinfo


### 1.1.2 - 08/08/2008

- manage cases where client ip/guid is unknown (thx to Anubis report and fix)


### 2.0.0 - 27/03/2009

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


### 2.1.0 - 27/11/2009

- in guid banlists, search is now case-insensitive


### 2.1.1 - 29/11/2009

- better handling of situations that can raise exceptions
- add tests


### 2.1.2 - 16/12/2009

- fix typo in config file example (ip_whitelist)


### 2.2 - 13/09/2010

- in config, '~', '@b3' and '@conf' are now expanded for 'file'


### 2.3 - 13/04/2011

- add support for Rules of Combat banlist format www.rulesofcombat.com


### 2.3.1 - 15/04/2011

- explicit encoding for downloading from www.rulesofcombat.com


### 2.4 - 29/04/2011

- makes use of ETag and Last-Modified HTTP headers to avoid downloading unchanged banlist
- supports gzip encoding while downloading banlists


### 2.4.1 - 24/08/2011

- fix config file validation for elements 'name' and 'file'


### 2.5 - 04/09/2012

- reduce I/O access by loading the banlist files into memory and caching check results


### 2.6 - 02/01/2013

- add support for banlist of Punkbuster ids


### 2.7 - 02/01/2013

- add support for IP range for IP ending with ".0.0" and ".0.0.0"



Support
-------

http://forum.bigbrotherbot.net/index.php?topic=389.0
