import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
results=[]
with sync_playwright() as p:
 b=p.chromium.launch()
 for site in ['agency-landing','saas-showcase']:
  for width in [375,1440]:
   page=b.new_page(viewport={'width':width,'height':900});page.goto((ROOT/site/'index.html').as_uri());page.evaluate('document.fonts.ready')
   page.add_script_tag(path=str(ROOT/'node_modules/axe-core/axe.min.js'))
   result=page.evaluate('''async () => {const result=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return {violations:result.violations,incomplete:result.incomplete.map(item=>({id:item.id,nodes:item.nodes.length})),passes:result.passes.length}}''')
   results.append({'site':site,'width':width,**result})
   page.close()
 b.close()
(ROOT/'test-results/accessibility-report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
for r in results:
 print(r['site'],r['width'],'violations',len(r['violations']),'manual-review',r['incomplete'])
 for v in r['violations']: print(v['id'],[(n['target'],n.get('failureSummary')) for n in v['nodes']])
assert not any(r['violations'] for r in results)
