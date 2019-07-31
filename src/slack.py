#!/usr/bin/env python3
# -*- coding: utf_8 -*-

"""
Simple Slack API wrapper
"""

from requests import get, post

def get_channels(token, exclude_archived=False, exclude_members=False):
    """
    Get channel list
    """
    params = {
        "token": token,
        "exclude_archived": exclude_archived,
        "exclude_members": exclude_members
    }
    r = get("https://slack.com/api/channels.list", params=params)
    if r.ok:
        rparsed = r.json()
        if rparsed["ok"]:
            return rparsed
        else:
            raise Exception(rparsed["error"])
    else:
        raise Exception("Slack API Returns error")


def get_users(token, include_locale=False, presence=False):
    """
    Get user list
    """
    params = {
        "token": token,
        "include_locale": include_locale,
        "presence": presence
    }
    r = get("https://slack.com/api/users.list", params=params)
    if r.ok:
        rparsed = r.json()
        if rparsed["ok"]:
            return rparsed
        else:
            raise Exception(rparsed["error"])
    else:
        raise Exception("Slack API Returns error")


def get_files(token, channel="", ts_from=0, ts_to=0, types=all):
    """
    Get file list
    """
    params = {
        "token": token,
        "channel": channel,
        "ts_from": ts_from,
        "ts_to": ts_to,
        "types": types
    }
    r = get("https://slack.com/api/files.list?token={}&channel={}&ts_to={}", params=params)
    if r.ok:
        rparsed = r.json()
        if rparsed["ok"]:
            return rparsed
        else:
            raise Exception(rparsed["error"])
    else:
        raise Exception("Slack API Returns error")


def delete_file(token, file):
    """
    Delete file
    """
    params = {
        "token": token,
        "file": file
    }
    r = get("https://slack.com/api/files.delete", params=params)
    if r.ok:
        rparsed = r.json()
        if rparsed["ok"]:
            return rparsed
        else:
            raise Exception(rparsed["error"])
    else:
        raise Exception("Slack API Returns error")


def post_file(token, content, channels="", filename="", filetype="", initial_comment="", title=""):
    """
    Upload file
    """
    params = {
        "token": token,
        "channels": channels,
        "filename": filename,
        "filetype": filetype,
        "initial_comment": initial_comment,
        "title": title
    }
    payload = {
        "content": content
    }

    r = post("https://slack.com/api/files.upload", params=params, data=payload)
    if r.ok:
        rparsed = r.json()
        if rparsed["ok"]:
            return rparsed
        else:
            raise Exception(rparsed["error"])
    else:
        raise Exception("Slack API Returns error")

def get_file(token, file):
    """
    Download file
    """
    params = {
        "token": token,
        "file": file
    }
    r = get("https://slack.com/api/files.info", params=params)
    if r.ok:
        rparsed = r.json()
        if rparsed["ok"]:
            headers = {
                "Authorization": "Bearer " + token
            }
            download = get(rparsed["file"]["url_private_download"], headers=headers)
            return download.content
        else:
            raise Exception(rparsed["error"])
    else:
        raise Exception("Slack API Returns error")

def get_channel_id(token, name, exclude_archived=False):
    """
    Get channel id from name
    """
    channels = get_channels(
        token,
        exclude_archived=exclude_archived,
        exclude_members=True
    )["channels"]
    return [channel for channel in channels if channel["name"] == name][0]["id"]
