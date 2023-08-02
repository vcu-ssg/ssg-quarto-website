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
#    bios_filepath = 'bios.xlsx'
#    bios_df.to_excel(bios_filepath, index=False)
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
#    filepath = 'roster.xlsx'
#    df.to_excel(filepath, index=False)
    # build list of users keyed to person_eid
    list = {}
    for i,row in df.iterrows():
        item = {}
        for column_name in df.columns:
            item[column_name] = row[column_name]
        list[item["person_eid"]] = item
    return list

def get_projects_from_gsheet():
    worksheet_name = "Projects"
    sheet = client.open_by_key(spreadsheet_key).worksheet(worksheet_name)
    data = sheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
#    filepath = 'roster.xlsx'
#    df.to_excel(filepath, index=False)
    # build list of users keyed to person_eid
    list = {}
    for i,row in df.iterrows():
        item = {}
        for column_name in df.columns:
            item[column_name] = row[column_name]
        list[item["project_id"]] = item
    return list

def get_projects_roster_from_gsheet():
    worksheet_name = "Projects-Roster"
    sheet = client.open_by_key(spreadsheet_key).worksheet(worksheet_name)
    data = sheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
#    filepath = 'roster.xlsx'
#    df.to_excel(filepath, index=False)
    # build list of users keyed to person_eid
    list = {}
    for i,row in df.iterrows():
        item = {}
        for column_name in df.columns:
            item[column_name] = row[column_name]
        if not item["person_eid"] in list.keys():
            list[item["person_eid"]] = []
        list[item["person_eid"]].append( item )
    return list



def write_index( biographies,roster ):
    filename = f'{destination_folder}index.qmd'
    with open(filename, 'w',encoding="utf-8") as file:
        file.write(f"""---
pagetitle: "SSG at VCU | Meet our team"
date: last-modified
format:
    html:
        toc: false
        include-in-header:
            text: |
                <script>
                function filterFunction( idToFilter ) {{
                    // Declare variables
                    var list, li, i;
                    
                    list = document.getElementById("member-list");
                    li = list.getElementsByTagName("li");

                    // Loop through all list items, toggling appropriate values on/off
                    for (i = 0; i < li.length; i++) {{
                        var toggle;
                        toggle = "none";
                        if (li[i].id==idToFilter || idToFilter==''){{
                            toggle = "block";
                        }}
                    //    td = tr[i].getElementsByTagName("td")[0];
                    //    if (td) {{
                    //    txtValue = td.textContent || td.innerText;
                    //    if (txtValue.toUpperCase().indexOf(filter) > -1) {{
                    //        //tr[i].style.display = "";
                    //        toggle = "";
                    //    }} else {{
                    //        //tr[i].style.display = "none";
                    //    }}
                    //    }}
                    
                        li[i].style.display = toggle;
                    }}
                }}
                   
                function toggleButtons( name ) {{
                   var buttons,i;
                   buttons = document.getElementsByTagName("button");
                   for (i=0;i<buttons.length; i++){{
                     if (buttons[i].id==name) {{
                       buttons[i].className="small-btn active";
                     }} else {{
                       buttons[i].className="small-btn";
                     }}
                   }}
                }}
                  
                function lightMeUp( name,filter ) {{
                   // toggle the button using name
                   toggleButtons( name );

                   // filter the list items
                   filterFunction( filter );
                }}
                </script>

---
                   
# Meet our team {{.section-header}}
                   
## Complete roster {{.bigmargin-bottom}}

::: {{.members-category-desc}}

::: {{.desc}}
                   
The SSG team is comprised of VCU students from different majors
working cross-functionally, with drive.
                   
:::

::: {{.filter-control}}

<button class="small-btn active" id="allMembersButton" onClick="lightMeUp('allMembersButton','')">All Members</button>
<button class="small-btn" id="currentStudentButton" onClick="lightMeUp('currentStudentButton','Current Student')">Current students</button>
<button class="small-btn" id="facultyMentorButton" onClick="lightMeUp('facultyMentorbutton','Faculty Mentor')">Faculty Mentors</button>
<button class="small-btn" id="ssgAlumniButton" onClick="lightMeUp('ssgAlumniButton','SSG Alumni')">SSG Alumni</button>

:::

:::


::: {{.members-card-wrap}}

<ul id="member-list">
                   
""")
        for eid in roster.keys():

            person_headshot = "hero-image.png"
            if roster[eid]["person_headshot"]!="":
                person_headshot = roster[eid]["person_headshot"]

            person_profile = "index.html"
            if eid in biographies.keys():
                person_profile = f"{eid}.qmd"
            file.write(f"""

<li id="{roster[eid]['person_role']}">
<a class="members-card" href="./{person_profile}">
<div class="card-shadow"></div>
<div class="info-wrap">
<div class="members-pic">
![](../assets/{person_headshot})
</div>
<div class="members-profile">
<div class="name">
{roster[eid]["person_name"]}
</div>
<div class="major">
{roster[eid]["person_role"]}
</div>
<div class="major">
{roster[eid]["person_major"]}
</div>
</div>
</div>
</a>
</li>


""")
            
        file.write(f"""
</ul>

:::
                   
""")
        file.close()
    

