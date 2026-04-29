# How Django REST Framework Routers Work

This note explains how `DefaultRouter` works in your Django URL configuration.

---

## 1. What is a router?

In Django REST Framework, a **router** automatically creates URL patterns for a `ViewSet`.

Instead of manually writing many `path()` entries, you register a `ViewSet` once, and the router generates the common REST API routes for you.

Example:

```python
router = DefaultRouter()
router.register(r'events', EventViewSet)
```

This tells Django REST Framework:

> Create API routes for `events`, and let `EventViewSet` handle them.

---

## 2. Why use a router?

Without a router, you may need to manually write URLs like this:

```python
path('api/public/events/', EventListView.as_view()),
path('api/public/events/<int:pk>/', EventDetailView.as_view()),
```

That becomes repetitive when you have many resources.

With a router, this is enough:

```python
router.register(r'events', EventViewSet)
```

The router creates the list and detail routes automatically.

---

## 3. What routes does the router create?

For this line:

```python
router.register(r'events', EventViewSet)
```

and this URL include:

```python
path('api/public/', include(router.urls))
```

Django REST Framework creates routes like:

```text
GET     /api/public/events/        -> list events
POST    /api/public/events/        -> create an event

GET     /api/public/events/1/      -> get event with ID 1
PUT     /api/public/events/1/      -> replace event with ID 1
PATCH   /api/public/events/1/      -> partially update event with ID 1
DELETE  /api/public/events/1/      -> delete event with ID 1
```

The exact routes depend on what actions your `ViewSet` supports.

---

## 4. How does the router know what function to call?

The router maps HTTP methods to `ViewSet` actions.

A typical `ModelViewSet` has actions like:

```python
list()            # GET /events/
create()          # POST /events/
retrieve()        # GET /events/1/
update()          # PUT /events/1/
partial_update()  # PATCH /events/1/
destroy()         # DELETE /events/1/
```

So when a request comes in:

```text
GET /api/public/events/
```

the router calls:

```python
EventViewSet.list()
```

And when this request comes in:

```text
GET /api/public/events/5/
```

the router calls:

```python
EventViewSet.retrieve()
```

---

## 5. What does `r'events'` mean?

In this line:

```python
router.register(r'events', EventViewSet)
```

`r'events'` is the URL prefix.

By itself, it creates:

```text
/events/
```

But because your code includes the router under:

```python
path('api/public/', include(router.urls))
```

the final route becomes:

```text
/api/public/events/
```

So this:

```python
router.register(r'venues', VenueViewSet)
```

becomes:

```text
/api/public/venues/
```

And this:

```python
router.register(r'news', PublicNewsArticleViewSet, basename='publicnews')
```

becomes:

```text
/api/public/news/
```

---

## 6. What is `basename`?

Sometimes Django REST Framework can automatically guess a route name from the `queryset` inside the `ViewSet`.

Example:

```python
class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
```

Because the `queryset` uses the `Event` model, DRF can guess route names like:

```text
event-list
event-detail
```

But if a `ViewSet` does not have a normal `queryset`, DRF may not know what name to use.

That is why you may see:

```python
router.register(r'news', PublicNewsArticleViewSet, basename='publicnews')
```

The `basename` tells DRF what internal name to use for URL reversing.

This creates route names like:

```text
publicnews-list
publicnews-detail
```

---

## 7. Why are there two routers?

Your code has two routers:

```python
router = DefaultRouter()
admin_router = DefaultRouter()
```

They are used to separate public API routes from admin API routes.

The public router is included here:

```python
path('api/public/', include(router.urls))
```

So routes registered on `router` become:

```text
/api/public/events/
/api/public/news/
/api/public/venues/
```

The admin router is included here:

```python
path('api/admin/', include(admin_router.urls))
```

So routes registered on `admin_router` become:

```text
/api/admin/news/
/api/admin/ai-recaps/
```

This keeps public and admin endpoints organized separately.

---

## 8. Router routes vs manual `path()` routes

Not every endpoint uses a router.

Router-based endpoints are good for resources like:

```text
events
venues
news
athletes
registrations
match-results
```

These usually need standard CRUD operations.

Manual `path()` routes are better for custom actions like:

```python
path('api/auth/login/', CookieTokenObtainPairView.as_view())
path('api/auth/logout/', LogoutView.as_view())
path('api/public/tryouts/send-otp/', TryoutSendOtpView.as_view())
path('api/public/rooney/query/', RooneyQueryView.as_view())
```

These are specific actions, not standard REST resources.

For example, `login` is not a normal object list or detail route, so it is written manually.

---

## 9. Simple analogy

A router is like a receptionist.

You tell it:

```text
events -> EventViewSet
venues -> VenueViewSet
news   -> PublicNewsArticleViewSet
```

Then when requests arrive, it sends them to the correct place.

Example:

```text
GET /api/public/events/
```

goes to:

```python
EventViewSet.list()
```

And:

```text
GET /api/public/events/5/
```

goes to:

```python
EventViewSet.retrieve()
```

---

## 10. Main idea

This line:

```python
router.register(r'events', EventViewSet)
```

means:

> Create standard REST API routes for `events`.

This line:

```python
path('api/public/', include(router.urls))
```

means:

> Put all router-generated routes under `/api/public/`.

Together, they create endpoints such as:

```text
/api/public/events/
/api/public/events/1/
```

So the router saves you from writing every URL manually.
