CREATE DATABASE n8n;
-- app_db is no longer needed if we use 'postgres' DB, but keeping it won't hurt.
-- Create the schema for the application
\c postgres
CREATE SCHEMA IF NOT EXISTS ai_dev;
SET search_path TO ai_dev;
CREATE TABLE IF NOT EXISTS public.daily_horoscopes (id SERIAL PRIMARY KEY, sign VARCHAR(50) NOT NULL, content TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
