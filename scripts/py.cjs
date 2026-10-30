// Runs a Python command with whichever interpreter exists: python3 first, then python.
// Usage: node scripts/py.cjs build.py   (arguments are forwarded unchanged)
const {spawnSync}=require('child_process');
const candidates=['python3','python'];
const args=process.argv.slice(2);
for(const cmd of candidates){
 const probe=spawnSync(cmd,['--version'],{stdio:'ignore'});
 if(probe.error||probe.status!==0)continue;
 const run=spawnSync(cmd,args,{stdio:'inherit'});
 if(run.error){console.error(run.error.message);process.exit(1)}
 process.exit(run.status===null?1:run.status);
}
console.error('Python not found: install python3 (or python) and make it available on PATH.');
process.exit(1);
