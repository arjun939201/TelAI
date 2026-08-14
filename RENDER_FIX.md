
## Persistent chat-time learning

For production chat-time learning, attach a Render PostgreSQL database and expose its connection string as `DATABASE_URL`. The app automatically initializes its `melimi_learning` table. Do not rely on the local SQLite file for production persistence because an application filesystem can be replaced during deploy/restart.
