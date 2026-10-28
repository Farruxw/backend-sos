import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { Activity, Ambulance, BarChart3, ClipboardList, HeartPulse, LayoutDashboard, LockKeyhole, MapPin, Moon, Navigation, Shield, Siren, Sun, Users, Zap } from 'lucide-react'
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'
import { callsApi, chatApi } from './services/api'
import type { CallDetail, EmergencyCall, ChatMessage } from './types/api'

const dict = {
  uz: { dashboard:'Boshqaruv', sos:'SOS', operator:'Operator', crew:'Brigada', doctor:'Shifokor', active:'Faol chaqiruvlar', send:'SOS yuborish', cancel:'Bekor qilish', location:'Joylashuv aniqlanmoqda', unavailable:'Bu funksiya backend endpointi talab qiladi' },
  ru: { dashboard:'Управление', sos:'SOS', operator:'Оператор', crew:'Бригада', doctor:'Врач', active:'Активные вызовы', send:'Отправить SOS', cancel:'Отменить', location:'Определение местоположения', unavailable:'Для этой функции нужен endpoint backend' },
  en: { dashboard:'Dashboard', sos:'SOS', operator:'Operator', crew:'Response unit', doctor:'Doctor', active:'Active emergencies', send:'Send SOS', cancel:'Cancel', location:'Detecting location', unavailable:'This function requires a backend endpoint' },
  kz: { dashboard:'Басқару', sos:'SOS', operator:'Оператор', crew:'Бригада', doctor:'Дәрігер', active:'Белсенді қоңыраулар', send:'SOS жіберу', cancel:'Бас тарту', location:'Орналасқан жер анықталуда', unavailable:'Бұл функция backend endpointін талап етеді' }
}
type Lang = keyof typeof dict

function useTranslations() { return dict[lang] }
let lang: Lang = 'uz'

function Shell() {
  const [, setTick] = useState(0)
  const [dark,setDark] = useState(false)
  const t = useTranslations()
  const changeLang=(value:string)=>{lang=value as Lang; setTick(v=>v+1)}
  return <div className={dark?'app dark':'app'}>
    <aside>
      <Link className="brand" to="/"><span><Shield size={22}/></span><b>SMART SOS</b></Link>
      <nav>
        <NavLink to="/"><LayoutDashboard/> {t.dashboard}</NavLink>
        <NavLink to="/sos"><Siren/> {t.sos}</NavLink>
        <NavLink to="/operator"><Activity/> {t.operator}</NavLink>
        <NavLink to="/crew"><Ambulance/> {t.crew}</NavLink>
        <NavLink to="/doctor"><HeartPulse/> {t.doctor}</NavLink>
        <NavLink to="/admin"><BarChart3/> Admin</NavLink>
      </nav>
      <div className="aside-foot"><span className="online"/> Dispatch connected</div>
    </aside>
    <main>
      <header><button className="icon-btn" aria-label="Theme" onClick={()=>setDark(v=>!v)}>{dark?<Sun/>:<Moon/>}</button>
      <select aria-label="Language" value={lang} onChange={e=>changeLang(e.target.value)}><option value="uz">UZ</option><option value="ru">RU</option><option value="en">EN</option><option value="kz">KZ</option></select></header>
      <Routes>
        <Route path="/" element={<Dashboard/>}/><Route path="/sos" element={<Sos/>}/>
        <Route path="/operator" element={<Operator/>}/><Route path="/crew" element={<Crew/>}/>
        <Route path="/doctor" element={<Doctor/>}/><Route path="/admin" element={<Admin/>}/><Route path="/login" element={<Login/>}/><Route path="/call/:id" element={<ActiveCall/>}/>
        <Route path="*" element={<Navigate to="/"/>}/>
      </Routes>
    </main>
  </div>
}

function Page({title,children,action}:{title:string;children:any;action?:any}) { return <div className="page"><div className="page-head"><h1>{title}</h1>{action}</div>{children}</div> }
function ErrorBox({text}:{text:string}) { return text ? <div className="error">{text}</div> : null }

function Dashboard(){
  const [calls,setCalls]=useState<EmergencyCall[]>([]); const [error,setError]=useState('')
  useEffect(()=>{callsApi.active().then(setCalls).catch(e=>setError(e.message))},[])
  return <Page title="Emergency operations" action={<Link className="primary compact" to="/sos"><Siren/> New SOS</Link>}>
    <ErrorBox text={error}/>
    <div className="stats"><Stat icon={<Siren/>} value={calls.length} label="Active calls" tone="red"/><Stat icon={<Users/>} value={calls.filter(c=>c.status==='NEW').length} label="Awaiting dispatch"/><Stat icon={<Navigation/>} value={calls.filter(c=>c.status==='ENROUTE').length} label="Units en route"/></div>
    <div className="grid-two"><section className="panel"><div className="panel-title"><h2>Live calls</h2><span className="live"><i/> LIVE</span></div>{calls.length?calls.map(CallRow):<Empty/>}</section><section className="panel map-panel"><Map marks={calls}/></section></div>
  </Page>
}
function Stat({icon,value,label,tone}:{icon:any;value:number;label:string;tone?:string}){return <div className="stat"><span className={tone||''}>{icon}</span><div><strong>{value}</strong><p>{label}</p></div></div>}
function Empty(){return <div className="empty"><ClipboardList/><p>No active emergencies</p></div>}
function CallRow(c:EmergencyCall){return <Link className="call-row" to={`/call/${c.id}`}><span className={`severity ${c.severity?.toLowerCase()}`}><i/></span><div><b>{c.text}</b><small>{c.address || `${c.lat.toFixed(4)}, ${c.lng.toFixed(4)}`} · {c.status}</small></div><strong>{c.services?.replaceAll(',', ' / ') || '—'}</strong></Link>}

