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
