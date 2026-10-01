import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function runEval() {
  const questionsPath = path.join(__dirname, 'eval_questions.json');
  const questions = JSON.parse(fs.readFileSync(questionsPath, 'utf-8'));
  
  let correct = 0;
  console.log('Starting Evaluation...');
  
  const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));
  for (const q of questions) {
    await sleep(15000);
    console.log(`\nQuestion: ${q.question}`);
    console.log(`Type: ${q.type}`);
    console.log(`Expected: ${q.expected_answer}`);
    
    try {
      const res = await fetch('http://localhost:3000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q.question, top_k: 5 })
      });
      const data = await res.json();
      console.log(`Actual Answer: ${data.answer}`);
      console.log(`Sources: ${data.citations ? data.citations.length : 0}`);
      
      if (q.type === 'unanswerable' && (!data.answer || data.unable_reason)) {
        correct++;
        console.log('Pass');
      } else if (q.type !== 'unanswerable' && data.answer && !data.unable_reason) {
        correct++;
        console.log('Pass');
      } else {
        console.log('Fail');
      }
    } catch (e) {
      console.error(`Error: ${e}`);
    }
  }
  
  const accuracy = correct / questions.length;
  console.log(`\nAccuracy: ${accuracy * 100}%`);
  if (accuracy >= 0.65) {
    console.log('PASSED THRESHOLD (>65%)');
  } else {
    console.log('FAILED THRESHOLD');
  }
}

runEval();
