import { sql } from 'drizzle-orm';
import { customType } from 'drizzle-orm/pg-core';
import { pgTable, 
         varchar, 
         text, 
         timestamp, 
         integer, 
         numeric, 
         index, 
         serial,
} from 'drizzle-orm/pg-core';

const vector = customType<{ data: number[]; driverData: string }>({
  dataType() {
    return 'vector(768)';
  },
  toDriver(value: number[]): string {
    return `[${value.join(',')}]`;
  },
});

export const announcements = pgTable('procurement_announcements', {
  id: varchar('announcement_id', { length: 50 }).primaryKey(),
  agency: varchar('agency', { length: 20 }).notNull(),
  title: text('title').notNull(),
  method: varchar('method', { length: 50 }),
  fiscalYear: integer('fiscal_year'),
  budgetAmount: numeric('budget_amount', { precision: 15, scale: 2 }),
  submissionDeadline: timestamp('submission_deadline', { withTimezone: true }),
  torPdfPath: text('tor_pdf_path'),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
}, (table) => {
  return {
    agencyIdx: index('idx_agency').on(table.agency),
    budgetIdx: index('idx_budget').on(table.budgetAmount),
  };
});

export const procurementItems = pgTable('procurement_items', {
  id: serial('id').primaryKey(),
  announcementId: varchar('announcement_id', { length: 50 }).references(() => announcements.id, { onDelete: 'cascade' }),
  lineNo: integer('line_no'),
  itemCode: varchar('item_code', { length: 50 }),
  description: text('description'),
  quantity: numeric('quantity', { precision: 10, scale: 2 }),
  unit: varchar('unit', { length: 50 }),
  unitPriceEstimate: numeric('unit_price_estimate', { precision: 15, scale: 2 }),
  totalPriceEstimate: numeric('total_price_estimate', { precision: 15, scale: 2 }),
});

export const embeddings = pgTable('embeddings', {
  id: serial('id').primaryKey(),
  announcementId: varchar('announcement_id', { length: 50 }).references(() => announcements.id, { onDelete: 'cascade' }),
  pageRef: varchar('page_ref', { length: 20 }),
  chunkText: text('chunk_text'),
  embedding: vector('embedding'),
});

export const documentChunks = pgTable('document_chunks', {
  id: varchar('id', { length: 255 }).primaryKey(),
  announcementId: varchar('announcement_id', { length: 50 }).references(() => announcements.id, { onDelete: 'cascade' }),
  content: text('content').notNull(),
  embedding: vector('embedding'), 
});