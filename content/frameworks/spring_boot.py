"""Spring Boot exercises (Spring Boot 3.5+, Java 21). Original content; compile-checked by tools/check_frameworks.py."""
from dsl import problem, approach, file

SB = dict(pattern="spring-boot", time="—", space="—")

problem(
    id="sb-hello-endpoint",
    title="Your First REST Endpoint",
    difficulty="Easy",
    topics=["Spring Boot", "REST", "Records"],
    statement="""
    Create a `GET /api/hello` endpoint that takes an optional `name` query parameter (default `"world"`) and returns
    JSON like `{"message": "Hello, Ada!"}`. Use a Java record for the response body.
    """,
    examples=[("GET /api/hello?name=Ada", "200 {\"message\":\"Hello, Ada!\"}", None), ("GET /api/hello", "200 {\"message\":\"Hello, world!\"}", None)],
    hints=["`@RestController` returns data, serialised to JSON by Jackson.", "`@RequestParam(defaultValue = ...)` handles the optional name."],
    approaches=[approach(
        name="@RestController + record", **SB,
        idea="""
        A `@RestController` class handles web requests and returns objects that Spring turns into JSON. `@GetMapping` maps a URL path to a method, and `@RequestParam` reads a query parameter.

        Returning a small immutable `record` keeps the response shape explicit and type-safe.
        """,
        files=[file("HelloController.java", '''
            import org.springframework.web.bind.annotation.*;

            @RestController
            @RequestMapping("/api")
            public class HelloController {

                public record Greeting(String message) {}

                @GetMapping("/hello")
                public Greeting hello(@RequestParam(defaultValue = "world") String name) {
                    return new Greeting("Hello, " + name + "!");
                }
            }
        ''')],
        steps=[
            ("@RestController", "@RestController marks this class as a web controller whose return values become the response body, as JSON."),
            ("@RequestMapping", "@RequestMapping on the class gives every endpoint inside a common /api prefix."),
            ("record Greeting", "A record is a compact immutable data class. Jackson serialises its message field automatically."),
            ("@GetMapping", "@GetMapping maps HTTP GET requests for /api/hello to this method."),
            ("@RequestParam", "@RequestParam reads the name query parameter, falling back to world when it's missing."),
            ("return new Greeting", "We return a Greeting; Spring writes it as {\"message\": ...} with status 200."),
        ],
    )],
)

problem(
    id="sb-path-variables",
    title="Path Variables and 404s",
    difficulty="Easy",
    topics=["Spring Boot", "REST", "ResponseEntity"],
    statement="""
    Expose `GET /api/books/{id}` that returns the book with that id, or **404 Not Found** if it doesn't exist.
    Keep books in an in-memory map for now.
    """,
    examples=[("GET /api/books/1", "200 {\"id\":1,\"title\":\"Dune\"}", None), ("GET /api/books/99", "404 (empty body)", None)],
    hints=["`@PathVariable` binds the {id} segment.", "`ResponseEntity.of(Optional)` returns 404 for an empty Optional."],
    approaches=[approach(
        name="@PathVariable + ResponseEntity", **SB,
        idea="""
        `@PathVariable` pulls the id out of the URL. Looking the book up returns an `Optional`, and `ResponseEntity.of` converts it: a present value becomes 200 with a body, an empty one becomes 404.
        """,
        files=[file("BookController.java", '''
            import java.util.Map;
            import java.util.Optional;
            import org.springframework.http.ResponseEntity;
            import org.springframework.web.bind.annotation.*;

            @RestController
            @RequestMapping("/api/books")
            public class BookController {

                public record Book(long id, String title) {}

                private final Map<Long, Book> books = Map.of(1L, new Book(1, "Dune"), 2L, new Book(2, "Neuromancer"));

                @GetMapping("/{id}")
                public ResponseEntity<Book> byId(@PathVariable long id) {
                    return ResponseEntity.of(Optional.ofNullable(books.get(id)));
                }
            }
        ''')],
        steps=[
            ("Map.of(", "An immutable in-memory map stands in for a database for now."),
            ("@GetMapping(\"/{id}\")", "Curly braces in the path declare a variable segment called id."),
            ("@PathVariable", "@PathVariable converts that segment to a long and passes it in."),
            ("ResponseEntity.of", "ResponseEntity.of turns a present Optional into 200 OK with the book, and an empty one into 404 Not Found."),
        ],
    )],
)

problem(
    id="sb-validated-create",
    title="Validated Create Endpoint (201 Created)",
    difficulty="Easy",
    topics=["Spring Boot", "REST", "Validation"],
    statement="""
    Add `POST /api/users` that accepts `{"email": ..., "name": ...}`. Reject invalid input with **400** (email must be
    valid, name 2–50 characters). On success return **201 Created** with a `Location` header pointing to the new user.
    """,
    examples=[("POST /api/users {\"email\":\"ada@example.com\",\"name\":\"Ada\"}", "201 Location: /api/users/1", None),
              ("POST /api/users {\"email\":\"nope\",\"name\":\"A\"}", "400 Bad Request", "Both fields fail validation.")],
    hints=["Bean Validation annotations go on the record components.", "`@Valid` triggers validation before your method runs."],
    approaches=[approach(
        name="@Valid record + ResponseEntity.created", **SB,
        idea="""
        Put Bean Validation constraints such as `@Email` and `@Size` directly on the request record. Annotating the parameter with `@Valid` makes Spring validate it before your code runs and answer 400 automatically on failure.

        REST convention for creation is 201 with a Location header; `ServletUriComponentsBuilder` builds that URL from the current request.
        """,
        files=[file("UserController.java", '''
            import jakarta.validation.Valid;
            import jakarta.validation.constraints.Email;
            import jakarta.validation.constraints.NotBlank;
            import jakarta.validation.constraints.Size;
            import java.net.URI;
            import java.util.Map;
            import java.util.concurrent.ConcurrentHashMap;
            import java.util.concurrent.atomic.AtomicLong;
            import org.springframework.http.ResponseEntity;
            import org.springframework.web.bind.annotation.*;
            import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

            @RestController
            @RequestMapping("/api/users")
            public class UserController {

                public record CreateUser(@NotBlank @Email String email, @NotBlank @Size(min = 2, max = 50) String name) {}

                public record User(long id, String email, String name) {}

                private final Map<Long, User> users = new ConcurrentHashMap<>();
                private final AtomicLong ids = new AtomicLong();

                @PostMapping
                public ResponseEntity<User> create(@Valid @RequestBody CreateUser req) {
                    User user = new User(ids.incrementAndGet(), req.email(), req.name());
                    users.put(user.id(), user);
                    URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                            .path("/{id}").buildAndExpand(user.id()).toUri();
                    return ResponseEntity.created(location).body(user);
                }
            }
        ''')],
        steps=[
            ("record CreateUser", "The request body is a record with validation rules on each component: a valid, non-blank email and a name of 2 to 50 characters."),
            ("ConcurrentHashMap", "A ConcurrentHashMap and an AtomicLong keep this in-memory store safe under concurrent requests."),
            ("@Valid @RequestBody", "@RequestBody reads JSON into the record; @Valid runs the constraints and returns 400 Bad Request if any fail."),
            ("ServletUriComponentsBuilder", "We build the new resource's URL from the current request, such as /api/users/1."),
            ("ResponseEntity.created", "ResponseEntity.created sets status 201 and the Location header in one call."),
        ],
    )],
)

