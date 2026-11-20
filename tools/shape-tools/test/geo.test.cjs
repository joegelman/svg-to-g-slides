const G = require('./geo-node.cjs');
const assert = require('assert');
const K = 0.5522847498;
const rect = (x, y, w, h) => ({ closed: true, nodes: [[x,y],[x+w,y],[x+w,y+h],[x,y+h]].map(([x,y]) => ({x,y,in:null,out:null})) });
const circle = (cx, cy, r) => { const k=r*K; return { closed: true, nodes: [
  {x:cx+r,y:cy,in:{x:cx+r,y:cy-k},out:{x:cx+r,y:cy+k}},
  {x:cx,y:cy+r,in:{x:cx+k,y:cy+r},out:{x:cx-k,y:cy+r}},
  {x:cx-r,y:cy,in:{x:cx-r,y:cy+k},out:{x:cx-r,y:cy-k}},
  {x:cx,y:cy-r,in:{x:cx-k,y:cy-r},out:{x:cx+k,y:cy-r}} ]}; };
const P = require('paper');
const area = (subs) => Math.abs(G.toPaper(subs).area);
const near = (a, b, tol, msg) => assert(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b}`);

const A = { subs: [rect(0,0,100,100)] }, B = { subs: [rect(50,50,100,100)] };
near(area(G.boolean('union',[A,B]).subs), 17500, 1, 'union');
near(area(G.boolean('subtract',[A,B]).subs), 7500, 1, 'subtract');
near(area(G.boolean('intersect',[A,B]).subs), 2500, 1, 'intersect');
near(area(G.boolean('exclude',[A,B]).subs), 15000, 1, 'exclude');
const C = { subs: [circle(100,50,40)] };
const u = G.boolean('union',[A,C]).subs;
const curved = u[0].nodes.filter(n=>n.in||n.out).length;
console.log('union rect+circle nodes', u[0].nodes.length, 'curved', curved);
assert(u[0].nodes.length < 12 && curved >= 2, 'curves kept');
// disjoint intersect -> empty
assert(G.boolean('intersect',[A,{subs:[rect(500,500,10,10)]}]).empty, 'empty intersect');
// three-way subtract
near(area(G.boolean('subtract',[A,{subs:[rect(0,0,10,10)]},{subs:[rect(90,90,10,10)]}]).subs), 9800, 1, 'subtract many');
// evenodd donut input
const donut = { subs:[rect(0,0,100,100), rect(25,25,50,50)], fillRule:'evenodd' };
near(area(G.boolean('union',[donut,{subs:[rect(200,0,10,10)]}]).subs), 7500+100, 1, 'evenodd donut keeps hole');
// stroke outline open polyline
const line = { closed:false, nodes:[{x:0,y:0},{x:100,y:0},{x:100,y:100}].map(p=>({...p,in:null,out:null})) };
const s1 = G.outlineStroke([line], 10, {cap:'butt', join:'miter'});
near(area(s1.subs), 2000, 30, 'butt stroke area');
const s2 = G.outlineStroke([line], 10, {cap:'round', join:'round'});
console.log('round stroke area', area(s2.subs).toFixed(1));
const s3 = G.outlineStroke([rect(0,0,100,100)], 10, {join:'miter'});
near(area(s3.subs), 110*110-90*90, 30, 'closed rect stroke ring');
console.log('rect ring subpaths', s3.subs.length);
const s4 = G.outlineStroke([circle(0,0,50)], 4, {});
near(area(s4.subs), Math.PI*(52*52-48*48), 20, 'circle ring');
console.log('circle ring nodes', s4.subs.map(s=>s.nodes.length));
const s5 = G.outlineStroke([line], 10, {cap:'butt', dashes:[20,10]});
console.log('dashed pieces', s5.subs.length, 'area', area(s5.subs).toFixed(1));
console.log('all ok');
