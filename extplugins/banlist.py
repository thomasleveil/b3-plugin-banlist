#
# Plugin for BigBrotherBot(B3) (www.bigbrotherbot.com)
# Copyright (C) 2008 Courgette
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# Changelog:
#
# 00:26 09/07/2008 - Courgette
# - allows to define multiple banlists
# - understands guid banlists
#
# 01:41 09/07/2008 - courgette
# - minor fix
#
# 01:46 21/07/2008 - 1.0.0 - Courgette
# - banlist can be updated hourly from an url
#
# 00:50 26/07/2008 - 1.1.0 - Courgette
# - makes use of thread while updating banlist from url
# - makes use of thread while checking a player
# - fails nicely on http error (thanks to flinkaflenkaflrsk's bug report)
# - when loading config, check all connected players
# - when loading config, if possible, update banlist files older than an hour
# - upon player check, if banlist file is missing, fail nicely
# - upon player check, if banlist file is missing and url is provided, update file from url and check player
# - fix minor bug when using command !reconfig
#
# 19:43 26/07/2008 - 1.1.1 - Courgette
# - better handling of network errors while updating banlist (Thx flinkaflenkaflrsk again for tests)
# - add !banlistinfo command
#
# 23:41 08/08/2008 - 1.1.2 - Courgette
# - manage cases where client ip/guid is unknown (thx to Anubis report)
#
# 23:35 15/10/2008 - 1.1.3 - Courgette
# -  add the ip/guid that triggered the kick in the kick message so it appears in the log/echelon
#
# 27/03/2009 - 2.0.0 - Courgette
# /!\ UPGRADING USERS : beware of major changes in config file format /!\
# - add immunity level, so admin won't be checked against banlists
# - add ip whitelist
# - add guid whitelist
# - add general "auto update" option
# - add command !banlistupdate that will update all banlist with a URL
# - add command !banlistcheck that will check all connected players
# - the force_ip_range option is now per banlist
# - message can contains the following keywords : $id, $ip, $guid, $name
# - a player found in a banlist but 'immunized' by its level is given a notice, (so it can be seen in Echelon)
#
# 27/11/2009 - 2.1.0 - Courgette
# - in guid banlists, search is now case-insensitive
#
# 29/11/2009 - 2.1.1 - Courgette
# - better handling of situations that can raise exceptions
# - add tests
#

__version__ = '2.1.1'
__author__  = 'Courgette'

import urllib2, random, thread, time, string
import b3, re, os
import b3.events
import b3.plugin

user_agent =  "B3 Banlist plugin/%s" % __version__

