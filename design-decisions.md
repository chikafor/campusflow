Ticket Loading and Startup Safety
CampusFlow loads ticket data once during application startup. 
If loading fails because the stored data is malformed or invalid, the application reports a startup error and exits with a nonzero status.
It does not continue with an empty ticket collection, preventing normal application operations from accidentally overwriting the invalid data.
Runtime reloads are not currently supported. 
If runtime reload functionality is introduced later, its error-handling and data-preservation behavior must be tested separately.
