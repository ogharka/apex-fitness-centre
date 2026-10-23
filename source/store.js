(function(){
var P=window.APEX_PRODUCTS||[],WA=window.APEX_WA,root=document.body.getAttribute('data-root')||'';
var KEY='apex_cart_v1',cart={};
try{cart=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(x){cart={}}
function save(){try{localStorage.setItem(KEY,JSON.stringify(cart))}catch(x){}}
function bySlug(s){for(var i=0;i<P.length;i++)if(P[i].slug===s)return P[i]}
function fmt(n){return 'Rs. '+Number(n).toLocaleString('en-IN')}
function $(s){return document.querySelector(s)}
var drawer=$('#drawer'),scrim=$('#scrim'),lastFocus=null;
function count(){var n=0;for(var k in cart)n+=cart[k];return n}
function render(){
  var n=count();['#cartCount','#cartCount2'].forEach(function(s){var el=$(s);if(el)el.textContent=n});
  var body=$('#cartBody'),foot=$('#cartFoot');if(!body)return;
  var keys=Object.keys(cart).filter(function(k){return bySlug(k)&&cart[k]>0});
  if(!keys.length){body.innerHTML='<p class="empty">Your cart is empty. Add a product to start your order.</p>';foot.innerHTML='<a class="btn line" href="'+root+'shop/">Browse products</a>';return}
  var total=0,lines=[],saved=0,sl=[];
  var cnt={};keys.forEach(function(k){cnt[k]=cart[k]});
  (window.APEX_RULES||[]).forEach(function(rl){var n=Infinity;rl.slugs.forEach(function(s){n=Math.min(n,cnt[s]||0)});if(n>0&&n<Infinity){rl.slugs.forEach(function(s){cnt[s]-=n});saved+=rl.off*n;sl.push(rl.name+(n>1?' x'+n:'')+': -'+fmt(rl.off*n))}});
  body.innerHTML=keys.map(function(k){var p=bySlug(k),q=cart[k];total+=p.price*q;lines.push(q+' x '+p.full+' ('+fmt(p.price*q)+')');
    return '<div class="ci"><img src="'+root+'assets/'+p.img+'" alt="'+p.full.replace(/"/g,'')+'" width="68" height="68"><div><h4>'+p.full+'</h4><div class="r"><div class="qty"><button type="button" data-d="-1" data-s="'+k+'" aria-label="Decrease">-</button><span>'+q+'</span><button type="button" data-d="1" data-s="'+k+'" aria-label="Increase">+</button></div><b>'+fmt(p.price*q)+'</b></div><button class="rm" type="button" data-rm="'+k+'">Remove</button></div></div>'}).join('');
  total-=saved;
  var msg='Hi Apex Fitness Centre, I want to order:\n'+lines.join('\n')+(saved?'\nStack saving: -'+fmt(saved)+' ('+sl.join(', ')+')':'')+'\nTotal: '+fmt(total)+'\nPlease confirm stock and send Khalti/bank payment details. My delivery address: ';
  var xs='',pairs=window.APEX_PAIRS||{};
  for(var i=0;i<keys.length&&!xs;i++){var ps=pairs[keys[i]],q=ps&&bySlug(ps);if(q&&!cart[ps])xs='<div class="xs"><b>Often bought together</b><div class="r2"><img src="'+root+'assets/'+q.img+'" alt="" width="48" height="48"><span>'+q.name+' &middot; '+fmt(q.price)+'</span></div><button class="add" type="button" data-add="'+ps+'">Add to cart</button></div>'}
  foot.innerHTML=xs+'<div class="free">Free delivery all over Nepal on this order.</div>'+(saved?'<div class="free">You saved '+fmt(saved)+' with stack pricing.</div>':'')+'<div class="tot"><span>Total</span><span>'+fmt(total)+'</span></div><a class="btn wa full" target="_blank" rel="noopener" href="https://wa.me/'+WA+'?text='+encodeURIComponent(msg)+'">Order on WhatsApp</a><small>Free delivery all over Nepal. Pay by Khalti or bank transfer, confirmed on WhatsApp.</small>';
}
function open(){lastFocus=document.activeElement;render();drawer.classList.add('open');drawer.setAttribute('aria-hidden','false');scrim.hidden=false;var c=$('#cartClose');if(c)c.focus()}
function close(){drawer.classList.remove('open');drawer.setAttribute('aria-hidden','true');scrim.hidden=true;if(lastFocus)lastFocus.focus()}
function add(s,q){cart[s]=Math.min(99,(cart[s]||0)+q);save();render()}
document.addEventListener('click',function(ev){
  var t=ev.target.closest('button,a');if(!t)return;
  if(t.id==='cartOpen'||t.id==='cartOpen2'){open();return}
  if(t.id==='cartClose'){close();return}
  if(t.hasAttribute('data-bundle')){t.getAttribute('data-bundle').split(',').forEach(function(s){add(s,1)});var ob=t.textContent;t.textContent='Added. Open cart';t.classList.add('done');setTimeout(function(){t.textContent=ob;t.classList.remove('done')},1400);open();return}
  if(t.hasAttribute('data-add')){var q=1,qi=$('#qv');if(qi&&t.id==='addBtn')q=Math.max(1,parseInt(qi.value,10)||1);add(t.getAttribute('data-add'),q);var o=t.textContent;t.textContent='Added';t.classList.add('done');setTimeout(function(){t.textContent=o;t.classList.remove('done')},1200);return}
  if(t.hasAttribute('data-d')){var s=t.getAttribute('data-s');cart[s]=(cart[s]||0)+parseInt(t.getAttribute('data-d'),10);if(cart[s]<=0)delete cart[s];save();render();return}
  if(t.hasAttribute('data-rm')){delete cart[t.getAttribute('data-rm')];save();render();return}
  if(t.id==='qm'){var i=$('#qv');i.value=Math.max(1,(parseInt(i.value,10)||1)-1);return}
  if(t.id==='qp'){var j=$('#qv');j.value=Math.min(99,(parseInt(j.value,10)||1)+1);return}
});
if(scrim)scrim.addEventListener('click',close);
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&drawer&&drawer.classList.contains('open'))close()});
var y=$('#yr');if(y)y.textContent=new Date().getFullYear();
render();
})();
