"""Angular exercises (modern Angular 20+: standalone, signals, control flow). Original content; type-checked by tools/check_frameworks.py."""
from dsl import problem, approach, file

NG = dict(pattern="angular", time="—", space="—")

problem(
    id="ng-counter-signals",
    title="A Counter With Signals",
    difficulty="Easy",
    topics=["Angular", "Signals", "Components"],
    statement="""
    Build a standalone `CounterComponent` with + / − / reset buttons. Show the count and a derived label
    ("even"/"odd") that updates automatically.
    """,
    examples=[("click + twice", "Count: 2 (even)", None)],
    hints=["`signal()` holds state; `computed()` derives from it.", "Read a signal by calling it: `count()`."],
    approaches=[approach(
        name="signal + computed", **NG,
        idea="""
        A `signal` is a reactive value: reading it in the template subscribes the view, and `set`/`update` notify it. `computed` derives a value from other signals and recalculates only when they change.

        No subscriptions, no manual change detection, and it works in zoneless apps.
        """,
        files=[file("counter.component.ts", '''
            import { ChangeDetectionStrategy, Component, computed, signal } from '@angular/core';

            @Component({
              selector: 'app-counter',
              changeDetection: ChangeDetectionStrategy.OnPush,
              template: `
                <p>Count: {{ count() }} ({{ parity() }})</p>
                <button (click)="decrement()">−</button>
                <button (click)="increment()">+</button>
                <button (click)="count.set(0)">Reset</button>
              `,
            })
            export class CounterComponent {
              readonly count = signal(0);
              readonly parity = computed(() => (this.count() % 2 === 0 ? 'even' : 'odd'));

              increment(): void {
                this.count.update((c) => c + 1);
              }

              decrement(): void {
                this.count.update((c) => c - 1);
              }
            }
        ''')],
        steps=[
            ("@Component", "Components are standalone by default in modern Angular: no NgModule needed."),
            ("OnPush", "OnPush plus signals means Angular only re-renders this view when a signal it reads changes."),
            ("{{ count() }}", "Templates read a signal by calling it like a function."),
            ("(click)=\"increment()\"", "Event binding: a click calls increment."),
            ("signal(0)", "signal(0) creates writable reactive state starting at zero."),
            ("computed(", "computed derives parity from count and recalculates only when count changes."),
            ("this.count.update", "update produces the next value from the previous one."),
        ],
    )],
)

problem(
    id="ng-input-output",
    title="Parent and Child: Inputs and Outputs",
    difficulty="Easy",
    topics=["Angular", "Components", "Signals"],
    statement="""
    Create a reusable `StarRatingComponent` that receives the current `rating` (required) and `max` (default 5) from
    its parent, renders clickable stars, and emits `rated` with the chosen value.
    """,
    examples=[("<app-star-rating [rating]=\"3\" (rated)=\"save($event)\"/>", "clicking the 4th star emits 4", None)],
    hints=["`input.required<number>()` declares a required signal input.", "`output<number>()` declares an event."],
    approaches=[approach(
        name="input() / output()", **NG,
        idea="""
        Signal inputs (`input()`, `input.required()`) receive data from the parent and are read like signals. `output()` creates an event the parent listens to with `( )` binding.

        Data flows down through inputs and events flow up through outputs, which keeps components reusable.
        """,
        files=[file("star-rating.component.ts", '''
            import { Component, computed, input, output } from '@angular/core';

            @Component({
              selector: 'app-star-rating',
              template: `
                @for (star of stars(); track star) {
                  <button type="button" (click)="rated.emit(star)" [attr.aria-label]="'Rate ' + star">
                    {{ star <= rating() ? '★' : '☆' }}
                  </button>
                }
              `,
            })
            export class StarRatingComponent {
              readonly rating = input.required<number>();
              readonly max = input(5);
              readonly rated = output<number>();
              readonly stars = computed(() => Array.from({ length: this.max() }, (_, i) => i + 1));
            }
        ''')],
        steps=[
            ("@for (star of stars(); track star)", "The built-in @for loop renders one button per star; track gives each item a stable identity."),
            ("rated.emit(star)", "Clicking emits the star number to the parent."),
            ("aria-label", "An aria-label makes each star accessible to screen readers."),
            ("input.required<number>()", "A required signal input: the parent must pass rating."),
            ("input(5)", "An optional input with a default of five stars."),
            ("output<number>()", "output declares the rated event carrying a number."),
            ("computed(() => Array.from", "stars derives the list 1 to max and updates if max changes."),
        ],
    )],
)

