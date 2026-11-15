import{createAccount,createClient}from"genlayer-js";
import{studioDevnet}from"genlayer-js/chains";
const contract=process.env.CONTRACT_ADDRESS?.trim()||"0x303D86EE0654099205d5B37Fad380EB0810B7243",raw=process.env.GENLAYER_PRIVATE_KEY?.trim();
if(!contract)throw new Error("CONTRACT_ADDRESS is required");if(!raw)throw new Error("GENLAYER_PRIVATE_KEY is required");
const key=raw.startsWith("0x")?raw:`0x${raw}`,chain={...studioDevnet,id:61997,name:"GenLayer Studio Next",rpcUrls:{default:{http:["https://studio-next.genlayer.com/api"]}}},account=createAccount(key),client=createClient({chain,account}),sleep=ms=>new Promise(r=>setTimeout(r,ms)),id=`plate-signal-${Date.now().toString(36)}`;
async function finalized(hash){for(let i=0;i<300;i++){const r=await client.getTransaction({hash}).catch(()=>null),s=String(r?.statusName??r?.status??"PENDING").toUpperCase();if(s==="FINALIZED")return r;if(["UNDETERMINED","DECLINED","CANCELED","CANCELLED"].includes(s))throw new Error(`Transaction ended ${s}`);await sleep(3000)}throw new Error("Transaction timed out")}
async function write(label,functionName,args,intelligent=false){const fees=await client.estimateTransactionFees({leaderTimeunitsAllocation:intelligent?500n:180n,validatorTimeunitsAllocation:intelligent?600n:360n}),hash=await client.writeContract({address:contract,functionName,args,fees});console.log(`${label}_TX=${hash}`);const r=await finalized(hash),execution=String(r.txExecutionResultName??r.txExecutionResult),consensus=String(r.resultName??r.result_name);if(execution!=="FINISHED_WITH_RETURN"||consensus==="MAJORITY_DISAGREE")throw new Error(`${label} failed: ${execution} / ${consensus}`);return hash}
const menu="https://raw.githubusercontent.com/nearar22/plate-signal/main/frontend/public/demo/menu-page.txt",guide="https://cdn.jsdelivr.net/gh/nearar22/plate-signal@main/frontend/public/demo/allergen-guide.txt";
const openTx=await write("OPEN","open_report",[id,"Copper Table","Garden Ember Bowl","Milk","Dairy-free",menu,guide]);
const reviewTx=await write("REVIEW","review_report",[id],true);
const reviewed=await client.readContract({address:contract,functionName:"get_report",args:[id],jsonSafeReturn:true});
if(reviewed.status!=="REVIEWED"||reviewed.analysis?.source_receipts?.length!==2)throw new Error("Live review did not persist two source receipts");
const sealTx=await write("SEAL","seal_report",[id]);
const state=await client.readContract({address:contract,functionName:"get_report",args:[id],jsonSafeReturn:true});
console.log(`REPORT_ID=${id}\nOPEN_TX=${openTx}\nREVIEW_TX=${reviewTx}\nSEAL_TX=${sealTx}\nSTATUS=${state.status}\nFINDING=${state.analysis?.finding}\nACTION=${state.analysis?.action}\nRECEIPT=${state.final_receipt}`);
if(state.status!=="SEALED"||state.analysis?.finding!=="CONFLICT"||!state.final_receipt)throw new Error("Live PlateSignal lifecycle failed");

