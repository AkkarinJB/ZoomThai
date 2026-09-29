import { serve } from '@hono/node-server'
import { Hono } from 'hono'
import { cors} from 'hono/cors'
import { zValidator } from '@hono/zod-validator'
import { db } from './db/index.js';
import { sql } from 'drizzle-orm';
import { SearchReqSchema, AskReqSchema } from './schema.js'

const app = new Hono()
app.use('/*' , cors())

app.get('/health', async (c) => {
  let dbStatus = 'disconnected';
  try {
    const result = await db.execute(sql`SELECT 1`);
    if (result) dbStatus = 'connected';
  } catch (error) {
    console.error('Database connection failed:', error);
  }

  return c.json({
    status: 'ok',
    database: dbStatus,
    version: '0.1.0'
  });
});

app.post('/search', zValidator('json', SearchReqSchema), async (c) => {
  const data = c.req.valid('json');
  console.log(`[Search] Query: ${data.query} | Limit: ${data.limit}`);
  // TODO: Implement PostgreSQL query
  const mockResponse = {
    total: 1,
    query_time_ms: 12.5,
    items: [
      {
        id: "PEA-TDDP.2(A)-082/2564",
        title: "Mock Project Title based on: " + data.query,
        agency: data.filters?.agency?.[0] || "PEA",
        budget_amount: 12500000.00,
        method: data.filters?.method || "e-bidding",
        submission_deadline: "2021-09-15T16:30:00+07:00",
        relevance_score: 0.99
      }
    ]
  };

  return c.json(mockResponse);
});

app.post('/ask', zValidator('json', AskReqSchema), async (c) => {
  const data = c.req.valid('json');
  console.log(`[Ask] Question: ${data.question}`);
  // TODO: Implement LLM query
  const mockResponse = {
    answer: "นี่คือคำตอบจำลองจากระบบ (Mock Answer)",
    citations: [
      {
        announcement_id: "PEA-TDDP.2(A)-082/2564",
        text_snippet: "ข้อความจำลองจากเอกสาร",
        page_number: 1
      }
    ],
    confidence: 0.85,
    reasoning: "เนื่องจากฐานข้อมูลยังไม่ได้เชื่อมต่อ",
    unable_reason: null
  };

  return c.json(mockResponse);
});

const PORT = 3000
console.log('API SERVER STARTING ON PORT ' + PORT)

serve({
  fetch: app.fetch,
  port: PORT
})
