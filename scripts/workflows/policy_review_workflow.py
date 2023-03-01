#!/usr/bin/env python3

import os
import sys
import json
import requests
import re

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_EVENT = os.getenv("GITHUB_EVENT")

API_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
}

# helper function


def update_issue(github_event, review_domains):
    review_domain_labels = []
    comment = "Reviews have been requested for:"
    for review_domain in review_domains:
        message += "\n{review_domain}"
        review_domain_labels.append(f"{review_domain}_policy_review_requested")

    r = requests.post(
        github_event["issue"]["comments_url"],
        headers=API_HEADERS,
        data=json.dumps({"body": comment}),
    )
    print("Adding comment", comment)
    print(r.json())

    r = requests.post(
        github_event["issue"]["labels_url"],
        headers=API_HEADERS,
        data=json.dumps({"labels": review_domain_labels}),
    )
    print("Adding labels", review_domain_labels)
    print(r.json())


def get_review_domain_from_event(github_event):
    before_body = github_event["changes"]["body"]["from"]
    after_body = github_event["comment"]["body"]

    before = re.findall("- \[ \] request (\w+) review", before_body)
    after = re.findall("- \[x\] request (\w+) review", after_body)

    review_domains = list(set(before) & set(after))
    print(f"Review_domains: {review_domains} were marked by user for review")

    return review_domains


def filter_existing_requested_review_domains(review_domains, labels):
    filtered_review_domains = []
    for review_domain in review_domains:
        if f"{review_domain}_policy_review_requested" in labels:
            print(
                f"Domain: {review_domain} has already been submitted for policy review")
        else:
            print(
                "Domain: {review_domain} has been marked for review submission")
            filtered_review_domains.append(review_domain)
    return filtered_review_domains


def main():
    try:
        github_event = json.loads(GITHUB_EVENT)
    except json.decoder.JSONDecodeError:
        print("not a Github event")
        exit(1)

    review_domains = get_review_domain_from_event(github_event)
    labels = github_event["issue"]["labels"]
    if review_domains:
        filtered_review_domains = filter_existing_requested_review_domains(
            review_domains, labels)
        update_issue(github_event, review_domains)


if __name__ == "__main__":
    main()
