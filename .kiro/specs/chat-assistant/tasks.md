# Implementation Plan - Chat Assistant for Worky

- [x] 1. Set up core infrastructure and database schema
  - Create database migration for `chat_messages`, `chat_audit_logs`, and `reminders` tables
  - Add indexes for performance (session_id, user_id, timestamp)
  - Update `api/requirements.txt` with new dependencies (openai, redis, tiktoken, prometheus-client)
  - Create configuration settings in `api/app/core/config.py` for LLM, Redis, and chat parameters
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 2. Implement data models and schemas
  - Create SQLAlchemy models for `ChatMessage`, `ChatAuditLog`, and `Reminder` in `api/app/models/`
  - Create Pydantic schemas for chat requests/responses in `api/app/schemas/chat.py`
  - Define intent types, action types, and entity types as enums
  - Create schema for session data structure
  - _Requirements: 1.4, 4.1, 4.2, 4.3, 4.4, 7.1, 7.2, 7.3, 7.4, 7.5, 10.2, 10.3_

- [x] 3. Build session management service
  - Create `api/app/services/session_service.py` with Redis integration
  - Implement session creation, retrieval, and expiration (30-minute TTL)
  - Implement conversation context storage (last 10 messages)
  - Add entity resolution from conversation history
  - Create session cleanup for expired sessions
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 4. Implement intent classification service
  - Create `api/app/services/intent_classifier.py`
  - Implement regex patterns for entity extraction (project IDs, task IDs, dates)
  - Build intent type detection (QUERY, ACTION, NAVIGATION, REPORT, CLARIFICATION)
  - Add confidence scoring for intent classification
  - Implement fallback to LLM for ambiguous queries
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 7.2, 7.3_

- [x] 5. Build data retrieval service with RBAC
  - Create `api/app/services/data_retriever.py`
  - Implement client-level filtering (user.client_id enforcement)
  - Add project-level access verification
  - Build query methods for tasks, projects, bugs, user stories by various filters
  - Implement aggregate queries for statistics and reports
  - Add soft-delete filtering (is_deleted=False) to all queries
  - _Requirements: 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 6. Implement LLM service integration
  - Create `api/app/services/llm_service.py` with OpenAI client
  - Implement prompt template with retrieved data injection
  - Add response parsing and structured output extraction
  - Implement timeout handling (30 seconds)
  - Add error handling for LLM unavailability with fallback responses
  - Implement token counting and usage tracking
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 5.3, 5.4_

- [x] 7. Build action handler service
  - Create `api/app/services/action_handler.py`
  - Implement VIEW_ENTITY action (generate deep links)
  - Implement SET_REMINDER action with validation
  - Implement UPDATE_STATUS action with permission checks
  - Implement CREATE_COMMENT action
  - Implement LINK_COMMIT action
  - Implement SUGGEST_REPORT action
  - Add action validation and permission enforcement
  - Reject destructive actions (delete, role changes) with clear error messages
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 2.5_

- [x] 8. Implement audit logging service
  - Create `api/app/services/audit_service.py`
  - Implement PII masking for emails, phones, and names
  - Create audit log entry creation with all required fields
  - Add batch logging for performance
  - Implement audit log querying for admin dashboard
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 9. Build rate limiting middleware
  - Create `api/app/middleware/chat_rate_limit_middleware.py`
  - Implement token bucket algorithm using Redis
  - Set limits: 60 req/min, 1000 req/hour per user
  - Add burst allowance (10 requests)
  - Return 429 status with retry-after header when limit exceeded
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 10. Create main chat service orchestrator
  - Create `api/app/services/chat_service.py` as main orchestrator
  - Integrate all services (session, intent, retriever, LLM, action, audit)
  - Implement end-to-end query processing flow
  - Add error handling for each service layer
  - Implement response formatting with UI action metadata
  - Add request ID generation and tracking
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 11. Implement chat API endpoints
  - Create `api/app/api/v1/endpoints/chat.py`
  - Implement POST /api/v1/chat endpoint with authentication
  - Implement GET /api/v1/chat/history/{session_id} endpoint
  - Implement DELETE /api/v1/chat/session/{session_id} endpoint
  - Implement GET /api/v1/chat/health endpoint
  - Add request validation and error responses
  - Register endpoints in `api/app/api/v1/router.py`
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 12. Add Prometheus metrics
  - Create `api/app/services/chat_metrics.py`
  - Implement request counter by intent type and status
  - Add request duration histogram
  - Add LLM call duration histogram
  - Add error counter by error type
  - Add rate limit exceeded counter
  - Add active sessions gauge
  - Add actions executed counter by action type
  - Integrate metrics into chat service
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 13. Build CRUD operations for reminders
  - Create `api/app/crud/crud_reminder.py`
  - Implement create, read, update, delete operations
  - Add query methods for user reminders and pending reminders
  - Implement reminder notification logic (background job or webhook)
  - _Requirements: 3.2, 3.3, 3.4_

