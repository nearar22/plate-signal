import test from"node:test";import assert from"node:assert/strict";
import{clean,short,findingLabel,findingTone,remaining,canCorrect}from"../src/model.mjs";
test("cleans bigint values",()=>assert.deepEqual(clean({a:3n,b:[4n]}),{a:3,b:[4]}));
test("maps every finding to a distinct signal",()=>{assert.equal(findingLabel("CONFLICT"),"CLAIM CONFLICT");assert.equal(findingTone("ALIGNED"),"aligned");assert.equal(findingTone("SOURCE_UNAVAILABLE"),"offline")});
test("correction is owner bound and time bounded",()=>{const r={status:"REVIEWED",owner:"0xabc",correction_used:false,correction_deadline:200};assert.equal(canCorrect(r,"0xAbC",100),true);assert.equal(canCorrect(r,"0xdef",100),false);assert.equal(canCorrect(r,"0xabc",201),false)});
test("formats identifiers and time",()=>{assert.equal(short("12345678901234567890",4),"1234…7890");assert.equal(remaining(3700,100),"1h 00m")});

