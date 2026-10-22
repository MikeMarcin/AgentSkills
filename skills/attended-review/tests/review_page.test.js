/* Deterministic execution of the real page with a minimal DOM/media model.
   This checks offline/state behavior; it does not qualify a native file browser. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const http=require('node:http');
const html=fs.readFileSync(path.join(__dirname,'../assets/review.html'),'utf8');
const script=html.split('<script>')[1].split('</script>')[0];
const candidate=(id,extra={})=>({id,title:id,revision:'fixture-1',fingerprint:`fp-${id}`,phase:'ready',protected:true,criteria:['Judge exact purpose'],decision:null,...extra});
const snapshot={session:'offline-fixture',sequence:1,checkout:'/fixture',candidates:[candidate('brief'),candidate('A',{question_type:'audio',comparison_group:'death',audio:{url:'data:audio/wav;base64,fixture',purpose:'Death',scope:'Isolation',variant:'Death A'}}),candidate('B',{question_type:'audio',comparison_group:'death',audio:{url:'data:audio/wav;base64,fixture-b',purpose:'Death',scope:'Isolation',variant:'Death B'}})]};
const storage=new Map();let rejectStorage=false;
function page(seed=snapshot,settings={}){
 const nodes=new Map(),requests=[],backend=structuredClone(seed);let document;
 class Element{
  constructor(tag,id){this.tag=tag;this.id=id;this.children=[];this.classList={toggle(){}};this.style={};this.dataset={};this.attrs={};this.value='';this.textContent='';this.paused=true;this.currentTime=0;this.hidden=false;this.checked=false;}
  append(...items){this.children.push(...items);}
  replaceChildren(...items){this.children=[...items];}
  setAttribute(k,v){this.attrs[k]=v;}
  removeAttribute(k){delete this.attrs[k];}
  focus(options){document.activeElement=this;this.focusOptions=options;}
  scrollIntoView(options){this.scrollOptions=options;this.scrollCount=(this.scrollCount||0)+1;}
  select(){}
  play(){this.paused=false;this.onplay?.();return Promise.resolve();}
  pause(){this.paused=true;}
  click(){if(!this.disabled)return this.onclick?.();}
  querySelectorAll(selector){const all=this.children.flatMap(c=>c instanceof Element?[c,...c.querySelectorAll('*')]:[]);if(selector==='*')return all;if(selector==='audio,video')return all.filter(c=>['audio','video'].includes(c.tag));if(selector==='input:checked')return all.filter(c=>c.tag==='input'&&c.checked);if(selector==='[aria-current="true"]')return all.filter(c=>c.attrs['aria-current']==='true');return all.filter(c=>c.tag===selector);}
  querySelector(selector){return this.querySelectorAll(selector)[0];}
 }
 const get=id=>{if(!nodes.has(id))nodes.set(id,new Element('div',id));return nodes.get(id);};
 document={activeElement:null,documentElement:new Element('html'),getElementById:get,createElement:tag=>new Element(tag),createTextNode:text=>text,querySelector:get,addEventListener(){}};
 // A live host is the real loopback server: its intake, not this fixture,
 // decides whether a note is saved.
 const live=settings.host?.link?linked(settings.host,requests):settings.host?async(url,options)=>{requests.push({url,body:options.body?JSON.parse(options.body):null});return globalThis.fetch(settings.host.origin+url,options);}:null;
 const fetch=live||async function(url,options){
  const body=options.body?JSON.parse(options.body):null;requests.push({url,body});
  if(url==='/api/decisions'){
   if(settings.failFeedback&&body.feedback?.length)return {ok:false,json:async()=>({error:'fixture save unavailable'})};
   for(const f of body.feedback||[])backend.candidates.find(c=>c.id===f.candidate).feedback={...f};
   for(const d of body.decisions||[])backend.candidates.find(c=>c.id===d.candidate).decision=d.outcome==='withdrawn'?null:{...d};
   backend.sequence++;
  }
  let response=backend;
  if(url==='/api/hand-back'){
   backend.handed_back=true;backend.sequence++;
   response={decided:backend.candidates.filter(c=>c.decision).map(c=>c.id),pending:backend.candidates.filter(c=>!c.decision).map(c=>c.id),feedback_pending:backend.candidates.filter(c=>!c.decision&&c.feedback).map(c=>c.id)};
  }
  // The fixture reads status the way the host does: sorted, a poll at the
  // current sequence is told only that, and material can be left out.
  const [route,search]=url.split('?'),query=new URLSearchParams(search||'');
  if(route==='/api/status'){
   if(query.has('after')&&Number(query.get('after'))===backend.sequence)response={session:backend.session,sequence:backend.sequence,unchanged:true};
   else response={...backend,candidates:[...backend.candidates].sort((a,b)=>(a.phase!=='ready')-(b.phase!=='ready')||Boolean(a.decision)-Boolean(b.decision)||(a.id===b.id?0:a.id<b.id?-1:1)).map(c=>{if(query.get('material')!=='omit')return c;const omitted=['media','audio'].filter(k=>k in c),v={...c};for(const k of omitted)delete v[k];return omitted.length?{...v,material_omitted:omitted}:v;})};
  }
  return {ok:true,json:async()=>structuredClone(response)};
 };
 // With a live host the note's save debounce runs on real timers.
 const timers=settings.host?{setTimeout,clearTimeout}:{setTimeout:()=>1,clearTimeout(){}};
 const context={console,document,fetch,polls:[],location:{hash:settings.host?`#token=${settings.host.token}`:'',protocol:settings.live?(settings.protocol||'http:'):'file:',pathname:'/fixture.html'},history:{replaceState(){}},localStorage:settings.storageThrows?{getItem(){throw Error('storage denied');},setItem(){throw Error('storage denied');},removeItem(){throw Error('storage denied');}}:{getItem:k=>storage.get(k),setItem(k,v){if(rejectStorage)throw Error('storage full');storage.set(k,v);},removeItem:k=>storage.delete(k)},matchMedia:()=>({matches:settings.wide!==false,addEventListener(){}}),...timers,setInterval(callback){context.polls.push(callback);},URL,URLSearchParams,Blob,window:{addEventListener(){}},navigator:{},crypto:{randomUUID:()=>`id-${Math.random()}`},getSelection:()=>({removeAllRanges(){},addRange(){}})};
 vm.createContext(context);vm.runInContext(script.replace('/*SESSION_DATA*/null',settings.live?'null':JSON.stringify(seed)).replace('\nboot();','\nglobalThis.ready=boot();'),context);
 const run=code=>vm.runInContext(code,context);
 return {run,get,context,requests,settings,backend,ready:context.ready};
}
// The real host behind a slow shared link, reached the way the browser reaches
// it: straight to loopback, or through Serve's tailnet name, which forwards the
// browser's Host and Origin to the separate review listener. Origin goes only on
// POST, as a browser sends it same-origin. Each reply arrives after its size
// over the link's rate, so a page that re-reads megabytes is slow to answer.
function linked(host,requests){
 return (url,options)=>new Promise((resolve,reject)=>{
  const target=new URL(host.origin+url),body=options.body||null,started=Date.now();
  const headers={...options.headers,...(host.authority?{Host:host.authority}:{})};
  if(options.method==='POST')headers.Origin=host.browserOrigin||host.origin;
  const out=http.request(target,{method:options.method,headers},response=>{
   const chunks=[];response.on('data',c=>chunks.push(c));
   response.on('end',()=>{
    const text=Buffer.concat(chunks).toString('utf8'),entry={url,method:options.method,body:body?JSON.parse(body):null,bytes:text.length,status:response.statusCode,started};
    requests.push(entry);
    setTimeout(()=>{entry.finished=Date.now();resolve({ok:response.statusCode<300,status:response.statusCode,json:async()=>JSON.parse(text)});},text.length/host.link*1000);
   });
  });
  out.on('error',reject);out.end(body);
 });
}
// Accept, Reject and Next on Accept/Reject questions whose images make the
// session megabytes long. Answering must not wait on reading every image again,
// a poll is never joined by a second while it is slow, and the question still
// shows its images afterwards.
async function liveAnswers(origin,token,prefix,authority,browserOrigin){
 const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
 const link=3000000,ids=[1,2,3].map(n=>`${prefix}-${n}`);
 storage.clear();const p=page(null,{live:true,protocol:authority?'https:':'http:',host:{origin,token,authority,browserOrigin,link}});await p.ready;
 const full=p.requests.find(r=>r.url==='/api/status');assert.ok(full&&full.status===200,'the page loaded its session');
 const fullDelay=full.bytes/link*1000;assert.ok(full.bytes>4000000,`fixture is megabytes long (${full.bytes})`);
 const told=()=>`${p.get('answer-notice').textContent} ${p.get('navigation-status').textContent}`;
 const usable=()=>{for(const id of ['accept','reject'])assert.equal(p.get(id).disabled,false,`${id} is usable: ${told()}`);
  assert.equal(p.get('next').disabled,!p.run('nextQuestion()'),`next is usable while a question is left: ${told()}`);};
 // An unchanged session costs a poll a few bytes, and a slow poll is not joined.
 const before=p.requests.length;const first=p.context.polls[0](),second=p.context.polls[0]();await Promise.all([first,second]);
 const polled=p.requests.slice(before);assert.equal(polled.length,1,'one poll in flight at a time');
 assert.ok(polled[0].bytes<1000,`an unchanged poll is short (${polled[0].bytes} bytes)`);
 const act=async(id,expect)=>{
  const from=p.requests.length,started=Date.now();await p.get(id).click();const elapsed=Date.now()-started;
  const moved=p.requests.slice(from).reduce((n,r)=>n+r.bytes,0);
  assert.ok(moved<full.bytes/4,`${id} read ${moved} bytes; the session is ${full.bytes}`);
  assert.ok(elapsed<fullDelay,`${id} took ${elapsed}ms; one full read takes ${Math.round(fullDelay)}ms`);
  if(expect)assert.equal(p.run('candidate().decision?.outcome'),expect,told());
  usable();
 };
 await p.run(`select(${JSON.stringify(ids[0])})`);usable();
 await act('accept','accept');assert.equal(p.get('accept').attrs['aria-pressed'],'true');assert.match(p.get('answer-notice').textContent,/Answer saved/);
 await act('next');assert.equal(p.run('current'),ids[1]);
 await act('reject','reject');assert.equal(p.get('reject').attrs['aria-pressed'],'true');
 await act('next');assert.equal(p.run('current'),ids[2]);
 await act('accept','accept');await act('reject','reject');
 // The answered question keeps the images it was answered on.
 assert.equal(p.get('media').querySelectorAll('img').length,1);assert.ok(p.run('candidate().media[0].url.length')>500000);
 await p.run(`select(${JSON.stringify(ids[0])})`);assert.equal(p.run('candidate().media.length'),1);
 // A later poll sees the answers and still leaves the images where they are.
 const after=p.requests.length;await p.context.polls[0]();assert.ok(p.requests.slice(after).every(r=>r.bytes<full.bytes/4));
 assert.equal(p.run(`state.candidates.filter(c=>${JSON.stringify(ids)}.includes(c.id)).map(c=>c.decision?.outcome).join()`),'accept,reject,reject');
 await wait(0);
 console.log(`PASS: Accept, Reject and Next answer promptly ${authority?'through the tailnet review listener':'on loopback'}; polls are short and never overlap`);
}
// A note typed around an answer reaches the real host with that answer, even
// when the reviewer answers first, types, and then changes Accept to Reject.
async function liveNotes(origin,token){
 const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
 const debounce=()=>wait(800);
 const type=(p,text)=>{p.get('note').value=text;p.get('note').oninput();};
 const open=async id=>{storage.clear();const p=page(null,{live:true,host:{origin,token}});await p.ready;await p.run(`select(${JSON.stringify(id)})`);return p;};
 const answer=p=>p.run('JSON.stringify(candidate().decision)');
 const told=p=>`${p.get('feedback-status').textContent} ${p.get('answer-notice').textContent}`;
 const settled=(p,outcome,note)=>{
  const d=JSON.parse(answer(p));assert.equal(d?.outcome,outcome,told(p));assert.equal(d.note,note,told(p));
  assert.equal(p.run('candidate().feedback.note'),note);
  assert.doesNotMatch(p.get('feedback-status').textContent,/Save failed/);
  assert.doesNotMatch(p.get('answer-notice').textContent,/not confirmed|Save or export/);
 };
 let p=await open('typed');type(p,'Limit the edit to the selected lines');await debounce();
 await p.get('reject').click();settled(p,'reject','Limit the edit to the selected lines');
 p=await open('quick');type(p,'Rejected before the save timer ran');
 await p.get('reject').click();settled(p,'reject','Rejected before the save timer ran');
 p=await open('switched');await p.get('accept').click();settled(p,'accept','');
 type(p,'On reflection, only the selected lines');await debounce();
 assert.equal(JSON.parse(answer(p)).note,'On reflection, only the selected lines',told(p));
 await p.get('reject').click();settled(p,'reject','On reflection, only the selected lines');
 p=await open('revised');type(p,'First thought');await p.get('accept').click();settled(p,'accept','First thought');
 type(p,'Second thought');await p.get('reject').click();settled(p,'reject','Second thought');
 p=await open('after');await p.get('reject').click();settled(p,'reject','');
 type(p,'Written after rejecting');await debounce();settled(p,'reject','Written after rejecting');
 // The same reviewer reloading the page keeps editing the saved note.
 p=await open('after');assert.equal(p.get('note').value,'Written after rejecting');
 type(p,'Written after rejecting, then revised');await debounce();await p.get('accept').click();
 settled(p,'accept','Written after rejecting, then revised');
 console.log('PASS: live host keeps the note typed before, between and after Accept and Reject');
}
(async()=>{
 if(process.argv[2]==='--host'){await liveNotes(process.argv[3],process.argv[4]);return;}
 if(process.argv[2]==='--answers'){await liveAnswers(...process.argv.slice(3));return;}
 // Next follows original queue order even when the active question was answered.
 // Both viewport widths return focus and scroll to the question's beginning.
 for(const wide of [true,false]){
  storage.clear();const navigation=page(snapshot,{wide});
  await navigation.run("select('A')");await navigation.get('accept').click();
  assert.equal(navigation.run('current'),'A');
  await navigation.get('next').click();assert.equal(navigation.run('current'),'B');
  assert.equal(navigation.context.document.activeElement,navigation.get('title'));
  assert.equal(navigation.get('title').focusOptions.preventScroll,true);
  assert.equal(navigation.get('title').scrollOptions.block,'start');
  if(!wide)assert.equal(navigation.get('queue').open,false);
  navigation.get('note').value='Pending feedback before moving on';navigation.run('edit()');
  await navigation.get('next').click();assert.equal(navigation.run('current'),'brief');
  assert.equal(navigation.run('state.candidates.filter(decision).length'),1);
  await navigation.run("select('B')");assert.equal(navigation.get('note').value,'Pending feedback before moving on');
  await navigation.get('accept').click();await navigation.get('next').click();await navigation.get('accept').click();
  assert.equal(navigation.get('next').disabled,true);assert.match(navigation.get('navigation-status').textContent,/Every question is answered/);
  await navigation.get('next').click();assert.equal(navigation.run('current'),'brief');
 }
 storage.clear();const one=page({...snapshot,candidates:[candidate('only')]});
 assert.equal(one.get('next').disabled,true);assert.match(one.get('navigation-status').textContent,/leave this question pending/);
 // The public host moves an answered question behind every ready unanswered
 // item. Navigation still follows its stable place, including after reload.
 storage.clear();const ordered={...snapshot,candidates:[candidate('brief'),candidate('clip-A'),candidate('clip-B')]};
 const reordered=page(ordered,{live:true});await reordered.ready;
 await reordered.run("select('clip-A')");await reordered.get('accept').click();
 assert.equal(reordered.run('state.candidates.map(c=>c.id).join()'),'brief,clip-B,clip-A');
 await reordered.get('next').click();assert.equal(reordered.run('current'),'clip-B');
 const reload=page(JSON.parse(reordered.run('JSON.stringify(state)')),{live:true});await reload.ready;
 await reload.run("select('clip-A')");await reload.get('next').click();assert.equal(reload.run('current'),'clip-B');
 // Both handback buttons run one handler. A failed draft on a previous question
 // blocks handback; retry saves it before the public handback request.
 for(const entry of ['finish','finish-answer']){
  storage.clear();const live=page(snapshot,{live:true,failFeedback:true});await live.ready;
  assert.equal(live.get('finish').onclick,live.get('finish-answer').onclick);
  await live.run("select('A')");live.get('note').value='Keep this unanswered feedback';live.run('edit()');
  await live.get('next').click();assert.equal(live.run('current'),'B');
  const clip=live.get('media').querySelector('audio');await clip.play();
  await live.get(entry).click();assert.equal(clip.paused,true);
  assert.equal(live.requests.some(r=>r.url==='/api/hand-back'),false);
  assert.match(live.get('answer-notice').textContent,/Handback stopped because feedback is unsaved/);
  assert.equal(live.get('fallback').open,true);live.get('export').click();
  assert.equal(JSON.parse(live.get('transfer').value).feedback[0].note,'Keep this unanswered feedback');
  assert.equal(live.get(entry).disabled,false);
  live.settings.failFeedback=false;await live.get(entry).click();
  assert.equal(live.requests.filter(r=>r.url==='/api/hand-back').length,1);
  assert.equal(live.run('state.candidates.filter(decision).length'),0);
  assert.equal(live.run("state.candidates.find(c=>c.id==='A').feedback.note"),'Keep this unanswered feedback');
  assert.equal(live.get('finish').disabled,true);assert.equal(live.get('finish-answer').disabled,true);
  assert.match(live.get('answer-notice').textContent,/0 answered, 3 unanswered, including 1 with feedback/);
 }
 storage.clear();const offline=page();await offline.run("select('A')");
 offline.get('note').value='Offline unanswered handback';offline.run('edit()');await offline.get('finish-answer').click();
 assert.equal(JSON.parse(offline.get('transfer').value).feedback[0].note,'Offline unanswered handback');
 assert.equal(JSON.parse(offline.get('transfer').value).decisions.length,0);
 storage.clear();
 let p=page();
 await p.run("select('A')");p.get('note').value='Reject for death; consider for pain';p.run('edit()');await p.run('flush()');
 assert.equal(p.run('packet().decisions.length'),0);
 assert.equal(p.run('packet().feedback[0].note'),'Reject for death; consider for pain');
 const audio=p.get('media').querySelector('audio');await audio.play();audio.currentTime=4.5;p.get('note').focus();p.run('draw()');
 assert.equal(p.get('media').querySelector('audio'),audio);assert.equal(audio.paused,false);assert.equal(audio.currentTime,4.5);assert.equal(p.context.document.activeElement,p.get('note'));
 p.get('loop').checked=true;p.get('loop').onchange();assert.equal(audio.loop,true);
 await p.get('replay').click();assert.equal(audio.currentTime,0);
 audio.currentTime=3.2;p.get('timestamp').click();assert.match(p.get('note').value,/\[0:03.2\]/);
 await p.run("select('B')");assert.equal(audio.paused,true);assert.equal(p.get('media').querySelector('audio').currentTime,0);assert.equal(p.get('note').value,'');
 await p.run("select('A')");assert.match(p.get('note').value,/consider for pain/);
 await p.run("record('reject')");assert.equal(p.run('packet().decisions[0].outcome'),'reject');assert.equal(p.run('state.candidates.filter(decision).length'),1);
 await p.run("record('withdrawn')");assert.equal(p.run('state.candidates.filter(decision).length'),0);assert.equal(p.run('packet().decisions[0].outcome'),'withdrawn');assert.match(p.run('packet().feedback[0].note'),/consider for pain/);
 p=page();await p.run("select('A')");assert.match(p.get('note').value,/consider for pain/);assert.equal(p.run('decision(candidate())'),null);
 await p.run("playbackError(candidate(),'Decode failed')");assert.equal(p.run('packet().diagnostics[0].message'),'Decode failed');assert.equal(p.run('state.candidates.filter(decision).length'),0);
 rejectStorage=true;p.get('note').value='Recoverable despite storage failure';p.run('edit()');assert.match(p.get('storage').textContent,/Export feedback/);p.get('export').click();assert.match(p.get('transfer').value,/Recoverable despite storage failure/);rejectStorage=false;
 // An embedded answer can be explicitly withdrawn offline and transferred.
 storage.clear();const answered=structuredClone(snapshot);answered.candidates[1].decision={candidate:'A',fingerprint:'fp-A',decision_id:'embedded-answer',outcome:'reject',note:'Original'};
 p=page(answered);await p.run("select('A')");await p.run("record('withdrawn')");assert.equal(p.run('packet().decisions[0].outcome'),'withdrawn');assert.equal(p.get('note').value,'Original');
 storage.clear();p=page();await p.run("select('A')");p.get('note').value='Draft on old material';p.run('edit()');
 const changed=structuredClone(snapshot);changed.candidates[1].fingerprint='fp-new';p.context.changed=changed;p.run('receive(changed)');
 assert.equal(p.run('candidate().fingerprint'),'fp-A');assert.equal(p.get('note').value,'Draft on old material');assert.match(p.get('notice').textContent,/older draft is retained/);
 p=page(changed);await p.run("select('A')");assert.equal(p.get('note').value,'');assert.equal(p.run('packet().feedback[0].fingerprint'),'fp-A');
 storage.clear();storage.set('attended-review:offline-fixture',JSON.stringify([{candidate:'A',fingerprint:'fp-A',decision_id:'legacy-local',outcome:'accept'}]));
 p=page();await p.run("select('A')");assert.equal(p.run('decision(candidate()).outcome'),'accept');
 // The note saves itself: no Save or Clear button competes with the decision.
 // Its status is quiet, and only a failed save offers Retry.
 const label=(q,id)=>q.get(id).children.filter(x=>typeof x==='string').join('');
 storage.clear();let q=page(snapshot,{live:true,failFeedback:true});await q.ready;await q.run("select('brief')");
 assert.equal(q.context.document.getElementById('clear-feedback').onclick,undefined);
 assert.equal(q.get('feedback-status').textContent,'Saves as you type');assert.equal(q.get('save-feedback').hidden,true);
 q.get('note').value='Needs a second look';q.run('edit()');assert.equal(q.get('feedback-status').textContent,'Saving…');
 assert.equal(await q.run('flush()'),false);assert.equal(q.get('feedback-status').dataset.tone,'error');
 assert.equal(q.get('save-feedback').hidden,false);assert.equal(q.get('answer-notice').dataset.tone,'error');
 q.settings.failFeedback=false;assert.equal(await q.get('save-feedback').click(),true);
 assert.equal(q.get('feedback-status').textContent,'Saved');assert.equal(q.get('save-feedback').hidden,true);
 // Accept and Reject are the decision; the pressed one is the recorded answer,
 // and pressing it again records nothing new.
 assert.equal(label(q,'accept'),'Accept');assert.equal(q.get('accept').attrs['aria-pressed'],'false');
 await q.get('reject').click();assert.equal(label(q,'reject'),'Rejected');assert.equal(q.get('reject').attrs['aria-pressed'],'true');
 assert.equal(q.get('answer').dataset.outcome,'reject');assert.equal(q.get('clear').hidden,false);
 const posted=()=>q.requests.filter(r=>r.url==='/api/decisions'&&r.body.decisions.length).length;
 const before=posted();await q.get('reject').click();assert.equal(posted(),before);assert.match(q.get('answer-notice').textContent,/Already recorded/);
 await q.get('accept').click();assert.equal(posted(),before+1);assert.equal(label(q,'accept'),'Accepted');assert.equal(q.get('reject').attrs['aria-pressed'],'false');
 // A message belongs to the question it was said about.
 await q.get('next').click();assert.equal(q.get('answer-notice').textContent,'');
 // Each attached image can be removed on its own, and the removal saves.
 q.run("pending.push({name:'one.png',data:'data:image/png;base64,AA'},{name:'two.png',data:'data:image/png;base64,AA'});edit();draw()");
 const remove=q.get('attachments').children[0].children[1].children[1];assert.equal(remove.attrs['aria-label'],'Remove one.png');
 await remove.click();await q.run('flush()');
 assert.equal(q.run('JSON.stringify(candidate().feedback.attachments.map(a=>a.name))'),JSON.stringify(['two.png']));
 // Hand-back is said once, in its own banner; the finish controls go away.
 await q.get('finish-answer').click();assert.equal(q.get('handed').hidden,false);assert.equal(q.get('finish').hidden,true);
 assert.match(q.get('handed-summary').textContent,/1 question answered, 2 left unanswered/);assert.equal(q.get('answer-notice').hidden,true);
 // Options are chosen inside the decision; a changed selection offers to replace it.
 storage.clear();q=page({...snapshot,candidates:[candidate('pick',{options:['A: outlined','B: filled']})]});await q.run("select('pick')");
 assert.equal(label(q,'accept'),'Choose selected');assert.equal(label(q,'reject'),'Reject all');
 await q.get('accept').click();assert.equal(q.run('decision(candidate())'),null);assert.match(q.get('answer-notice').textContent,/Tick at least one option/);
 const [first,second]=q.get('options').children.map(l=>l.children[0]);first.checked=true;first.onchange();
 await q.get('accept').click();assert.equal(q.run('JSON.stringify(decision(candidate()).selected)'),JSON.stringify(['A: outlined']));assert.equal(label(q,'accept'),'Chosen');
 second.checked=true;second.onchange();assert.equal(label(q,'accept'),'Choose these instead');
 await q.get('accept').click();assert.equal(q.run('JSON.stringify(decision(candidate()).selected)'),JSON.stringify(['A: outlined','B: filled']));
 // Offline, finishing exports, and the button says so.
 assert.equal(q.get('finish').textContent,'Finish and export');assert.match(q.get('feedback-status').textContent,/until you export/);
 // The theme follows the system until the reviewer picks one. The choice is this
 // browser's preference: it survives a reload, never reaches the session or the
 // export, and without storage the page stays on System.
 storage.clear();let t=page();const theme=x=>x.context.document.documentElement.attrs['data-theme'];
 assert.equal(t.get('theme').value,'system');assert.equal(theme(t),undefined);
 t.get('theme').value='dark';t.get('theme').onchange();assert.equal(theme(t),'dark');assert.equal(storage.get('attended-review:theme'),'dark');
 t=page();assert.equal(t.get('theme').value,'dark');assert.equal(theme(t),'dark');
 assert.doesNotMatch(t.run('JSON.stringify(packet())'),/theme|dark/);
 t.get('theme').value='light';t.get('theme').onchange();assert.equal(theme(t),'light');
 t.get('theme').value='system';t.get('theme').onchange();assert.equal(theme(t),undefined);assert.equal(storage.has('attended-review:theme'),false);
 storage.set('attended-review:theme','sepia');t=page();assert.equal(t.get('theme').value,'system');assert.equal(theme(t),undefined);
 t=page(snapshot,{storageThrows:true});assert.equal(t.get('theme').value,'system');
 t.get('theme').value='dark';t.get('theme').onchange();assert.equal(theme(t),'dark');
 // A live page sends no theme to the host.
 storage.clear();t=page(snapshot,{live:true});await t.ready;t.get('theme').value='light';t.get('theme').onchange();
 await t.run("select('A')");await t.get('accept').click();
 assert.equal(t.requests.some(r=>JSON.stringify(r.body||'').includes('theme')),false);
 // The head script applies a saved choice before the first paint, and ignores
 // anything else, including storage that refuses to be read.
 const boot=html.match(/<script id="theme-boot">([\s\S]*?)<\/script>/)[1];
 assert.ok(html.indexOf('<script id="theme-boot">')<html.indexOf('<style>'));
 const paint=store=>{const root=new (t.context.document.documentElement.constructor)('html');vm.runInNewContext(boot,{document:{documentElement:root},localStorage:store});return root.attrs['data-theme'];};
 assert.equal(paint({getItem:()=> 'dark'}),'dark');assert.equal(paint({getItem:()=> 'light'}),'light');
 assert.equal(paint({getItem:()=> 'sepia'}),undefined);assert.equal(paint({getItem(){throw Error('denied');}}),undefined);
 storage.clear();
 // HTTPS is the same online intake: an unanswered note survives a reconnect,
 // then handback preserves it without synthesizing a verdict.
 storage.clear();const secure=page(snapshot,{live:true,protocol:'https:'});await secure.ready;
 assert.equal(secure.run('online'),true);await secure.run("select('A')");
 secure.get('note').value='Saved from the tailnet phone';secure.run('edit()');await secure.run('flush()');
 assert.equal(secure.requests.find(r=>r.body?.feedback?.length).url,'/api/decisions');
 await secure.get('finish-answer').click();
 assert.ok(secure.requests.some(r=>r.url==='/api/hand-back'));
 assert.equal(secure.run("candidate().decision"),null);
 assert.equal(secure.run("candidate().feedback.note"),'Saved from the tailnet phone');
 assert.match(secure.get('answer-notice').textContent,/Handed back/);
 // A refresh leaves out material the page holds; a replaced candidate's new
 // material arrives with one full read, and an older poll never undoes an answer.
 storage.clear();const pictured={...snapshot,candidates:[candidate('pic',{media:[{kind:'image',url:'data:image/png;base64,old',label:'old'}]}),candidate('other')]};
 const lean=page(pictured,{live:true});await lean.ready;await lean.run("select('other')");
 const reads=()=>lean.requests.filter(r=>r.url.startsWith('/api/status')).map(r=>r.url);
 let seen=reads().length;await lean.get('accept').click();
 assert.deepEqual(reads().slice(seen),['/api/status?material=omit']);
 assert.equal(lean.run("state.candidates.find(c=>c.id==='pic').media[0].url"),'data:image/png;base64,old');
 assert.equal(lean.run("'material_omitted' in state.candidates.find(c=>c.id==='pic')"),false);
 seen=reads().length;await lean.context.polls[0]();assert.deepEqual(reads().slice(seen),[`/api/status?material=omit&after=${lean.backend.sequence}`]);
 Object.assign(lean.backend.candidates.find(c=>c.id==='pic'),{fingerprint:'fp-pic-2',media:[{kind:'image',url:'data:image/png;base64,new',label:'new'}]});lean.backend.sequence++;
 seen=reads().length;await lean.context.polls[0]();
 assert.deepEqual(reads().slice(seen),[`/api/status?material=omit&after=${lean.backend.sequence-1}`,'/api/status']);
 assert.equal(lean.run("state.candidates.find(c=>c.id==='pic').media[0].url"),'data:image/png;base64,new');
 const older=lean.run('({...state,sequence:state.sequence-1,candidates:state.candidates.map(c=>({...c,decision:null}))})');
 lean.context.older=older;lean.run('receive(older)');assert.equal(lean.run("decision(state.candidates.find(c=>c.id==='other')).outcome"),'accept');
 storage.clear();
 if(process.argv[2]){
  storage.clear();const saved=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));p=page(saved);
  const audioId=saved.candidates.find(c=>c.question_type==='audio').id;
  await p.run(`select(${JSON.stringify(audioId)})`);p.get('note').value='Offline unanswered feedback for exact clip';p.run('edit()');await p.run('flush()');
  fs.writeFileSync(process.argv[3],p.run('JSON.stringify(packet())'));
 }
 console.log('PASS: answered/pending next-question order across server regrouping/reload, wide/narrow focus and scroll, end-of-queue state, both handback entrypoints with failed prior-draft recovery; offline draft/reload/export, independent answer/withdrawal, keyed playback, controls, diagnostics, storage-failure recovery; self-saving note with retry only on failure, pressed decision buttons, per-image removal, options inside the decision, single hand-back banner; lean refreshes that keep held material and read a replaced candidate in full; System/Light/Dark theme kept in this browser only and applied before first paint');
})().catch(e=>{console.error(e);process.exitCode=1;});
