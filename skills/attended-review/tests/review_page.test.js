/* Deterministic execution of the real page with a minimal DOM/media model.
   This checks offline/state behavior; it does not qualify a native file browser. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const html=fs.readFileSync(path.join(__dirname,'../assets/review.html'),'utf8');
const script=html.split('<script>')[1].split('</script>')[0];
const candidate=(id,extra={})=>({id,title:id,revision:'fixture-1',fingerprint:`fp-${id}`,phase:'ready',protected:true,criteria:['Judge exact purpose'],decision:null,...extra});
const snapshot={session:'offline-fixture',sequence:1,checkout:'/fixture',candidates:[candidate('brief'),candidate('A',{question_type:'audio',comparison_group:'death',audio:{url:'data:audio/wav;base64,fixture',purpose:'Death',scope:'Isolation',variant:'Death A'}}),candidate('B',{question_type:'audio',comparison_group:'death',audio:{url:'data:audio/wav;base64,fixture-b',purpose:'Death',scope:'Isolation',variant:'Death B'}})]};
const storage=new Map();let rejectStorage=false;
function page(seed=snapshot){
 const nodes=new Map();let document;
 class Element{
  constructor(tag,id){this.tag=tag;this.id=id;this.children=[];this.classList={toggle(){}};this.style={};this.dataset={};this.attrs={};this.value='';this.textContent='';this.paused=true;this.currentTime=0;this.hidden=false;this.checked=false;}
  append(...items){this.children.push(...items);}
  replaceChildren(...items){this.children=[...items];}
  setAttribute(k,v){this.attrs[k]=v;}
  focus(){document.activeElement=this;}
  scrollIntoView(){}
  select(){}
  play(){this.paused=false;this.onplay?.();return Promise.resolve();}
  pause(){this.paused=true;}
  click(){return this.onclick?.();}
  querySelectorAll(selector){const all=this.children.flatMap(c=>c instanceof Element?[c,...c.querySelectorAll('*')]:[]);if(selector==='*')return all;if(selector==='audio,video')return all.filter(c=>['audio','video'].includes(c.tag));if(selector==='input:checked')return all.filter(c=>c.tag==='input'&&c.checked);return all.filter(c=>c.tag===selector);}
  querySelector(selector){return this.querySelectorAll(selector)[0];}
 }
 const get=id=>{if(!nodes.has(id))nodes.set(id,new Element('div',id));return nodes.get(id);};
 document={activeElement:null,getElementById:get,createElement:tag=>new Element(tag),createTextNode:text=>text,querySelector:get,addEventListener(){}};
 const context={console,document,location:{hash:'',protocol:'file:',pathname:'/fixture.html'},history:{replaceState(){}},localStorage:{getItem:k=>storage.get(k),setItem(k,v){if(rejectStorage)throw Error('storage full');storage.set(k,v);}},matchMedia:()=>({matches:true,addEventListener(){}}),setTimeout:()=>1,clearTimeout(){},setInterval(){},URL,URLSearchParams,Blob,window:{addEventListener(){}},navigator:{},crypto:{randomUUID:()=>`id-${Math.random()}`},getSelection:()=>({removeAllRanges(){},addRange(){}})};
 vm.createContext(context);vm.runInContext(script.replace('/*SESSION_DATA*/null',JSON.stringify(seed)),context);
 const run=code=>vm.runInContext(code,context);
 return {run,get,context};
}
(async()=>{
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
 if(process.argv[2]){
  storage.clear();const saved=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));p=page(saved);
  const audioId=saved.candidates.find(c=>c.question_type==='audio').id;
  await p.run(`select(${JSON.stringify(audioId)})`);p.get('note').value='Offline unanswered feedback for exact clip';p.run('edit()');await p.run('flush()');
  fs.writeFileSync(process.argv[3],p.run('JSON.stringify(packet())'));
 }
 console.log('PASS: offline draft/reload/export, independent answer/withdrawal, keyed playback, controls, diagnostics, storage-failure recovery');
})().catch(e=>{console.error(e);process.exitCode=1;});
