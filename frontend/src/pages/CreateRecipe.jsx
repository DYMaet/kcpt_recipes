import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { myRecipesApi, ingredientsApi } from '../api';

export default function CreateRecipe() {
  const [ingredients, setIngredients] = useState([]);
  const [form, setForm] = useState({ title: '', description: '', calories: '', cook_time: '', image_url: '', is_public: true, ingredients: [] });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    ingredientsApi.list().then(r => setIngredients(r.data.ingredients));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
    if (errors[name]) setErrors({ ...errors, [name]: '' });
  };

  const handleIngredientChange = (ingId, field, value) => {
    const newIngs = form.ingredients.map(i => i.ingredient_id === ingId ? { ...i, [field]: value } : i);
    setForm({ ...form, ingredients: newIngs });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = {};
    if (!form.title) newErrors.title = 'Обязательно';
    if (!form.description) newErrors.description = 'Обязательно';
    if (!form.calories) newErrors.calories = 'Обязательно';
    if (!form.cook_time) newErrors.cook_time = 'Обязательно';
    if (form.ingredients.length === 0) newErrors.ingredients = 'Добавьте ингредиенты';
    if (Object.keys(newErrors).length) return setErrors(newErrors);

    setLoading(true);
    try {
      const { data } = await myRecipesApi.create({
        ...form,
        calories: +form.calories,
        cook_time: +form.cook_time,
        ingredients: form.ingredients.map(i => ({ ingredient_id: +i.ingredient_id, quantity: i.quantity, unit: i.unit }))
      });
      navigate(`/recipe/${data.id}`);
    } catch (e) {
      if (e.response?.data?.errors) setErrors(e.response.data.errors);
      else alert(e.response?.data?.message || 'Ошибка');
    }
    setLoading(false);
  };

  const addIngredient = () => {
    setForm({ ...form, ingredients: [...form.ingredients, { ingredient_id: '', quantity: '', unit: '' }] });
  };

  const removeIngredient = (idx) => {
    setForm({ ...form, ingredients: form.ingredients.filter((_, i) => i !== idx) });
  };

  return (
    <div className="create-recipe-page">
      <h1>Создать рецепт</h1>
      <form onSubmit={handleSubmit} className="recipe-form">
        <div className="form-group">
          <label>Название *</label>
          <input name="title" value={form.title} onChange={handleChange} />
          {errors.title && <span className="error">{errors.title}</span>}
        </div>
        <div className="form-group">
          <label>Описание *</label>
          <textarea name="description" value={form.description} onChange={handleChange} />
          {errors.description && <span className="error">{errors.description}</span>}
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Калории *</label>
            <input type="number" name="calories" value={form.calories} onChange={handleChange} />
            {errors.calories && <span className="error">{errors.calories}</span>}
          </div>
          <div className="form-group">
            <label>Время (мин) *</label>
            <input type="number" name="cook_time" value={form.cook_time} onChange={handleChange} />
            {errors.cook_time && <span className="error">{errors.cook_time}</span>}
          </div>
        </div>
        <div className="form-group">
          <label>URL изображения</label>
          <input name="image_url" value={form.image_url} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>Публичный</label>
          <input type="checkbox" name="is_public" checked={form.is_public} onChange={e => setForm({ ...form, is_public: e.target.checked })} />
        </div>

        <h3>Ингредиенты</h3>
        {errors.ingredients && <span className="error">{errors.ingredients}</span>}
        {form.ingredients.map((ing, idx) => (
          <div key={idx} className="ingredient-row">
            <select value={ing.ingredient_id} onChange={e => handleIngredientChange(ing.ingredient_id, 'ingredient_id', e.target.value)} required>
              <option value="">Выберите</option>
              {ingredients.map(i => <option key={i.id} value={i.id}>{i.name}</option>)}
            </select>
            <input type="text" placeholder="Количество" value={ing.quantity} onChange={e => handleIngredientChange(ing.ingredient_id, 'quantity', e.target.value)} />
            <input type="text" placeholder="Ед." value={ing.unit} onChange={e => handleIngredientChange(ing.ingredient_id, 'unit', e.target.value)} />
            <button type="button" onClick={() => removeIngredient(idx)}>×</button>
          </div>
        ))}
        <button type="button" onClick={addIngredient}>+ Ингредиент</button>

        {errors.ingredients && <span className="error">{errors.ingredients}</span>}
        <button type="submit" disabled={loading} className="btn btn-primary">{loading ? 'Сохранение...' : 'Создать'}</button>
      </form>
    </div>
  );
}