problem(
    id="ng-control-flow",
    title="Lists, Empty States and Conditions",
    difficulty="Easy",
    topics=["Angular", "Templates", "Control Flow"],
    statement="""
    Render a task list: show a loading message while loading, each task with a ✓ when done, an empty-state message when
    there are no tasks, and a count of remaining tasks.
    """,
    examples=[("tasks = []", "\"Nothing to do 🎉\"", None)],
    hints=["Use `@if`, `@for ... track`, and `@empty`."],
    approaches=[approach(
        name="@if / @for / @empty", **NG,
        idea="""
        Angular's built-in control flow replaces `*ngIf` and `*ngFor`. `@for` requires a `track` expression so Angular can reuse DOM nodes efficiently, and `@empty` handles the no-items case without an extra `@if`.
        """,
        files=[file("task-list.component.ts", '''
            import { Component, computed, input } from '@angular/core';

            export interface Task {
              id: number;
              title: string;
              done: boolean;
            }

            @Component({
              selector: 'app-task-list',
              template: `
                @if (loading()) {
                  <p>Loading…</p>
                } @else {
                  <ul>
                    @for (task of tasks(); track task.id) {
                      <li [class.done]="task.done">{{ task.title }} @if (task.done) { ✓ }</li>
                    } @empty {
                      <li>Nothing to do 🎉</li>
                    }
                  </ul>
                  <small>{{ remaining() }} remaining</small>
                }
              `,
            })
            export class TaskListComponent {
              readonly tasks = input<Task[]>([]);
              readonly loading = input(false);
              readonly remaining = computed(() => this.tasks().filter((t) => !t.done).length);
            }
        ''')],
        steps=[
            ("export interface Task", "A typed Task interface keeps templates and code in sync."),
            ("@if (loading())", "@if with @else shows either the loading message or the list."),
            ("track task.id", "Tracking by id lets Angular move existing DOM rows instead of recreating them."),
            ("[class.done]", "Class binding toggles the done CSS class per task."),
            ("@empty", "@empty renders when the list has no items: a friendly empty state."),
            ("computed(() => this.tasks().filter", "remaining is derived from tasks, so it's always correct."),
        ],
    )],
)

problem(
    id="ng-reactive-form",
    title="Sign-Up Form With Validation",
    difficulty="Medium",
    topics=["Angular", "Forms", "Validation"],
    statement="""
    Build a sign-up form with email (required, valid), password (min 8 chars) and confirm-password fields. Show
    errors only after a field is touched, add a custom "passwords match" validator, and disable submit while invalid.
    """,
    examples=[("password 'abc12345', confirm 'abc' ", "\"Passwords must match\" error; submit disabled", None)],
    hints=["Use a typed `NonNullableFormBuilder`.", "A group-level validator can compare two controls."],
    approaches=[approach(
        name="Typed Reactive Forms", **NG,
        idea="""
        Reactive forms model the form in TypeScript, which makes validation logic testable and type-safe. `NonNullableFormBuilder` gives strongly typed controls whose values are never null.

        A custom validator on the group compares password and confirmation, and the template shows messages only for touched controls.
        """,
        files=[file("signup.component.ts", '''
            import { Component, inject } from '@angular/core';
            import { AbstractControl, NonNullableFormBuilder, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';

            export function passwordsMatch(group: AbstractControl): ValidationErrors | null {
              const pass = group.get('password')?.value;
              const confirm = group.get('confirm')?.value;
              return pass === confirm ? null : { mismatch: true };
            }

            @Component({
              selector: 'app-signup',
              imports: [ReactiveFormsModule],
              template: `
                <form [formGroup]="form" (ngSubmit)="submit()">
                  <input formControlName="email" type="email" placeholder="Email" />
                  @if (form.controls.email.touched && form.controls.email.invalid) {
                    <small>Enter a valid email.</small>
                  }
                  <input formControlName="password" type="password" placeholder="Password" />
                  @if (form.controls.password.touched && form.controls.password.hasError('minlength')) {
                    <small>At least 8 characters.</small>
                  }
                  <input formControlName="confirm" type="password" placeholder="Confirm" />
                  @if (form.controls.confirm.touched && form.hasError('mismatch')) {
                    <small>Passwords must match.</small>
                  }
                  <button type="submit" [disabled]="form.invalid">Create account</button>
                </form>
              `,
            })
            export class SignupComponent {
              private readonly fb = inject(NonNullableFormBuilder);

              readonly form = this.fb.group(
                {
                  email: ['', [Validators.required, Validators.email]],
                  password: ['', [Validators.required, Validators.minLength(8)]],
                  confirm: ['', Validators.required],
                },
                { validators: passwordsMatch },
              );

              submit(): void {
                if (this.form.invalid) return;
                const { email, password } = this.form.getRawValue();
                console.log('creating account for', email, password.length);
              }
            }
        ''')],
        steps=[
            ("export function passwordsMatch", "A validator is just a function: return null when valid, or an error object."),
            ("imports: [ReactiveFormsModule]", "Standalone components import what their template needs directly."),
            ("[formGroup]=\"form\"", "The form element binds to the FormGroup defined in the class."),
            ("form.controls.email.touched", "Show an error only after the user has left the field: touched plus invalid."),
            ("hasError('mismatch')", "Group-level errors live on the form itself."),
            ("[disabled]=\"form.invalid\"", "The submit button stays disabled while anything is invalid."),
            ("inject(NonNullableFormBuilder)", "inject() fetches dependencies without a constructor; the non-nullable builder keeps values typed as string."),
            ("{ validators: passwordsMatch }", "Attach the custom cross-field validator to the whole group."),
            ("getRawValue()", "getRawValue returns the fully typed form value."),
        ],
    )],
)

