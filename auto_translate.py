# -*- coding: utf-8 -*-
"""

TODO
----
 - replace len(nick)>2 with a more sane filter of messages, without need of translating
"""

SCRIPT_NAME = "auto_translate"
SCRIPT_AUTHOR = "anonymous2ch (get help @ freenode.#s2ch)"
SCRIPT_VERSION = "0.0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Automatically translate every message in irc channel to target language via google translate"
SCRIPT_COMMAND = "auto_translate"

try:
    import weechat as w
    import requests, urllib.parse, json
    import time
    import re
    from urllib.parse import urldefrag
    IMPORT_ERR = 0
except ImportError:
    IMPORT_ERR = 1
import os



auto_translate_settings_default = {
    'language': ('en','language code to translate to'),
    'translated_channels': ('freenode.#s2ch,freenode.#test','comma-separated list of channels, which should be translated'),
    'google_endpoint': ('https://clients5.google.com/translate_a/t', 'google translate endpoint'),
    'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36','Browser version to emulate')
}
auto_translate_settings = {}

def auto_translate_cb(data, buffer, date, tags, displayed, highlight, prefix, message):
    
    
    channel = w.buffer_get_string(buffer, 'name')
    
    
    nick = prefix
    
    
    if channel in str(auto_translate_settings['translated_channels']) and len(nick)>2:
      
        try:
           mesg = message.decode('utf-8')
        except AttributeError:
           mesg = message
           
       
        
        headers = {
        'User-Agent':auto_translate_settings['user-agent']
        }
        params = {
        "client":"dict-chrome-ex",
        "sl":"auto",
        "tl":auto_translate_settings['language'],
        "q":mesg
        }
        
        
        
        resp = requests.get(auto_translate_settings['google_endpoint'],headers=headers,params=params).text
        
        data =  json.loads(resp)
        
        
        for sentence in data["sentences"]:
          try:
            w.prnt_date_tags(buffer, 0, 'no_log,notify_none', sentence['trans'])
          except KeyError:
            return w.WEECHAT_RC_OK
        
    return w.WEECHAT_RC_OK


def auto_translate_load_config():
    global auto_translate_settings_default, auto_translate_settings
    version = w.info_get('version_number', '') or 0
    for option, value in auto_translate_settings_default.items():
        if w.config_is_set_plugin(option):
            auto_translate_settings[option] = w.config_get_plugin(option)
        else:
            w.config_set_plugin(option, value[0])
            auto_translate_settings[option] = value[0]
        if int(version) >= 0x00030500:
            w.config_set_desc_plugin(option, value[1])


def auto_translate_config_cb(data, option, value):
    """Called each time an option is changed."""
    auto_translate_load_config()
    return w.WEECHAT_RC_OK

def auto_translate_cmd_cb(data, buffer, args):
   
    if not args or len(args.split())>1:
        w.command('', '/help %s' %SCRIPT_COMMAND)
        return w.WEECHAT_RC_OK
        
    w.config_set_plugin("translated_channels", args)
    auto_translate_settings["translated_channels"] = w.config_get_plugin("translated_channels")
    w.prnt_date_tags(buffer, 0, 'no_log,notify_none', "Translating channel: "+auto_translate_settings["translated_channels"] )
    return w.WEECHAT_RC_OK
    
    
if w.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
              SCRIPT_LICENSE, SCRIPT_DESC, '', ''):
    if IMPORT_ERR:
        w.prnt("", "something bad happened")
  
    auto_translate_load_config()
 

    w.hook_print('', 'irc_privmsg', '', 1, 'auto_translate_cb', '')
    
    w.hook_command("auto_translate",
                    SCRIPT_DESC,
                   "<channel(s)>",
"""
usage: /auto_translate <channel(s)>
for example:
/auto_translate freenode.#s2ch,freenode.#chlor
""","",
"auto_translate_cmd_cb", "")

