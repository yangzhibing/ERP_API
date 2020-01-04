# -*- encoding: utf-8 -*-
from flask import Flask, jsonify, request, json, session, abort, redirect
# 导入xmlrpc库，这个库是python的标准库。
import xmlrpclib
import datetime
from os import path
from flask import Blueprint
from ..config import Config

from wechatpy.oauth import WeChatOAuth, WeChatOAuthException
from wechatpy.client.api import WeChatJSAPI
from wechatpy.client import WeChatClient
import time


wechat_blueprint = Blueprint(
    'wechat',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'wechat'),
    url_prefix="/wechat"
)
@wechat_blueprint.route('/set_back_uri', methods=['GET'])
def set_back_uri():
    back_uri = request.args.get('back_uri')
    if back_uri:
        session['back_uri'] = back_uri
    return jsonify({'data': 'ok'})

# 微信登录
@wechat_blueprint.route('/post_login', methods=['GET'])
def post_login():
    back_uri = request.args.get('back_uri')
    if back_uri:
        session['back_uri'] = back_uri
    redirect_uri = 'http://'+ Config.DOMAIN +'/wechat/post_login'
    wechat_oauth = WeChatOAuth(Config.APP_ID, Config.APP_SECRET, redirect_uri, scope='snsapi_base', state='')
    code = request.args.get('code', None)
    odoo_uids = None
    access_token = None
    url = wechat_oauth.authorize_url
    openid = None

    if code:
        try:
            if session.has_key('access_token') and session['access_token'] is not None:
                access_token = session['access_token']
            else:
                access_token = wechat_oauth.fetch_access_token(code)
                session['access_token'] = access_token
            if access_token is not None:
                session['access_token'] = access_token
            print('access_token: ' + json.dumps(access_token))

        except Exception as e:
            if e is WeChatOAuthException:
                print e.errmsg, e.errcode
                # 这里需要处理请求里包含的 code 无效的情况

            else:
                print("another error")
                print e

                print('error access_token: ' + json.dumps(access_token))
            abort(400)

        else:
            openid = access_token['openid']
            print("openid has saved: " + openid)

    else:
        print("redirect url to :" + url)
        return redirect(url)
    if openid is None:
        abort(401)
    odoo_uids  = Config.models.execute_kw(Config.dbname, Config.uid, Config.password,
                                            'res.users', 'search',
                                            [[['x_openid', '=', openid]]])
    if odoo_uids:
        if session.has_key('back_uri') and session['back_uri'] is not None:
            back_uri = session['back_uri']
            print("odoo uid has got:" + str(odoo_uids[0]))
            session[odoo_uids[0]] = back_uri
            redirect_url = Config.smartcell_url + '?uid=' + str(odoo_uids[0]) + '&back_uri=' + back_uri
            print('redirect_url: ' + redirect_url)
            return redirect(redirect_url)

    else:
        abort(403)


# http://docs.wechatpy.org/zh_CN/master/client/jsapi.html#
@wechat_blueprint.route('/get_jsapi_ticket', methods=['GET'])
def get_jsapi_ticket():
    wechat_client = WeChatClient(Config.APP_ID, Config.APP_SECRET)
    wechat_js_api = WeChatJSAPI(wechat_client)
    wechat_jsapi_ticket = wechat_js_api.get_jsapi_ticket()
    data = {'jsapi_ticket': wechat_jsapi_ticket }
    return jsonify({'data': data })


@wechat_blueprint.route('/get_ticket', methods=['GET'])
def get_ticket():
    wechat_client = WeChatClient(Config.APP_ID, Config.APP_SECRET)
    wechat_js_api = WeChatJSAPI(wechat_client)
    wechat_ticket = wechat_js_api.get_ticket()
    data = {'ticket': wechat_ticket}
    return jsonify({'data': data})


@wechat_blueprint.route('/get_jsapi_signature', methods=['GET'])
def get_jsapi_signature():
    wechat_client = WeChatClient(Config.APP_ID, Config.APP_SECRET)
    wechat_js_api = WeChatJSAPI(wechat_client)
    ticket = wechat_js_api.get_jsapi_ticket()
    url = request.args.get('url')
    print("signature url: " + url)

    timestamp = str(int(time.time()))
    wechat_signature = wechat_js_api.get_jsapi_signature(Config.NONCESTR, ticket, timestamp, url)
    print("wechat_signature: " + wechat_signature)
    data = {'signature': wechat_signature,
            'appId': Config.APP_ID,
            'nounceStr': Config.NONCESTR,
            'timestamp': timestamp,
            'ticket': str(ticket)
            }
    return jsonify({'data': data})