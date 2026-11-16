import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    if (errors[e.target.name]) setErrors({ ...errors, [e.target.name]: '' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = {};
    if (!form.email) newErrors.email = 'Обязательно';
    if (!form.password) newErrors.password = 'Обязательно';
    if (Object.keys(newErrors).length) return setErrors(newErrors);

    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate('/');
    } catch (e) {
      if (e.response?.data?.errors) setErrors(e.response.data.errors);
      else setErrors({ form: e.response?.data?.message || 'Ошибка входа' });
    }
    setLoading(false);
  };

  return (
    <div className="auth-page">
      <h1>Вход</h1>
      <form onSubmit={handleSubmit} className="auth-form">
        {errors.form && <div className="error">{errors.form}</div>}
        <div className="form-group">
          <label>Email *</label>
          <input type="email" name="email" value={form.email} onChange={handleChange} />
          {errors.email && <span className="error">{errors.email}</span>}
        </div>
        <div className="form-group">
          <label>Пароль *</label>
          <input type="password" name="password" value={form.password} onChange={handleChange} />
          {errors.password && <span className="error">{errors.password}</span>}
        </div>
        <button type="submit" disabled={loading} className="btn btn-primary">{loading ? 'Вход...' : 'Войти'}</button>
      </form>
      <p>Нет аккаунта? <Link to="/register">Регистрация</Link></p>
    </div>
  );
}