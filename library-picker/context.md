# Project: Tinybox POS

A point-of-sale (POS) web app for small retail shops — cafés, indie bookstores, market stalls.

## Stack

- **Backend:** Node.js 20, Express 4, TypeScript (strict mode)
- **Database:** PostgreSQL via Prisma
- **Frontend:** React 18 + Vite, TailwindCSS
- **Auth:** session-based, `express-session` + Postgres store
- **Tests:** Vitest

## Features (in scope)

- Product catalog (CRUD) with categories, prices, stock counts
- Cart + checkout with cash and card payments
- Receipt printing (thermal printer over USB or network)
- Barcode scanning at the till
- Daily sales reports + simple charts on an admin dashboard
- Offline-first cart: continue selling if the network drops, sync when it comes back

## Constraints

- Small-business budget — prefer free, permissive licenses (MIT/Apache/BSD)
- Total frontend bundle target: < 500 kB gzipped
- Cashier UI must be keyboard-driven (touchscreen + USB barcode scanner)
- Must run on cheap hardware (4 GB RAM mini-PCs)

## Already chosen — do not recommend replacements

Express, Prisma, React, Vite, TailwindCSS, Vitest.