def write_page( name, biographies, roster, projects, joins ):
    """ Write about page for individuals in list """
    filename = f'{destination_folder}{name}.qmd'
    with open(filename, 'w',encoding="utf-8") as file:
        file.write(f"""---
pagetitle: "SSG at VCU | {biographies[name]["person_name"]}"
date: last-modified
format:
    html:
        toc: false
#        style: ../assets/quarto_ssgvip.scss
---
<a id="goback-btn" href="./index.html">
<i class="bi bi-arrow-left-circle">
View all Members
</i>
</a>

<div class='profile-wrap'>

<div class='profile-bio'>

<div class='profile-pic-frame'>
<div class='profile-pic'>
<img src='../assets/{roster[name]["person_headshot"]}' class='img-fluid'>
</div>
</div>

<div class='profile-name-links'>
<h1>{biographies[name]['person_name']}</h1>
<div class='profile-links'><p>
""")

        if roster[name]["person_linkedin"]!="":
            file.write(f"<a href='{roster[name]['person_linkedin']}'><i class='bi bi-linkedin'></i>LinkedIn</a>")

        if roster[name]["person_portfolio"]!="":
            file.write(f"<a href='{roster[name]['person_portfolio']}'><i class='bi bi-link-45deg'></i>Portfolio</a>")

        if roster[name]["person_github_id"]!="":
            file.write(f"<a href='https://github.com/" + roster[name]['person_github_id'] + "'><i class='bi bi-github'></i>GitHub</a>")

        if roster[name]["person_orcid"]!="":
            file.write(f"<a href='{roster[name]['person_orcid']}'><svg viewBox='0 0 512 512'><path d='M294.75 188.19h-45.92V342h47.47c67.62 0 83.12-51.34 83.12-76.91 0-41.64-26.54-76.9-84.67-76.9zM256 8C119 8 8 119 8 256s111 248 248 248 248-111 248-248S393 8 256 8zm-80.79 360.76h-29.84v-207.5h29.84zm-14.92-231.14a19.57 19.57 0 1 1 19.57-19.57 19.64 19.64 0 0 1-19.57 19.57zM300 369h-81V161.26h80.6c76.73 0 110.44 54.83 110.44 103.85C410 318.39 368.38 369 300 369z' /></svg>ORCID</a>")

        file.write(f"""
</p>
</div>
</div>
  
<div class='member-status'>
<div class='status-wrap'>
<div class='status'>{roster[name]["person_role"]}</div>
""")
        for project in joins[name]:
            if project['project_id'] in projects.keys():
                file.write(f"<a href='{projects[project['project_id']]['project_url']}'><div class='project'>{ projects[project['project_id']]['project_name'] }</div></a>\n")
        file.write(f"""
</div>
</div>

""")
        if "bio" in biographies[name]["categories"].keys():
            for item in biographies[name]["categories"]["bio"]["items"]:
                file.write(f"\n<p>\n{item['item_description']}\n</p>\n\n")
        file.write(f"""

</div>

""")

        if "education" in biographies[name]["categories"].keys():
            file.write("\n## Education\n\n")
            for item in biographies[name]["categories"]["education"]["items"]:
                if "item_url" in item.keys() and item["item_url"]!='':
                    file.write(f"* <span class='item'>[{item['item_description']}]({item['item_url']})")
                else:
                    file.write(f"* <span class='item'>{item['item_description']}")
                file.write("\n")
                if "item_year" in item.keys() and (item["item_year"]!="" or item["item_year"] is not None):
                    file.write(f" <span class='date'>{item['item_year']}</span>")
                file.write("</span>\n")


        if "experience" in biographies[name]["categories"].keys():
            file.write("\n## Experience\n\n")
            for item in biographies[name]["categories"]["experience"]["items"]:
                if "item_url" in item.keys() and item["item_url"]!='':
                    file.write(f"* <span class='item'>[{item['item_description']}]({item['item_url']})")
                else:
                    file.write(f"* <span class='item'>{item['item_description']}")
                file.write("\n")

                if "item_year" in item.keys() and (item["item_year"]!="" or item["item_year"] is not None):
                    file.write(f" <span class='date'>{item['item_year']}</span>")
                file.write("</span>\n")

        if "certification" in biographies[name]["categories"].keys():
            file.write("\n## Badges and Certificates\n\n")
            for item in biographies[name]["categories"]["certification"]["items"]:
                if "item_url" in item.keys() and item["item_url"]!='':
                    file.write(f"* <span class='item'>[{item['item_description']}]({item['item_url']})</span>")
                else:
                    file.write(f"* <span class='item'>{item['item_description']}</span>")
                file.write("\n")

        if "skills" in biographies[name]["categories"].keys():
            file.write("\n## Skills\n\n")
            for item in biographies[name]["categories"]["skills"]["items"]:
                if "item_url" in item.keys() and item["item_url"]!='':
                    file.write(f"* <span class='item'>[{item['item_description']}]({item['item_url']})</span>")
                else:
                    file.write(f"* <span class='item'>{item['item_description']}</span>")
                file.write("\n")


        file.write(f"""

</div>
             

""")

    file.close()



@cli.command
@click.pass_context
def bios(ctx):
    biographies = get_biographies_from_gsheet()
    roster = get_roster_from_gsheet()
    projects = get_projects_from_gsheet()
    joins = get_projects_roster_from_gsheet()
    for name in biographies.keys():
        write_page( name, biographies, roster, projects, joins )
    write_index( biographies, roster )


if __name__=="__main__":
    cli()