problem(
    id="sb-problem-details",
    title="Consistent Errors With Problem Details",
    difficulty="Medium",
    topics=["Spring Boot", "Error Handling", "REST"],
    statement="""
    Make every error response follow RFC 9457 Problem Details (`type`, `title`, `status`, `detail`). Map a custom
    `NotFoundException` to 404 and validation failures to 400 with a field-to-message map.
    """,
    examples=[("GET /api/orders/42 (missing)", "404 {\"title\":\"Not Found\",\"status\":404,\"detail\":\"Order 42 not found\"}", None)],
    hints=["A `@RestControllerAdvice` class handles exceptions for all controllers.", "`ProblemDetail.forStatusAndDetail` builds the body."],
    approaches=[approach(
        name="@RestControllerAdvice + ProblemDetail", **SB,
        idea="""
        Centralise error handling in one `@RestControllerAdvice`. Each `@ExceptionHandler` turns an exception into a `ProblemDetail`, Spring's built-in model of the standard error format.

        Clients then parse one predictable shape, and you never leak stack traces.
        """,
        files=[file("ApiErrors.java", '''
            import java.util.Map;
            import java.util.stream.Collectors;
            import org.springframework.http.HttpStatus;
            import org.springframework.http.ProblemDetail;
            import org.springframework.web.bind.MethodArgumentNotValidException;
            import org.springframework.web.bind.annotation.ExceptionHandler;
            import org.springframework.web.bind.annotation.RestControllerAdvice;

            @RestControllerAdvice
            public class ApiErrors {

                public static class NotFoundException extends RuntimeException {
                    public NotFoundException(String message) { super(message); }
                }

                @ExceptionHandler(NotFoundException.class)
                public ProblemDetail notFound(NotFoundException ex) {
                    return ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
                }

                @ExceptionHandler(MethodArgumentNotValidException.class)
                public ProblemDetail invalid(MethodArgumentNotValidException ex) {
                    ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "Validation failed");
                    Map<String, String> fields = ex.getBindingResult().getFieldErrors().stream()
                            .collect(Collectors.toMap(e -> e.getField(), e -> String.valueOf(e.getDefaultMessage()), (a, b) -> a));
                    pd.setProperty("errors", fields);
                    return pd;
                }
            }
        ''')],
        steps=[
            ("@RestControllerAdvice", "@RestControllerAdvice applies these handlers to every controller in the app."),
            ("class NotFoundException", "A small domain exception expresses intent: the thing you asked for doesn't exist."),
            ("@ExceptionHandler(NotFoundException.class)", "This handler catches it anywhere and answers 404."),
            ("ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND", "ProblemDetail fills in type, title and status for us; we add the human-readable detail."),
            ("MethodArgumentNotValidException", "Failed @Valid checks raise this exception; we translate it into a 400."),
            ("Collectors.toMap", "We collect each invalid field and its message into a map."),
            ("setProperty(\"errors\"", "Extra properties are allowed in problem details, so clients get field-level errors."),
        ],
    )],
)

problem(
    id="sb-jpa-repository",
    title="Entities and Repositories With Spring Data JPA",
    difficulty="Medium",
    topics=["Spring Boot", "JPA", "Database"],
    statement="""
    Model a `Book` entity (id, title, author, year) and a repository that can find books by author, search titles
    containing a keyword (case-insensitive), and list books published after a year, newest first, without writing SQL.
    """,
    examples=[("repo.findByTitleContainingIgnoreCase(\"dune\")", "[Book(Dune), Book(Dune Messiah)]", None)],
    hints=["Spring Data derives queries from method names.", "Use `@Id @GeneratedValue` for the primary key."],
    approaches=[approach(
        name="@Entity + JpaRepository", **SB,
        idea="""
        An `@Entity` class maps to a table. Extending `JpaRepository` gives you CRUD operations for free, and Spring Data derives queries from method names such as `findByAuthor`.

        For anything complex, use `@Query` with JPQL instead of very long method names.
        """,
        files=[
            file("Book.java", '''
                import jakarta.persistence.*;

                @Entity
                public class Book {
                    @Id
                    @GeneratedValue(strategy = GenerationType.IDENTITY)
                    private Long id;
                    private String title;
                    private String author;
                    private int publishedYear;

                    protected Book() {}

                    public Book(String title, String author, int publishedYear) {
                        this.title = title;
                        this.author = author;
                        this.publishedYear = publishedYear;
                    }

                    public Long getId() { return id; }
                    public String getTitle() { return title; }
                    public String getAuthor() { return author; }
                    public int getPublishedYear() { return publishedYear; }
                }
            '''),
            file("BookRepository.java", '''
                import java.util.List;
                import org.springframework.data.jpa.repository.JpaRepository;
                import org.springframework.data.jpa.repository.Query;

                public interface BookRepository extends JpaRepository<Book, Long> {
                    List<Book> findByAuthor(String author);

                    List<Book> findByTitleContainingIgnoreCase(String keyword);

                    List<Book> findByPublishedYearGreaterThanOrderByPublishedYearDesc(int year);

                    @Query("select b from Book b where b.author = :author and b.publishedYear >= :year")
                    List<Book> recentByAuthor(String author, int year);
                }
            '''),
        ],
        steps=[
            ("@Entity", "@Entity maps this class to a database table named book.", 0),
            ("@GeneratedValue", "The database generates the primary key with an identity column.", 0),
            ("protected Book()", "JPA needs a no-argument constructor; making it protected keeps it out of normal use.", 0),
            ("extends JpaRepository", "Extending JpaRepository gives save, findById, findAll, delete, paging and more, with no implementation.", 1),
            ("findByAuthor", "Spring Data reads the method name and generates WHERE author = ?.", 1),
            ("findByTitleContainingIgnoreCase", "Containing plus IgnoreCase becomes a case-insensitive LIKE '%keyword%' query.", 1),
            ("OrderByPublishedYearDesc", "Even the sort order can be part of the method name.", 1),
            ("@Query", "For anything clearer written by hand, @Query takes JPQL with named parameters.", 1),
        ],
    )],
)

