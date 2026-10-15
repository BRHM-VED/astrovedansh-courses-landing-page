CREATE TABLE `course_orders` (
	`id` text PRIMARY KEY NOT NULL,
	`user_id` text NOT NULL,
	`razorpay_order_id` text,
	`payment_id` text,
	`amount` integer NOT NULL,
	`currency` text NOT NULL,
	`status` text NOT NULL,
	`created_at` integer NOT NULL,
	`verified_at` integer
);
--> statement-breakpoint
CREATE UNIQUE INDEX `course_orders_razorpay_order_id_unique` ON `course_orders` (`razorpay_order_id`);--> statement-breakpoint
CREATE UNIQUE INDEX `course_orders_payment_id_unique` ON `course_orders` (`payment_id`);--> statement-breakpoint
CREATE INDEX `orders_user_created` ON `course_orders` (`user_id`,`created_at`);