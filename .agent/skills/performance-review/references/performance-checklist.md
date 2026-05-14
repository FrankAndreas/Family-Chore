# Performance & Scalability Standards Checklist

Evaluate the codebase against these core standards.

## 1. Database & Query Efficiency
- **N+1 Queries**: Are ORM relationships lazy-loaded inside loops? (Look for missing `joinedload` or `.populate()`).
- **Indexing**: Do frequent lookup columns, foreign keys, and filter parameters lack database indexes?
- **Data Fetching**: Are queries fetching `SELECT *` when only a few columns are needed?

## 2. API & Network Efficiency
- **Payload Size**: Are API responses returning large, unneeded nested objects?
- **Pagination**: Are list endpoints missing pagination, risking massive payloads as data grows?
- **Waterfall Requests**: Is the frontend making sequential dependent API calls when they could be parallelized?

## 3. Caching Strategies
- **Server-Side Caching**: Are computationally expensive endpoints or frequent static queries cached (e.g., Redis, memory)?
- **Client-Side Caching**: Are HTTP cache headers (`Cache-Control`, `ETag`) utilized for static assets and immutable data?

## 4. Asynchronous & Background Processing
- **Blocking Operations**: Are heavy operations (image processing, email sending, PDF generation) blocking the main web request thread?
- **Task Queues**: Are background workers (Celery, Bull, sidekiq) used effectively for long-running tasks?

## 5. Frontend Delivery & Rendering
- **Asset Optimization**: Are images optimized and served in modern formats? Are fonts subset?
- **Bundle Size**: Is tree-shaking effective? Are large third-party libraries bloating the main JS bundle?
- **Core Web Vitals**: Are there scripts blocking the main thread (First Input Delay)? Are layouts shifting dynamically (Cumulative Layout Shift)?