problem(
    id="sb-pagination",
    title="Paginated, Sortable Listing",
    difficulty="Medium",
    topics=["Spring Boot", "JPA", "REST", "Pagination"],
    statement="""
    Expose `GET /api/books?page=0&size=20&sort=title,asc` returning one page of books as lightweight DTOs, with the
    page size capped at 100 so clients can't request huge pages.
    """,
    examples=[("GET /api/books?page=1&size=2&sort=title", "200 {\"content\":[...2 books...],\"page\":{\"number\":1,...}}", None)],
    hints=["A `Pageable` parameter is filled from page, size and sort automatically.", "Map entities to DTOs before returning."],
    approaches=[approach(
        name="Pageable + DTO projection", **SB,
        idea="""
        Declaring a `Pageable` parameter lets Spring parse page, size and sort from the query string. The repository returns a `Page`, and `map` converts each entity into a DTO so you never expose JPA entities directly.

        `@PageableDefault` sets sensible defaults; the global `spring.data.web.pageable.max-page-size` property caps abuse.
        """,
        files=[
            file("BookPageController.java", '''
                import org.springframework.data.domain.Page;
                import org.springframework.data.domain.Pageable;
                import org.springframework.data.domain.Sort;
                import org.springframework.data.web.PageableDefault;
                import org.springframework.web.bind.annotation.*;

                @RestController
                @RequestMapping("/api/books")
                public class BookPageController {

                    public record BookDto(Long id, String title) {}

                    private final BookRepository repo;

                    public BookPageController(BookRepository repo) { this.repo = repo; }

                    @GetMapping
                    public Page<BookDto> list(@PageableDefault(size = 20, sort = "title", direction = Sort.Direction.ASC) Pageable pageable) {
                        return repo.findAll(pageable).map(b -> new BookDto(b.getId(), b.getTitle()));
                    }
                }
            '''),
            file("BookRepository.java", '''
                import org.springframework.data.jpa.repository.JpaRepository;

                public interface BookRepository extends JpaRepository<Book, Long> {}
            '''),
            file("Book.java", '''
                import jakarta.persistence.*;

                @Entity
                public class Book {
                    @Id @GeneratedValue private Long id;
                    private String title;

                    public Long getId() { return id; }
                    public String getTitle() { return title; }
                }
            '''),
            file("application.properties", '''
                spring.data.web.pageable.max-page-size=100
                spring.data.web.pageable.one-indexed-parameters=false
            '''),
        ],
        steps=[
            ("record BookDto", "A small DTO record controls exactly which fields leave the API.", 0),
            ("public BookPageController(BookRepository repo)", "Constructor injection: Spring passes the repository in, and the field can be final.", 0),
            ("@PageableDefault", "Defaults apply when the client sends no paging parameters: 20 items sorted by title.", 0),
            ("repo.findAll(pageable)", "findAll(pageable) runs a LIMIT/OFFSET query plus a count query.", 0),
            (".map(b -> new BookDto", "Page.map converts each entity to a DTO while keeping the paging metadata.", 0),
            ("max-page-size=100", "This property caps page sizes globally, so size=10000 is silently reduced to 100.", 3),
        ],
    )],
)

problem(
    id="sb-transactional-transfer",
    title="Safe Money Transfer With @Transactional",
    difficulty="Medium",
    topics=["Spring Boot", "Transactions", "JPA", "Concurrency"],
    statement="""
    Implement `transfer(fromId, toId, amount)` so both balance updates succeed or neither does, insufficient funds are
    rejected, and two concurrent transfers can't silently overwrite each other's updates.
    """,
    examples=[("transfer(1, 2, 50) with balances 100 / 0", "balances 50 / 50", None),
              ("transfer(1, 2, 500) with balance 100", "throws InsufficientFundsException; nothing changes", None)],
    hints=["`@Transactional` rolls back on unchecked exceptions.", "A `@Version` field enables optimistic locking."],
    approaches=[approach(
        name="@Transactional + Optimistic Locking", **SB,
        idea="""
        `@Transactional` wraps the method in one database transaction: if anything throws, both updates roll back. Inside it, JPA's dirty checking writes the changed balances automatically on commit.

        The `@Version` column makes concurrent updates safe: if another transaction changed the row first, the commit fails with an optimistic-lock exception instead of losing an update.
        """,
        files=[
            file("Account.java", '''
                import jakarta.persistence.*;
                import java.math.BigDecimal;

                @Entity
                public class Account {
                    @Id private Long id;
                    private BigDecimal balance;
                    @Version private long version;

                    protected Account() {}

                    public BigDecimal getBalance() { return balance; }

                    public void withdraw(BigDecimal amount) {
                        if (balance.compareTo(amount) < 0) throw new TransferService.InsufficientFundsException(id);
                        balance = balance.subtract(amount);
                    }

                    public void deposit(BigDecimal amount) { balance = balance.add(amount); }
                }
            '''),
            file("TransferService.java", '''
                import java.math.BigDecimal;
                import org.springframework.data.jpa.repository.JpaRepository;
                import org.springframework.stereotype.Service;
                import org.springframework.transaction.annotation.Transactional;

                @Service
                public class TransferService {

                    public interface AccountRepository extends JpaRepository<Account, Long> {}

                    public static class InsufficientFundsException extends RuntimeException {
                        public InsufficientFundsException(Long id) { super("Insufficient funds in account " + id); }
                    }

                    private final AccountRepository accounts;

                    public TransferService(AccountRepository accounts) { this.accounts = accounts; }

                    @Transactional
                    public void transfer(long fromId, long toId, BigDecimal amount) {
                        Account from = accounts.findById(fromId).orElseThrow();
                        Account to = accounts.findById(toId).orElseThrow();
                        from.withdraw(amount);
                        to.deposit(amount);
                    }
                }
            '''),
        ],
        steps=[
            ("BigDecimal balance", "Money uses BigDecimal, never double, to avoid rounding errors.", 0),
            ("@Version", "The version column increments on every update; JPA checks it to detect concurrent writes.", 0),
            ("public void withdraw", "Business rules live on the entity: withdraw refuses to go negative.", 0),
            ("@Transactional", "Everything in transfer runs in one transaction: all or nothing.", 1),
            ("findById(fromId)", "Load both accounts inside the transaction so they're managed entities.", 1),
            ("from.withdraw(amount)", "If this throws, the transaction rolls back and no balance changes.", 1),
            ("to.deposit(amount)", "No explicit save is needed: dirty checking flushes both changes when the method commits.", 1),
        ],
    )],
)