problem(
    id="ng-http-service",
    title="A Typed HTTP Data Service",
    difficulty="Medium",
    topics=["Angular", "HttpClient", "Services", "RxJS"],
    statement="""
    Create a `ProductService` that loads `/api/products` with `HttpClient`, returns typed data, and falls back to an
    empty list (while logging) when the request fails. Show the products in a component as a signal.
    """,
    examples=[("GET /api/products → 500", "component shows an empty list, error logged", None)],
    hints=["`inject(HttpClient)` inside an `@Injectable({ providedIn: 'root' })` service.", "`toSignal` converts an Observable into a signal."],
    approaches=[approach(
        name="Injectable service + toSignal", **NG,
        idea="""
        Keep HTTP logic in a root-provided service so components stay simple and the service is easy to mock. `catchError` turns failures into a safe fallback value.

        In the component, `toSignal` subscribes to the Observable for you and exposes the latest value as a signal, unsubscribing automatically.
        """,
        files=[
            file("product.service.ts", '''
                import { HttpClient } from '@angular/common/http';
                import { Injectable, inject } from '@angular/core';
                import { Observable, catchError, of } from 'rxjs';

                export interface Product {
                  id: number;
                  name: string;
                  price: number;
                }

                @Injectable({ providedIn: 'root' })
                export class ProductService {
                  private readonly http = inject(HttpClient);

                  list(): Observable<Product[]> {
                    return this.http.get<Product[]>('/api/products').pipe(
                      catchError((err) => {
                        console.error('Failed to load products', err);
                        return of([]);
                      }),
                    );
                  }
                }
            '''),
            file("product-list.component.ts", '''
                import { CurrencyPipe } from '@angular/common';
                import { Component, inject } from '@angular/core';
                import { toSignal } from '@angular/core/rxjs-interop';
                import { ProductService } from './product.service';

                @Component({
                  selector: 'app-product-list',
                  imports: [CurrencyPipe],
                  template: `
                    @for (p of products(); track p.id) {
                      <div>{{ p.name }}: {{ p.price | currency }}</div>
                    }
                  `,
                })
                export class ProductListComponent {
                  readonly products = toSignal(inject(ProductService).list(), { initialValue: [] });
                }
            '''),
        ],
        steps=[
            ("export interface Product", "Describe the API's JSON shape once and reuse it everywhere.", 0),
            ("providedIn: 'root'", "providedIn root creates one shared instance and lets unused services be tree-shaken.", 0),
            ("this.http.get<Product[]>", "get with a type parameter returns a typed Observable.", 0),
            ("catchError", "catchError logs the failure and substitutes an empty list, so the UI never breaks.", 0),
            ("toSignal(", "toSignal subscribes and turns the stream into a signal with an initial empty value.", 1),
            ("| currency", "The currency pipe formats prices for the user's locale.", 1),
        ],
    )],
)