#--------------------------------------------------------------------------------------------------
class BanlistPlugin(b3.plugin.Plugin):
  _adminPlugin = None
  _banlists = None
  _whitelists = None
  _immunity_level = None
  _auto_update = None

    
  def onStartup(self):
    self.registerEvent(b3.events.EVT_CLIENT_AUTH)
          
  def onLoadConfig(self):
    self.debug('method onLoadConfig()')
    
    # get the admin plugin 
    self._adminPlugin = self.console.getPlugin('admin')
    if not self._adminPlugin:
      # something is wrong, can't start without admin plugin
      self.error('Could not find admin plugin')
      return False
   
    # register our commands
    if 'commands' in self.config.sections():
      for cmd in self.config.options('commands'):
        level = self.config.get('commands', cmd)
        sp = cmd.split('-')
        alias = None
        if len(sp) == 2:
          cmd, alias = sp

        func = self.getCmd(cmd)
        if func:
          self._adminPlugin.registerCommand(self, cmd, level, func, alias)
          
          
    # remove eventual existing crontabs
    if self._banlists:
      for banlist in self._banlists:
        if banlist._cronTab :
          # remove existing crontab
          self.console.cron - banlist._cronTab
    if self._whitelists:
      for whitelist in self._whitelists:
        if whitelist._cronTab :
          # remove existing crontab
          self.console.cron - whitelist._cronTab
  
    # load immunity level setting
    try:
      self._immunity_level = self.config.getint('global_settings', 'immunity_level')
    except:
      self._immunity_level = 100
    self.info('immunity level : %s' % self._immunity_level)
    
    # load auto update setting
    try:
      self._auto_update = self.config.getboolean('global_settings', 'auto_update')
    except:
      self._auto_update = True
    self.info('auto update : %s' % self._auto_update)
    
    
    # load banlists from config
    self._banlists = []
    for banlistconfig in self.config.get('ip_banlist'):
      try:
        b = IpBanlist(self, banlistconfig)
        self._banlists.append(b)
        self.info("IpBanlist [%s] loaded" % b.name)
      except Exception, e:
        self.error(e)
        
    for banlistconfig in self.config.get('guid_banlist'):
      try:
        b = GuidBanlist(self, banlistconfig)
        self._banlists.append(b)
        self.info("GuidBanlist [%s] loaded" % b.name)
      except Exception, e:
        self.error(e)

    self.debug("%d banlist loaded"% len(self._banlists))

    # load whitelists from config
    self._whitelists = []
    for whitelistconfig in self.config.get('ip_whitelist'):
      try:
        b = IpBanlist(self, whitelistconfig)
        self._whitelists.append(b)
        self.info("IP white list [%s] loaded" % b.name)
      except Exception, e:
        self.error(e)
        
    for whitelistconfig in self.config.get('guid_whitelist'):
      try:
        b = GuidBanlist(self, whitelistconfig)
        self._whitelists.append(b)
        self.info("Guid white list [%s] loaded" % b.name)
      except Exception, e:
        self.error(e)

    self.debug("%d whitelists loaded"% len(self._whitelists))
    
    self.checkConnectedPlayers()
        
        
  def onEvent(self, event):  
    if self._banlists is None or len(self._banlists)==0:
      return
      
    if event.type == b3.events.EVT_CLIENT_AUTH:
      self.onPlayerConnect(event.client)
       
       
  def getCmd(self, cmd):
    cmd = 'cmd_%s' % cmd
    if hasattr(self, cmd):
      func = getattr(self, cmd)
      return func

    return None
    
    
  def onPlayerConnect(self, client):
    thread.start_new_thread(self.checkClient, (client,))
      
      
  def checkConnectedPlayers(self):
    self.info("checking all connected players")
    clients = self.console.clients.getList()
    for c in clients:
      self.checkClient(c)
      
  def checkClient(self, client):
    """\
    Examine players ip-bans and allow/deny to connect.
    """
    self.debug('checking slot: %s, %s, %s, %s' % (client.cid, client.name, client.ip, client.guid))
    
    for whitelist in self._whitelists:
      result = whitelist.isBanned(client)
      if result is not False:
        self.info('@%s %s, ip:%s, guid:%s. Found in whitelist : %s' % (client.id, client.name, client.ip, client.guid, whitelist.name))
        msg = whitelist.getMessage(client)
        if msg and msg!="":
          self.console.write(msg)
        return
        
    for banlist in self._banlists:
      result = banlist.isBanned(client)
      if result is not False:
        if client.maxLevel < self._immunity_level:
            client.kick('BANLISTED [%s] %s' % (banlist.name, result), keyword="banlist", silent=True)
            self.info('kicking @%s %s, ip:%s, guid:%s. Found in banlist : %s' % (client.id, client.name, client.ip, client.guid, banlist.name))
            msg = banlist.getMessage(client)
            if msg and msg!="":
              self.console.write(msg)
            return
        else:
            client.notice("%s, ip:%s, guid:%s found in banlist [%s] but is immune due to its level %s" % (client.name, client.ip, client.guid, banlist.name, client.maxLevel), None)
            self.info("@%s %s, ip:%s, guid:%s found in banlist [%s] but is immune due to its level %s" % (client.id, client.name, client.ip, client.guid, banlist.name, client.maxLevel))
            return
      
  def cmd_banlistinfo(self, data=None, client=None, cmd=None):
    """\
    [<num> <name|file|time|url|force_ip_range>] - get info about specified banlist
    """
    if client is None: return
    
    if not data:
      client.message('Loaded lists :')
      banlistnames = []
      for b in self._banlists:
        banlistnames.append('^3[%s]^2 %s' % (self._banlists.index(b), b.name))
      for b in self._whitelists:
        banlistnames.append('^3[%s]^2 %s' % (len(self._banlists) + self._whitelists.index(b), b.name))
      client.message(", ".join(banlistnames))
        
    else:
      m = re.match(r"(?P<num>\d+) (?P<info>name|file|time|url|force_ip_range)", data)
      if m is None:
        if client:
          client.message('invalid data, try !help banlistinfo')
          return 
          
      index = int(m.group('num'))
      info = m.group('info')
      try:
        b = self._banlists[index]
      except IndexError:
          try:
            whitelistindex = index - len(self._banlists)
            b = self._whitelists[whitelistindex]
          except IndexError:
            client.message('cannot find banlist [%s]' % index)
            return
        
      msg = None
      if info == 'time':
        msg = self.console.formatTime(b.getModifiedTime())
      else:
        msg = getattr(b, info)
      if client:
        client.message('%s' % msg)
      else:
        self.debug('%s' % msg)
          
          
          
  def cmd_banlistupdate(self, data=None, client=None, cmd=None):
    """\
    update all banlists from URL
    """
    
    if client is None: return
    self.debug("%s requested banlist update" % client.name)
    
    for banlist in self._banlists:
        if banlist.url is not None:
            thread.start_new_thread(self._verboseUpdateBanListFromUrl, (client, banlist))
                
    for banlist in self._whitelists:
        if banlist.url is not None:
            thread.start_new_thread(self._verboseUpdateBanListFromUrl, (client, banlist))
            
            
    
  def _verboseUpdateBanListFromUrl(self, client, banlist):
    try:
        result = banlist.updateFromUrl()
        if result is True:
            client.message('^7[^4%s^7] ^2updated' % banlist.name)
        else:
            client.message('^7[^4%s^7] update ^1failed^7: %s' % (banlist.name, result))
    except BanlistException, e:
        self.warning("%s" % e.message())
        client.message('^7[^4%s^7] update ^1failed^7: %s' % (banlist.name, e.message()))
    
  def cmd_banlistcheck(self, data=None, client=None, cmd=None):
    """\
    check all players against banlists
    """
    if client is not None: client.message("checking players ...")
    self.checkConnectedPlayers()
    if client is not None: client.message("^4done")
    
          