function Sos(){
  const [form,setForm]=useState({fullName:'',phone:'',address:'',text:'',lat:41.2995,lng:69.2401,accuracy:null as number|null})
  const [error,setError]=useState(''); const [busy,setBusy]=useState(false); const [holding,setHolding]=useState(false); const [count,setCount]=useState<number|null>(null); const hold=useRef<number | undefined>(undefined); const startedAt=useRef(0)
  const detect=()=>navigator.geolocation?.getCurrentPosition(p=>setForm(f=>({...f,lat:p.coords.latitude,lng:p.coords.longitude,accuracy:p.coords.accuracy})),()=>setError('GPS access denied'))
  const start=()=>{startedAt.current=Date.now(); setHolding(true); hold.current=window.setTimeout(()=>setHolding(true),2000)}
  const finish=()=>{clearTimeout(hold.current); setHolding(false); if(Date.now()-startedAt.current>=2000) void submit()}
  const submit=async()=>{ setBusy(true); setError(''); try{const c=await callsApi.create({...form,text:form.text.trim() || 'Emergency assistance required'}); setCount(5); const timer=setInterval(()=>setCount(v=>{if(v===1){clearInterval(timer);window.location.assign(`/call/${c.id}`)}return v? v-1:null}),1000)}catch(e:any){setError(e.message)}finally{setBusy(false)}}
  return <Page title="Emergency assistance"><div className="sos-layout"><section className="sos-main"><div className="sos-orb"><button disabled={busy} onPointerDown={start} onPointerUp={finish} onPointerLeave={()=>{clearTimeout(hold.current);setHolding(false)}} className={holding?'holding':''}><Siren/><strong>SOS</strong><small>{count===null?'HOLD 2 SEC':`${count} SEC TO CANCEL`}</small></button></div>{count!==null&&<button className="cancel-btn" onClick={()=>setCount(null)}><Shield/> Cancel transmission</button>}</section><section className="form panel"><h2>Emergency details</h2><ErrorBox text={error}/><div className="field-grid"><label>Full name<input value={form.fullName} onChange={e=>setForm({...form,fullName:e.target.value})}/></label><label>Phone<input value={form.phone} onChange={e=>setForm({...form,phone:e.target.value})}/></label></div><label>Address<div className="input-action"><input value={form.address} onChange={e=>setForm({...form,address:e.target.value})}/><button onClick={detect} title="Detect location"><MapPin/></button></div></label><label>What happened?<textarea rows={4} value={form.text} onChange={e=>setForm({...form,text:e.target.value})} placeholder="Describe the emergency..."/></label><div className="location-bar"><MapPin/><span>GPS: {form.lat.toFixed(5)}, {form.lng.toFixed(5)}<small>{form.accuracy?`Accuracy ±${Math.round(form.accuracy)} m`:'Default location'}</small></span><button onClick={detect}>Locate</button></div></section></div></Page>
}