problem(
    id="sb-config-properties",
    title="Type-Safe Configuration for an LLM Client",
    difficulty="Easy",
    topics=["Spring Boot", "Configuration", "AI Engineering"],
    statement="""
    Bind `app.llm.*` settings (base URL, model name, timeout, max tokens) into an immutable, validated configuration
    object, so a missing or invalid value fails fast at startup instead of at the first request.
    """,
    examples=[("app.llm.model= (blank)", "Application fails to start: model must not be blank", None)],
    hints=["`@ConfigurationProperties` binds a prefix onto a record.", "Add `@Validated` plus constraints to fail fast."],
    approaches=[approach(
        name="@ConfigurationProperties record", **SB,
        idea="""
        A record annotated with `@ConfigurationProperties("app.llm")` receives every matching property, converted to the right types (a `Duration` from `20s`, for example).

        `@Validated` with constraint annotations checks the values at startup, which is much better than a NullPointerException in production.
        """,
        files=[
            file("LlmProperties.java", '''
                import jakarta.validation.constraints.Max;
                import jakarta.validation.constraints.NotBlank;
                import java.net.URI;
                import java.time.Duration;
                import org.springframework.boot.context.properties.ConfigurationProperties;
                import org.springframework.validation.annotation.Validated;

                @Validated
                @ConfigurationProperties("app.llm")
                public record LlmProperties(URI baseUrl, @NotBlank String model, Duration timeout, @Max(32000) int maxTokens) {}
            '''),
            file("LlmConfig.java", '''
                import org.springframework.boot.context.properties.EnableConfigurationProperties;
                import org.springframework.context.annotation.Configuration;

                @Configuration
                @EnableConfigurationProperties(LlmProperties.class)
                public class LlmConfig {}
            '''),
            file("application.yml", '''
                app:
                  llm:
                    base-url: https://llm.internal.example
                    model: support-assistant-v3
                    timeout: 20s
                    max-tokens: 1024
            '''),
        ],
        steps=[
            ("@ConfigurationProperties(\"app.llm\")", "Every property under app.llm binds to a component of this record.", 0),
            ("Duration timeout", "Spring converts text such as 20s or 500ms into a Duration for you.", 0),
            ("@NotBlank String model", "Constraints plus @Validated make startup fail if the model name is missing.", 0),
            ("@EnableConfigurationProperties", "Registering the record makes it injectable like any other bean.", 1),
            ("base-url:", "Kebab-case keys in YAML map onto camelCase components such as baseUrl.", 2),
        ],
    )],
)

problem(
    id="sb-security-chain",
    title="Locking Down an API With Spring Security",
    difficulty="Medium",
    topics=["Spring Boot", "Security"],
    statement="""
    Secure the API: `/actuator/health` and `GET /api/public/**` are open, `/api/admin/**` requires role `ADMIN`,
    everything else requires authentication. Use stateless HTTP Basic (no sessions, CSRF disabled for this pure API)
    and BCrypt-hashed passwords.
    """,
    examples=[("GET /api/admin/stats as role USER", "403 Forbidden", None), ("GET /api/orders without credentials", "401 Unauthorized", None)],
    hints=["Define a `SecurityFilterChain` bean.", "Rules are checked in order: put the specific ones first."],
    approaches=[approach(
        name="SecurityFilterChain bean", **SB,
        idea="""
        Modern Spring Security is configured with a `SecurityFilterChain` bean built by a lambda DSL. Authorization rules are matched top to bottom, so open endpoints come first and the catch-all comes last.

        Stateless session management suits token or Basic auth for APIs; never store plain-text passwords, so expose a `PasswordEncoder` bean.
        """,
        files=[file("SecurityConfig.java", '''
            import org.springframework.context.annotation.Bean;
            import org.springframework.context.annotation.Configuration;
            import org.springframework.http.HttpMethod;
            import org.springframework.security.config.Customizer;
            import org.springframework.security.config.annotation.web.builders.HttpSecurity;
            import org.springframework.security.config.http.SessionCreationPolicy;
            import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
            import org.springframework.security.crypto.password.PasswordEncoder;
            import org.springframework.security.web.SecurityFilterChain;

            @Configuration
            public class SecurityConfig {

                @Bean
                SecurityFilterChain api(HttpSecurity http) throws Exception {
                    return http
                            .csrf(csrf -> csrf.disable())
                            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                            .authorizeHttpRequests(auth -> auth
                                    .requestMatchers("/actuator/health").permitAll()
                                    .requestMatchers(HttpMethod.GET, "/api/public/**").permitAll()
                                    .requestMatchers("/api/admin/**").hasRole("ADMIN")
                                    .anyRequest().authenticated())
                            .httpBasic(Customizer.withDefaults())
                            .build();
                }

                @Bean
                PasswordEncoder passwordEncoder() {
                    return new BCryptPasswordEncoder();
                }
            }
        ''')],
        steps=[
            ("SecurityFilterChain api", "One SecurityFilterChain bean defines how every request is secured."),
            ("csrf.disable()", "CSRF protection matters for cookie-based browser sessions; a stateless API using headers can disable it."),
            ("SessionCreationPolicy.STATELESS", "Stateless means no HTTP session: every request must authenticate itself."),
            ("requestMatchers(\"/actuator/health\")", "Health checks stay open so load balancers can probe the service."),
            ("hasRole(\"ADMIN\")", "Admin endpoints require the ADMIN role, otherwise 403 Forbidden."),
            ("anyRequest().authenticated()", "The catch-all rule comes last: everything else needs a logged-in user, otherwise 401."),
            ("BCryptPasswordEncoder", "BCrypt hashes passwords with a salt and a tunable cost, so a stolen table is hard to crack."),
        ],
    )],
)