problem(
    id="ng-debounced-search",
    title="Debounced Search Box",
    difficulty="Medium",
    topics=["Angular", "RxJS", "Forms"],
    statement="""
    Search as the user types, without sending a request for every keystroke: wait until typing pauses for 300 ms,
    skip repeated terms, ignore terms shorter than 2 characters, and cancel stale requests when a new term arrives.
    """,
    examples=[("type 'ang' quickly", "one request for 'ang' after 300 ms", None)],
    hints=["`debounceTime`, `distinctUntilChanged`, `filter`, `switchMap`."],
    approaches=[approach(
        name="RxJS pipeline + switchMap", **NG,
        idea="""
        A `FormControl`'s `valueChanges` is a stream of keystrokes. `debounceTime` waits for a pause, `distinctUntilChanged` drops repeats, and `switchMap` cancels the previous HTTP request whenever a new term arrives, so stale results can't overwrite fresh ones.
        """,
        files=[file("search.component.ts", '''
            import { HttpClient } from '@angular/common/http';
            import { Component, inject } from '@angular/core';
            import { toSignal } from '@angular/core/rxjs-interop';
            import { FormControl, ReactiveFormsModule } from '@angular/forms';
            import { debounceTime, distinctUntilChanged, filter, map, of, switchMap } from 'rxjs';

            @Component({
              selector: 'app-search',
              imports: [ReactiveFormsModule],
              template: `
                <input [formControl]="query" placeholder="Search docs…" />
                <ul>
                  @for (hit of results(); track hit) {
                    <li>{{ hit }}</li>
                  }
                </ul>
              `,
            })
            export class SearchComponent {
              private readonly http = inject(HttpClient);
              readonly query = new FormControl('', { nonNullable: true });

              readonly results = toSignal(
                this.query.valueChanges.pipe(
                  map((q) => q.trim()),
                  debounceTime(300),
                  distinctUntilChanged(),
                  filter((q) => q.length >= 2 || q.length === 0),
                  switchMap((q) => (q ? this.http.get<string[]>('/api/search', { params: { q } }) : of([]))),
                ),
                { initialValue: [] as string[] },
              );
            }
        ''')],
        steps=[
            ("[formControl]=\"query\"", "The input binds to a standalone FormControl."),
            ("valueChanges.pipe", "valueChanges emits on every keystroke; the pipe shapes that stream."),
            ("debounceTime(300)", "Wait until the user stops typing for 300 milliseconds."),
            ("distinctUntilChanged()", "Skip the request if the term didn't actually change."),
            ("filter((q)", "Ignore one-letter searches, but let an empty box through to clear results."),
            ("switchMap", "switchMap cancels the in-flight request when a newer term arrives, so there are no out-of-order results."),
            ("initialValue", "toSignal exposes the latest results as a signal for the template."),
        ],
    )],
)

problem(
    id="ng-route-params",
    title="Routes With Parameters",
    difficulty="Easy",
    topics=["Angular", "Router"],
    statement="""
    Configure routes for a list page and a detail page `/products/:id`, plus a wildcard 404 page. Let the detail
    component receive `id` directly as an input.
    """,
    examples=[("navigate to /products/42", "ProductDetail shows id 42", None)],
    hints=["`withComponentInputBinding()` maps route params onto inputs."],
    approaches=[approach(
        name="Routes + component input binding", **NG,
        idea="""
        Routes map URL patterns to components. With `withComponentInputBinding()`, route parameters such as `:id` are passed straight into matching `input()`s, so there's no `ActivatedRoute` subscription.
        """,
        files=[
            file("app.routes.ts", '''
                import { Component, input } from '@angular/core';
                import { Routes } from '@angular/router';

                @Component({ selector: 'app-products', template: `<h1>All products</h1>` })
                export class ProductsPage {}

                @Component({ selector: 'app-product-detail', template: `<h1>Product {{ id() }}</h1>` })
                export class ProductDetailPage {
                  readonly id = input.required<string>();
                }

                @Component({ selector: 'app-not-found', template: `<h1>Page not found</h1>` })
                export class NotFoundPage {}

                export const routes: Routes = [
                  { path: '', redirectTo: 'products', pathMatch: 'full' },
                  { path: 'products', component: ProductsPage, title: 'Products' },
                  { path: 'products/:id', component: ProductDetailPage },
                  { path: '**', component: NotFoundPage },
                ];
            '''),
            file("app.config.ts", '''
                import { ApplicationConfig } from '@angular/core';
                import { provideRouter, withComponentInputBinding } from '@angular/router';
                import { routes } from './app.routes';

                export const appConfig: ApplicationConfig = {
                  providers: [provideRouter(routes, withComponentInputBinding())],
                };
            '''),
        ],
        steps=[
            ("input.required<string>()", "The detail page declares an id input: the router will fill it.", 0),
            ("redirectTo: 'products'", "The empty path redirects to the list. pathMatch full means only an exactly empty URL.", 0),
            ("title: 'Products'", "Routes can set the browser tab title.", 0),
            ("'products/:id'", "The colon marks a route parameter named id.", 0),
            ("path: '**'", "The wildcard route must come last: it catches every unknown URL.", 0),
            ("withComponentInputBinding()", "This feature binds route params, query params and data to component inputs.", 1),
        ],
    )],
)