function Operator(){
  const [calls,setCalls]=useState<EmergencyCall[]>([]); const [error,setError]=useState('')
  const refresh=()=>callsApi.active().then(setCalls).catch(e=>setError(e.message))
  useEffect(()=>{refresh(); const i=setInterval(refresh,10000);return()=>clearInterval(i)},[])
  const assign=async(id:number)=>{try{await callsApi.assign(id);await refresh()}catch(e:any){setError(e.message)}}
  return <Page title="Dispatch console" action={<button className="secondary" onClick={refresh}><Zap/> Refresh</button>}><ErrorBox text={error}/><div className="dispatch"><section className="panel"><div className="panel-title"><h2>Incoming calls</h2><span>{calls.length}</span></div>{calls.map(c=><div className="dispatch-row" key={c.id}><div><span className={`badge ${c.severity?.toLowerCase()}`}>{c.severity}</span><b>{c.services}</b><p>{c.text}</p><small>{c.status} · #{c.id}</small></div><button onClick={()=>assign(c.id)}>{c.unitId?'Reassign':'Assign unit'}</button></div>)}</section><section className="panel"><h2>Fleet overview</h2><div className="notice"><Ambulance/><div><b>Unit availability</b><p>No unit listing endpoint is available. Assignment uses the nearest free unit in the backend.</p></div></div></section></div></Page>
}

function Crew(){return <Page title="Response unit"><div className="notice"><Ambulance/><div><b>Assigned unit view</b><p>{dict[lang].unavailable}. Use the call and assignment endpoints from the operator dashboard.</p></div></div><section className="panel map-panel"><Map/></section></Page>}

function Login(){return <Page title="Account access"><section className="panel login-panel"><LockKeyhole/><h2>Authentication is not implemented</h2><p>This backend has no login, registration, SMS verification, session, or profile endpoint. Do not enter real credentials on this prototype.</p></section></Page>}

function Admin(){return <Page title="Administration"><div className="stats"><Stat icon={<BarChart3/>} value={0} label="Statistics unavailable" tone="red"/><Stat icon={<Users/>} value={0} label="User management unavailable"/><Stat icon={<Ambulance/>} value={0} label="Unit management unavailable"/></div><div className="notice"><LockKeyhole/><div><b>Backend endpoints required</b><p>No aggregate statistics, audit log, CSV export, authentication, user management, or unit management API exists. Live call counts and dispatch actions above are real backend integrations.</p></div></div></Page>}

function Doctor(){
  const specialty='General Medicine'; const [messages,setMessages]=useState<ChatMessage[]>([]); const [text,setText]=useState(''); const [error,setError]=useState('')
  useEffect(()=>{chatApi.history(specialty).then(setMessages).catch(e=>setError(e.message))},[])
  const send=async()=>{if(!text.trim())return;try{await chatApi.send(specialty,text);setText('');setMessages(await chatApi.history(specialty))}catch(e:any){setError(e.message)}}
  return <Page title="Medical assistance"><div className="medical"><aside className="panel"><h2>Specialists</h2>{['General Medicine','Cardiology','Neurology','Traumatology'].map((s,i)=><button className={i===0?'selected':''} key={s}><HeartPulse/><span>{s}<small>{i===0?'Available':'Reference information only'}</small></span></button>)}</aside><section className="chat panel"><div className="chat-head"><HeartPulse/><div><b>{specialty}</b><small>AI assistant · not a medical diagnosis</small></div></div><div className="messages">{messages.map(m=><div className={`message ${m.sender==='AI'?'ai':''}`} key={m.id}>{m.text}</div>)}</div><ErrorBox text={error}/><div className="composer"><input value={text} onChange={e=>setText(e.target.value)} onKeyDown={e=>e.key==='Enter'&&send()} placeholder="Describe symptoms..."/><button onClick={send}>Send</button></div></section></div></Page>
}

function ActiveCall(){
  const id=Number(location.pathname.split('/').pop()); const [data,setData]=useState<CallDetail>(); const [error,setError]=useState('')
  const load=()=>callsApi.detail(id).then(setData).catch(e=>setError(e.message))
  useEffect(()=>{load();const i=setInterval(load,5000);return()=>clearInterval(i)},[id])
  const action=(fn:(id:number)=>Promise<unknown>)=>fn(id).then(load).catch((e:any)=>setError(e.message))
  return <Page title={`Emergency #${id}`}><ErrorBox text={error}/>{data&&<div className="active-layout"><section className="panel status-panel"><span className="live"><i/> {data.call.status}</span><h2>{data.call.text}</h2><p>{data.call.address || `${data.call.lat}, ${data.call.lng}`}</p><div className="eta"><Navigation/><div><strong>{data.etaMinutes} min</strong><small>Estimated arrival</small></div></div>{data.unit&&<div className="unit"><Ambulance/><div><b>{data.unit.name}</b><small>{data.unit.crew} · {data.unit.plate}</small></div></div>}<div className="action-row"><button className="secondary" onClick={()=>action(callsApi.cancel)}>Cancel emergency</button>{data.call.status==='NEW'&&<button className="primary" onClick={()=>action(callsApi.assign)}>Assign unit</button>}{data.call.status==='ENROUTE'&&<button className="primary" onClick={()=>action(callsApi.arrive)}>Mark arrived</button>}{data.call.status==='ARRIVED'&&<button className="primary" onClick={()=>action(callsApi.done)}>Complete</button>}</div></section><section className="panel map-panel"><Map marks={[data.call]} unit={data.unit}/></section></div>}</Page>
}

function Map({marks=[],unit}:{marks?:EmergencyCall[];unit?:any}){const center:[number,number]=marks[0]?[marks[0].lat,marks[0].lng]:[41.2995,69.2401];return <MapContainer center={center} zoom={13} scrollWheelZoom><TileLayer attribution='&copy; OpenStreetMap' url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'/>{marks.map(c=><Marker position={[c.lat,c.lng]} key={c.id}><Popup>Emergency #{c.id}<br/>{c.text}</Popup></Marker>)}{unit&&<Marker position={[unit.lat,unit.lng]}><Popup>{unit.name}</Popup></Marker>}</MapContainer>}

export default function App(){return <Shell/>}
