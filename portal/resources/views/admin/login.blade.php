@extends('admin.layout')
@section('title', 'Log in')
@section('content')
<div class="card narrow">
  <h1>Log in</h1>
  <p class="muted">BWS Engineering staff only.</p>
  <form method="POST" action="{{ url('/login') }}" class="stack">
    @csrf
    <label>Email <input type="email" name="email" value="{{ old('email') }}" autocomplete="username" required autofocus></label>
    <label>Password <input type="password" name="password" autocomplete="current-password" required></label>
    @error('email')<p class="error" role="alert">{{ $message }}</p>@enderror
    <label class="check"><input type="checkbox" name="remember" value="1"> Keep me logged in on this computer</label>
    <button class="btn" type="submit">Log in</button>
  </form>
</div>
@endsection
