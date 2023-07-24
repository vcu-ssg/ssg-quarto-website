"""
Main entry code for the cli
"""
import os
import sys
import json
import gspread
import loguru
import click
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
from IPython.display import Markdown
from tabulate import tabulate

destination_folder = "../website/about/"
spreadsheet_key = "19I04Ljy8X8f1mqhpEh5-XRmj4iIEv1huaijqy60a42E"

# define scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# create credentials object
credential_file = os.path.join(os.path.expanduser("~"), ".gsecrets", "gsheets-credentials.json")
if not os.path.isfile( credential_file ):
  print("Missing credential file:",credential_file)
  sys.exit()

creds = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scope)
client = gspread.authorize(creds)

@click.group
@click.pass_context
def cli(ctx):
    pass

def get_biographies_from_gsheet():
    worksheet_name = "Biographies"
    sheet = client.open_by_key(spreadsheet_key).worksheet(worksheet_name)
    data = sheet.get_all_values()
    headers = data.pop(0)
    bios_df = pd.DataFrame(data, columns=headers)
    bios_filepath = 'bios.xlsx'
    bios_df.to_excel(bios_filepath, index=False)
    # build list of users to create pages
    list = {}
    for i,bio in bios_df.iterrows():
        item = {"item_name":bio["item_name"],"item_description":bio["item_description"],"item_year":bio["item_year"],"item_url":bio["item_url"]}
        category = {"cat_name":bio["item_name"],"items":[]}
        b = {"person_name":bio["person_name"],"person_eid":bio["person_eid"],"categories":{}}
        if bio["person_eid"] not in list.keys():
            list[bio["person_eid"]] = b
        if category["cat_name"] not in list[bio["person_eid"]]["categories"].keys():
            list[bio["person_eid"]]["categories"][category["cat_name"]] = category
        list[bio["person_eid"]]["categories"][category["cat_name"]]["items"].append( item )
    return list

def get_roster_from_gsheet():
    worksheet_name = "Roster"
    sheet = client.open_by_key(spreadsheet_key).worksheet(worksheet_name)
    data = sheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    filepath = 'roster.xlsx'
    df.to_excel(filepath, index=False)
    # build list of users keyed to person_eid
    list = {}
    for i,row in df.iterrows():
        item = {}
        for column_name in df.columns:
            item[column_name] = row[column_name]
        list[item["person_eid"]] = item
    return list


def write_index( biographies,roster ):
    filename = f'{destination_folder}index.qmd'
    with open(filename, 'w',encoding="utf-8") as file:
        file.write(f"""---
title: "Meet our team"
date: last-modified
format:
    html:
        toc: false
        style: ../assets/quarto_ssgvip.scss
---
                   
::: {{.roster-wrap}}

""")
        for eid in biographies.keys():
            file.write(f"""
::: {{.roster-person}}

<a href="./{eid}.qmd">

::: {{.roster-pic-frame}}
::: {{.roster-pic}}
![](../assets/{roster[eid]["person_headshot"]})
:::
:::

::: {{.roster-person-name}}
{roster[eid]["person_name"]}
:::

::: {{.roster-person-role}}
{roster[eid]["person_role"]}
:::

</a>

:::

""")
            
        file.write(f"""
:::

""")
        file.close()
    

def write_page( name, biographies, roster ):
    """ Write about page for individuals in list """
    filename = f'{destination_folder}{name}.qmd'
    with open(filename, 'w',encoding="utf-8") as file:
        file.write(f"""---
title: "{biographies[name]["person_name"]}"
date: last-modified
format:
    html:
        toc: false
        style: ../assets/quarto_ssgvip.scss
---
<a id="goback-btn" href="./index.html">
<i class="bi bi-arrow-left-circle">
View all Members
</i>
</a>

::: {{.profile-wrap}}

::: {{.profile-bio}}

::: {{.profile-pic-frame}}

::: {{.profile-pic}}

![](../assets/{roster[name]["person_headshot"]})

:::

:::

""")
        if "bio" in biographies[name]["categories"].keys():
            for item in biographies[name]["categories"]["bio"]["items"]:
                file.write(f"\n{item['item_description']}\n")

        if "education" in biographies[name]["categories"].keys():
            file.write("\n## Education\n\n")
            for item in biographies[name]["categories"]["education"]["items"]:
                file.write(f"* <span class='item'>{item['item_description']} <span class='date'>{item['item_year']}</span></span>\n")

        if "experience" in biographies[name]["categories"].keys():
            file.write("\n## Experience\n\n")
            for item in biographies[name]["categories"]["experience"]["items"]:
                file.write(f"* <span class='item'>{item['item_description']}")
                if "item_year" in item.keys() and (item["item_year"]!="" or item["item_year"] is not None):
                    file.write(f" <span class='date'>{item['item_year']}</span>")
                file.write("</span>\n")

        if "certification" in biographies[name]["categories"].keys():
            file.write("\n## Badges and Certificates\n\n")
            for item in biographies[name]["categories"]["certification"]["items"]:
                if "item_url" in item.keys() and (item["item_url"]!="" or item["item_url"] is not None):
                    file.write(f"* <span class='item'>[{item['item_description']}]({item['item_url']})</span>")
                else:
                    file.write(f"* <span class='item'>{item['item_description']}</span>")
                file.write("\n")

        file.write(f"""

:::
                   
:::

""")

    file.close()



@cli.command
@click.pass_context
def bios(ctx):
    biographies = get_biographies_from_gsheet()
    roster = get_roster_from_gsheet()
    for name in biographies.keys():
        write_page( name, biographies, roster )
    write_index( biographies, roster )


if __name__=="__main__":
    cli()

