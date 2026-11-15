export const blankReport={id:"",restaurant:"",dish:"",allergen:"",advertised_claim:"",status:"OPEN",sources:[],analysis:{},history:[],correction_used:false,correction_deadline:0,final_receipt:""};
export function clean(value){if(typeof value==="bigint")return Number(value);if(Array.isArray(value))return value.map(clean);if(value&&typeof value==="object")return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,clean(v)]));return value}
export function short(value,n=7){const text=String(value||"");return text.length>n*2?`${text.slice(0,n)}…${text.slice(-n)}`:text}
export function findingLabel(value){return({CONFLICT:"CLAIM CONFLICT",ALIGNED:"SOURCES ALIGNED",INSUFFICIENT:"MORE DETAIL NEEDED",SOURCE_UNAVAILABLE:"SOURCE OFFLINE"})[value]||"AWAITING REVIEW"}
export function findingTone(value){return({CONFLICT:"conflict",ALIGNED:"aligned",INSUFFICIENT:"uncertain",SOURCE_UNAVAILABLE:"offline"})[value]||"waiting"}
export function remaining(deadline,now=Math.floor(Date.now()/1000)){const seconds=Math.max(0,Number(deadline||0)-now);if(!seconds)return"window closed";const h=Math.floor(seconds/3600),m=Math.floor((seconds%3600)/60);return`${h}h ${String(m).padStart(2,"0")}m`}
export function canCorrect(report,wallet,now=Math.floor(Date.now()/1000)){return report.status==="REVIEWED"&&!report.correction_used&&Boolean(wallet)&&String(report.owner||"").toLowerCase()===String(wallet).toLowerCase()&&now<=Number(report.correction_deadline||0)}

