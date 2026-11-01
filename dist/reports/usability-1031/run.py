"""Controlled MiroFish/OASIS customer interviews, using only local inference."""
import os
os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
import asyncio
import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = Path(__file__).parent
BACKEND = Path('D:/Claude/MiroFish-local/backend')
sys.path.insert(0, str(BACKEND))
from app.config import Config
from app.models.project import ProjectManager, ProjectStatus
from app.services.local_graph_store import LocalGraphStore
from app.services.oasis_profile_generator import OasisAgentProfile
from app.services.simulation_manager import SimulationManager, SimulationStatus

ROLES = [
 ('auto','首次跨州運車客戶',32,'女','從洛杉磯運車到紐約，第一次運車。想知道要準備哪些資料、報價如何確認以及如何聯絡。'),
 ('moving','家庭搬家客戶',40,'男','全家跨州搬遷，家具、紙箱和汽車一起安排，需要電梯預約與入住前倉儲。'),
 ('trust','謹慎查證的客戶',48,'女','會閱讀原文案例和價格，擔心過期資訊、找不到指南，以及把詢價誤認成正式預訂。'),
 ('english','English-speaking mover',29,'男','Uses English only. Needs a route checklist, accessible details, a copy of the inquiry and clear Gmail handoff. Respond in Traditional Chinese for the reviewer.'),
]