class Banlist(object):
  _cronTab = None
  plugin = None
  name = None
  file = None
  message = None
  url = None
  
  def __init__(self, plugin, config):
    self.plugin = plugin
    
    node = config.find('name')
    if node is None or node.text == '':
      self.plugin.warning("name not found in config")
    else:
      self.name = node.text

    node = config.find('file')
    if node is None or node.text == '':
      raise BanlistException("file not found in config")
    else:
      self.file = node.text

    node = config.find('url')
    if node is not None and node.text != '':
      self.url = node.text
    
    node = config.find('message')
    if node is not None and node.text != '':
      self.message = node.text
      
      
    if not os.path.isfile(self.file):
      if self.url is None:
        raise BanlistException("file '%s' not found or not a file."%self.file)
      else:
        # create file from url
        result = self.updateFromUrl()
        if result is not True:
          raise BanlistException("failed to create '%s' from %s. (%s)" % (self.file, self.url, result))
        
    elif self.url is not None:
      # check if file ues older than an hour
      fileage = (time.time() - os.stat("%s" % self.file)[8]) 
      self.plugin.debug("%s age is %s" % (self.file, fileage))
      if fileage > 3600:
        self.plugin.debug("[%s] file is older than an hour" % self.name)
        if self.plugin._auto_update: 
            result = self.updateFromUrl()
            if result is not True:
                raise BanlistException("failed to create '%s' from %s. (%s)" % (self.file, self.url, result))
        else: 
            self.plugin.warning("%s [%s] file is older than an hour, consider updating" % (self.__class__.__name__, self.name))

        
    if self.url is not None and self.plugin._auto_update:
      rmin = random.randint(0,59)
      self.plugin.debug("[%s] will be autoupdated at %s min of every hour" % (self.name, rmin))
      self._cronTab = b3.cron.PluginCronTab(self.plugin, self.autoUpdateFromUrl, 0, rmin, '*', '*', '*', '*')
      self.plugin.console.cron + self._cronTab
        
    self.plugin.info("loading %s [%s], file:[%s], url:[%s], message:[%s]" % (self.__class__.__name__, self.name, self.file, self.url, self.message))

  def _checkFileExists(self):
    if not os.path.isfile(self.file):
      if self.url is None:
        self.plugin.error("file '%s' not found or not a file."%self.file)
        return False
      else:
        # create file from url
        self._updateFromUrlAndCheckAll()
        return False # return False as _updateFromUrlAndCheckAll will call onBanlistUpdate
    else:
      return True

  def _updateFromUrlAndCheckAll(self):
    try:
        result = self.updateFromUrl()
        if result is not True:
          raise BanlistException("failed to update '%s' from %s. (%s)" % (self.file, self.url, result))
        self.plugin.checkConnectedPlayers()
    except BanlistException, e:
        self.warning("%s" % e.message())
      
  def updateFromUrl(self):
    """
    Download the banlist from the url found in config and save it.
    Return True if succeeded
    Else return a string with the reason of failure
    """
    
    self.plugin.info("[%s] updating from %s"% (self.name, self.url))
    
    try:
      headers =  { 'User-Agent'  : user_agent  }
      req =  urllib2.Request(self.url, None, headers)
      webFile =  urllib2.urlopen(req)
      localFile = open(self.file, 'w')
      localFile.write(webFile.read())
      webFile.close()
      localFile.close()
      return True
    except IOError, e:
      if hasattr(e, 'reason'):
        return "%s" % e.reason
      elif hasattr(e, 'code'):
        return "error code: %s" % e.code
      self.plugin.debug("%s"%e)
      return "%s"%e
    except Exception, e:
      return "%s" % e.message
      
  def autoUpdateFromUrl(self):
    thread.start_new_thread(self._updateFromUrlAndCheckAll, ())

  def getMessage(self, client):
    """
    Return the message with pattern $name replaced with the banlist's name.
    """
    return self.message.replace('$name','%s'%client.name)\
        .replace('$ip','%s'%client.ip)\
        .replace('$guid','%s'%client.guid)\
        .replace('$id','@%s'%client.id)

    


  def getModifiedTime(self):
      """
      return the last modified time of the banlist file
      """
      return os.stat("%s" % self.file)[8]
      
      
    
