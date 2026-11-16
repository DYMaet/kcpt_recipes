import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import { useEffect, useState } from 'react';
import './App.css';

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  return user ? children : <Navigate to="/login" />;
}

function PublicOnly({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  return user ? <Navigate to="/" /> : children;
}

function Layout({ children }) {
  const { user, logout } = useAuth();
  return (
    <div className="app">
      <header className="header">
        <h1><a href="/">Рецепты</a></h1>
        <nav>
          <a href="/">Все рецепты</a>
          {user && (
            <>
              <a href="/my-recipes">Мои рецепты</a>
              <a href="/constructor">Конструктор</a>
              <a href="/create-recipe">Создать</a>
              <button onClick={logout} className="btn-logout">Выйти</button>
            </>
          )}
          {!user && (
            <>
              <a href="/login">Войти</a>
              <a href="/register">Регистрация</a>
            </>
          )}
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}

function AppRoutes() {
  const { user } = useAuth();
  return (
    <Routes>
      <Route path="/" element={<Layout><RecipeList /></Layout>} />
      <Route path="/recipe/:id" element={<Layout><RecipeView /></Layout>} />
      <Route path="/constructor" element={<Layout><Constructor /></Layout>} />
      <Route path="/my-recipes" element={<PrivateRoute><Layout><MyRecipes /></Layout></PrivateRoute>} />
      <Route path="/create-recipe" element={<PrivateRoute><Layout><CreateRecipe /></Layout></PrivateRoute>} />
      <Route path="/edit-recipe/:id" element={<PrivateRoute><Layout><EditRecipe /></Layout></PrivateRoute>} />
      <Route path="/login" element={<PublicOnly><Layout><Login /></Layout></PublicOnly>} />
      <Route path="/register" element={<PublicOnly><Layout><Register /></Layout></PublicOnly>} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

import RecipeList from './pages/RecipeList';
import RecipeView from './pages/RecipeView';
import MyRecipes from './pages/MyRecipes';
import CreateRecipe from './pages/CreateRecipe';
import EditRecipe from './pages/EditRecipe';
import Constructor from './pages/Constructor';
import Login from './pages/Login';
import Register from './pages/Register';

export default App;