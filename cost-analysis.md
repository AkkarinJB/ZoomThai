# Part D — Cost, Scale, and PDPA

## Cost Analysis (640,000 pages, 440,000 queries per month)

| Component | Option 1 (OpenAI) | Option 2 (Google Gemini) | Option 3 (Open Source / Local) |
| --- | --- | --- | --- |
| **LLM (RAG)** | GPT-4o-mini (~$20/mo) | Gemini 1.5 Flash (Free Tier / ~$10/mo) | Llama 3 (Hosted on Groq, ~$30/mo) |
| **VLM (Extraction)** | GPT-4o (~$1,200/mo) | Gemini 1.5 Flash (~$80/mo) | LLaVA (Self-hosted on AWS g4dn, ~$400/mo) |
| **Embeddings** | text-embedding-3-small (~$5/mo) | text-embedding-004 (~$2/mo) | BGE-M3 (Self-hosted) |
| **Vector Store** | Pinecone (~$70/mo) | PostgreSQL + pgvector (Self-hosted, ~$20/mo) | Qdrant Cloud (~$30/mo) |

**Recommendation:** **Option 2 (Google Gemini + pgvector)**
Gemini 1.5 Flash provides exceptional multi-modal capabilities at a fraction of the cost of GPT-4o, making the VLM fallback strategy economically viable at 640k pages/month. `pgvector` keeps the stack simple and unified.

## Scale Bottleneck (Growing to 50 Agencies)
- **Bottleneck:** The VLM Fallback Pipeline and Embedding Pipeline.
- **Why:** 4x scale means ~2.5 million pages/month. Sync processing will timeout or hit API rate limits.
- **Redesign:** Introduce **RabbitMQ or AWS SQS**. The orchestrator should push extraction jobs to a queue. Worker nodes will scale horizontally to process PDFs and insert results asynchronously.

## PDPA Considerations
- **Redistribution:** Government procurement is public data, but personal data (phone numbers, officer names) is incidental and not the core value of TOR documents.
- **Masking:** PII should be masked using NLP Named Entity Recognition (NER) *before* chunking and indexing to prevent LLMs from inadvertently outputting personal phone numbers.
- **Open Data License:** Thailand's Open Government Data License permits reuse, but PDPA supersedes it regarding PII. Therefore, masking is legally required.
