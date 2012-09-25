import xchat
import re

__module_name__ = "Autoghost"
__module_version__ = "0.1"
__module_description__ = "Python module to automatically ghost and renick"

NICKPATTERN = re.compile("^:([^!]+)!")

def ghostcb(word, word_eol, userdata):
    c = xchat.get_context()
    nick = word[3] #use this instead of preferred nick, I guess.
    pw = c.get_info("nickserv")
    u = {"context":c, "nick":nick}
    u["hook"] = xchat.hook_server("NOTICE", noticecb, userdata=u)
    xchat.command("msg nickserv ghost {} {}".format(nick, pw))
    return xchat.EAT_NONE

def noticecb(word, word_eol, userdata):
    match = NICKPATTERN.match(word[0])
    matchtxt = 'Ghost with your nick has been killed.'
    if not match or match.group(1) != 'NickServ':
        return xchat.EAT_NONE
    if word_eol[-2][1:] == 'Access denied.':
        xchat.unhook(userdata["hook"])
    elif len(word_eol) > 7 and word_eol[-7][1:] == matchtxt:
        u = {}
        u.update(userdata)
        c = u["context"]
        c.command("nick " + u["nick"])
        u["hook"] = xchat.hook_server("", identifycb,
                                             userdata=u)
        xchat.unhook(userdata["hook"])
    return xchat.EAT_NONE

def identifycb(word, word_eol, userdata):
    c = xchat.get_context()
    match = NICKPATTERN.match(word[0])
    matchtxt = "This nickname is registered and protected."
    if not match or match.group(1) != 'NickServ':
        return xchat.EAT_NONE
    if matchtxt in word_eol[0]:
        c.command("msg nickserv identify " + c.get_info('nickserv'))
    return xchat.EAT_NONE

def onconnectcb(word, word_eol, userdata):
    c = xchat.get_context()
    if c.get_info('nick') != xchat.get_prefs('irc_nick1'):
        c.command('nick ' + xchat.get_prefs('irc_nick1'))

xchat.hook_server("433", ghostcb) #server numeric for failed nick change
xchat.hook_server("NOTICE", identifycb) #watch for nickserv warning to identify
xchat.hook_server("2", onconnectcb) #server numeric sent when first connecting

def unloadcb(userdata):
    xchat.prnt("{} unloaded.".format(__module_name__))
xchat.hook_unload(unloadcb)
xchat.prnt("{} loaded.".format(__module_name__))
