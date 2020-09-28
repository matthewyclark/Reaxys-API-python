# -*- coding: utf-8 -*-
# Python wrapper for the Reaxys API
#
# Version: 1.1.0-beta.2
#
# Author:  Dr. Sebastian Radestock, Elsevier
# Author:  Dr. Alexander Riemer, Elsevier
# Author:  Dr. Markus Fischer, Elsevier
# Date:    July 26th, 2019
# Change Log 1.1.0-beta.1, July 26th, 2019
# A. Support for Python 3
# B. get_field_content modifications
# B.1. returns values for elements with highlights
# B.2. new method argument highlight_only. If True will return only a value if field contains highlights
#
# Change Log 1.1.0-beta.2, July 26th, 2019
# A. Method retrieve now supports clustering hitsets
# A.1. Added optional arguments dbname and context, that are required to formulate group by statements

import http.cookiejar, xml.dom.minidom,  re
from urllib.request import Request, urlopen
import socks
import socket


class Reaxys_API:

    def __init__(self, proxy=None, port=None):
        
        self.url = ""
        self.headers = {'Content-type' : 'text/xml; charset="UTF-8"'}
        self.callername = ""
        self.sessionid = ""
        self.resultname = ""
        self.resultsize = ""
        self.citationset = ""
        self.citationcount = ""
        self.proxy = proxy
        self.port = port

        if proxy and port:
            socks.setdefaultproxy(
                socks.PROXY_TYPE_SOCKS5, self.proxy, self.port)
            socket.socket = socks.socksocket

        # Set True for verbose output:
        self.debug = False

    def _get_resultname(self, response_dom):
        
        #response_dom = xml.dom.minidom.parseString(response_xml)
        

        # Length of response_dom.getElementsByTagName("resultsname") should always be 1.
        # Node resultsname should not conatin subnodes.
        try:
            resultname = response_dom.getElementsByTagName("resultname")[0].childNodes[0].nodeValue
        except IndexError:
            resultname = None
        return resultname

    def _get_resultsize(self, response_dom):
        
        #response_dom = xml.dom.minidom.parseString(response_xml)

        # Length of response_dom.getElementsByTagName("resultsize") should always be 1.
        # Node resultsize should not conatin subnodes.
        try:
            resultsize = response_dom.getElementsByTagName("resultsize")[0].childNodes[0].nodeValue
        except IndexError:
            resultsize = None

        return resultsize

    def _get_citationset(self, response_dom):
        
        #response_dom = xml.dom.minidom.parseString(response_xml)

        # Length of response_dom.getElementsByTagName("citationset") should always be 1.
        # Node citationset should not conatin subnodes.          
        return response_dom.getElementsByTagName("citationset")[0].childNodes[0].nodeValue

    def _get_citationcount(self, response_dom):
        
        #response_dom = xml.dom.minidom.parseString(response_xml)

        # Length of response_dom.getElementsByTagName("citationcount") should always be 1.
        # Node citationcount should not conatin subnodes.          
        return response_dom.getElementsByTagName("citationcount")[0].childNodes[0].nodeValue

    def get_facts_availability(self, response_dom, field):

        facts_availability = "0"
        
        #response_dom = xml.dom.minidom.parseString(response_xml)

        facts = response_dom.getElementsByTagName("facts")[0]
        for fact in facts.childNodes:
            if 'name="' + field + '"' in fact.toxml():
                facts_availability = fact.childNodes[0].nodeValue.split("(")[0]

        return facts_availability

    def get_field_content(self, response_dom, field, highlight_only=False):
        
        field_content = []
        
        #response_dom = xml.dom.minidom.parseString(response_xml)
        
        for element in response_dom.getElementsByTagName(field):

            # Concatenate text values if highlight is present
            if element.getAttribute('highlight') == 'true':
                field_content.append(
                    ''.join([e.data
                             if type(e) == xml.dom.minidom.Text
                             else e.childNodes[0].data for e in element.childNodes]))

            # If node contains further sub-nodes: return full xml.
            elif len(element.childNodes) > 1 and highlight_only is False:
                field_content.append(element.toxml())

            # If node does not conatin further sub-nodes: return node value.
            elif len(element.childNodes) == 1 and highlight_only is False:
                field_content.append(element.childNodes[0].nodeValue)
                
        return field_content

    def connect(self, url, url_main, username, password, callername):
        
        self.url = url
        self.callername = callername
        cookies = http.cookiejar.CookieJar()
        
        connect_template = """<?xml version="1.0"?>
          <xf>
            <request caller="%s">
              <statement command="connect" username="%s" password="%s"/>
            </request>
          </xf>\n"""
        payload = connect_template % (callername, username, password)
        data = payload.encode()

        # Header reset.
        self.headers = {'Content-type' : 'text/xml; charset="UTF-8"'}

        # ELSAPI support
        self.headers['X-ELS-APIKey'] = callername
        self.headers['Accept'] = "*/*"
        request = Request(self.url, data=data, headers=self.headers)
        
        if self.debug:
            print('-----------------------\nQuery headers from connect:')
            print(self.headers)
            print('-----------------------\nQuery from connect:')
            print(payload)

        response = urlopen(request)
        response_xml = response.read()
        response_dom = xml.dom.minidom.parseString(response_xml)
        
        if self.debug:
            print('-----------------------\nResponse headers from connect:')
            print(response.info())
            print('-----------------------\nResponse from connect:')
            print(response_xml)

        # Get sessionid.
        
        element = response_dom.getElementsByTagName("sessionid")
        self.sessionid = element[0].childNodes[0].nodeValue
        
        # Cookies are read from the response and stored in self.header
        #     which is used as a request header for subsequent requests.
        cookies.extract_cookies(response, request)
        
        # Cookie handling 3.0: Simply store and resend ALL cookies received from server
        self.headers['Cookie'] = "; ".join(re.findall(r"(?<=Cookie ).*?=\S*", str(cookies)))

    def disconnect(self):
        
        disconnect_template = """<?xml version="1.0"?>
          <xf>
            <request caller="%s">
              <statement command="disconnect" sessionid="%s"/>
            </request>
          </xf>\n"""
        payload = disconnect_template%(self.callername, self.sessionid)
        data = payload.encode()

        request = Request(self.url, data=data, headers=self.headers)

        if self.debug:
            print('-----------------------\nQuery headers from disconnect:')
            print(self.headers)
            print('-----------------------\nQuery from disconnect:')
            print(payload)

        response = urlopen(request)
        response_xml = response.read()
        
        if self.debug:
            print('-----------------------\nResponse headers from disconnect:')
            print(response.info())
            print('-----------------------\nResponse from disconnect:')
            print(response_xml)

    def select(self, dbname, context, where_clause, order_by, options):
        
        select_template = """<?xml version="1.0" encoding="UTF-8"?>
          <xf>
            <request caller="%s" sessionid="">
              <statement command="select"/>
              <select_list>
                <select_item/>
              </select_list>
              <from_clause dbname="%s" context="%s">
              </from_clause>
              <where_clause>%s</where_clause>
              <order_by_clause>%s</order_by_clause>
              <options>%s</options>
            </request>
          </xf>\n"""
        payload = select_template%(self.callername, dbname, context, where_clause, order_by, options)
        data = payload.encode()
        request = Request(self.url, data=data, headers=self.headers)

        if self.debug:
            print('-----------------------\nQuery headers from select:')
            print(self.headers)
            print('-----------------------\nQuery from select:')
            print(payload)

        response = urlopen(request)
        response_xml = response.read()
        response_dom = xml.dom.minidom.parseString(response_xml)
        
        if self.debug:
            print('-----------------------\nResponse headers from select:')
            print(response.info())
            print('-----------------------\nResponse from select:')
            print(response_xml)

        
        self.resultname = self._get_resultname(response_dom)
        self.resultsize = self._get_resultsize(response_dom)
        
        if ("NO_CORESULT" not in options) and ("C" not in context):
            self.citationset = self._get_citationset(response_dom)
            self.citationcount = self._get_citationcount(response_dom)

        return response_dom

    def expand(self, dbname, first_item, last_item, where_clause):
        
        select_template = """<?xml version="1.0" encoding="UTF-8"?>
          <xf>
            <request caller="%s" sessionid="%s">
              <statement command="expand"/>
              <from_clause dbname="%s" first_item="%s" last_item="%s">
              </from_clause>
              <where_clause>%s</where_clause>
            </request>
          </xf>\n"""
        payload = select_template%(self.callername, self.sessionid, dbname, first_item, last_item, where_clause)
        data = payload.encode()
        request = Request(self.url, data=data, headers=self.headers)

        if self.debug:
            print('-----------------------\nQuery headers from expand:')
            print(self.headers)
            print('-----------------------\nQuery from expand:')
            print(payload)
        
        response = urlopen(request)
        response_xml = response.read()
        response_dom = xml.dom.minidom.parseString(response_xml)
        
        if self.debug:
            print('-----------------------\nResponse headers from expand:')
            print(response.info())
            print('-----------------------\nResponse from expand:')
            print(response_xml)

        return response_dom

    def post(self, payload):

        data = payload.encode()
        request = Request(self.url, data=data, headers=self.headers)

        if self.debug:
            print('-----------------------\nQuery headers from post:')
            print(self.headers)
            print('-----------------------\nQuery from post:')
            print(payload)
        
        response = urlopen(request)
        response_xml = response.read()
        
        if self.debug:
            print('-----------------------\nResponse headers from post:')
            print(response.info())
            print('-----------------------\nResponse from post:')
            print(response_xml)

    def retrieve(self, resultname, select_items, first_item, last_item, order_by, group_by, group_item, options,
                 dbname=None, context=None):
        # if group_by is given, please provide group_item, e.g. "1" or "1,2"
        
        if group_by != '':
            grouplist = 'grouplist="' + group_item + '"'
        else:
            grouplist = ''

        db_template = ''
        if dbname is not None:
            db_template = 'dbname="%s"' % dbname

        context_template = ''
        if context is not None:
            context_template = 'context="%s"' % context


        select_item_template = """                <select_item>%s</select_item>\n"""
        select_template = """<?xml version="1.0" encoding="UTF-8"?>
          <xf>
            <request caller="%s" sessionid="%s">
              <statement command="select"/>
              <select_list>\n"""
        for index in range (0,len(select_items)):
            select_template = select_template + select_item_template%(select_items[index])
        select_template = select_template + """              </select_list>
              <from_clause %s %s resultname="%s" %s first_item="%s" last_item="%s">
              </from_clause>
              <order_by_clause>%s</order_by_clause>
              <group_by_clause>%s</group_by_clause>
              <options>%s</options>
            </request>
          </xf>\n"""
        payload = select_template % (
            self.callername, self.sessionid, db_template, context_template, resultname, grouplist,
            first_item, last_item, order_by, group_by, options)
        data = payload.encode()
        
        request = Request(self.url, data=data, headers=self.headers)

        if self.debug:
            print('-----------------------\nQuery headers from retrieve:')
            print(self.headers)
            print('-----------------------\nQuery from retrieve:')
            print(payload)
        
        response = urlopen(request)
        response_xml = response.read().decode()
        
        if self.debug:
            print('-----------------------\nResponse headers from retrieve:')
            print(response.info())
            print('-----------------------\nResponse from retrieve:')
            print(response_xml)

        return xml.dom.minidom.parseString(response_xml)
        #return response_xml
