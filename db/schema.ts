import { sqliteTable, text, integer, index } from 'drizzle-orm/sqlite-core';
export const courseOrders = sqliteTable('course_orders', {
 id: text('id').primaryKey(),
 userId: text('user_id').notNull(),
 razorpayOrderId: text('razorpay_order_id').unique(),
 paymentId: text('payment_id').unique(),
 amount: integer('amount').notNull(),
 currency: text('currency').notNull(),
 status: text('status').notNull(),
 createdAt: integer('created_at').notNull(),
 verifiedAt: integer('verified_at'),
}, table => [index('orders_user_created').on(table.userId, table.createdAt)]);

export const emailPurchases = sqliteTable('email_purchases', {
 paymentId:text('payment_id').primaryKey(),email:text('email'),status:text('status').notNull(),amount:integer('amount').notNull(),createdAt:integer('created_at').notNull(),
},t=>[index('email_purchase_lookup').on(t.email,t.status)]);
export const emailLinks = sqliteTable('email_links', {
 id:text('id').primaryKey(),reason:text('reason').notNull().unique(),email:text('email').notNull(),tokenHash:text('token_hash').notNull().unique(),createdAt:integer('created_at').notNull(),expiresAt:integer('expires_at').notNull(),usedAt:integer('used_at'),sentAt:integer('sent_at'),lang:text('lang').notNull(),
});
export const emailSessions = sqliteTable('email_sessions', {
 tokenHash:text('token_hash').primaryKey(),email:text('email').notNull(),expiresAt:integer('expires_at').notNull(),
});
export const emailLimits = sqliteTable('email_limits', {key:text('key').primaryKey(),bucket:integer('bucket').notNull(),count:integer('count').notNull()});