problem(
    id="ng-auth-guard",
    title="Protecting Routes With a Guard",
    difficulty="Medium",
    topics=["Angular", "Router", "Security"],
    statement="""
    Only signed-in users may open `/account`. Write a functional route guard that lets authenticated users through and
    redirects everyone else to `/login?returnUrl=...`.
    """,
    examples=[("visit /account while signed out", "redirected to /login?returnUrl=%2Faccount", None)],
    hints=["A `CanActivateFn` can `inject()` services.", "Return a `UrlTree` to redirect."],
    approaches=[approach(
        name="Functional CanActivateFn", **NG,
        idea="""
        Guards are plain functions in modern Angular. `inject()` works inside them, so the guard can read the auth state and return either `true` or a `UrlTree` that redirects, which is safer than calling `navigate` inside a guard.

        Guards are a UX convenience: the server must still enforce permissions.
        """,
        files=[file("auth.guard.ts", '''
            import { Injectable, inject, signal } from '@angular/core';
            import { CanActivateFn, Router } from '@angular/router';

            @Injectable({ providedIn: 'root' })
            export class AuthService {
              readonly user = signal<{ name: string } | null>(null);
            }

            export const authGuard: CanActivateFn = (_route, state) => {
              const auth = inject(AuthService);
              const router = inject(Router);
              if (auth.user()) return true;
              return router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
            };
        ''')],
        steps=[
            ("signal<{ name: string } | null>", "The current user lives in a signal; null means signed out."),
            ("export const authGuard: CanActivateFn", "A functional guard: just a function with the CanActivateFn type."),
            ("inject(AuthService)", "inject works inside guards, interceptors and resolvers."),
            ("if (auth.user()) return true", "Signed in: allow the navigation."),
            ("createUrlTree", "Otherwise return a UrlTree to /login, remembering where the user wanted to go."),
        ],
    )],
)

problem(
    id="ng-auth-interceptor",
    title="HTTP Interceptor for Tokens and Retries",
    difficulty="Medium",
    topics=["Angular", "HttpClient", "Security", "Resilience"],
    statement="""
    Every API call needs `Authorization: Bearer <token>`. Write a functional HTTP interceptor that adds the header to
    requests for `/api`, retries GET requests twice on network or 503 errors with a short delay, and register it.
    """,
    examples=[("GET /api/orders", "sent with Authorization header; retried on 503", None)],
    hints=["`HttpInterceptorFn` receives `req` and `next`.", "Requests are immutable: use `req.clone`."],
    approaches=[approach(
        name="HttpInterceptorFn + retry", **NG,
        idea="""
        Interceptors sit between your code and the network. Since requests are immutable, clone the request with the extra header. RxJS `retry` with a delay function re-subscribes on failure; limit it to safe, idempotent GET requests and to errors that are worth retrying.
        """,
        files=[
            file("auth.interceptor.ts", '''
                import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
                import { retry, throwError, timer } from 'rxjs';

                export const authInterceptor: HttpInterceptorFn = (req, next) => {
                  const token = localStorage.getItem('token');
                  const authed = token && req.url.startsWith('/api')
                    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
                    : req;
                  return next(authed).pipe(
                    retry({
                      count: req.method === 'GET' ? 2 : 0,
                      delay: (err: HttpErrorResponse, attempt) =>
                        err.status === 0 || err.status === 503 ? timer(300 * attempt) : throwError(() => err),
                    }),
                  );
                };
            '''),
            file("app.config.ts", '''
                import { ApplicationConfig } from '@angular/core';
                import { provideHttpClient, withInterceptors } from '@angular/common/http';
                import { authInterceptor } from './auth.interceptor';

                export const appConfig: ApplicationConfig = {
                  providers: [provideHttpClient(withInterceptors([authInterceptor]))],
                };
            '''),
        ],
        steps=[
            ("HttpInterceptorFn = (req, next)", "A functional interceptor receives the request and a next handler.", 0),
            ("req.clone({ setHeaders", "Requests are immutable, so clone with the Authorization header added, only for our own /api URLs.", 0),
            ("retry({", "retry re-sends the request when it fails.", 0),
            ("req.method === 'GET' ? 2 : 0", "Only GET requests are retried, because repeating a POST could create duplicates.", 0),
            ("timer(300 * attempt)", "Network errors (status 0) and 503s wait a little longer each attempt; other errors fail immediately.", 0),
            ("withInterceptors([authInterceptor])", "Register the interceptor when providing HttpClient.", 1),
        ],
    )],
)

