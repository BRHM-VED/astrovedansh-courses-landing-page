CREATE TABLE `email_limits` (
	`key` text PRIMARY KEY NOT NULL,
	`bucket` integer NOT NULL,
	`count` integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE `email_links` (
	`id` text PRIMARY KEY NOT NULL,
	`reason` text NOT NULL,
	`email` text NOT NULL,
	`token_hash` text NOT NULL,
	`created_at` integer NOT NULL,
	`expires_at` integer NOT NULL,
	`used_at` integer,
	`sent_at` integer,
	`lang` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `email_links_reason_unique` ON `email_links` (`reason`);--> statement-breakpoint
CREATE UNIQUE INDEX `email_links_token_hash_unique` ON `email_links` (`token_hash`);--> statement-breakpoint
CREATE TABLE `email_purchases` (
	`payment_id` text PRIMARY KEY NOT NULL,
	`email` text,
	`status` text NOT NULL,
	`amount` integer NOT NULL,
	`created_at` integer NOT NULL
);
--> statement-breakpoint
CREATE INDEX `email_purchase_lookup` ON `email_purchases` (`email`,`status`);--> statement-breakpoint
CREATE TABLE `email_sessions` (
	`token_hash` text PRIMARY KEY NOT NULL,
	`email` text NOT NULL,
	`expires_at` integer NOT NULL
);
