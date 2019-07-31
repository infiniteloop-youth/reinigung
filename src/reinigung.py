#!/usr/bin/env python
# -*- Coding: utf-8 -*-

from argparse import  ArgumentParser
from os import environ, makedirs
from datetime import datetime
from os.path import abspath, join, dirname, exists, splitext
from time import time
from dotenv import load_dotenv

import slack

DIR = dirname(dirname(abspath(__file__)))

load_dotenv(join(DIR, ".env"))

ADMIN_SLACK_TOKEN = environ.get("ADMIN_SLACK_TOKEN")
POST_SLACK_TOKEN = environ.get("POST_SLACK_TOKEN")
TARGET_CHANNEL = environ.get("TARGET_CHANNEL")
TARGET_AGO = int(environ.get("TARGET_AGO"))
DOWNLOAD_PATH = environ.get("DOWNLOAD_PATH")
REPORT_CHANNEL = environ.get("REPORT_CHANNEL")

def normalization(text, char):
    """
    Replace symbols which cant use in filename
    """
    symbols = list(range(0, 33)) + [34, 39] + list(range(42, 48)) + list(range(58, 64)) + list(range(91, 95)) + [96] + list(range(123, 128))
    for symbol in symbols:
        text = text.replace(chr(symbol), char)
    return text

def main(is_dry, is_all):
    """
    Knock knock
    """

    started_at = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    delete_to = int(time() - TARGET_AGO)

    print("Reinigung")
    print("started_at:"+started_at)

    if is_dry:
        print("Dry run")

    # Read settings
    is_all = True if TARGET_CHANNEL == "" else False

    print("All channel" if is_all else "")

    all_channels = slack.get_channels(ADMIN_SLACK_TOKEN, exclude_archived=True, exclude_members=True)["channels"]
    users = slack.get_users(ADMIN_SLACK_TOKEN)["members"]

    # set find range
    if is_all:
        channels = [channel for channel in all_channels if channel["is_channel"] and not channel["is_private"]]
    else:
        channels = [channel for channel in all_channels if channel["name"] == TARGET_CHANNEL]

    report_log = ""
    total_count = 0

    # in channel
    for channel in channels:
        channel_count = 0

        report_log += "#{}({}) - {}\n\n".format(
            channel["name"],
            channel["id"],
            channel["purpose"]["value"]
        )

        folder_path = abspath(join(DIR, DOWNLOAD_PATH, channel["name"]))

        print("in #{}".format(channel["name"]))

        # make folder
        if not exists(folder_path) and not is_dry:
            makedirs(folder_path)

        files = slack.get_files(
            ADMIN_SLACK_TOKEN,
            channel=channel["id"],
            ts_to=delete_to
        )["files"]

        # in file
        for file in files:
            # make file name
            file_name = "{}-{}-{}-{}{}-{}{}".format(
                datetime.fromtimestamp(int(file["timestamp"])).strftime("%Y%m%d%H%M%S"),
                file["id"],
                [user["name"] for user in users if user["id"] == file["user"]][0],
                normalization(file["title"], "_")[:10],
                "-"+normalization(file["initial_comment"]["comment"], "_")[:30] if "initial_comment" in file else "",
                normalization(splitext(file["name"])[0], "_"),
                splitext(file["name"])[1]
            )
            file_path = abspath(join(folder_path, file_name))

            if not is_dry:
                # download
                file_content = slack.get_file(ADMIN_SLACK_TOKEN, file["id"])
                with open(file_path, "wb") as save_file:
                    save_file.write(file_content)
                # delete
                    deleted = slack.delete_file(ADMIN_SLACK_TOKEN, file["id"])

            # increment channel counter
            channel_count += 1

            # add log
            report_log += "- {} @{} {} - {} {}\n  - {}\n\n".format(
                datetime.fromtimestamp(int(file["timestamp"])).strftime("%Y/%m/%d %H:%M:%S"),
                [user["name"] for user in users if user["id"] == file["user"]][0],
                file["title"],
                file["initial_comment"]["comment"].replace("\n","") if "initial_comment" in file else "",
                file["name"],
                file_name
            )

            print("- {}".format(file_path))

        # increment total counter
        total_count += channel_count

        report_log += "Total : {} files\n\n".format(channel_count)

    finished_at = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    # make great report
    report = """
Reinigung - Auto clean up slack files

===== Settings report =====

All delete?    : {}
Dry run?       : {}
Target channel : {}
Delete before  : {}
Started at     : {}
Finished at    : {}

===== Running report =====

Total delete     : {} files

===== Running log =====

{}

===== End of report ======
""".format(
    "Yes" if is_all else "No",
    "Yes" if is_dry else "No",
    TARGET_CHANNEL,
    datetime.fromtimestamp(delete_to).strftime("%Y/%m/%d %H:%M:%S"),
    started_at,
    finished_at,
    total_count,
    report_log
    )
    slack.post_file(
        POST_SLACK_TOKEN,
        report,
        channels=slack.get_channel_id(ADMIN_SLACK_TOKEN, REPORT_CHANNEL),
        filename="reinigung-report-{}.txt".format(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")),
        filetype="text",
        title="Reinigung report"
    )
    print("finished_at:"+finished_at)
    print("done")

if __name__ == "__main__":
    # Parse arguments
    parser = ArgumentParser(description="Auto clean up slack files")
    parser.add_argument("-d", "--dry", help="Testing mode", action="store_true")
    parser.add_argument("-a", "--all", help="Remove in all channel", action="store_true")
    args = parser.parse_args()

    # Call main function
    main(is_dry=args.dry, is_all=args.all)