problem(
    id="sb-rate-limit-filter",
    title="Per-Key Sliding Window Rate Limiter Filter",
    difficulty="Hard",
    topics=["Spring Boot", "Rate Limiting", "Sliding Window", "Concurrency"],
    statement="""
    Protect an AI endpoint: each `X-API-Key` may make at most 60 requests in any rolling 60 seconds. Extra requests get
    **429 Too Many Requests** with a `Retry-After` header. Implement it as a servlet filter using the sliding-window log
    idea, safe under concurrent requests.
    """,
    examples=[("61st request from key K within 60 s", "429 Retry-After: 12", None)],
    hints=["Keep a deque of request timestamps per key.", "Synchronise on the per-key deque, not on the whole filter."],
    approaches=[approach(
        name="OncePerRequestFilter + per-key deque", **SB,
        idea="""
        This is the sliding-window algorithm from the Practice tab, inside a real web filter. Each API key owns a deque of request times. On each request, drop timestamps older than the window from the front; if the deque is still full, reject with 429.

        Locking only the key's own deque keeps different clients from blocking each other. In a multi-instance deployment you'd move this state to Redis.
        """,
        files=[file("RateLimitFilter.java", '''
            import jakarta.servlet.FilterChain;
            import jakarta.servlet.ServletException;
            import jakarta.servlet.http.HttpServletRequest;
            import jakarta.servlet.http.HttpServletResponse;
            import java.io.IOException;
            import java.util.ArrayDeque;
            import java.util.Deque;
            import java.util.Map;
            import java.util.concurrent.ConcurrentHashMap;
            import org.springframework.stereotype.Component;
            import org.springframework.web.filter.OncePerRequestFilter;

            @Component
            public class RateLimitFilter extends OncePerRequestFilter {

                private static final int LIMIT = 60;
                private static final long WINDOW_MS = 60_000;
                private final Map<String, Deque<Long>> logs = new ConcurrentHashMap<>();

                @Override
                protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
                        throws ServletException, IOException {
                    String key = req.getHeader("X-API-Key");
                    if (key == null) {
                        res.sendError(HttpServletResponse.SC_UNAUTHORIZED);
                        return;
                    }
                    long now = System.currentTimeMillis();
                    Deque<Long> log = logs.computeIfAbsent(key, k -> new ArrayDeque<>());
                    synchronized (log) {
                        while (!log.isEmpty() && now - log.peekFirst() >= WINDOW_MS) log.pollFirst();
                        if (log.size() >= LIMIT) {
                            long retryAfter = (WINDOW_MS - (now - log.peekFirst()) + 999) / 1000;
                            res.setHeader("Retry-After", String.valueOf(retryAfter));
                            res.sendError(429, "Rate limit exceeded");
                            return;
                        }
                        log.addLast(now);
                    }
                    chain.doFilter(req, res);
                }
            }
        ''')],
        steps=[
            ("extends OncePerRequestFilter", "OncePerRequestFilter guarantees the filter runs exactly once per request, before any controller."),
            ("ConcurrentHashMap<>()", "Each API key gets its own deque of timestamps in a thread-safe map."),
            ("req.getHeader(\"X-API-Key\")", "Requests without an API key are rejected with 401 straight away."),
            ("computeIfAbsent", "computeIfAbsent creates the key's deque atomically on its first request."),
            ("synchronized (log)", "We lock only this key's deque, so other clients are never blocked."),
            ("while (!log.isEmpty()", "Slide the window: drop timestamps that are 60 seconds old or more from the front."),
            ("if (log.size() >= LIMIT)", "If the window is still full, the client must wait."),
            ("retryAfter", "Retry-After tells the client exactly when the oldest request leaves the window."),
            ("log.addLast(now)", "Otherwise record this request and let it continue down the filter chain."),
        ],
    )],
)

problem(
    id="sb-embedding-cache",
    title="Caching Expensive Embedding Calls",
    difficulty="Medium",
    topics=["Spring Boot", "Caching", "AI Engineering"],
    statement="""
    Computing a text embedding costs money and ~200 ms. Cache embeddings by input text so repeated texts are free, and
    provide a way to evict a single entry when the model changes.
    """,
    examples=[("embed(\"hello\") twice", "first call hits the model; second returns from cache", None)],
    hints=["`@EnableCaching` plus `@Cacheable` on the service method.", "Only calls through the Spring proxy are cached."],
    approaches=[approach(
        name="@Cacheable / @CacheEvict", **SB,
        idea="""
        `@Cacheable("embeddings")` checks the cache before running the method, keyed by its argument; on a miss it runs the method and stores the result.

        Caching works through a Spring proxy, so calling the method from inside the same class bypasses the cache. In production you'd back it with Caffeine or Redis and set a size or time limit.
        """,
        files=[file("EmbeddingService.java", '''
            import org.springframework.cache.annotation.CacheEvict;
            import org.springframework.cache.annotation.Cacheable;
            import org.springframework.cache.annotation.EnableCaching;
            import org.springframework.context.annotation.Configuration;
            import org.springframework.stereotype.Service;

            @Service
            public class EmbeddingService {

                @Configuration
                @EnableCaching
                static class CacheConfig {}

                public interface EmbeddingModel {
                    float[] embed(String text);
                }

                private final EmbeddingModel model;

                public EmbeddingService(EmbeddingModel model) { this.model = model; }

                @Cacheable(cacheNames = "embeddings", key = "#text")
                public float[] embed(String text) {
                    return model.embed(text);
                }

                @CacheEvict(cacheNames = "embeddings", key = "#text")
                public void evict(String text) {}
            }
        ''')],
        steps=[
            ("@EnableCaching", "@EnableCaching switches on Spring's caching proxies."),
            ("interface EmbeddingModel", "The model client sits behind an interface, so tests can swap in a fake."),
            ("@Cacheable", "@Cacheable looks up the text in the embeddings cache; only a miss calls the model."),
            ("model.embed(text)", "The expensive remote call happens once per distinct text."),
            ("@CacheEvict", "@CacheEvict removes one entry, for example after the embedding model is upgraded."),
        ],
    )],
)

