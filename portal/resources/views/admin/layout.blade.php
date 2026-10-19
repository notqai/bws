<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>@yield('title') | BWS Portal</title>
<link rel="icon" href="{{ asset('favicon.svg') }}" type="image/svg+xml">
<link rel="stylesheet" href="{{ asset('css/admin.css') }}?v={{ filemtime(public_path('css/admin.css')) }}">
</head>
<body>
<header class="bar">
  <a class="brand" href="{{ url('/admin') }}"><img src="{{ asset('logo-white.svg') }}" alt="BWS Engineering" width="72" height="48"><span>Portal</span></a>
  @auth
  <nav aria-label="Admin">
    <a href="{{ route('admin.applications.index') }}" @class(['on' => request()->routeIs('admin.applications.*')])>Applications</a>
    <a href="{{ route('admin.enquiries.index') }}" @class(['on' => request()->routeIs('admin.enquiries.*')])>Enquiries</a>
    <a href="{{ route('admin.vacancies.index') }}" @class(['on' => request()->routeIs('admin.vacancies.*')])>Vacancies</a>
    <a href="{{ route('admin.hse.index') }}" @class(['on' => request()->routeIs('admin.hse.*')])>HSE figures</a>
  </nav>
  <form method="POST" action="{{ route('admin.logout') }}" class="logout">@csrf<button type="submit">Log out <span class="who">{{ auth()->user()->name }}</span></button></form>
  @endauth
</header>
<main class="wrap">
  @if (session('status'))<p class="flash" role="status">{{ session('status') }}</p>@endif
  @yield('content')
</main>
</body>
</html>
