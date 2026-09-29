import { z } from 'zod';

export const SearchReqSchema = z.object({
    query: z.string().min(1, { message: 'Query is required' }),
    filters: z.object({
        agency: z.array(z.string()).optional(),
        date_form: z.string().optional(),
        date_to: z.string().optional(),
        budget_min: z.number().optional(),
        budget_max: z.number().optional(),
        method: z.enum(["e-bidding", "สอบราคา", "คัดเลือก", "เฉพาะเจาะจง"]).optional(),

    }).optional(),
    limit: z.number().int().min(1).max(100).default(20),
    offset: z.number().int().min(0).default(0)
});

export const AskReqSchema = z.object({
    question: z.string().min(1, "Question is required"),
    top_k: z.number().int().min(1).max(20).default(5),
    model: z.string().optional()
})

export type SearchReq = z.infer<typeof SearchReqSchema>;
export type AskReq = z.infer<typeof AskReqSchema>;