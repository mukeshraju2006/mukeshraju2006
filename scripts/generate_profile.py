import os,json,urllib.request,base64
from collections import Counter
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C=json.load(open(os.path.join(R,"profile","config.json"),encoding="utf-8")); U=C["username"]; T=os.environ.get("GITHUB_TOKEN")
def g(p):
 h={"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","Authorization":"Bearer "+T}
 return json.load(urllib.request.urlopen(urllib.request.Request("https://api.github.com"+p,headers=h),timeout=30))
def pages(p):
 o=[];i=1
 while 1:
  x=g(p+("? " if "?" not in p else "&").replace("? ","?")+f"per_page=100&page={i}")
  if not x:return o
  o+=x
  if len(x)<100:return o
  i+=1
def read(n,p):
 try:
  x=g(f"/repos/{U}/{n}/contents/{p}")
  return base64.b64decode(x["content"]).decode("utf8","replace") if x.get("type")=="file" else ""
 except:return ""
def dom(r):
 s=(" ".join([r.get("name",""),r.get("description") or ""," ".join(r.get("topics") or []),r.get("language") or ""])).lower()
 if any(x in s for x in ["machine learning"," ai"," ml","neural","model","data"]):return "AI / ML"
 if any(x in s for x in ["system","linux","agent","orchestration","infra","cli","sdk"]):return "Systems"
 if any(x in s for x in ["api","backend","server","database"]):return "Backend"
 if any(x in s for x in ["web","next.js","react","website","frontend"]):return "Web"
 return "Software"
rs=[x for x in pages(f"/users/{U}/repos?type=public&sort=updated") if not x.get("archived") and not x.get("disabled")]
by={x["name"]:x for x in rs}; lb=Counter(); lr=Counter(); tech=Counter()
rules={"Python":["python","requirements.txt","pyproject.toml"],"TypeScript":["typescript","package.json",".ts"],"JavaScript":["javascript","package.json",".js"],"Java":["java","pom.xml","build.gradle"],"PostgreSQL / SQL":["postgresql","prisma","alembic",".sql"],"FastAPI":["fastapi"],"Next.js":["next"],"React":["react"],"Prisma":["prisma"],"Docker":["dockerfile","docker-compose"],"GitHub Actions":[".github/workflows"]}
for r in rs:
 n=r["name"]
 try:
  for k,v in g(f"/repos/{U}/{n}/languages").items():lb[k]+=v;lr[k]+=1
 except:pass
 try:f=" ".join(x["name"].lower() for x in g(f"/repos/{U}/{n}/contents"))+" "+read(n,"README.md").lower()+" "+read(n,"package.json").lower()+" "+read(n,"requirements.txt").lower()
 except:f=""
 for k,v in rules.items():
  if any(p in f for p in v) or k==r.get("language"):tech[k]+=1
con={}; days=[]; merged_prs=[]
try:
 merged_prs=g(f"/search/issues?q=is%3Apr+is%3Amerged+author%3A{U}&sort=updated&order=desc&per_page=20").get("items",[])
