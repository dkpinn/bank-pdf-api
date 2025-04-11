# Bank PDF Parser (FastAPI + Vercel)

This project parses bank statement PDFs and extracts transactions into CSV format.

## Features

- Upload PDF bank statements
- Extracts DATE, DESCRIPTION, AMOUNT, BALANCE
- Merges multi-line descriptions
- CORS enabled for frontend apps (e.g. Lovable.dev)
- Returns a downloadable CSV

## How to Deploy on Vercel

1. Create a GitHub repo and push these files.
2. Go to [https://vercel.com](https://vercel.com) and sign in.
3. Click **New Project**, import your GitHub repo.
4. Vercel will auto-detect and deploy the FastAPI backend.
5. You’ll get a public URL like `https://your-app.vercel.app/parse`

## How to Use with Lovable.dev

- Set your upload button to send a `POST` request to `/parse`
- Send the file as `multipart/form-data` with field name `file`
- When response arrives, download the returned CSV