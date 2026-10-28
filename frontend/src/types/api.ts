export type CallStatus = 'NEW'|'ENROUTE'|'ARRIVED'|'DONE'|'CANCELLED'
export interface EmergencyCall {
  id:number; fullName?:string; phone?:string; address?:string; lat:number; lng:number;
  accuracy?:number; text:string; services?:string; severity?:'HIGH'|'MEDIUM'|'LOW';
  aiSummary?:string; status:CallStatus; unitId?:number|null; createdAt:string; arrivedAt?:string|null
}
export interface Unit { id:number; name:string; service:string; lat:number; lng:number; busy:boolean; crew?:string; plate?:string }
export interface CallDetail { call:EmergencyCall; unit:Unit|null; etaMinutes:number }
export interface ChatMessage { id:number; specialty:string; sender:'PATIENT'|'DOCTOR'|'AI'; text:string; createdAt:string }
export interface NewCall { fullName:string; phone:string; address:string; lat:number; lng:number; accuracy:number|null; text:string }