problem(
    id="sb-parallel-calls",
    title="Calling Services in Parallel",
    difficulty="Medium",
    topics=["Spring Boot", "Concurrency", "CompletableFuture"],
    statement="""
    A dashboard needs a user's profile (300 ms) and recommendations (500 ms) from two services. Fetch both concurrently
    so the total is about 500 ms, with a 2-second overall timeout.
    """,
    examples=[("GET /api/dashboard/7", "200 {profile:..., recommendations:[...]} in ≈500 ms", None)],
    hints=["`CompletableFuture.supplyAsync` runs work on an executor.", "Java 21 virtual threads make blocking calls cheap."],
    approaches=[approach(
        name="CompletableFuture + virtual threads", **SB,
        idea="""
        Start both calls with `supplyAsync` on a virtual-thread executor, then combine them with `thenCombine` once both finish. `orTimeout` fails the whole request if it takes too long.

        Virtual threads (Java 21) let blocking HTTP calls scale without a big thread pool; Spring Boot can also enable them globally with `spring.threads.virtual.enabled=true`.
        """,
        files=[file("DashboardController.java", '''
            import java.util.List;
            import java.util.concurrent.CompletableFuture;
            import java.util.concurrent.ExecutorService;
            import java.util.concurrent.Executors;
            import java.util.concurrent.TimeUnit;
            import org.springframework.web.bind.annotation.*;

            @RestController
            public class DashboardController {

                public record Dashboard(String profile, List<String> recommendations) {}

                public interface Profiles { String fetch(long userId); }

                public interface Recommender { List<String> fetch(long userId); }

                private final ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor();
                private final Profiles profiles;
                private final Recommender recommender;

                public DashboardController(Profiles profiles, Recommender recommender) {
                    this.profiles = profiles;
                    this.recommender = recommender;
                }

                @GetMapping("/api/dashboard/{userId}")
                public CompletableFuture<Dashboard> dashboard(@PathVariable long userId) {
                    var profile = CompletableFuture.supplyAsync(() -> profiles.fetch(userId), pool);
                    var recs = CompletableFuture.supplyAsync(() -> recommender.fetch(userId), pool);
                    return profile.thenCombine(recs, Dashboard::new).orTimeout(2, TimeUnit.SECONDS);
                }
            }
        ''')],
        steps=[
            ("newVirtualThreadPerTaskExecutor", "A virtual thread per task: cheap, so blocking calls don't exhaust a pool."),
            ("supplyAsync(() -> profiles.fetch", "Start the profile call without waiting for it."),
            ("supplyAsync(() -> recommender.fetch", "Start the recommendations call at the same time."),
            ("thenCombine", "thenCombine waits for both and builds the Dashboard, so the total is the slower call, not the sum."),
            ("orTimeout", "orTimeout fails the future after 2 seconds instead of hanging the client."),
            ("CompletableFuture<Dashboard> dashboard", "Spring MVC accepts a CompletableFuture and writes the response when it completes."),
        ],
    )],
)

problem(
    id="sb-llm-client-retry",
    title="Resilient LLM API Client",
    difficulty="Medium",
    topics=["Spring Boot", "HTTP Client", "Resilience", "AI Engineering"],
    statement="""
    Call an LLM completion API with Spring's `RestClient`: send the prompt as JSON, read the answer, apply timeouts,
    and retry up to 3 times with exponential backoff (500 ms, 1 s, 2 s) on HTTP 429 or 5xx, never on other 4xx errors.
    """,
    examples=[("first call → 503, second → 200", "returns the answer after one retry", None),
              ("call → 400 Bad Request", "throws immediately, no retry", None)],
    hints=["Only retry errors that are likely temporary.", "Back off exponentially to avoid hammering a struggling service."],
    approaches=[approach(
        name="RestClient + backoff loop", **SB,
        idea="""
        `RestClient` is Spring's modern synchronous HTTP client with a fluent API. Configure base URL and timeouts once, then each call is a short chain.

        Retry only transient failures: 429 (rate limited) and 5xx (server problems). Client errors like 400 won't fix themselves. Doubling the delay each time (exponential backoff) gives the service room to recover.
        """,
        files=[file("LlmClient.java", '''
            import java.time.Duration;
            import org.springframework.http.MediaType;
            import org.springframework.http.client.SimpleClientHttpRequestFactory;
            import org.springframework.stereotype.Component;
            import org.springframework.web.client.HttpStatusCodeException;
            import org.springframework.web.client.RestClient;

            @Component
            public class LlmClient {

                public record CompletionRequest(String model, String prompt, int maxTokens) {}

                public record CompletionResponse(String text) {}

                private final RestClient http;

                public LlmClient(RestClient.Builder builder) {
                    var factory = new SimpleClientHttpRequestFactory();
                    factory.setConnectTimeout(Duration.ofSeconds(2));
                    factory.setReadTimeout(Duration.ofSeconds(30));
                    this.http = builder.baseUrl("https://llm.internal.example").requestFactory(factory).build();
                }

                public String complete(String prompt) throws InterruptedException {
                    long delay = 500;
                    for (int attempt = 1; ; attempt++) {
                        try {
                            return http.post().uri("/v1/complete")
                                    .contentType(MediaType.APPLICATION_JSON)
                                    .body(new CompletionRequest("support-assistant-v3", prompt, 512))
                                    .retrieve()
                                    .body(CompletionResponse.class)
                                    .text();
                        } catch (HttpStatusCodeException e) {
                            boolean transientError = e.getStatusCode().value() == 429 || e.getStatusCode().is5xxServerError();
                            if (!transientError || attempt == 3) throw e;
                            Thread.sleep(delay);
                            delay *= 2;
                        }
                    }
                }
            }
        ''')],
        steps=[
            ("record CompletionRequest", "Records describe the JSON request and response bodies precisely."),
            ("RestClient.Builder builder", "Spring Boot provides a pre-configured RestClient.Builder with JSON converters."),
            ("setConnectTimeout", "Always set timeouts: a 2-second connect timeout and a 30-second read timeout for long generations."),
            ("http.post().uri", "The fluent chain: POST to /v1/complete with a JSON body."),
            (".retrieve()", "retrieve() throws an HttpStatusCodeException for 4xx and 5xx responses."),
            ("boolean transientError", "Only 429 and 5xx count as temporary; anything else is our fault and is rethrown."),
            ("Thread.sleep(delay)", "Wait, then double the delay: 500 milliseconds, 1 second, 2 seconds."),
        ],
    )],
)