- [x] 14. Create frontend chat widget component
  - Create `ui/src/components/chat/ChatWidget.tsx` as floating widget
  - Implement chat message display with user/assistant roles
  - Add input field with send button
  - Implement typing indicator during LLM processing
  - Add error message display
  - Create collapsible/expandable widget UI
  - _Requirements: 1.4, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 15. Implement chat API client in frontend
  - Create `ui/src/services/chatApi.ts`
  - Implement sendMessage function with JWT token
  - Implement getHistory function
  - Implement clearSession function
  - Add error handling and retry logic
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 16. Build rich response rendering components
  - Create `ui/src/components/chat/MessageCard.tsx` for entity cards
  - Create `ui/src/components/chat/ActionButton.tsx` for clickable actions
  - Create `ui/src/components/chat/DataTable.tsx` for tabular results
  - Implement deep link navigation to entity detail pages
  - Add support for rendering charts/visualizations
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 17. Implement session management in frontend
  - Create `ui/src/contexts/ChatContext.tsx` for session state
  - Implement session ID generation and persistence
  - Add conversation history management
  - Implement session expiration handling
  - Add context reset on user logout
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 18. Add chat widget to main application layout
  - Update `ui/src/App.tsx` to include ChatWidget
  - Add chat icon button in header/footer for widget toggle
  - Implement widget positioning (bottom-right corner)
  - Add keyboard shortcut to open chat (Ctrl+K or Cmd+K)
  - Ensure widget is accessible on all authenticated pages
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]* 19. Write integration tests for chat flow
  - Create `api/tests/integration/test_chat_workflow.py`
  - Test end-to-end query processing (query → response)
  - Test multi-turn conversation with context retention
  - Test action execution and confirmation
  - Test RBAC enforcement (client and project access)
  - Test rate limiting behavior
  - Test error scenarios (invalid query, LLM timeout, access denied)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 6.1, 6.2_

- [ ]* 20. Write unit tests for core services
  - Create `api/tests/services/test_intent_classifier.py`
  - Create `api/tests/services/test_data_retriever.py`
  - Create `api/tests/services/test_action_handler.py`
  - Create `api/tests/services/test_session_service.py`
  - Test intent classification accuracy
  - Test entity extraction
  - Test RBAC filtering in data retriever
  - Test action permission validation
  - Test session context management
  - _Requirements: 1.1, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 7.1, 7.2, 7.3_

- [ ]* 21. Create API documentation
  - Update OpenAPI schema with chat endpoints
  - Add example requests and responses to endpoint docstrings
  - Create `api/CHAT_API_GUIDE.md` with usage examples
  - Document intent types and supported queries
  - Document action types and permissions
  - Document error codes and troubleshooting
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ]* 22. Set up monitoring dashboards
  - Create Prometheus queries for chat metrics
  - Build Grafana dashboard for usage metrics (queries/hour, active users)
  - Build Grafana dashboard for performance metrics (latency, error rate)
  - Build Grafana dashboard for security metrics (failed auth, rate limits)
  - Add alerting rules for high error rates and slow responses
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 23. Implement optional vector search for documents
  - Install and configure pgvector extension in PostgreSQL
  - Create embeddings table for long-form content
  - Implement embedding generation for descriptions and comments
  - Add semantic search to data retriever
  - Create background job for embedding updates
  - _Requirements: 1.3, 9.1, 9.2, 9.3_

- [ ]* 24. Add admin dashboard for chat analytics
  - Create `ui/src/pages/ChatAnalyticsPage.tsx`
  - Display usage statistics (total queries, top users, popular intents)
  - Show audit log viewer with filters
  - Add export functionality for audit logs
  - Display performance metrics and error trends
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3_
