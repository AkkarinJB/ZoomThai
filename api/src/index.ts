import { serve } from '@hono/node-server'
import { Hono } from 'hono'
import { cors} from 'hono/cors'
import { zValidator } from '@hono/zod-validator'
import { db } from './db/index.js';
import { sql, eq, or, ilike, and, gte, lte, inArray  } from 'drizzle-orm';
import { SearchReqSchema, AskReqSchema } from './schema.js'
import { announcements, procurementItems } from './db/schema.js';
import { GoogleGenAI, Type } from '@google/genai';
import 'dotenv/config';

const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) { console.error("GEMINI_API_KEY is missing!"); process.exit(1); }
const ai = new GoogleGenAI({ apiKey });
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
  const startTime = performance.now();
  console.log(`[Search] Query: ${data.query} | Limit: ${data.limit}`);
  try {
    const conditions = [];

    if (data.query) {
      conditions.push(or(ilike(announcements.title, `%${data.query}%`), ilike(announcements.id, `%${data.query}%`)));
    }

    if (data.filters?.agency && data.filters.agency.length > 0) {
      conditions.push(inArray(announcements.agency, data.filters.agency));
    }

    if (data.filters?.method) {
      conditions.push(eq(announcements.method, data.filters.method));
    }

    if (data.filters?.budget_min !== undefined) {
      conditions.push(gte(announcements.budgetAmount, data.filters.budget_min.toString()));
    }
    if (data.filters?.budget_max !== undefined) {
      conditions.push(lte(announcements.budgetAmount, data.filters.budget_max.toString()));
    }

    const items = await db
      .select()
      .from(announcements)
      .where(conditions.length > 0 ? and(...conditions) : undefined)
      .limit(data.limit)
      .offset(data.offset);

    const queryTime = performance.now() - startTime;
    
    return c.json({
      total: items.length, 
      query_time_ms: Number(queryTime.toFixed(2)),
      items: items
    });
    } catch (error) {
    console.error('Search query failed:', error);
    return c.json({ error: 'Internal Server Error' }, 500);
  }
});


app.get('/announcements/:id/items', async (c) => {
  const announcementId = c.req.param('id');
  
  try {
    const items = await db
      .select()
      .from(procurementItems)
      .where(eq(procurementItems.announcementId, announcementId));
      
    return c.json({
      announcement_id: announcementId,
      total_items: items.length,
      items: items
    });
  } catch (error) {
    console.error('Fetch items failed:', error);
    return c.json({ error: 'Internal Server Error' }, 500);
  }
});


