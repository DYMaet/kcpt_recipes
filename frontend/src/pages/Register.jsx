import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function Register() {
  const [form, setForm] = useState({ email: '', name: '', password: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    if (errors[e.target.name]) setErrors({ ...errors, [e.target.name]: '' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = {};
    if (!form.email) newErrors.email = 'Обязательно';
    else if (!form.email.includes('@')) newErrors.email = 'Неверный email';
    if (!form.name) newErrors.name = 'Обязательно';
    if (!form.password) newErrors.password = 'Обязательно';
    else if (form.password.length < 5) newErrors.password = 'Мин. 5 символов';
    else if (!/[a-z]/.test(form.password)) newErrors.password = 'Нужна строчная';
    else if (!/[A-Z]/.test(form.password)) newErrors.password = 'Нужна заглавная';
    else if (!/[-_#$]/.test(form.password)) newErrors.password = 'Нужен спецсимвол (- _ # $)';
    if (Object.keys(newErrors).length) return setErrors(newErrors);

    setLoading(true);
    try {
      await register(form.email, form.name, form.password);
      navigate('/login');
    } catch (e) {
      if (e.response?.data?.errors) setErrors(e.response.data.errors);
      else setErrors({ form: e.response?.data?.message || 'Ошибка регистрации' });
    }
    setLoading(false);
  };

  return (
    <div className="auth-page">
      <h1>Регистрация</h1>
      <form onSubmit={handleSubmit} className="auth-form">
        {errors.form && <div className="error">{errors.form}</div>}
        <div className="form-group">
          <label>Email *</label>
          <input type="email" name="email" value={form.email} onChange={handleChange} />
          {errors.email && <span className="error">{errors.email}</span>}
        </div>
        <div className="form-group">
          <label>Имя *</label>
          <input name="name" value={form.name} onChange={handleChange} />
          {errors.name && <span className="error">{errors.name}</span>}
        </div>
        <div className="form-group">
          <label>Пароль * (мин. 5, строчная, заглавная, спецсимвол -_#$)</label>
          <input type="password" name="password" value={form.password} onChange={handleChange} />
          {errors.password && <span className="error">{errors.password}</span>}
        </div>
        <button type="submit" disabled={loading} className="btn btn-primary">{loading ? 'Регистрация...' : 'Зарегистрироваться'}</button>
      </form>
      <p>Есть аккаунт? <Link to="/login">Войти</Link></p>
    </div>
  );
}