class IpBanlist(Banlist):
  _forceRange = None
  
  def __init__(self, plugin, config):
    Banlist.__init__(self, plugin, config)
    
    # set specific settings 
    node = config.find('force_ip_range')
    if node is not None and string.upper(node.text) in ('YES', '1', 'ON', 'TRUE'):
      self._forceRange = True
    else:
      self._forceRange = False
    self.plugin.debug("%s [%s] force IP range : %s" % (self.__class__.__name__, self.name, self._forceRange))
  
  def isBanned(self, client):
  
    if client.ip is None or client.ip == '':
      return False
  
    if not self._checkFileExists():
      return False
      
    f=open(self.file)
    banlist=f.read()
    
    # search the exact ip
    rStrict=re.compile("([\n]|^)%s" % client.ip.replace('.','\.'))
    if rStrict.search(banlist) is not None:
      f.close()
      return client.ip
    
    # search the ip with .0 at the end
    rRange=re.compile("([\n]|^)%s" % '\.'.join(client.ip.split('.')[0:3])+'\.0')
    if rRange.search(banlist) is not None:
      f.close()
      return client.ip
    
    # if force range is set, enfore search by range event if banlist ip are not ending with ".0"
    rForceRange=re.compile("([\n]|^)%s" % '\.'.join(client.ip.split('.')[0:3])+'\.')
    if self._forceRange and rForceRange.search(banlist) is not None:
      f.close()
      return client.ip
    
    f.close()
    return False


class GuidBanlist(Banlist):
    
  def isBanned(self, client):
  
    if client.guid is None or client.guid == '':
      return False
  
    if not self._checkFileExists():
      return False
      
    f=open(self.file)
    banlist=f.read()
    
    if re.compile("([\n]|^)%s" % client.guid, re.IGNORECASE).search(banlist) is not None:
      f.close()
      return client.guid
   
    f.close()
    return False

class BanlistException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)



if __name__ == '__main__':
    
    from b3.fake import fakeConsole
    from b3.fake import FakeClient
    
    conf1 = b3.config.XmlConfigParser()
    conf1.loadFromString("""
    <configuration plugin="banlist">
        <settings name="global_settings">
            <set name="immunity_level">60</set>
            <set name="auto_update">yes</set>
        </settings>
        <settings name="commands">
            <set name="banlistinfo-blinfo">20</set>
            <set name="banlistupdate-blupdate">20</set>
            <set name="banlistcheck-blcheck">20</set>
        </settings>
        <ip_banlist>
          <name>UAA</name>
          <file>c:/temp/banlist-uaa.txt</file>
          <message>^4$name^7 is ^1BANNED^7 by the ^5[UAA]</message>
          <url>
            <![CDATA[http://www.urtadmins.com/e107_files/public/banlist.txt]]>
          </url>
        </ip_banlist>  
        <ip_banlist>
          <name>test ip list</name>
          <file>c:/temp/banlist-ip.txt</file>
          <message>^4$name^7 is ^1BANNED^4 (test ip list)</message>
        </ip_banlist>
    </configuration>
    """)
    
    p = BanlistPlugin(fakeConsole, conf1)
    p.onStartup()
    jack = FakeClient(fakeConsole, name="Jack", exactName="Jack", guid="qsd654sqf", _maxLevel=1, authed=True, ip='11.111.11.111')
    
    time.sleep(2)
    jack.connects(45)

    time.sleep(1)
#    moderator.says('!blinfo')
#    moderator.says('!blupdate')
#    time.sleep(5)
    moderator.says('!blcheck')
    
    time.sleep(5)
    
    jack.connects(948)
    
    while True: pass
    
    