except: merged_prs=[]
try:
 q='query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}'
 b=json.dumps({"query":q,"variables":{"l":U}}).encode(); req=urllib.request.Request("https://api.github.com/graphql",data=b,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"})
 con=json.load(urllib.request.urlopen(req)).get("data",{}).get("user",{}).get("contributionsCollection",{})
 days=[d for w in con.get("contributionCalendar",{}).get("weeks",[]) for d in w["contributionDays"]]
except:pass
days=sorted(days,key=lambda x:x["date"])[-91:]; total=sum(x["contributionCount"] for x in days); active=sum(x["contributionCount"]>0 for x in days)
try: starred=pages(f"/users/{U}/starred")
except:starred=[]
releases=[]
for r in rs:
 try:releases += [(x,r["name"]) for x in g(f"/repos/{U}/{r['name']}/releases?per_page=20")]
 except:pass
releases.sort(key=lambda x:x[0].get("published_at") or "",reverse=True)
try:
 q='query($l:String!){user(login:$l){pinnedItems(first:6,types:REPOSITORY){nodes{... on Repository{name description url stargazerCount forkCount primaryLanguage{name}}}}}}'
 b=json.dumps({"query":q,"variables":{"l":U}}).encode();req=urllib.request.Request("https://api.github.com/graphql",data=b,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"})
 pinned=json.load(urllib.request.urlopen(req)).get("data",{}).get("user",{}).get("pinnedItems",{}).get("nodes",[])
except:pinned=[]
L=["# Mukesh Raju Podilapu","","Integrated M.Tech CSE student @ VIT-AP University","","**AI/ML engineering · systems · open source · first-principles engineering**","","I like understanding what happens underneath the abstraction, then building enough of it to find out.","","## ENGINEERING SNAPSHOT","","| Signal | Current footprint |","|---|---|",f"| Public repositories | **{len(rs)}** |",f"| Stars received | **{sum(x.get('stargazers_count',0) for x in rs)}** |",f"| Forks received | **{sum(x.get('forks_count',0) for x in rs)}** |",f"| Contributions in last 91 days | **{total}** across **{active}** active days |",f"| Releases published | **{len(releases)}** |",f"| Detected languages | **{len(lb)}** |","","## CONTRIBUTION PULSE","","Legend: · none   ▪ 1–2   ■ 3–5   █ 6+","","<pre>",matrix,"</pre>","","## TECHNOLOGY FOOTPRINT","","| Technology | Repositories | Footprint |","|---|---:|---|"]
m=max(tech.values()) if tech else 1
for k,v in tech.most_common():L.append(f"| {k} | {v} | {('█'*round(v/m*12)).ljust(12,'░')} |")
L+=["","## LANGUAGE FOOTPRINT","","| Language | Repositories | Byte share |","|---|---:|---:|"]
z=sum(lb.values()) or 1
for k,v in lb.most_common():L.append(f"| {k} | {lr[k]} | {v/z:.1%} |")
L+=["","## FEATURED BUILDS","","| Project | Domain | Language | Stars |","|---|---|---|---:|"]
for n in C["featured_repositories"]:
 if n in by:
  r=by[n];L.append(f"| [{n}](https://github.com/{U}/{n}) | {dom(r)} | {r.get('language') or '—'} | {r.get('stargazers_count',0)} |")
L+=["","## REPOSITORY PORTFOLIO","","| Repository | Domain | Language | Updated |","|---|---|---|---|"]
for r in rs:L.append(f"| [{r['name']}](https://github.com/{U}/{r['name']}) | {dom(r)} | {r.get('language') or '—'} | {(r.get('updated_at') or '')[:10]} |")
if pinned:
 L+=["","## PINNED ON GITHUB","","| Repository | Description | Stars | Forks |","|---|---|---:|---:|"]
 for r in pinned:L.append(f"| [{r['name']}]({r['url']}) | {(r.get('description') or '—').replace('|','\\|')} | {r.get('stargazerCount',0)} | {r.get('forkCount',0)} |")
L+=["","## STARRED / RESEARCH RADAR",""]
my_starred=[r for r in starred if r.get("owner",{}).get("login")==U or r.get("full_name","").startswith(U+"/")]
for r in my_starred[:20]:
 f=r.get("full_name","");L.append(f"- [{f}](https://github.com/{f}) · {r.get('language') or '—'} · ★ {r.get('stargazers_count',0)}")
if not my_starred:L.append("_None of my repositories are currently starred._")
L+=["","## RELEASE HISTORY",""]
for x,n in releases[:20]:L.append(f"- **{(x.get('published_at') or x.get('created_at') or '')[:10]}** · [{n}](https://github.com/{U}/{n}) · {x.get('tag_name') or x.get('name') or 'release'}")
if not releases:L.append("_No published releases detected across public repositories._")
L+=["","## APPLICATIONS",""]
for a in C.get("applications",[]):L.append(f"- **[{a['name']}]({a['url']})** · {a['status']} · source: [{a['repository']}](https://github.com/{U}/{a['repository']})")
L+=["","## RECENT BUILD ACTIVITY",""]
for r in sorted(rs,key=lambda x:x.get("pushed_at",""),reverse=True)[:10]:L.append(f"- {(r.get('pushed_at') or '')[:10]} · [{r['name']}](https://github.com/{U}/{r['name']}) · {dom(r)}")
L+=["","<details>","<summary><b>Engineering principles</b></summary>","","- Prefer understanding the system over memorising the abstraction.","- Build small enough to reason about.","- Measure before guessing.","- Treat failures as evidence.","- Learn by implementing, debugging, and reading real systems.","","</details>","","<details>","<summary><b>Current direction</b></summary",""]+[f"- {x}" for x in C["manual_focus"]]+["","</details>","","---","","<sub>Generated from GitHub repository, contribution, language, release, pinned, and starred data. Refreshed automatically by GitHub Actions.</sub>"]
open(os.path.join(R,"README.md"),"w",encoding="utf8").write("\n".join(L)+"\n")