problem(
    id="sb-streaming-tokens",
    title="Streaming LLM Tokens With Server-Sent Events",
    difficulty="Medium",
    topics=["Spring Boot", "SSE", "Streaming", "AI Engineering"],
    statement="""
    Users shouldn't stare at a spinner while a model writes a long answer. Expose `GET /api/chat/stream?q=...` that
    streams each generated token to the browser as a Server-Sent Event, then sends a final `done` event.
    """,
    examples=[("GET /api/chat/stream?q=hi", "event:token data:Hel … event:token data:lo! … event:done", None)],
    hints=["`SseEmitter` keeps the HTTP response open and sends events.", "Generate on another thread so the request thread is freed."],
    approaches=[approach(
        name="SseEmitter on a virtual thread", **SB,
        idea="""
        `SseEmitter` holds the response open and lets you push events with `send`. Run the generation on a separate (virtual) thread: for each token from the model, send a `token` event; finish with a `done` event and `complete()`.

        If the client disconnects, `send` throws, so stop and call `completeWithError` to free resources.
        """,
        files=[file("ChatStreamController.java", '''
            import java.io.IOException;
            import java.util.function.Consumer;
            import org.springframework.http.MediaType;
            import org.springframework.web.bind.annotation.*;
            import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

            @RestController
            public class ChatStreamController {

                public interface TokenStream {
                    void generate(String prompt, Consumer<String> onToken);
                }

                private final TokenStream model;

                public ChatStreamController(TokenStream model) { this.model = model; }

                @GetMapping(path = "/api/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
                public SseEmitter stream(@RequestParam String q) {
                    SseEmitter emitter = new SseEmitter(120_000L);
                    Thread.ofVirtual().start(() -> {
                        try {
                            model.generate(q, token -> {
                                try {
                                    emitter.send(SseEmitter.event().name("token").data(token));
                                } catch (IOException e) {
                                    throw new IllegalStateException("client disconnected", e);
                                }
                            });
                            emitter.send(SseEmitter.event().name("done").data(""));
                            emitter.complete();
                        } catch (Exception e) {
                            emitter.completeWithError(e);
                        }
                    });
                    return emitter;
                }
            }
        ''')],
        steps=[
            ("interface TokenStream", "The model client calls onToken for every token it generates."),
            ("TEXT_EVENT_STREAM_VALUE", "The endpoint produces text/event-stream, the Server-Sent Events format browsers understand."),
            ("new SseEmitter(120_000L)", "The emitter keeps the response open for up to two minutes."),
            ("Thread.ofVirtual().start", "Generation runs on a virtual thread, so the request thread returns immediately."),
            ("event().name(\"token\")", "Each token goes out as a named token event the moment it arrives."),
            ("name(\"done\")", "A final done event tells the client the answer is complete."),
            ("completeWithError", "On errors or a disconnected client, completeWithError closes the stream cleanly."),
        ],
    )],
)

problem(
    id="sb-idempotency-key",
    title="Idempotent Payments With an Idempotency Key",
    difficulty="Hard",
    topics=["Spring Boot", "Distributed Systems", "Reliability"],
    statement="""
    Mobile clients retry `POST /api/payments` when the network drops, which must never charge twice. Require an
    `Idempotency-Key` header: the first request with a key is processed; any retry with the same key returns the
    original result without charging again, even if two retries arrive at the same time.
    """,
    examples=[("POST twice with Idempotency-Key: abc", "one charge; both responses identical", None)],
    hints=["Store results by key.", "`ConcurrentHashMap.computeIfAbsent` runs the work at most once per key."],
    approaches=[approach(
        name="computeIfAbsent result store", **SB,
        idea="""
        Keep a map from idempotency key to the payment result. `computeIfAbsent` atomically runs the charge only for the first request with a key; concurrent duplicates wait and receive the same stored result.

        In production this map lives in a database table with a unique constraint on the key, plus an expiry policy.
        """,
        files=[file("PaymentController.java", '''
            import java.math.BigDecimal;
            import java.util.Map;
            import java.util.UUID;
            import java.util.concurrent.ConcurrentHashMap;
            import org.springframework.http.ResponseEntity;
            import org.springframework.web.bind.annotation.*;

            @RestController
            @RequestMapping("/api/payments")
            public class PaymentController {

                public record PaymentRequest(String account, BigDecimal amount) {}

                public record PaymentResult(String paymentId, String status) {}

                public interface PaymentGateway { void charge(String account, BigDecimal amount); }

                private final Map<String, PaymentResult> results = new ConcurrentHashMap<>();
                private final PaymentGateway gateway;

                public PaymentController(PaymentGateway gateway) { this.gateway = gateway; }

                @PostMapping
                public ResponseEntity<PaymentResult> pay(@RequestHeader("Idempotency-Key") String key,
                                                         @RequestBody PaymentRequest req) {
                    PaymentResult result = results.computeIfAbsent(key, k -> {
                        gateway.charge(req.account(), req.amount());
                        return new PaymentResult(UUID.randomUUID().toString(), "CHARGED");
                    });
                    return ResponseEntity.ok(result);
                }
            }
        ''')],
        steps=[
            ("@RequestHeader(\"Idempotency-Key\")", "The client generates a unique key per logical payment and resends it on every retry. A missing header gets a 400 automatically."),
            ("ConcurrentHashMap", "Results are remembered by key."),
            ("computeIfAbsent", "computeIfAbsent runs the lambda at most once per key, even when duplicates race."),
            ("gateway.charge", "The real charge happens only inside that once-per-key block."),
            ("ResponseEntity.ok(result)", "Retries get the stored result, the same payment id, without a second charge."),
        ],
    )],
)