problem(
    id="ng-custom-pipe",
    title="A Custom 'Time Ago' Pipe",
    difficulty="Easy",
    topics=["Angular", "Pipes"],
    statement="""
    Write a pure pipe `timeAgo` that turns a date into friendly text: "just now", "5 min ago", "3 h ago" or "2 d ago".
    """,
    examples=[("{{ comment.createdAt | timeAgo }} (7 minutes ago)", "7 min ago", None)],
    hints=["Implement `PipeTransform`; keep it pure (no side effects)."],
    approaches=[approach(
        name="Pure pipe", **NG,
        idea="""
        A pipe transforms a value for display. Pure pipes (the default) run only when their input changes, so they're cheap. Keep formatting logic here instead of repeating it in components.
        """,
        files=[file("time-ago.pipe.ts", '''
            import { Pipe, PipeTransform } from '@angular/core';

            @Pipe({ name: 'timeAgo' })
            export class TimeAgoPipe implements PipeTransform {
              transform(value: Date | string | number, now: number = Date.now()): string {
                const seconds = Math.max(0, Math.floor((now - new Date(value).getTime()) / 1000));
                if (seconds < 60) return 'just now';
                const minutes = Math.floor(seconds / 60);
                if (minutes < 60) return `${minutes} min ago`;
                const hours = Math.floor(minutes / 60);
                if (hours < 24) return `${hours} h ago`;
                return `${Math.floor(hours / 24)} d ago`;
              }
            }
        ''')],
        steps=[
            ("@Pipe({ name: 'timeAgo' })", "@Pipe registers the name used in templates."),
            ("implements PipeTransform", "PipeTransform requires a transform method."),
            ("now: number = Date.now()", "An optional now parameter makes the pipe easy to unit test."),
            ("Math.max(0", "Clamp future dates to zero seconds, which protects against clock skew."),
            ("if (seconds < 60)", "Pick the largest unit that makes sense: seconds, minutes, hours, then days."),
        ],
    )],
)

problem(
    id="ng-highlight-directive",
    title="An Attribute Directive",
    difficulty="Easy",
    topics=["Angular", "Directives"],
    statement="""
    Create `appHighlight`, an attribute directive that highlights an element's background on hover with a configurable
    color (default yellow).
    """,
    examples=[("<p appHighlight=\"lightblue\">Hover me</p>", "light blue background while hovered", None)],
    hints=["Use the `host` metadata to listen to events and bind styles."],
    approaches=[approach(
        name="Directive with host bindings", **NG,
        idea="""
        Attribute directives add behaviour to existing elements. The `host` metadata listens to DOM events and binds properties on the host element, and a signal tracks the hover state.
        """,
        files=[file("highlight.directive.ts", '''
            import { Directive, input, signal } from '@angular/core';

            @Directive({
              selector: '[appHighlight]',
              host: {
                '(mouseenter)': 'hovered.set(true)',
                '(mouseleave)': 'hovered.set(false)',
                '[style.backgroundColor]': "hovered() ? (appHighlight() || 'yellow') : null",
              },
            })
            export class HighlightDirective {
              readonly appHighlight = input('');
              readonly hovered = signal(false);
            }
        ''')],
        steps=[
            ("selector: '[appHighlight]'", "The square brackets make this an attribute selector."),
            ("'(mouseenter)'", "Host listeners react to events on the element the directive sits on."),
            ("'[style.backgroundColor]'", "A host binding sets the background while hovered."),
            ("readonly appHighlight = input('')", "An input with the directive's own name receives the attribute's value, the color."),
        ],
    )],
)

problem(
    id="ng-signal-store",
    title="A Shopping Cart Store With Signals",
    difficulty="Medium",
    topics=["Angular", "Signals", "State Management"],
    statement="""
    Manage cart state in a service: add items (merging quantities), remove items, and expose derived totals that every
    component can read. Keep the state read-only from outside.
    """,
    examples=[("add(apple ×2), add(apple ×1)", "one line: apple ×3; total updates everywhere", None)],
    hints=["Private writable signal, public `asReadonly()`.", "Derived values are `computed`."],
    approaches=[approach(
        name="Service store with signals", **NG,
        idea="""
        A root service owns a private writable signal and exposes a read-only view. Methods describe the allowed changes and compute new immutable arrays, while `computed` values such as the total update automatically.

        This covers most app state needs before reaching for a state library.
        """,
        files=[file("cart.store.ts", '''
            import { Injectable, computed, signal } from '@angular/core';

            export interface CartItem {
              id: string;
              name: string;
              price: number;
              qty: number;
            }

            @Injectable({ providedIn: 'root' })
            export class CartStore {
              private readonly state = signal<CartItem[]>([]);
              readonly items = this.state.asReadonly();
              readonly count = computed(() => this.state().reduce((n, i) => n + i.qty, 0));
              readonly total = computed(() => this.state().reduce((sum, i) => sum + i.price * i.qty, 0));

              add(item: CartItem): void {
                this.state.update((items) => {
                  const existing = items.find((i) => i.id === item.id);
                  return existing
                    ? items.map((i) => (i.id === item.id ? { ...i, qty: i.qty + item.qty } : i))
                    : [...items, item];
                });
              }

              remove(id: string): void {
                this.state.update((items) => items.filter((i) => i.id !== id));
              }
            }
        ''')],
        steps=[
            ("private readonly state = signal", "The writable signal is private, so only the store can change it."),
            ("asReadonly()", "Components get a read-only signal: they can read it but not write it."),
            ("computed(() => this.state().reduce((n", "count and total are derived and always consistent."),
            ("items.find", "Adding an existing item merges quantities instead of duplicating the line."),
            ("{ ...i, qty: i.qty + item.qty }", "Immutable updates: create new objects, so signals detect the change."),
            ("items.filter", "remove produces a new array without the item."),
        ],
    )],
)

