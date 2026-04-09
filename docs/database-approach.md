# Database Approach

We will use SQLite with a simple relational model for users, boards, columns, and cards. Each user has exactly one board for the MVP, enforced by a unique constraint on boards.user_id.

Ordering is stored by integer position fields on columns and cards, with unique indexes scoped to their parent (board or column). This keeps ordering deterministic and easy to update.

Timestamps are stored as ISO-8601 text values. The backend will initialize tables if they do not exist and seed a default board per user when needed.