problem(
    id="sb-webmvc-test",
    title="Testing a Controller With MockMvc",
    difficulty="Medium",
    topics=["Spring Boot", "Testing", "MockMvc"],
    statement="""
    Write fast slice tests for `GreetingController` (which delegates to a `GreetingService`): one checks the JSON body
    of a successful call, another checks that a blank name returns 400. Mock the service.
    """,
    examples=[("GET /greet?name=Ada", "expects 200 and $.message == \"Hi Ada\"", None)],
    hints=["`@WebMvcTest` loads only the web layer.", "`@MockitoBean` replaces the service with a Mockito mock."],
    approaches=[approach(
        name="@WebMvcTest + MockMvc + @MockitoBean", **SB,
        idea="""
        `@WebMvcTest` starts only the MVC slice (controllers, advice, JSON), which makes tests much faster than a full `@SpringBootTest`. `MockMvc` performs requests without a real server, and `@MockitoBean` swaps the service for a mock you control.

        Assert on status and on JSON fields with JsonPath expressions.
        """,
        files=[
            file("GreetingController.java", '''
                import jakarta.validation.constraints.NotBlank;
                import org.springframework.validation.annotation.Validated;
                import org.springframework.web.bind.annotation.*;

                @Validated
                @RestController
                public class GreetingController {

                    public interface GreetingService { String greet(String name); }

                    public record Greeting(String message) {}

                    private final GreetingService service;

                    public GreetingController(GreetingService service) { this.service = service; }

                    @GetMapping("/greet")
                    public Greeting greet(@RequestParam @NotBlank String name) {
                        return new Greeting(service.greet(name));
                    }
                }
            '''),
            file("GreetingControllerTest.java", '''
                import static org.mockito.Mockito.when;
                import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
                import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
                import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

                import org.junit.jupiter.api.Test;
                import org.springframework.beans.factory.annotation.Autowired;
                import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
                import org.springframework.test.context.bean.override.mockito.MockitoBean;
                import org.springframework.test.web.servlet.MockMvc;

                @WebMvcTest(GreetingController.class)
                class GreetingControllerTest {

                    @Autowired MockMvc mvc;
                    @MockitoBean GreetingController.GreetingService service;

                    @Test
                    void returnsGreeting() throws Exception {
                        when(service.greet("Ada")).thenReturn("Hi Ada");
                        mvc.perform(get("/greet").param("name", "Ada"))
                                .andExpect(status().isOk())
                                .andExpect(jsonPath("$.message").value("Hi Ada"));
                    }

                    @Test
                    void rejectsBlankName() throws Exception {
                        mvc.perform(get("/greet").param("name", " "))
                                .andExpect(status().isBadRequest());
                    }
                }
            '''),
        ],
        steps=[
            ("@NotBlank String name", "Method validation on the request parameter rejects blank names.", 0),
            ("@WebMvcTest(GreetingController.class)", "Load only the web layer for this controller: fast and focused.", 1),
            ("@MockitoBean", "Replace the real service bean with a Mockito mock.", 1),
            ("when(service.greet", "Stub the mock: greeting Ada returns Hi Ada.", 1),
            ("mvc.perform(get(\"/greet\")", "Perform a GET request through the full Spring MVC pipeline, with no network involved.", 1),
            ("jsonPath(\"$.message\")", "JsonPath asserts on the response JSON.", 1),
            ("isBadRequest", "The second test proves validation turns a blank name into 400.", 1),
        ],
    )],
)

problem(
    id="sb-health-indicator",
    title="Health Check for a Model Dependency",
    difficulty="Easy",
    topics=["Spring Boot", "Actuator", "Observability"],
    statement="""
    Kubernetes should stop routing traffic to an instance whose model server is unreachable. Add a custom Actuator
    health indicator that reports `DOWN` (with details) when the model server's ping fails.
    """,
    examples=[("GET /actuator/health while the model is down", "503 {\"status\":\"DOWN\",\"components\":{\"model\":{...}}}", None)],
    hints=["Implement `HealthIndicator` and return `Health.up()` or `Health.down()`."],
    approaches=[approach(
        name="HealthIndicator bean", **SB,
        idea="""
        Any bean implementing `HealthIndicator` joins the aggregate `/actuator/health` result under a name derived from its class. If any component is DOWN, the endpoint answers 503, which load balancers and Kubernetes probes understand.
        """,
        files=[file("ModelHealthIndicator.java", '''
            import org.springframework.boot.actuate.health.Health;
            import org.springframework.boot.actuate.health.HealthIndicator;
            import org.springframework.stereotype.Component;

            @Component("model")
            public class ModelHealthIndicator implements HealthIndicator {

                public interface ModelServer { long pingMillis() throws Exception; }

                private final ModelServer server;

                public ModelHealthIndicator(ModelServer server) { this.server = server; }

                @Override
                public Health health() {
                    try {
                        long ms = server.pingMillis();
                        return Health.up().withDetail("latencyMs", ms).build();
                    } catch (Exception e) {
                        return Health.down(e).withDetail("hint", "model server unreachable").build();
                    }
                }
            }
        ''')],
        steps=[
            ("@Component(\"model\")", "The bean name model becomes the component name in the health JSON."),
            ("implements HealthIndicator", "Implementing HealthIndicator plugs into Actuator automatically."),
            ("server.pingMillis()", "Ping the dependency, ideally with a short timeout."),
            ("Health.up()", "Healthy: report UP, plus the latency as a useful detail."),
            ("Health.down(e)", "Unhealthy: DOWN makes /actuator/health return 503, so traffic shifts away."),
        ],
    )],
)