problem(
    id="ng-lazy-defer",
    title="Faster Loads With Lazy Routes and @defer",
    difficulty="Medium",
    topics=["Angular", "Performance", "Router"],
    statement="""
    Cut the initial bundle: lazy-load the admin area only when visited, and defer rendering a heavy chart component
    until it scrolls into view, with a placeholder and loading state.
    """,
    examples=[("first page load", "admin and chart code are not downloaded yet", None)],
    hints=["`loadComponent` / `loadChildren` with dynamic `import()`.", "`@defer (on viewport)` with `@placeholder` and `@loading`."],
    approaches=[approach(
        name="loadComponent + @defer", **NG,
        idea="""
        A route's `loadComponent` uses a dynamic `import()`, so its code becomes a separate chunk fetched on first navigation.

        Inside templates, `@defer` lazily loads the components in its block when a trigger fires, such as `on viewport`, and shows `@placeholder` and `@loading` content meanwhile.
        """,
        files=[
            file("app.routes.ts", '''
                import { Routes } from '@angular/router';

                export const routes: Routes = [
                  { path: 'admin', loadComponent: () => import('./admin.page').then((m) => m.AdminPage) },
                ];
            '''),
            file("admin.page.ts", '''
                import { Component } from '@angular/core';

                @Component({ selector: 'app-sales-chart', template: `<canvas aria-label="Sales chart"></canvas>` })
                export class SalesChartComponent {}

                @Component({
                  selector: 'app-admin',
                  imports: [SalesChartComponent],
                  template: `
                    <h1>Admin</h1>
                    @defer (on viewport) {
                      <app-sales-chart />
                    } @placeholder {
                      <div class="chart-skeleton">Chart</div>
                    } @loading (minimum 300ms) {
                      <p>Loading chart…</p>
                    }
                  `,
                })
                export class AdminPage {}
            '''),
        ],
        steps=[
            ("loadComponent: () => import", "Dynamic import splits the admin page into its own chunk, downloaded on first visit.", 0),
            ("@defer (on viewport)", "The chart's code loads only when the placeholder scrolls into view.", 1),
            ("@placeholder", "The placeholder shows before loading starts; it's also what the viewport trigger watches.", 1),
            ("@loading (minimum 300ms)", "The loading block shows for at least 300 milliseconds to avoid flicker.", 1),
        ],
    )],
)