def save(name, data):
    (BASE/name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def prepare():
    pages=json.loads((BASE/'pages.json').read_text(encoding='utf8'))
    assert all(p['status']==200 for p in pages)
    source='\n\n'.join('PAGE '+p['path']+'\n'+p['text'] for p in pages)
    (BASE/'website-source.md').write_text(source,encoding='utf8')
    seed='Synthetic controlled interviews only. Text excerpts, not screenshots. No browsing, clicks or real customers. Missing from excerpts does not prove missing from the site. Quote a short exact phrase and page path. Evaluate discoverability, preparation detail, historical claims, Gmail draft versus sending, and actionable next steps. Do not invent prices, timing or observed behaviour.\n'
    seed+='\n'.join('【頁面 '+p['path']+'】\n'+p['text'][:(2600 if '/plan/' in p['path'] else 850)] for p in pages if p['path'] in ['/zh-hant/','/zh-hant/plan/','/zh-hant/guides/pricing/','/en/plan/'])
    (BASE/'pilot-seed.md').write_text(seed,encoding='utf8')
    project=ProjectManager.create_project('168 website controlled usability interviews 2026-10-31')
    project.simulation_requirement='Four manually defined moving scenarios, two guided interview rounds. Text-only hypotheses; no real-user prediction.'
    project.graph_id='one68_review_'+project.project_id
    project.ontology={'entity_types':[{'name':'Customer','description':'Synthetic moving customer','attributes':[]}], 'edge_types':[]}
    project.status=ProjectStatus.GRAPH_COMPLETED
    ProjectManager.save_extracted_text(project.project_id,source)
    ProjectManager.save_project(project)
    graph=LocalGraphStore(project.graph_id)
    graph.set_meta(project.name,project.simulation_requirement,project.ontology,datetime.now().isoformat())
    graph.add_episode(seed)
    profiles=[]
    for i,(key,name,age,gender,description) in enumerate(ROLES):
        node=graph.add_node(name,['Entity','Customer'],description,{'synthetic':True})
        p=OasisAgentProfile(user_id=i,user_name='mover_'+key,name=name,bio=description,
           persona='你是使用美國搬遷網站的'+name+'。'+description+'請依自身需求發言，不必支持品牌，不要迎合其他人。以繁體中文回答。',
           age=age,gender=gender,mbti='ISTJ',country='Taiwan',source_entity_uuid=node,source_entity_type='Customer')
        profiles.append(p.to_reddit_format())
    save('profiles.json',profiles)
    manager=SimulationManager()
    state=manager.create_simulation(project.project_id,project.graph_id,False,True)
    state.entities_count=state.profiles_count=4
    state.entity_types=['Customer']
    state.status=SimulationStatus.RUNNING
    manager._save_simulation_state(state)
    metadata={'project_id':project.project_id,'graph_id':project.graph_id,'simulation_id':state.simulation_id,
       'model':'espner-qwen25','endpoint':'http://127.0.0.1:11434/v1','mode':'controlled OASIS interviews; manually seeded profiles and graph; not automatic ontology/config generation',
       'source_root':'D:/Christina/168-unified-demo','base_commit':'9cae508', 'review':'uncommitted owner-review and planning changes','source_includes_uncommitted_changes':True,
       'roles':4,'rounds':2,'visual_input':False,'status':'running'}
    save('run.json',metadata)
    return seed,metadata,manager,state

async def main():
    seed,metadata,manager,state=prepare()
    print('Prepared MiroFish project and manual scenario profiles',flush=True)
    import oasis
    from oasis import ActionType, ManualAction
    from camel.models import ModelFactory
    from camel.types import ModelPlatformType
    model=ModelFactory.create(model_platform=ModelPlatformType.OPENAI,model_type='espner-qwen25',
        api_key='ollama',url='http://127.0.0.1:11434/v1',
        model_config_dict={'temperature':0.5,'max_tokens':240})
    agents=await oasis.generate_reddit_agent_graph(str(BASE/'profiles.json'),model=model,
        available_actions=[ActionType.CREATE_POST,ActionType.INTERVIEW])
    db=BASE/'oasis.db'
    if db.exists(): raise RuntimeError('Refusing to overwrite existing simulation database')
    env=oasis.make(agent_graph=agents,platform=oasis.DefaultPlatformType.REDDIT,database_path=str(db),semaphore=1)
    await env.reset()
    results=[]
    try:
      for round_num in [1,2]:
        peer=''
        if round_num==2:
          peer='\n第一輪其他角色的原始意見：\n'+'\n'.join(x['role']+'：'+x['response'] for x in results)
        for i,role in enumerate(ROLES):
          # Show each role the relevant routes, while preserving the complete seed file.
          relevant=seed
          prompt=relevant+peer+'\n你現在是'+role[1]+'。'+role[4]
          if round_num==1:
            prompt+='\n直接用繁體中文100字內回答三點：吸引繼續看的具體資料；最阻礙選購的一件事；下一步想確認什麼。引用一個頁面路徑與短原文。只依節錄，不推估真實顧客比例。不要分析作答要求，不要呼叫工具。'
          else:
            prompt+='\n直接用繁體中文100字內回答：對其他意見的同意或不同意之處；你自己的第一優先改進項目；給一個可驗證的頁面改法。不得聲稱看到任何新頁面或改版。不要分析作答要求，不要呼叫工具。'
          prompt+='\n請直接給顧客觀點的答案。'
          with (BASE/'prompts.jsonl').open('a',encoding='utf-8') as handle:
            handle.write(json.dumps({'round':round_num,'agent_id':i,'prompt':prompt},ensure_ascii=False)+'\n')
          print(f'Interview round={round_num} role={role[1]}',flush=True)
          before=0
          with sqlite3.connect(db) as conn:
            before=conn.execute('select coalesce(max(rowid),0) from trace').fetchone()[0]
          agent=agents.get_agent(i)
          await env.step({agent:ManualAction(action_type=ActionType.INTERVIEW,action_args={'prompt':prompt})})
          with sqlite3.connect(db) as conn:
            rows=conn.execute('select info from trace where rowid>? and user_id=? order by rowid desc',(before,i)).fetchall()
          response=None
          for (info,) in rows:
            payload=json.loads(info)
            if payload.get('response'):
              response=payload['response'];break
          if not response: raise RuntimeError(f'No recorded interview response for {i}')
          results.append({'round':round_num,'agent_id':i,'role':role[1],'response':response})
          save('interviews.json',results)
          await env.step({agent:ManualAction(action_type=ActionType.CREATE_POST,action_args={'content':response})})
          print(f'Recorded {len(results)}/8 interviews',flush=True)
      state.status=SimulationStatus.COMPLETED
      state.current_round=2
      state.reddit_status='completed'
      metadata['status']='completed'
      metadata['interviews']=len(results)
      save('run.json',metadata)
    except BaseException as e:
      state.status=SimulationStatus.FAILED
      state.error=str(e)
      metadata['status']='failed';metadata['error']=str(e)
      save('run.json',metadata)
      raise
    finally:
      manager._save_simulation_state(state)
      await env.close()

if __name__=='__main__':
    asyncio.run(main())
