#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# benjamin.kubitz@sap.com

import re
from github import Github
from mdutils.mdutils import MdUtils
import requests
from getpass import getpass
requests.packages.urllib3.disable_warnings()

# function to get the diff for a given PR
def get_diff(token, pr):
    diff_url = ''.format(pr) # can be found within the URL in GitHub
    diff_headers = {'Authorization': 'token {} '.format(token),'Accept': 'application/vnd.github.v3.diff'}
    r = requests.get(diff_url, headers=diff_headers, verify=False)
    diff = r.text
    return diff
# create a dict containing the changed cookbooks with its new tags
def create_mapping(diff):
    diff_dict = {}
    changed_raw = re.findall(r'^\+cookbook.*', diff, re.MULTILINE) #get all cookbooks that has been updated from diff
    changed_cookbooks = re.findall(r"\+\w+\s+'(.*?)'", str(changed_raw), re.MULTILINE) # now extract only the cookbook names
    changed_tags = re.findall(r"tag: '(.*?)'", str(changed_raw), re.MULTILINE) # get the tags for the updated cookbooks
    diff_dict = dict(zip(changed_cookbooks, changed_tags)) # create a dict with k=cookbook and v=tag
    return diff_dict
# get the tag and release notes
def get_release_info(token, cookbook, release_id):
    g = Github(base_url='', verify=False, login_or_token='{}'.format(token))
    release = g.get_repo('CloudChef/{}'.format(cookbook)).get_release('{}'.format(release_id))
    return release 

def main():
    # get the API Token
    # token = getpass('Enter your GitHub API-Token: ')
    token = ''
    # first we need the diff of the PR
    pr = input('Enter PR number: ')
    diff = get_diff(token, pr)
    # now we need to extract the changes and store them as k:v
    changed = create_mapping(diff)
    # now the release infos based on the GitHub tags
    changelog = [] #release notes without cookbook name used to build the mdFile     
    # create a mdFile object
    mdFile = MdUtils(file_name='{}.'.format(pr), title='PR_{}_comment'.format(pr))

    for k, v in changed.items():
        changelog.clear() # flush the list to avoid doubled entrys caused by the loop
        # print(k,v) #cookbook + versioon
        ### print(release.tag_name, release.title)
        mdFile.write(text=k, bold_italics_code='b')
        release = get_release_info(token, k, v) # this is an object
        # release.tage_name = e.g. 1.3.4
        # release.title = Making resolver cookbook SLES15 compatible
        tag_name = release.tag_name
        release_title = release.title
        release_summary = '- {0}: `{1}`'.format(tag_name, release_title)
        changelog.append(release_summary)
        mdFile.new_list(changelog)
    
    
    print(mdFile.file_data_text)
    

if __name__ == "__main__":
    main()