problem(
    id="ng-component-test",
    title="Unit Testing a Component",
    difficulty="Medium",
    topics=["Angular", "Testing"],
    statement="""
    Test `CounterComponent`: it starts at 0, clicking + shows 1, and the parity label updates. Use `TestBed` and query
    the rendered DOM like a user would.
    """,
    examples=[("click + once", "text contains 'Count: 1 (odd)'", None)],
    hints=["`TestBed.createComponent` then `fixture.detectChanges()`.", "Query buttons through `fixture.nativeElement`."],
    approaches=[approach(
        name="TestBed + DOM assertions", **NG,
        idea="""
        `TestBed` compiles the standalone component in a test module. Interact through the DOM: click buttons and assert on visible text. That tests behaviour, not implementation details. `detectChanges` (or `whenStable` in zoneless apps) updates the view after each action.
        """,
        files=[
            file("counter.component.spec.ts", '''
                import { TestBed } from '@angular/core/testing';
                import { CounterComponent } from './counter.component';

                describe('CounterComponent', () => {
                  it('increments and updates parity', () => {
                    const fixture = TestBed.createComponent(CounterComponent);
                    fixture.detectChanges();
                    const el: HTMLElement = fixture.nativeElement;
                    expect(el.textContent).toContain('Count: 0 (even)');

                    const plus = Array.from(el.querySelectorAll('button')).find((b) => b.textContent?.trim() === '+');
                    plus?.click();
                    fixture.detectChanges();

                    expect(el.textContent).toContain('Count: 1 (odd)');
                  });
                });
            '''),
            file("counter.component.ts", '''
                import { Component, computed, signal } from '@angular/core';

                @Component({
                  selector: 'app-counter',
                  template: `
                    <p>Count: {{ count() }} ({{ parity() }})</p>
                    <button (click)="count.set(count() - 1)">−</button>
                    <button (click)="count.set(count() + 1)">+</button>
                  `,
                })
                export class CounterComponent {
                  readonly count = signal(0);
                  readonly parity = computed(() => (this.count() % 2 === 0 ? 'even' : 'odd'));
                }
            '''),
        ],
        steps=[
            ("TestBed.createComponent", "createComponent instantiates the standalone component inside a test environment.", 0),
            ("fixture.detectChanges()", "detectChanges renders the template so we can inspect the DOM.", 0),
            ("toContain('Count: 0 (even)')", "Assert on visible text, exactly what the user sees.", 0),
            ("plus?.click()", "Find the plus button and click it like a user would.", 0),
            ("toContain('Count: 1 (odd)')", "After re-rendering, both the count and the derived parity updated.", 0),
        ],
    )],
)

problem(
    id="ng-ai-chat-stream",
    title="Streaming AI Chat UI",
    difficulty="Medium",
    topics=["Angular", "Signals", "SSE", "AI Engineering"],
    statement="""
    Build a chat component that sends a question to `/api/chat/stream?q=...` (Server-Sent Events) and renders the
    answer token by token as it arrives, disables input while streaming, and closes the stream when done or destroyed.
    """,
    examples=[("ask 'What is RAG?'", "the answer appears word by word; the input re-enables at the end", None)],
    hints=["`EventSource` receives named SSE events.", "Append tokens to a signal; clean up in `DestroyRef.onDestroy`."],
    approaches=[approach(
        name="EventSource + signals", **NG,
        idea="""
        The browser's `EventSource` connects to an SSE endpoint and fires a handler per named event. Each `token` event appends text to an `answer` signal, so the view updates live. The `done` event, an error, or the component being destroyed closes the connection.

        This pairs with the Spring Boot SSE exercise to give an end-to-end streaming LLM feature.
        """,
        files=[file("chat.component.ts", '''
            import { Component, DestroyRef, inject, signal } from '@angular/core';
            import { FormsModule } from '@angular/forms';

            @Component({
              selector: 'app-chat',
              imports: [FormsModule],
              template: `
                <form (ngSubmit)="ask()">
                  <input name="q" [(ngModel)]="question" [disabled]="streaming()" placeholder="Ask anything…" />
                  <button type="submit" [disabled]="streaming() || !question">Send</button>
                </form>
                <p class="answer" aria-live="polite">{{ answer() }}@if (streaming()) {<span class="cursor">▍</span>}</p>
              `,
            })
            export class ChatComponent {
              question = '';
              readonly answer = signal('');
              readonly streaming = signal(false);
              private source?: EventSource;

              constructor() {
                inject(DestroyRef).onDestroy(() => this.source?.close());
              }

              ask(): void {
                this.source?.close();
                this.answer.set('');
                this.streaming.set(true);
                const source = new EventSource(`/api/chat/stream?q=${encodeURIComponent(this.question)}`);
                source.addEventListener('token', (e) => this.answer.update((a) => a + (e as MessageEvent).data));
                source.addEventListener('done', () => this.finish());
                source.onerror = () => this.finish();
                this.source = source;
              }

              private finish(): void {
                this.source?.close();
                this.streaming.set(false);
              }
            }
        ''')],
        steps=[
            ("[(ngModel)]=\"question\"", "Two-way binding keeps the question field in sync. It's disabled while an answer streams."),
            ("aria-live=\"polite\"", "aria-live lets screen readers announce the growing answer."),
            ("signal('')", "The answer is a signal that grows token by token."),
            ("onDestroy(() => this.source?.close())", "Close the connection if the user navigates away mid-answer."),
            ("new EventSource", "EventSource opens the Server-Sent Events stream. Always URL-encode user input."),
            ("addEventListener('token'", "Every token event appends its text, and the view updates instantly."),
            ("addEventListener('done'", "The done event or any error ends the stream and re-enables the form."),
        ],
    )],
)