app.post('/ask', zValidator('json', AskReqSchema), async (c) => {
  const data = c.req.valid('json');
  console.log(`[Ask] Question: ${data.question}`);
  
  try {
    const embedResponse = await ai.models.embedContent({
      model: 'gemini-embedding-001',
      contents: data.question,
    });
    
    const queryVector = embedResponse?.embeddings?.[0]?.values;
    if (!queryVector) {
      return c.json({
        answer: "ไม่สามารถแปลงข้อความคำถามเป็น Vector ได้ในขณะนี้",
        citations: [],
        confidence: 0.0,
        reasoning: "Embedding generation failed",
        unable_reason: "EMBEDDING_ERROR"
      }, 500);
    }
    const vectorString = `[${queryVector.join(',')}]`;

    // Hybrid search: Vector + FTS
    const similarChunksRaw = await db.execute(sql`
      SELECT 
        announcement_id as "announcementId", 
        id as "pageRef", 
        content as "content"
      FROM document_chunks
      ORDER BY (
        (1 - (embedding <=> ${vectorString})) + 
        ts_rank(to_tsvector('english', content), plainto_tsquery('english', ${data.question}))
      ) DESC
      LIMIT 5
    `);
    const similarChunks = (Array.isArray(similarChunksRaw) ? similarChunksRaw : (similarChunksRaw as any).rows || []) as any[];

    if (similarChunks.length === 0) {
      return c.json({
        answer: null, reason: "insufficient_evidence",
        citations: [],
        confidence: 0.0,
        reasoning: "ไม่พบข้อมูลบริบทที่เกี่ยวข้องในฐานข้อมูล",
        unable_reason: "NO_CONTEXT"
      });
    }

    const contextTexts = similarChunks.map(chunk => chunk.content || chunk.chunkText).join('\n\n---\n\n');
    const prompt = `
      คุณคือผู้ช่วยตอบคำถามเกี่ยวกับเอกสารจัดซื้อจัดจ้างภาครัฐ (TOR)
      จงตอบคำถามต่อไปนี้โดยอ้างอิงจาก "ข้อมูลบริบท" ที่กำหนดให้เท่านั้น
      หากข้อมูลบริบทไม่มีคำตอบ ให้ตอบตามตรงว่า "ไม่พบข้อมูลที่ระบุในเอกสาร" ห้ามเดาหรือแต่งข้อมูลขึ้นมาเอง

      ข้อมูลบริบท:
      ${contextTexts}

      คำถาม: ${data.question}
    `;

    const chatResponse = await ai.models.generateContent({
      model: 'gemini-3.8-flash',
      contents: prompt,
      config: {
        tools: [{
        functionDeclarations: [
          {
            name: "execute_sql",
            description: "Execute a SELECT SQL query on the procurement database. Tables: procurement_announcements (announcement_id, agency, title, method, fiscal_year, budget_amount), procurement_items (id, announcement_id, description, quantity, unit_price_estimate, total_price_estimate).",
            parameters: {
              type: Type.OBJECT,
              properties: {
                query: {
                  type: Type.STRING,
                  description: "A valid PostgreSQL SELECT query.",
                },
              },
              required: ["query"],
            }
          }
        ]
      }]
      }
    });

    let finalAnswer = chatResponse.text;
    if (chatResponse.text && chatResponse.text.includes("ไม่พบข้อมูล")) { finalAnswer = ""; }
    let methodUsed = "hybrid_search";
    
    if (chatResponse.functionCalls && chatResponse.functionCalls.length > 0) {
      const call = chatResponse.functionCalls[0];
      if (call.name === "execute_sql") {
        methodUsed = "sql_aggregation";
        try {
          const sqlRes = await db.execute(sql.raw((call.args as any)?.query || ""));
          const secondResponse = await ai.models.generateContent({
            model: 'gemini-3.8-flash',
            contents: [
              { role: 'user', parts: [{ text: prompt }] },
              { role: 'model', parts: [{ functionCall: call }] },
              { role: 'user', parts: [{ text: `Result from execute_sql: ` + JSON.stringify(sqlRes).substring(0, 3000) }] }
            ]
          });
          finalAnswer = secondResponse.text;
        } catch (e) {
          console.error("INNER CATCH ERROR:", e);

          finalAnswer = "เกิดข้อผิดพลาดในการดึงข้อมูลจากฐานข้อมูล (SQL Error)";
        }
      }
    }

    return c.json({
      answer: finalAnswer === "" ? null : finalAnswer,
      reason: finalAnswer === "" ? "insufficient_evidence" : undefined,
      citations: similarChunks.map(chunk => ({
        announcement_id: chunk.announcementId || "UNKNOWN",
        text_snippet: chunk.content.substring(0, 150) + "...",
        page_number: parseInt((chunk.pageRef || "1").replace(/\D/g, "") || "1") 
      })),
      confidence: 0.85,
      reasoning: "ประมวลผลคำตอบจาก Vector Search และโมเดล Gemini สำเร็จ",
      unable_reason: null
    });
    } catch (error) {
    console.error('RAG Pipeline Error:', error);
    return c.json({ error: 'Internal Server Error' }, 500);
  }
});

const PORT = 3000
console.log('API SERVER STARTING ON PORT ' + PORT)

serve({
  fetch: app.fetch,
  port: PORT
})
