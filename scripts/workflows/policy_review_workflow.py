#!/usr/bin/env python3

import os
import sys
import json
import requests
import re

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

GITHUB_EVENT = os.getenv("GITHUB_EVENT")

PR_NUMBER = os.getenv("PR_NUMBER")
REF_ID = os.getenv("REF_ID")

URI = "https://api.github.com"
API_SEARCH_URL = f"{URI}/search"
API_REPO_URL = f"{URI}/repos/{GITHUB_REPOSITORY}"
REPO_URL = f"{URI}/repos/{GITHUB_REPOSITORY}"

API_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
}

# helper function


def get_labels(pr_number):
    """ getting PR's labels """
    r = requests.get(
        f"{API_REPO_URL}/issues/{pr_number}/labels", headers=API_HEADERS)
    return [res["name"] for res in r.json()]


def add_labels(pr_number, labels):
    if not labels:
        return
    r = requests.post(
        f"{API_REPO_URL}/issues/{pr_number}/labels",
        headers=API_HEADERS,
        data=json.dumps({"labels": labels}),
    )
    print("Adding Labels", labels)
    print(r.json())


def post_review_request_comment(domains, pr_number):
    message = f"Reviews have been requested for: {domains}"
    r = requests.post(
        f"{API_REPO_URL}/issues/{pr_number}/comments",
        headers=API_HEADERS,
        data=json.dumps({"body": message}),
    )


def get_review_domain_from_event(github_event):
    before_body = github_event["changes"]["body"]["from"]
    after_body = github_event["comment"]["body"]

    before = re.findall("- \[ \] request (\w+) review", before_body)
    after = re.findall("- \[[xX]]\] request (\w+) review", after_body)

    return list(set(before) & set(after))


if __name__ == "__main__":
    pr_number = PR_NUMBER
    try:
        github_event = json.loads(GITHUB_EVENT)
    except json.decoder.JSONDecodeError:
        print("not a Github event")
        exit(1)

    review_domains = get_review_domain_from_event(github_event)
    print(f"review_domains: {review_domains}")
    if review_domains:
        post_review_request_comment(review_domains, pr_number)
