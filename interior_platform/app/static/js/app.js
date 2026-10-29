document.addEventListener('click',e=>{const b=e.target.closest('[data-toggle]');if(!b)return;const el=document.getElementById(b.dataset.toggle);if(el)el.classList.toggle('hidden')});
setTimeout(()=>document.querySelectorAll('.flash').forEach(x=>x.classList.add('fade')),3500);
